## 消费组
### 定义
* Consumer group是kafka提供的可扩展且具有容错性的消费者机制.
* 该组都共享一个公共的id称为groupID
* 组内的所有消费者协调在一起来消费订阅主题的所有分区
* 理想情况下，Consumer 实例的数量应该等于该 Group 订阅主题的分区总数。
* 针对Consumer Group，Kafka 是怎么管理位移的呢
  * 位移就是消费者在消费过程中需要记录自己消费了多少数据，即消费位置信息
  * Map<TopicPartition, Long>，其中 TopicPartition 表示一个分区，而 Long 表示位移的类型
  * 在新版本的Consumer group中，kafka社区重新设计了Consumer group的位移管理方式，采用将位移保存在kafka内部主题的方法（老版本是放到zk上，缺点：大量的更新会拖慢zk集群的性能）,这个内部主题就是__Consumer_offsets
* consumer group的重平衡
  * 本质上是一种协议，规定了一个consumer group下所有的consumer如何达成一致，来分配订阅topic的每个分区。
    * 比如 某个group下有20个consumer实例，他订阅了一个具有100个分区的topic，正常情况下，kafka平均会为每个consumer分配5个分区，这种分配的过程就叫做rebalance(重平衡)
