### Rocketmq发送流程



#### 先参考下官方的例子

```
public static void main(String[] args) throws MQClientException, InterruptedException {

    /*
     * 1.使用生产者组名称进行实例化.
     */
    DefaultMQProducer producer = new DefaultMQProducer("please_rename_unique_group_name");
		
		// 2.启动producer
    producer.start();
    
    // 3.发送消息
        try {
        
            Message msg = new Message("TopicTest" /* Topic */,
                "TagA" /* Tag */,
                ("Hello RocketMQ " + i).getBytes(RemotingHelper.DEFAULT_CHARSET)
            );

            SendResult sendResult = producer.send(msg);

            System.out.printf("%s%n", sendResult);
        } catch (Exception e) {
            e.printStackTrace();
            Thread.sleep(1000);
        }
    
		// 3.关闭
    producer.shutdown();
}
```

注

* 代码位置:org.apache.rocketmq.example.quickstart.Producer

根据上面的例子，接下来我们一步一步分析

#### 初始化发送器

DefaultMQProducer producer = new DefaultMQProducer("please_rename_unique_group_name")

```java
public DefaultMQProducer(final String namespace, final String producerGroup, RPCHook rpcHook) {
    this.namespace = namespace;
    this.producerGroup = producerGroup;
    defaultMQProducerImpl = new DefaultMQProducerImpl(this, rpcHook);
}
```

* namespace和RPCHook 都设置为null

