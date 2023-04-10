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

            // 解析Broker地址
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
* 解析Broker地址
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

## RecordAccumulator
RecordAccumulator是Kafka消息传输机制的核心组件之一，主要功能是将多个ProducerRecord对象批量打包成RecordBatch，并将RecordBatch添加到RecordBatchBuilder中等待发送。

### 成员变量
```
    /**
     * 用于存储正在等待发送的RecordBatch
     */
    private final AtomicInteger flushesInProgress;
    /**
     * 已经发送完成但还未被确认的RecordBatch
     */
    private final AtomicInteger appendsInProgress;
    /**
     * 批次大小
     */
    private final int batchSize;
    /**
     * RecordAccumulator可以使用LZ4和Gzip等压缩方式对RecordBatch进行压缩，以减少数据传输时的带宽占用和网络延迟。
     */
    private final CompressionType compression;
    /**
     * 消息 batch 延迟多久再发送的时间
     */
    private final int lingerMs;
    /**
     * 重试 间隔时间
     */
    private final long retryBackoffMs;
    private final int deliveryTimeoutMs;
    
    /**
     * 缓冲池
     */
    private final BufferPool free;
    private final Time time;
    private final ApiVersions apiVersions;
    // topic的缓存
    private final ConcurrentMap<String /*topic*/, TopicInfo> topicInfoMap = new CopyOnWriteMap<>();
    // node的状态
    private final ConcurrentMap<Integer /*nodeId*/, NodeLatencyStats> nodeStats = new CopyOnWriteMap<>();
    // 未完成的批次
    private final IncompleteBatches incomplete;
    // The following variables are only accessed by the sender thread, so we don't need to protect them.
    private final Set<TopicPartition> muted;
    private final Map<String, Integer> nodesDrainIndex;
    private final TransactionManager transactionManager;
```

