## 消费者分区

* Kafka 的消息组织方式实际上是三级结构：主题 - 分区 - 消息。
* 主题下的每条消息只会保存在某一个分区中，而不会在多个分区中被保存多份
![messages-with-without-keys](messages-with-without-keys.png)
### 为什么分区要这么设计呢
* 其实分区的作用就是提供负载均衡的能力，主要目的是为了提高kafka的高伸缩性

### 分区策略
所谓的分区策略其实就是生产者将消息发送到哪个分区的算法，kafka提供了默认的分区策略，也支持自定的分区策略

  * 轮询分区策略
    * 轮询策略有非常优秀的负载均衡表现，它总是能保证消息最大限度地被平均分配到所有分区上，故默认情况下它是最合理的分区策略，也是我们最常用的分区策略之一。
  * 随机策略
    * 随机就是我们随意地将消息放置到任意一个分区上
  * 按消息键保序策略
    * 一旦消息被定义了 Key，那么你就可以保证同一个 Key 的所有消息都进入到相同的分区里面，由于每个分区下的消息处理都是有顺序的，故这个策略被称为按消息键保序策略


## 引言
我们平常使用kafka发消息,那么kafka是怎么发送到broker，生产者内部都做哪些工作？
有哪些好的设计值得我们借鉴，我们带着这些问题，跟着kafka的生产者源码看看kafka是怎么设计的

0.10.2 的 Kafka 中，其 Client 端是由 Java 实现，Server 端是由 Scala 来实现的

## 名词解释
* Topics 
* Partitions 
* Offsets
* Broker
* Replication
* Leader
* Producers and Consumers 生产者和消费者

## 例子

```

public class Producer {
    private final KafkaProducer<Integer, String> producer;
  
    public Producer(final String topic,
                    final String transactionalId,
                    final boolean enableIdempotency,
                    final int transactionTimeoutMs
                    ) {
        Properties props = new Properties();
        props.put(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG, KafkaProperties.KAFKA_SERVER_URL + ":" + KafkaProperties.KAFKA_SERVER_PORT);
        props.put(ProducerConfig.CLIENT_ID_CONFIG, "DemoProducer");
        props.put(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG, IntegerSerializer.class.getName());
        props.put(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG, StringSerializer.class.getName());
        if (transactionTimeoutMs > 0) {
            props.put(ProducerConfig.TRANSACTION_TIMEOUT_CONFIG, transactionTimeoutMs);
        }
        if (transactionalId != null) {
            props.put(ProducerConfig.TRANSACTIONAL_ID_CONFIG, transactionalId);
        }
        props.put(ProducerConfig.ENABLE_IDEMPOTENCE_CONFIG, enableIdempotency);
        // 重点 分析1
        producer = new KafkaProducer<>(props);
    }


    private void sendAsync(final int messageKey, final String messageStr, final long currentTimeMs) {
      // 重点 分析2
        this.producer.send(new ProducerRecord<>(topic,
                        messageKey,
                        messageStr),
                new DemoCallBack(currentTimeMs, messageKey, messageStr));
    }

}

class DemoCallBack implements Callback {

    private final long startTime;
    private final int key;
    private final String message;

    public DemoCallBack(long startTime, int key, String message) {
        this.startTime = startTime;
        this.key = key;
        this.message = message;
    }

    public void onCompletion(RecordMetadata metadata, Exception exception) {
        long elapsedTime = System.currentTimeMillis() - startTime;
        if (metadata != null) {
            System.out.println(
                "message(" + key + ", " + message + ") sent to partition(" + metadata.partition() +
                    "), " +
                    "offset(" + metadata.offset() + ") in " + elapsedTime + " ms");
        } else {
            exception.printStackTrace();
        }
    }
}

```

说明:
* 根据上面的例子，我们重点分析：
  * KafkaProducer的构造方法
  * producer.send()真正的发送方法

## 架构图
kafka的生产者采用生产者-消费者模式,在调用producer.send()的时候，并没有真正的发送到kafka的broker服务器上，而是先把消息保存到内存,然后有sender线程去发送到poll,
主线程产生消息,sender线程是发送消费
1. 


## KafkaProducer的构造方法

