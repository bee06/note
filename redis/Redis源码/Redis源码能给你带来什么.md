## 学习源码能给你带来什么
* 了解redis的实现细节
* 学习良好的编程规范和技巧，写出高质量的代码
* 学习计算机系统的设计思想，实现职业能力进阶
  * 单机键值数据库的关键技术
    * 支持高性能访问的数据脚骨
    * 支持高效空间利用的数据结构
    * 网络服务器高并发通信
    * 高效线程执行模型
    * 内存管理
    * 日志机制
  * 分布式的关键技术
    * 主从复制机制
    * 可扩展集群数据切片和放置技术
    * 可扩展集群通信机制

## redis源码的整体结构
* 数据类型
  - String(t_string.c、sds.c、 bitops.c)
  - List(t_list.c、ziplist.c) 
  - Hash(t_hash.c、ziplist.c、dict.c) 
  - Set(t_set.c、intset.c) 
  - Sorted Set(t_zset.c、ziplist.c、dict.c) 
  - HyperLogLog(hyperloglog.c) 
  - Geo(geo.c、geohash.c、geohash_helper.c) 
  - Stream(t_stream.c、rax.c、 listpack.c) 
* 全局
  - Server(Service.c,anet.c) 
  - Object(object.c) 
  - 键值对(ae.c、ae_epoll.c、ae_kqueue.c、ae_evport.c、ae_select.c、networking.c) 
  - 事件驱动(ae.c) 
  - 内存回收(expire.c、lazyfree.c)
  - 数据替换(evict.c) 
  - 后台线程(bio.c) 
  - 事务(multe.c) 
  - pubsub(pubsub.c) 
  - 内存分配(zmalloc.c) 
  - 双向链表(adlist.c) 
  
* 高可用&集群
  - 持久化 RDB（rdb.c、redis-check-rdb.c)、AOF（aof.c、redis-check-aof.c）
  - 主从复制(replication.c) 
  - 哨兵(sentinel.c) 
  - 集群(cluster.c) 

* 辅助功能
  - 延迟统计(latency.c)
  - 慢日志(slowlog.c)
  - 通知n(otify.c)
  - 基准性能(redis-benchmark.c)