### 如何追加消息的流程
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
                

                // 根据TopicPartition获取或新建Deque双端队列
                Deque<ProducerBatch> dq = topicInfo.batches.computeIfAbsent(effectivePartition, k -> new ArrayDeque<>());
                synchronized (dq) {
                    // 获取锁后，验证分区没有更改，然后重试.
                    if (partitionChanged(topic, topicInfo, partitionInfo, dq, nowMs, cluster))
                        continue;
                    // 尝试将消息加入到缓冲区中
                    RecordAppendResult appendResult = tryAppend(timestamp, key, value, headers, callbacks, dq, nowMs);
                    if (appendResult != null) {
                        // 追加成功
                        boolean enableSwitch = allBatchesFull(dq);
                        topicInfo.builtInPartitioner.updatePartitionInfo(partitionInfo, appendResult.appendedBytes, cluster, enableSwitch);
                        return appendResult;
                    }
                }

                // 我们没有正在进行的记录批处理，请尝试分配一个新批处理
                if (abortOnNewBatch) {
                    return new RecordAppendResult(null, false, false, true, 0);
                }
                // 分配缓存区
                if (buffer == null) {
                    byte maxUsableMagic = apiVersions.maxUsableProduceMagic();
                    // 取16k和消息大小的最大值
                    int size = Math.max(this.batchSize, AbstractRecords.estimateSizeInBytesUpperBound(maxUsableMagic, compression, key, value, headers));
                    
                    // 如果耗尽缓冲区空间，重新分配，此调用可能阻塞.
                    buffer = free.allocate(size, maxTimeToBlock);
                    nowMs = time.milliseconds();
                }

                synchronized (dq) {
                    
                    if (partitionChanged(topic, topicInfo, partitionInfo, dq, nowMs, cluster))  continue;
                    // 
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
        // 重点是这里
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
* recordsBuilder.append的方法实际上是调用MemoryRecordsBuilder#appendWithOffset方法，代码如下
### MemoryRecordsBuilder#appendWithOffset

```
private void appendWithOffset(long offset, boolean isControlRecord, long timestamp, ByteBuffer key,
                              ByteBuffer value, Header[] headers) {
    try {
        // 检查是否可以将控制记录追加到控制批次中
        if (isControlRecord != isControlBatch) {
            throw new IllegalArgumentException("Control records can only be appended to control batches");
        }

        // 检查新记录的偏移量是否合法
        if (lastOffset != null && offset <= lastOffset) {
            throw new IllegalArgumentException(String.format("Illegal offset %s following previous offset %s " +
                    "(Offsets must increase monotonically).", offset, lastOffset));
        }

        // 检查时间戳是否合法
        if (timestamp < 0 && timestamp != RecordBatch.NO_TIMESTAMP) {
            throw new IllegalArgumentException("Invalid negative timestamp " + timestamp);
        }

        // 检查是否支持记录头
        if (magic < RecordBatch.MAGIC_VALUE_V2 && headers != null && headers.length > 0) {
            throw new IllegalArgumentException("Magic v" + magic + " does not support record headers");
        }

        // 设置基准时间戳
        if (baseTimestamp == null) {
            baseTimestamp = timestamp;
        }

        // 根据不同的魔数调用不同的追加记录方法
        if (magic > RecordBatch.MAGIC_VALUE_V1) {
            appendDefaultRecord(offset, timestamp, key, value, headers);
        } else {
            appendLegacyRecord(offset, timestamp, key, value, magic);
        }
    } catch (IOException e) {
        throw new KafkaException("I/O exception when writing to the append stream, closing", e);
    }
}

```
根据RecordBatch类中的定义 byte CURRENT_MAGIC_VALUE = MAGIC_VALUE_V2;所以我们直接看appendLegacyRecord方法的实现

### appendLegacyRecord

```
private long appendLegacyRecord(long offset, long timestamp, ByteBuffer key, ByteBuffer value, byte magic) throws IOException {
    // 检查消息追加器是否已经打开，如果未打开则抛出异常
    ensureOpenForRecordAppend();

    // 如果消息的压缩类型为NONE，时间戳类型为LOG_APPEND_TIME，则将时间戳设置为当前追加时间
    if (compressionType == CompressionType.NONE && timestampType == TimestampType.LOG_APPEND_TIME) {
        timestamp = logAppendTime;
    }

    // 计算记录的大小
    int size = LegacyRecord.recordSize(magic, key, value);

    // 向追加流中写入记录头
    AbstractLegacyRecordBatch.writeHeader(appendStream, toInnerOffset(offset), size);

    // 如果时间戳类型为LOG_APPEND_TIME，则将时间戳设置为当前追加时间
    if (timestampType == TimestampType.LOG_APPEND_TIME) {
        timestamp = logAppendTime;
    }

    // 调用遗留记录的写入方法写入记录，并返回记录的CRC校验码
    long crc = LegacyRecord.write(appendStream, magic, timestamp, key, value, CompressionType.NONE, timestampType);

    // 更新已写入的记录数和字节数
    recordWritten(offset, timestamp, size + Records.LOG_OVERHEAD);

    return crc;
}

```

##### 说明

* RecordAccumulator采用了分区级别的缓冲机制，即每个分区都有一个对应的缓冲区。这样可以避免多个分区之间的竞争，提高发送消息的效率
* RecordAccumulator会对消息进行压缩，但是不会立即进行压缩操作，而是会等待一段时间后再进行压缩。这样可以让更多的消息被累积到一个批次中，从而提高压缩的效率。
* RecordAccumulator会将多个批次中的消息合并成一个更大的批次进行发送。这样可以减少网络I/O操作的次数，从而提高发送消息的效率。
* RecordAccumulator会根据当前发送消息的速度动态调整批次的大小。如果发送速度很快，就会增加批次的大小；如果发送速度很慢，就会减小批次的大小。这样可以保证发送消息的效率和稳定性

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
    // 当前可发送数据的分区列表
    RecordAccumulator.ReadyCheckResult result = this.accumulator.ready(cluster, now);
    //如果存在未知领导者（Leader），则将其添加到元数据中，并请求更新元数据
    if (!result.unknownLeaderTopics.isEmpty()) {
        for (String topic : result.unknownLeaderTopics) {
            this.metadata.add(topic, now);
        }
        unknownLeaderTopics);
        this.metadata.requestUpdate();
    }

    Iterator<Node> iter = result.readyNodes.iterator();
    long notReadyTimeout = Long.MAX_VALUE;
    while (iter.hasNext()) {
        Node node = iter.next();
        //删除未准备好发送到的所有节点，并更新节点的延迟统计数据。
        if (!this.client.ready(node, now)) {
            this.accumulator.updateNodeLatencyStats(node.id(), now, false);
            iter.remove();
            notReadyTimeout = Math.min(notReadyTimeout, this.client.pollDelayMs(node, now));
        } else {
            this.accumulator.updateNodeLatencyStats(node.id(), now, true);
        }
    }
    // 将可发送的批次添加到正在进行中的批次列表中。    
    Map<Integer, List<ProducerBatch>> batches = this.accumulator.drain(cluster, result.readyNodes, this.maxRequestSize, now);
    addToInflightBatches(batches);

    if (guaranteeMessageOrder) {
        for (List<ProducerBatch> batchList : batches.values()) {
            for (ProducerBatch batch : batchList) {
                this.accumulator.mutePartition(batch.topicPartition);
            }
        }
    }

    accumulator.resetNextBatchExpiryTime();
    // 将所有已过期的批次删除，并标记为失败
    List<ProducerBatch> expiredInflightBatches = getExpiredInflightBatches(now);
    List<ProducerBatch> expiredBatches = this.accumulator.expiredBatches(now);
    expiredBatches.addAll(expiredInflightBatches);

    if (!expiredBatches.isEmpty()) {
        log.trace("Expired {} batches in accumulator", expiredBatches.size());
    }
    for (ProducerBatch expiredBatch : expiredBatches) {
        String errorMessage = "Expiring " + expiredBatch.recordCount + " record(s) for " + expiredBatch.topicPartition
            + ":" + (now - expiredBatch.createdMs) + " ms has passed since batch creation";
        failBatch(expiredBatch, new TimeoutException(errorMessage), false);
        if (transactionManager != null && expiredBatch.inRetry()) {
            transactionManager.markSequenceUnresolved(expiredBatch);
        }
    }
   

    //计算poll的超时时间
    long pollTimeout = Math.min(result.nextReadyCheckDelayMs, notReadyTimeout);
    pollTimeout = Math.min(pollTimeout, this.accumulator.nextExpiryTimeMs() - now);
    pollTimeout = Math.max(pollTimeout, 0);

    if (!result.readyNodes.isEmpty()) {
        pollTimeout = 0;
    }
    // 发送请求到Kafka集群
    sendProduceRequests(batches, now);
    return pollTimeout;
}