```
KafkaProducer(ProducerConfig config,
                  Serializer<K> keySerializer,
                  Serializer<V> valueSerializer,
                  ProducerMetadata metadata,
                  KafkaClient kafkaClient,
                  ProducerInterceptors<K, V> interceptors,
                  Time time) {
        try {
            // 生产者的配置项
            this.producerConfig = config;
            this.time = time;
            // 事务id
            String transactionalId = config.getString(ProducerConfig.TRANSACTIONAL_ID_CONFIG);
            // 客户端id
            this.clientId = config.getString(ProducerConfig.CLIENT_ID_CONFIG);

            // 日志
            LogContext logContext;
            if (transactionalId == null)
                logContext = new LogContext(String.format("[Producer clientId=%s] ", clientId));
            else
                logContext = new LogContext(String.format("[Producer clientId=%s, transactionalId=%s] ", clientId, transactionalId));
            log = logContext.logger(KafkaProducer.class);
            log.trace("Starting the Kafka producer");

            // 配置生产者监控
            Map<String, String> metricTags = Collections.singletonMap("client-id", clientId);
            MetricConfig metricConfig = new MetricConfig().samples(config.getInt(ProducerConfig.METRICS_NUM_SAMPLES_CONFIG))
                    .timeWindow(config.getLong(ProducerConfig.METRICS_SAMPLE_WINDOW_MS_CONFIG), TimeUnit.MILLISECONDS)
                    .recordLevel(Sensor.RecordingLevel.forName(config.getString(ProducerConfig.METRICS_RECORDING_LEVEL_CONFIG)))
                    .tags(metricTags);
            List<MetricsReporter> reporters = CommonClientConfigs.metricsReporters(clientId, config);
            MetricsContext metricsContext = new KafkaMetricsContext(JMX_PREFIX,
                    config.originalsWithPrefix(CommonClientConfigs.METRICS_CONTEXT_PREFIX));
            this.metrics = new Metrics(metricConfig, reporters, time, metricsContext);
            this.producerMetrics = new KafkaProducerMetrics(metrics);

            // 设置对应的分区器
            this.partitioner = config.getConfiguredInstance(
                    ProducerConfig.PARTITIONER_CLASS_CONFIG,
                    Partitioner.class,
                    Collections.singletonMap(ProducerConfig.CLIENT_ID_CONFIG, clientId));
            warnIfPartitionerDeprecated();
            this.partitionerIgnoreKeys = config.getBoolean(ProducerConfig.PARTITIONER_IGNORE_KEYS_CONFIG);
            // 失败重试的退避时间
            long retryBackoffMs = config.getLong(ProducerConfig.RETRY_BACKOFF_MS_CONFIG);

            // 序列化
            if (keySerializer == null) {
                this.keySerializer = config.getConfiguredInstance(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG,
                                                                                         Serializer.class);
                this.keySerializer.configure(config.originals(Collections.singletonMap(ProducerConfig.CLIENT_ID_CONFIG, clientId)), true);
            } else {
                config.ignore(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG);
                this.keySerializer = keySerializer;
            }
            if (valueSerializer == null) {
                this.valueSerializer = config.getConfiguredInstance(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG,
                                                                                           Serializer.class);
                this.valueSerializer.configure(config.originals(Collections.singletonMap(ProducerConfig.CLIENT_ID_CONFIG, clientId)), false);
            } else {
                config.ignore(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG);
                this.valueSerializer = valueSerializer;
            }

            // 配置生产者的拦截器
            List<ProducerInterceptor<K, V>> interceptorList = (List) config.getConfiguredInstances(
                    ProducerConfig.INTERCEPTOR_CLASSES_CONFIG,
                    ProducerInterceptor.class,
                    Collections.singletonMap(ProducerConfig.CLIENT_ID_CONFIG, clientId));
            if (interceptors != null)
                this.interceptors = interceptors;
            else
                this.interceptors = new ProducerInterceptors<>(interceptorList);

            // 集群资源变更监听器
            ClusterResourceListeners clusterResourceListeners = configureClusterResourceListeners(this.keySerializer,
                    this.valueSerializer, interceptorList, reporters);
            //设置消息的最大的长度，默认1M，生产环境可以提高到10M
            this.maxRequestSize = config.getInt(ProducerConfig.MAX_REQUEST_SIZE_CONFIG);
            // 设置发送消息的缓冲区的大小
            this.totalMemorySize = config.getLong(ProducerConfig.BUFFER_MEMORY_CONFIG);
            // 压缩类型
            this.compressionType = CompressionType.forName(config.getString(ProducerConfig.COMPRESSION_TYPE_CONFIG));
            // 最大阻塞时间
            this.maxBlockTimeMs = config.getLong(ProducerConfig.MAX_BLOCK_MS_CONFIG);
            // 投递的超时时间
            int deliveryTimeoutMs = configureDeliveryTimeout(config, log);

            this.apiVersions = new ApiVersions();
            // 事务管理器
            this.transactionManager = configureTransactionState(config, logContext);
            // There is no need to do work required for adaptive partitioning, if we use a custom partitioner.
            boolean enableAdaptivePartitioning = partitioner == null &&
                config.getBoolean(ProducerConfig.PARTITIONER_ADPATIVE_PARTITIONING_ENABLE_CONFIG);

            // 分区器的配置
            RecordAccumulator.PartitionerConfig partitionerConfig = new RecordAccumulator.PartitionerConfig(
                enableAdaptivePartitioning,
                config.getLong(ProducerConfig.PARTITIONER_AVAILABILITY_TIMEOUT_MS_CONFIG)
            );

            // 按Kafka生产者配置配置大小。Size可以设置为0以显式禁用批处理，这实际上意味着使用批处理大小为1
            int batchSize = Math.max(1, config.getInt(ProducerConfig.BATCH_SIZE_CONFIG));
            // 累加器
            this.accumulator = new RecordAccumulator(logContext,
                    batchSize,
                    this.compressionType,
                    lingerMs(config),
                    retryBackoffMs,
                    deliveryTimeoutMs,
                    partitionerConfig,
                    metrics,
                    PRODUCER_METRIC_GROUP_NAME,
                    time,
                    apiVersions,
                    transactionManager,
                    new BufferPool(this.totalMemorySize, batchSize, metrics, time, PRODUCER_METRIC_GROUP_NAME));

            // 服务端配置
            List<InetSocketAddress> addresses = ClientUtils.parseAndValidateAddresses(
                    config.getList(ProducerConfig.BOOTSTRAP_SERVERS_CONFIG),
                    config.getString(ProducerConfig.CLIENT_DNS_LOOKUP_CONFIG));

            // 生产端的元信息配置
            if (metadata != null) {
                this.metadata = metadata;
            } else {
                this.metadata = new ProducerMetadata(retryBackoffMs,
                        config.getLong(ProducerConfig.METADATA_MAX_AGE_CONFIG),
                        config.getLong(ProducerConfig.METADATA_MAX_IDLE_CONFIG),
                        logContext,
                        clusterResourceListeners,
                        Time.SYSTEM);
                this.metadata.bootstrap(addresses);
            }
            this.errors = this.metrics.sensor("errors");

            // 创建发送器
            this.sender = newSender(logContext, kafkaClient, this.metadata);
            String ioThreadName = NETWORK_THREAD_PREFIX + " | " + clientId;
            this.ioThread = new KafkaThread(ioThreadName, this.sender, true);
            this.ioThread.start();

            config.logUnused();
            // 注册mb的相关的
            AppInfoParser.registerAppInfo(JMX_PREFIX, clientId, metrics, time.milliseconds());
            log.debug("Kafka producer started");
        } catch (Throwable t) {
            // call close methods if internal objects are already constructed this is to prevent resource leak. see KAFKA-2121
            close(Duration.ofMillis(0), true);
            // now propagate the exception
            throw new KafkaException("Failed to construct kafka producer", t);
        }
    }

```

