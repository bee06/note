---
theme: healer-readable
highlight: atelier-forest-light
---
# 引言
在 Kafka 中，生产者（Producer）负责将消息发送到 Kafka 集群，是实现高效数据流动的关键组件之一。本文将从源码层面分析 Kafka 生产者的实现细节，帮助读者更好地理解 Kafka 生产者的工作原理和性能特征。

注明:
> 0.10.2 的 Kafka 中，其 Client 端是由 Java 实现，Server 端是由 Scala 来实现的

# 能学到什么
1.  Kafka 生产者是如何实现消息的发送和分发的？
2.  Kafka 生产者的代码实现中有哪些值得我们注意的细节和技巧？

#  架构图


![生产者流程-架构图.png](https://p3-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/af7a21f274ae4ae2a16bccb275b64d99~tplv-k3u1fbpfcp-watermark.image?)

从上图,我们了解到:
1. kafka的生产者采用生产者-消费者模式,生产者发送消息的过程可以分为两个阶段：
    * 第一个阶段是将待发送的消息缓存到 RecordAccumulator(记录叠加器)中
    * 第二个阶段是从 RecordAccumulator 中取出消息进行网络发送。
2. kafka的生产者其实分为三部分
    * kafkaProducer主线程
    * RecordAccumulator
    * sender线程
 
# 开始分析

## 生产者的例子

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
* 上面的例子，最关键的两个地方（尤其是send消息的）:
  * KafkaProducer的构造方法
  * producer.send消息
  


## KafkaProducer的介绍

### 组成部分

![iShot_2023-04-10_17.02.18.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/edd009ec857f4edf886557adcac55036~tplv-k3u1fbpfcp-watermark.image?)

#### 说明
1.  `producerConfig`: 存储了Kafka Producer的配置信息，包括连接的Kafka集群地址、序列化器、确认机制等参数。
1.  `metrics`: 存储了生产者的指标数据，例如发送的消息数量、成功发送的消息数量、失败的消息数量等。
1.  `sender`: 负责将消息发送到Kafka集群的组件。它会将消息转换成Kafka可识别的格式，然后将其发送到指定的分区。
1.  `recordAccumulator`: 缓存待发送的消息。生产者将消息发送到recordAccumulator后，sender从recordAccumulator中获取消息并发送到Kafka集群。
1.  `metadata`: 存储了Kafka集群中所有主题和分区的元数据信息，包括分区的leader、ISR（in-sync replicas）列表等。
1.  `interceptors`: 消息拦截器列表。生产者可以配置多个拦截器，用于在消息发送前、发送后对消息进行处理，例如添加时间戳、打印日志等。
1.  `bufferMemory`: 缓存待发送消息的总大小。如果recordAccumulator中待发送消息的大小超过了bufferMemory，则生产者将等待sender将消息发送出去，以释放recordAccumulator中的空间。
1.  `maxBlockMs`: 生产者在发送消息时，如果recordAccumulator已满，会等待sender将消息发送出去。如果sender在指定的时间内无法发送消息，则生产者会抛出异常。maxBlockMs指定了等待sender的最大时间。
1.  `requestTimeoutMs`: 生产者等待Kafka Broker的响应的最大时间。如果在指定时间内没有收到Broker的响应，则生产者会重试发送消息或抛出异常。
1.  `transactionManager`: 支持事务的生产者需要配置transactionManager。transactionManager负责管理事务的状态、事务中发送的消息等信息。

### 构造方法

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
#### 说明：
* 配置生产者的监控
* 设置对应的分区器
* 配置发送失败的重试时间
* key和value的序列化
* 配置生产者的拦截器
* 分区器的配置
* 初始化累加器
* 生产端的元信息配置
* 创建发送器并且启动的IO线程

## KafkaProducer发送消息

### 说明
* 生产者发送消息的过程可以分为两个阶段：
    * 将发送的消息缓存到 RecordAccumulator(记录叠加器)中
    * RecordAccumulator是如何存储消息的
    * sender线程取出消息进行网络发送。

### 将消息缓存到记录叠加器

#### 代码

##### send方法

```
public Future<RecordMetadata> send(ProducerRecord<K, V> record, Callback callback) {  
 
    ProducerRecord<K, V> interceptedRecord = this.interceptors.onSend(record);  
    return doSend(interceptedRecord, callback);  
}
```
##### doSend方法

```
private Future < RecordMetadata > doSend(ProducerRecord < K, V > record, Callback callback) {
    
    AppendCallbacks < K, V > appendCallbacks = new AppendCallbacks < K, V > (callback, this.interceptors, record);

    try {
       
        long nowMs = time.milliseconds();
        ClusterAndWaitTime clusterAndWaitTime = waitOnMetadata(record.topic(), record.partition(), nowMs, maxBlockTimeMs);
        
        nowMs += clusterAndWaitTime.waitedOnMetadataMs;
        long remainingWaitMs = Math.max(0, maxBlockTimeMs - clusterAndWaitTime.waitedOnMetadataMs);
        Cluster cluster = clusterAndWaitTime.cluster;
        // key和value序列化
        ....
        // 计算分区，但注意，在调用之后，它可以是RecordMetadata。UNKNOWN_PARTITION
        // 这意味着RecordAccumulator将使用内置逻辑(可能会考虑代理负载，每个分区产生的数据量等)选择一个分区.
        int partition = partition(record, serializedKey, serializedValue, cluster);

        // 将记录追加到累加器
        RecordAccumulator.RecordAppendResult result = accumulator.append(record.topic(), partition, timestamp, serializedKey,
            serializedValue, headers, appendCallbacks, remainingWaitMs, abortOnNewBatch, nowMs, cluster);
       
        // 在累加器成功追加分区后，将其添加到事务中（如果正在进行）。我们不能在此之前执行此操作，因为该分区可能是未知的，
        // 或者当批处理关闭时初始选择的分区可能会更改（如“abortForNewBatch”所示）。请注意，“发送方”将拒绝从累加器中出队批次，直到它们被添加到事务中。
        if (transactionManager != null) {
            transactionManager.maybeAddPartition(appendCallbacks.topicPartition());
        }
        // 如果累加器满了或者新创建的批次
        if (result.batchIsFull || result.newBatchCreated) {
            log.trace("Waking up the sender since topic {} partition {} is either full or getting a new batch", record.topic(), appendCallbacks.getPartition());
            // 唤醒发送器线程
            this.sender.wakeup();
        }
        return result.future;
        //处理异常并记录错误 对于 API 异常，将它们返回Future，对于其他异常直接抛出
    } catch (ApiException e) {
        
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
        this.interceptors.onSendError(record, appendCallbacks.topicPartition(), e);
        throw e;
    }
}
```
##### 说明
![iShot_2023-04-10_17.17.46.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/0be7ef57d93c445d9637f4430233196a~tplv-k3u1fbpfcp-watermark.image?)

## RecordAccumulator是如何存储消息的

```
public RecordAppendResult append(String topic,
                                     int partition,
                                     long timestamp,
                                     byte[] key,
                                     byte[] value,
                                     Header[] headers,
                                     AppendCallbacks callbacks,
                                     long maxTimeToBlock,
                                     boolean abortOnNewBatch,
                                     long nowMs,
                                     Cluster cluster) throws InterruptedException {
        // 创建或获取指定主题的 `TopicInfo` 对象，`TopicInfo` 用于跟踪与指定主题相关的信息，如分区信息、分区内的批次
        TopicInfo topicInfo = topicInfoMap.computeIfAbsent(topic, k -> new TopicInfo(logContext, k, batchSize));

        // 跟踪追加线程的数量，以确保在abortIncompleteBatches()中不会遗漏批次.
        appendsInProgress.incrementAndGet();
        ByteBuffer buffer = null;
        if (headers == null) headers = Record.EMPTY_HEADERS;
        try {
            // 循环-在遇到分区器的竞态条件时重试.
            while (true) {
                // 分区关联
                final BuiltInPartitioner.StickyPartitionInfo partitionInfo;
                final int effectivePartition;
                if (partition == RecordMetadata.UNKNOWN_PARTITION) {
                    partitionInfo = topicInfo.builtInPartitioner.peekCurrentPartitionInfo(cluster);
                    effectivePartition = partitionInfo.partition();
                } else {
                    partitionInfo = null;
                    effectivePartition = partition;
                }

                // 现在我们知道了有效分区，让调用者知道.
                setPartition(callbacks, effectivePartition);

                // 检查一下我们是否有正在生产的批次
                Deque<ProducerBatch> dq = topicInfo.batches.computeIfAbsent(effectivePartition, k -> new ArrayDeque<>());
                synchronized (dq) {
                    // 获取锁后，验证分区没有更改，然后重试.
                    if (partitionChanged(topic, topicInfo, partitionInfo, dq, nowMs, cluster))
                        continue;

                    RecordAppendResult appendResult = tryAppend(timestamp, key, value, headers, callbacks, dq, nowMs);
                    if (appendResult != null) {
                        // 如果队列中有不完整的批.
                        boolean enableSwitch = allBatchesFull(dq);
                        topicInfo.builtInPartitioner.updatePartitionInfo(partitionInfo, appendResult.appendedBytes, cluster, enableSwitch);
                        return appendResult;
                    }
                }

                // 我们没有正在进行的记录批处理，请尝试分配一个新批处理
                if (abortOnNewBatch) {
                    return new RecordAppendResult(null, false, false, true, 0);
                }

                if (buffer == null) {
                    byte maxUsableMagic = apiVersions.maxUsableProduceMagic();
                    int size = Math.max(this.batchSize, AbstractRecords.estimateSizeInBytesUpperBound(maxUsableMagic, compression, key, value, headers));
                    log.trace("Allocating a new {} byte message buffer for topic {} partition {} with remaining timeout {}ms", size, topic, partition, maxTimeToBlock);
                    // 如果耗尽缓冲区空间，重新分配，此调用可能阻塞.
                    buffer = free.allocate(size, maxTimeToBlock);
                    nowMs = time.milliseconds();
                }

                synchronized (dq) {
                    
                    if (partitionChanged(topic, topicInfo, partitionInfo, dq, nowMs, cluster))  continue;
                    // 创建新的批次
                    RecordAppendResult appendResult = appendNewBatch(topic, effectivePartition, dq, timestamp, key, value, headers, callbacks, buffer, nowMs);
                    
                    if (appendResult.newBatchCreated)
                        buffer = null;
                 
                    boolean enableSwitch = allBatchesFull(dq);
                    topicInfo.builtInPartitioner.updatePartitionInfo(partitionInfo, appendResult.appendedBytes, cluster, enableSwitch);
                    return appendResult;
                }
            }
        } finally {
            free.deallocate(buffer);
            appendsInProgress.decrementAndGet();
        }
    }

```

### tryAppend

```

public FutureRecordMetadata tryAppend(long timestamp, byte[] key, byte[] value, Header[] headers, Callback callback, long now) {  
    if (!recordsBuilder.hasRoomFor(timestamp, key, value, headers)) {  
        return null;  
    } else {  
        this.recordsBuilder.append(timestamp, key, value, headers);  
        this.maxRecordSize = Math.max(this.maxRecordSize, AbstractRecords.estimateSizeInBytesUpperBound(magic(), recordsBuilder.compressionType(), key, value, headers));  
        this.lastAppendTime = now;  
        FutureRecordMetadata future = new FutureRecordMetadata(this.produceFuture, this.recordCount,  
            timestamp,  
            key == null ? -1 : key.length,  
            value == null ? -1 : value.length,  
            Time.SYSTEM);  

        thunks.add(new Thunk(callback, future));  
        this.recordCount++;  
        return future;  
    }  
}


```
##### 说明
* 则将消息追加到批次中，并更新批次中最大的消息大小、最后追加消息的时间等信息。
* 方法会创建一个FutureRecordMetadata对象，表示这条消息的元数据，并将其添加到thunks队列中。
* thunks队列中保存的是每个用户在添加消息时传入的Callback函数和对应的FutureRecordMetadata对象

### sender线程取出消息进行网络发送

##### 说明
回忆下在kafkaProducer的构造方法里面会初始化sender线程：

```
public static final String NETWORK_THREAD_PREFIX = "kafka-producer-network-thread";
// 创建发送器

this.sender = newSender(logContext, kafkaClient, this.metadata);  
String ioThreadName = NETWORK_THREAD_PREFIX + " | " + clientId;  
this.ioThread = new KafkaThread(ioThreadName, this.sender, true);  
this.ioThread.start();
```
* newSender方法其实就是构建一个 Sender对象

#### Sender对象的组成


![iShot_2023-04-10_18.07.38.png](https://p9-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/e3d2df43ea0e49bcbf3ce5df004892b3~tplv-k3u1fbpfcp-watermark.image?)

sender类实现了Runnable接口,那么我们直接看run方法

##### Run

```
public void run() {
    log.debug("Starting Kafka producer I/O thread.");

    // main loop, runs until close is called
    while (running) {
        try {
            runOnce();
        } catch (Exception e) {
            log.error("Uncaught error in Kafka producer I/O thread: ", e);
        }
    }
    ... // 删除其他代码
    log.debug("Shutdown of Kafka producer I/O thread has completed.");
}

```

##### runOnce

```
void runOnce() {
    if (transactionManager != null) {
        try {
            transactionManager.maybeResolveSequences();

            // 如果transaction manager处于失败状态，不再发送消息
            if (transactionManager.hasFatalError()) {
                RuntimeException lastError = transactionManager.lastError();
                if (lastError != null)
                    maybeAbortBatches(lastError);
                client.poll(retryBackoffMs, time.milliseconds());
                return;
            }

            // 检查是否需要一个新的producerId，如果需要，则发送一个InitProducerId请求
            transactionManager.bumpIdempotentEpochAndResetIdIfNeeded();

            if (maybeSendAndPollTransactionalRequest()) {
                return;
            }
        } catch (AuthenticationException e) {
          
            transactionManager.authenticationFailed(e);
        }
    }

    long currentTimeMs = time.milliseconds();
    long pollTimeout = sendProducerData(currentTimeMs);
    client.poll(pollTimeout, currentTimeMs);
}

```
说明:
* 这里我们只看 sendProducerData和poll的方法

##### sendProducerData

```
private long sendProducerData(long now) {
    Cluster cluster = metadata.fetch();
    // 获取准备发送数据的分区列表
    RecordAccumulator.ReadyCheckResult result = this.accumulator.ready(cluster, now);

    // 如果有任何分区的领导者还不知道，强制更新元数据
    if (!result.unknownLeaderTopics.isEmpty()) {
        // 包含未知领导者的主题集合
        // 包括正在等待选举领导者的主题以及可能已过期的主题。
        // 将该主题再次添加到元数据中，以确保它被包括在内，
        // 并请求元数据更新，因为有消息要发送到该主题。
        for (String topic : result.unknownLeaderTopics) {
            this.metadata.add(topic, now);
        }

        log.debug("Requesting metadata update due to unknown leader topics from the batched records: {}",
                result.unknownLeaderTopics);
        this.metadata.requestUpdate();
    }

    // 删除我们还没有准备好发送到的所有节点
    Iterator<Node> iter = result.readyNodes.iterator();
    long notReadyTimeout = Long.MAX_VALUE;
    while (iter.hasNext()) {
        Node node = iter.next();
        if (!this.client.ready(node, now)) {
            // 仅更新延迟统计数据的readyTimeMs，
            // 以便在每次批处理就绪时向前移动
            // (然后readyTimeMs和drainTimeMs之间的差异将表示数据等待节点的时间).
            this.accumulator.updateNodeLatencyStats(node.id(), now, false);
            iter.remove();
            notReadyTimeout = Math.min(notReadyTimeout, this.client.pollDelayMs(node, now));
        } else {
            // 更新readyTimeMs和drainTimeMs，这将“重置”节点延迟.
            this.accumulator.updateNodeLatencyStats(node.id(), now, true);
        }
    }

    // 创建生产请求
    Map<Integer, List<ProducerBatch>> batches = this.accumulator.drain(cluster, result.readyNodes, this.maxRequestSize, now);
    addToInflightBatches(batches);
    if (guaranteeMessageOrder) {
        // Mute all the partitions drained
        for (List<ProducerBatch> batchList : batches.values()) {
            for (ProducerBatch batch : batchList) {
                this.accumulator.mutePartition(batch.topicPartition);
            }
        }
    }

    accumulator.resetNextBatchExpiryTime();
    List<ProducerBatch> expiredInflightBatches = getExpiredInflightBatches(now);
    List<ProducerBatch>

```

##### poll

```
public List<ClientResponse> poll(long timeout, long now) { ensureActive();
    if (!abortedSends.isEmpty()) {
        // 如果有由于不支持的版本异常或断开连接而中止发送的请求，则立即处理它们，无需等待 Selector#poll。
        List<ClientResponse> responses = new ArrayList<>();
        handleAbortedSends(responses);
        completeResponses(responses);
        return responses;
    }

    // 更新元数据的超时时间
    long metadataTimeout = metadataUpdater.maybeUpdate(now);
    try {
        // 调用 Selector#poll 进行轮询
        this.selector.poll(Utils.min(timeout, metadataTimeout, defaultRequestTimeoutMs));
    } catch (IOException e) {
        log.error("I/O 错误", e);
    }

    // 处理已完成的操作
    long updatedNow = this.time.milliseconds();
    List<ClientResponse> responses = new ArrayList<>();
    handleCompletedSends(responses, updatedNow);
    handleCompletedReceives(responses, updatedNow);
    handleDisconnections(responses, updatedNow);
    handleConnections();
    handleInitiateApiVersionRequests(updatedNow);
    handleTimedOutConnections(responses, updatedNow);
    handleTimedOutRequests(responses, updatedNow);
    completeResponses(responses);

    return responses;
}
```

# 总结
Kafka 生产者的设计具有多个精妙之处，其中包括：

* 高效的异步发送：Kafka 生产者使用 RecordAccumulator 进行消息缓存，并利用 Sender 线程异步发送消息，这种设计可以提高消息发送的吞吐量。

* 批量发送：Kafka 生产者可以将多个消息批量发送，从而减少网络开销和服务端的负载压力。

* 可靠的重试机制：Kafka 生产者使用重试机制来保证消息能够成功发送，当消息发送失败时，生产者会自动进行重试，直到消息发送成功或者达到最大重试次数。

* 动态分区分配：Kafka 生产者可以根据生产者和分区的数量动态分配分区，从而实现负载均衡和优化网络使用。

* 可配置的消息压缩：Kafka 生产者支持多种消息压缩算法，可以根据实际需求进行配置，从而减少网络传输的数据量。
这些设计使得 Kafka 生产者能够高效、可靠地发送消息，并适应不同的应用场景和需求。