```

##### sendProduceRequests

```
private void sendProduceRequest(long now, int destination, short acks, int timeout, List<ProducerBatch> batches) {
    if (batches.isEmpty())
        return;

    final Map<TopicPartition, ProducerBatch> recordsByPartition = new HashMap<>(batches.size());

    // 找到创建记录集时使用的最小版本
    byte minUsedMagic = apiVersions.maxUsableProduceMagic();
    for (ProducerBatch batch : batches) {
        if (batch.magic() < minUsedMagic)
            minUsedMagic = batch.magic();
    }

    ProduceRequestData.TopicProduceDataCollection tpd = new ProduceRequestData.TopicProduceDataCollection();
    for (ProducerBatch batch : batches) {
        TopicPartition tp = batch.topicPartition;
        MemoryRecords records = batch.records();

        if (!records.hasMatchingMagic(minUsedMagic))
            records = batch.records().downConvert(minUsedMagic, 0, time).records();

        ProduceRequestData.TopicProduceData tpData = tpd.find(tp.topic());
        if (tpData == null) {
            tpData = new ProduceRequestData.TopicProduceData().setName(tp.topic());
            tpd.add(tpData);
        }

        tpData.partitionData().add(new ProduceRequestData.PartitionProduceData()
                .setIndex(tp.partition())
                .setRecords(records));
        recordsByPartition.put(tp, batch);
    }

    String transactionalId = null;
    if (transactionManager != null && transactionManager.isTransactional()) {
        transactionalId = transactionManager.transactionalId();
    }

    ProduceRequest.Builder requestBuilder = ProduceRequest.forMagic(minUsedMagic,
            new ProduceRequestData()
                    .setAcks(acks)
                    .setTimeoutMs(timeout)
                    .setTransactionalId(transactionalId)
                    .setTopicData(tpd));

    RequestCompletionHandler callback = response -> handleProduceResponse(response, recordsByPartition, time.milliseconds());

    String nodeId = Integer.toString(destination);
    ClientRequest clientRequest = client.newClientRequest(nodeId, requestBuilder, now, acks != 0,
            requestTimeoutMs, callback);
    client.send(clientRequest, now);
}