说明：
* 配置生产者的监控
* 设置对应的分区器
* 配置发送失败的重试时间
* key和value的序列化
* 配置生产者的拦截器
* 分区器的配置
* 初始化累加器
* 生产端的元信息配置
* 创建发送器并且启动的IO线程


## producer#send

```
private Future<RecordMetadata> doSend(ProducerRecord<K, V> record, Callback callback) {
        // Append回调处理以下内容:
        //  - 在完成时调用拦截器和用户回调
        //  - 记住在RecordAccumulator.append中计算的分区
        AppendCallbacks<K, V> appendCallbacks = new AppendCallbacks<K, V>(callback, this.interceptors, record);

        try {
            throwIfProducerClosed();
            // first make sure the metadata for the topic is available
            long nowMs = time.milliseconds();
            ClusterAndWaitTime clusterAndWaitTime;
            try {
                clusterAndWaitTime = waitOnMetadata(record.topic(), record.partition(), nowMs, maxBlockTimeMs);
            } catch (KafkaException e) {
                if (metadata.isClosed())
                    throw new KafkaException("Producer closed while send in progress", e);
                throw e;
            }
            nowMs += clusterAndWaitTime.waitedOnMetadataMs;
            long remainingWaitMs = Math.max(0, maxBlockTimeMs - clusterAndWaitTime.waitedOnMetadataMs);
            Cluster cluster = clusterAndWaitTime.cluster;
            byte[] serializedKey;
            try {
                serializedKey = keySerializer.serialize(record.topic(), record.headers(), record.key());
            } catch (ClassCastException cce) {
                throw new SerializationException("Can't convert key of class " + record.key().getClass().getName() +
                        " to class " + producerConfig.getClass(ProducerConfig.KEY_SERIALIZER_CLASS_CONFIG).getName() +
                        " specified in key.serializer", cce);
            }
            byte[] serializedValue;
            try {
                serializedValue = valueSerializer.serialize(record.topic(), record.headers(), record.value());
            } catch (ClassCastException cce) {
                throw new SerializationException("Can't convert value of class " + record.value().getClass().getName() +
                        " to class " + producerConfig.getClass(ProducerConfig.VALUE_SERIALIZER_CLASS_CONFIG).getName() +
                        " specified in value.serializer", cce);
            }

            // 尝试计算分区，但注意，在调用之后，它可以是RecordMetadata。UNKNOWN_PARTITION
            // 这意味着RecordAccumulator将使用内置逻辑(可能会考虑代理负载，每个分区产生的数据量等)选择一个分区.
            int partition = partition(record, serializedKey, serializedValue, cluster);

            setReadOnly(record.headers());
            Header[] headers = record.headers().toArray();

            int serializedSize = AbstractRecords.estimateSizeInBytesUpperBound(apiVersions.maxUsableProduceMagic(),
                    compressionType, serializedKey, serializedValue, headers);
            ensureValidRecordSize(serializedSize);
            long timestamp = record.timestamp() == null ? nowMs : record.timestamp();

            // 自定义分区器可以利用onNewBatch回调.
            boolean abortOnNewBatch = partitioner != null;

            // 将记录追加到累加器。注意，实际的分区可以在那里计算，并且可以通过appendCallbacks.topicPartition进行访问.
            RecordAccumulator.RecordAppendResult result = accumulator.append(record.topic(), partition, timestamp, serializedKey,
                    serializedValue, headers, appendCallbacks, remainingWaitMs, abortOnNewBatch, nowMs, cluster);
            assert appendCallbacks.getPartition() != RecordMetadata.UNKNOWN_PARTITION;

            if (result.abortForNewBatch) {
                int prevPartition = partition;
                onNewBatch(record.topic(), cluster, prevPartition);
                partition = partition(record, serializedKey, serializedValue, cluster);
                if (log.isTraceEnabled()) {
                    log.trace("Retrying append due to new batch creation for topic {} partition {}. The old partition was {}", record.topic(), partition, prevPartition);
                }
                result = accumulator.append(record.topic(), partition, timestamp, serializedKey,
                    serializedValue, headers, appendCallbacks, remainingWaitMs, false, nowMs, cluster);
            }

            // 在累加器成功追加分区后，将其添加到事务中（如果正在进行）。我们不能在此之前执行此操作，因为该分区可能是未知的，
            // 或者当批处理关闭时初始选择的分区可能会更改（如“abortForNewBatch”所示）。请注意，“发送方”将拒绝从累加器中出队批次，直到它们被添加到事务中。
            if (transactionManager != null) {
                transactionManager.maybeAddPartition(appendCallbacks.topicPartition());
            }

            if (result.batchIsFull || result.newBatchCreated) {
                log.trace("Waking up the sender since topic {} partition {} is either full or getting a new batch", record.topic(), appendCallbacks.getPartition());
                this.sender.wakeup();
            }
            return result.future;
            // 处理异常并记录错误
            // for API exceptions return them in the future,
            // for other exceptions throw directly
        } catch (ApiException e) {
            log.debug("Exception occurred during message send:", e);
            if (callback != null) {
                TopicPartition tp = appendCallbacks.topicPartition();
                RecordMetadata nullMetadata = new RecordMetadata(tp, -1, -1, RecordBatch.NO_TIMESTAMP, -1, -1);
                callback.onCompletion(nullMetadata, e);
            }
            this.errors.record();
            this.interceptors.onSendError(record, appendCallbacks.topicPartition(), e);
            if (transactionManager != null) {
                transactionManager.maybeTransitionToErrorState(e);
            }
            return new FutureFailure(e);
        } catch (InterruptedException e) {
            this.errors.record();
            this.interceptors.onSendError(record, appendCallbacks.topicPartition(), e);
            throw new InterruptException(e);
        } catch (KafkaException e) {
            this.errors.record();
            this.interceptors.onSendError(record, appendCallbacks.topicPartition(), e);
            throw e;
        } catch (Exception e) {
            // we notify interceptor about all exceptions, since onSend is called before anything else in this method
            this.interceptors.onSendError(record, appendCallbacks.topicPartition(), e);
            throw e;
        }
    }
```
