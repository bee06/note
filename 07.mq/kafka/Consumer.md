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
    * 比如 某个group下有20个consumer实例，他订阅了一个具有100个分区的topic，正常情况下，kafka平均会为每个consumer分配5个分区，这种分配的过程就叫做Rebalance(重平衡)
  * 那么consumer group进行Rebalance呢，触发Rebalance的触发条件有3个:
    * 组成员数发生变更，比如说新增加了consumer或者有consumer离开的消费组
    * 订阅主题数发生变更
    * 订阅主题的分区数发生变更
  * Rebalance发生时，group下所有的consumer实例都会协调在一起共同参与，kafka默认提供了3种分配策略:
    * 公平分配，比如说group内有10个consumer实例，要消费100个分区，每个实例平均得到10个分区，如果出现严重倾斜，势必会出现，有的实例会闲死或者忙死
    * 轮询分配
    * range策略
  * 缺点
    * Rebalance 过程对 Consumer Group 消费过程有极大的影响,在 Rebalance 过程中，所有 Consumer 实例都会停止消费，等待 Rebalance 完成
    * 其次，目前 Rebalance 的设计是所有 Consumer 实例共同参与，全部重新分配所有分区
## 神秘的位移
### 定义
* kafka内部神秘的主题:__consumer_offsets
* 保存kafka的消费者的位移消息
* 位移主题的 Key 中应该保存 3 部分内容：<GroupID，主题名，分区号 >
* 当kafka集群中的第一个consumer程序启动时，kafka会自动创建位移主题
* 目前 Kafka Consumer 提交位移的方式有两种：
  * 自动提交位移和手动提交位移。
* Consumer 端有个参数叫 enable.auto.commit，如果值是 true，则 Consumer 在后台默默地为你定期提交位移,提交间隔由一个专属的参数 auto.commit.interval.ms 来控制
* kafka使用了compact策略来删除位移主题中的过期消息，避免该主题无限期膨胀
* Kafka 提供了专门的后台线程定期地巡检待 Compact 的主题，看看是否存在满足条件的可删除数据。这个后台线程叫 Log Cleaner