```
client.send 是调用NetworkClient#doSend的方法来发送数据的

##### NetworkClient#doSend

```
private void doSend(ClientRequest clientRequest, boolean isInternalRequest, long now) {
    // 校验是否可用
    ensureActive();
    // 获取目的地的node节点
    String nodeId = clientRequest.destination();
    if (!isInternalRequest) {
        if (!canSendRequest(nodeId, now))
            throw new IllegalStateException("Attempt to send a request to node " + nodeId + " which is not ready.");
    }
    AbstractRequest.Builder<?> builder = clientRequest.requestBuilder();
    try {
        NodeApiVersions versionInfo = apiVersions.get(nodeId);
        short version;
        
        if (versionInfo == null) {
            version = builder.latestAllowedVersion();
          
        } else {
            version = versionInfo.latestUsableVersion(clientRequest.apiKey(),
                                                       builder.oldestAllowedVersion(),
                                                       builder.latestAllowedVersion());
        }
       // 真正的发送
        doSend(clientRequest, isInternalRequest, now, builder.build(version));
    } catch (UnsupportedVersionException unsupportedVersionException) {
        
        ClientResponse clientResponse = new ClientResponse(clientRequest.makeHeader(builder.latestAllowedVersion()),
                                                            clientRequest.callback(),
                                                            clientRequest.destination(), now, now, false,
                                                            unsupportedVersionException, null, null);

        if (!isInternalRequest)
            abortedSends.add(clientResponse);
        else if (clientRequest.apiKey() == ApiKeys.METADATA)
            metadataUpdater.handleFailedRequest(now, Optional.of(unsupportedVersionException));
    }
}

private void doSend(ClientRequest clientRequest, boolean isInternalRequest, long now, AbstractRequest request) {
    String destination = clientRequest.destination();
    RequestHeader header = clientRequest.makeHeader(request.version());
   
    Send send = request.toSend(header);
    InFlightRequest inFlightRequest = new InFlightRequest(
        clientRequest,
        header,
        isInternalRequest,
        request,
        send,
        now
    );
    this.inFlightRequests.add(inFlightRequest);
    selector.send(new NetworkSend(destination, send));
}


```

##### selector.send

```
/**
 * 主要实现了 Kafka 客户端的网络请求的排队功能，能够将网络请求加入到发送队列中，等待后续的 poll 方法进行发送
 *
 * @param send The request to send
 */
public void send(NetworkSend send) {
    // 获取目标连接的连接 ID
    String connectionId = send.destinationId();
    //获得 KafkaChannel 对象，
    KafkaChannel channel = openOrClosingChannelOrFail(connectionId);
    //若连接正在关闭，则将连接 ID 添加到 failedSends 队列中
    if (closingChannels.containsKey(connectionId)) {
        this.failedSends.add(connectionId);
    } else {
        try {
            //将网络请求交给 KafkaChannel 对象处理
            channel.setSend(send);
        } catch (Exception e) {
            // 如果 KafkaChannel 对象在处理过程中抛出异常，将连接状态设置为 FAILED_SEND，并将连接 ID 添加到 failedSends 队列中，然后关闭连接，并将异常向上抛出，以便上层代码处理
            channel.state(ChannelState.FAILED_SEND);
            this.failedSends.add(connectionId);
            close(channel, CloseMode.DISCARD_NO_NOTIFY);
            if (!(e instanceof CancelledKeyException)) {
                throw e;
            }
        }
    }
}

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


