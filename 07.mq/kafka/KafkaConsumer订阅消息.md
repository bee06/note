# 概述
KafkaConsumer是从Kafka服务端拉取消息的API，开发人员可以基于这套API轻松实现从Kafka服务端拉取消息的功能;
消费者是如何与Kafka服务端之间实现网络连接的管理、心跳检测、请求超时重试等功能
消费者是如何实现订阅Topic的分区数量、以及Consumer Group的重平衡、自动提交offset的功能。

我们从的三部分介绍KafkaConsumer的源码:
1. 消费者初始化(本文介绍)
2. 消费者如何拉取的数据的
3. 消费者是如何与协调者(ConsumerCoordinator)交互的

来分析上面的问题



# 名词解释
消费组:消费者组是一组消费者，它们合作消费来自某些主题的数据
offset:位移,Kafka服务端并不会记录消费者的消费位置， 而是由消费者自己决定如何保存如何记录其消费的offset。旧版本的消费者会将其消费位置记录到Zookeeper中，在新版本消贵者中为了缓解Zookeeper集群的压力，在Kafka服务端中添加了一个名为“consumer offsets”的内部Topic
分区重新分配:当消费者上下线都会触发消费组进行重平衡操作，对分区进行重新分配，待重平衡操作完后，消费者就可以读取offserts topic中的记录的offset，并从offset位置继续消费。

# 代码入口