* 主要是创建 DefaultMQProducerImpl

  * ```java
    public DefaultMQProducerImpl(final DefaultMQProducer defaultMQProducer, RPCHook rpcHook) {
        this.defaultMQProducer = defaultMQProducer;
        this.rpcHook = rpcHook;
    
        this.asyncSenderThreadPoolQueue = new LinkedBlockingQueue<Runnable>(50000);
        this.defaultAsyncSenderExecutor = new ThreadPoolExecutor(
            Runtime.getRuntime().availableProcessors(),
            Runtime.getRuntime().availableProcessors(),
            1000 * 60,
            TimeUnit.MILLISECONDS,
            this.asyncSenderThreadPoolQueue,
            new ThreadFactory() {
                private AtomicInteger threadIndex = new AtomicInteger(0);
    
                @Override
                public Thread newThread(Runnable r) {
                    return new Thread(r, "AsyncSenderExecutor_" + this.threadIndex.incrementAndGet());
                }
            });
    }
    ```

  * 除了设置发送器和rpchook以外，还构建了队列和异步线程池

  #### 启动producer

  producer.start();

  ```java
  @Override
  public void start() throws MQClientException {
      this.setProducerGroup(withNamespace(this.producerGroup));
      this.defaultMQProducerImpl.start();
      if (null != traceDispatcher) {
          try {
              traceDispatcher.start(this.getNamesrvAddr(), this.getAccessChannel());
          } catch (MQClientException e) {
              log.warn("trace dispatcher start failed ", e);
          }
      }
  }
  ```

  * this.setProducerGroup(withNamespace(this.producerGroup));设置生产组

  * this.defaultMQProducerImpl.start();

    * 实际上是调用 实现类的启动类

      * ```
        public void start() throws MQClientException {
            this.start(true);
        }
        ```

        ```java
        public void start(final boolean startFactory) throws MQClientException {
            
            
            
            switch (this.serviceState) {
                case CREATE_JUST:
                		// 设置状态 默认值为启动失败
                    this.serviceState = ServiceState.START_FAILED;
        						// 检查参数
                    this.checkConfig();
        
                    if (!this.defaultMQProducer.getProducerGroup().equals(MixAll.CLIENT_INNER_PRODUCER_GROUP)) {
                        this.defaultMQProducer.changeInstanceNameToPID();
                    }
        						// MQClientInstance 默认实例
                    this.mQClientFactory = MQClientManager.getInstance().getOrCreateMQClientInstance(this.defaultMQProducer, rpcHook);
        						
        						// 注册成功
                    boolean registerOK = mQClientFactory.registerProducer(this.defaultMQProducer.getProducerGroup(), this);
              		// 注册非成功
              		if (!registerOK) {
                        this.serviceState = ServiceState.CREATE_JUST;
                        throw new MQClientException("The producer group[" + this.defaultMQProducer.getProducerGroup()
                            + "] has been created before, specify another name please." + FAQUrl.suggestTodo(FAQUrl.GROUP_NAME_DUPLICATE_URL),
                            null);
                    }
        
         // 放入缓存中           this.topicPublishInfoTable.put(this.defaultMQProducer.getCreateTopicKey(), new TopicPublishInfo());
        
        						// 启动
                    if (startFactory) {
                        mQClientFactory.start();
                    }
        
                    log.info("the producer [{}] start OK. sendMessageWithVIPChannel={}", this.defaultMQProducer.getProducerGroup(),
                        this.defaultMQProducer.isSendMessageWithVIPChannel());
                    this.serviceState = ServiceState.RUNNING;
                    break;
                case RUNNING:
                case START_FAILED:
                case SHUTDOWN_ALREADY:
                    throw new MQClientException("The producer service state not OK, maybe started once, "
                        + this.serviceState
                        + FAQUrl.suggestTodo(FAQUrl.CLIENT_SERVICE_NOT_OK),
                        null);
                default:
                    break;
            }
        
            this.mQClientFactory.sendHeartbeatToAllBrokerWithLock();
        
            this.timer.scheduleAtFixedRate(new TimerTask() {
                @Override
                public void run() {
                    try {
                        RequestFutureTable.scanExpiredRequest();
                    } catch (Throwable e) {
                        log.error("scan RequestFutureTable exception", e);
                    }
                }
            }, 1000 * 3, 1000);
        }
        ```

        * 状态枚举

          ```java
          public enum ServiceState {
              /**
               * Service just created,not start
               */
              CREATE_JUST,
              /**
               * Service Running
               */
              RUNNING,
              /**
               * Service shutdown
               */
              SHUTDOWN_ALREADY,
              /**
               * Service Start failure
               */
              START_FAILED;
          }
          ```

        * 校验参数

        * 创建MQClientInstance（非常重要的类）

          * ```java
            public MQClientInstance getOrCreateMQClientInstance(final ClientConfig clientConfig, RPCHook rpcHook) {
                String clientId = clientConfig.buildMQClientId();
                MQClientInstance instance = this.factoryTable.get(clientId);
                if (null == instance) {
                    instance =
                        new MQClientInstance(clientConfig.cloneClientConfig(),
                            this.factoryIndexGenerator.getAndIncrement(), clientId, rpcHook);
                    MQClientInstance prev = this.factoryTable.putIfAbsent(clientId, instance);
                    if (prev != null) {
                        instance = prev;
                        log.warn("Returned Previous MQClientInstance for clientId:[{}]", clientId);
                    } else {
                        log.info("Created new MQClientInstance for clientId:[{}]", clientId);
                    }
                }
            
                return instance;
            }
            ```

          * 构建MQClientInstance

            

                public MQClientInstance(ClientConfig clientConfig, int instanceIndex, String clientId, RPCHook rpcHook) {
                      this.clientConfig = clientConfig;
                      this.instanceIndex = instanceIndex;
                      this.nettyClientConfig = new NettyClientConfig();
                      this.nettyClientConfig.setClientCallbackExecutorThreads(clientConfig.getClientCallbackExecutorThreads());
                      this.nettyClientConfig.setUseTLS(clientConfig.isUseTLS());
                      this.clientRemotingProcessor = new ClientRemotingProcessor(this);
                      this.mQClientAPIImpl = new MQClientAPIImpl(this.nettyClientConfig, this.clientRemotingProcessor, rpcHook, clientConfig);
                  if (this.clientConfig.getNamesrvAddr() != null) {
                      this.mQClientAPIImpl.updateNameServerAddressList(this.clientConfig.getNamesrvAddr());
                      log.info("user specified name server address: {}", this.clientConfig.getNamesrvAddr());
                  }
                
                  this.clientId = clientId;
                
                  this.mQAdminImpl = new MQAdminImpl(this);
                    // 初始化发送消息  pullMessageService 继承 ServiceThread 
                  this.pullMessageService = new PullMessageService(this);
                    // 初始化负载均衡服务 RebalanceService 同样继承了 ServiceThread
                  this.rebalanceService = new RebalanceService(this);
                
                  this.defaultMQProducer = new DefaultMQProducer(MixAll.CLIENT_INNER_PRODUCER_GROUP);
                  //重置配置项
                  this.defaultMQProducer.resetClientConfig(clientConfig);
                	// 状态管理
                  this.consumerStatsManager = new ConsumerStatsManager(this.scheduledExecutorService);
                }

            * 先说下RebalanceService

            * ```java
              @Override
              public void run() {
                  log.info(this.getServiceName() + " service started");
              
                  while (!this.isStopped()) {
                      this.waitForRunning(waitInterval);
                      this.mqClientFactory.doRebalance();
                  }
              
                  log.info(this.getServiceName() + " service end");
              }
              ```

              * 实际上 org.apache.rocketmq.client.impl.factory.MQClientInstance#doRebalance 

        * 注册

        * 启动

      ### 发送消息

      ```java
      public SendResult send(
          Message msg) throws MQClientException, RemotingException, MQBrokerException, InterruptedException {
          Validators.checkMessage(msg, this);
          msg.setTopic(withNamespace(msg.getTopic()));
          return this.defaultMQProducerImpl.send(msg);
      }
      ```

      * 核心逻辑
        * 校验消息
        * Topic路有数据拉取
        * MessageQueue选择
        * 跟Broker建立网络连接
        * 通过网络连接发送消息到Broker去，
      * 同步发送消息（仅当发送过程完全完成时，此方法才返回）
        * 校验消息
        * 设置topic
        * 发送消息