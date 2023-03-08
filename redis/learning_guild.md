## 博客和文档
### 1. Redis作者（Salvatore Sanfilippo）的博客：
http://antirez.com/news/125
### 2. Redis官方文档：
https://redis.io/documentation

### 3. Redis模板文档：
https://redis.io/modules

### 4. Redis命令文档：
https://redis.io/commands

### 5. 中文版Redis doc（黄健宏维护）：
http://redisdoc.com/

### 6. 知识星球：
Redis技术交流

### 7. 微信公众号：
Redis开发运维实战



## 三、视频资料
###  1. redis conf：全球redis开发者齐聚一堂

每年的视频和资料都会公开出来，对于想了解Redis前沿是个不错的选择。

(1) video: 自己去youtube搜索redis conf关键字

(2) slides: https://www.slideshare.net/RedisLabs

### 2. 计算机视频网站

有很多计算机学习视频网站都有类似磕碜，我也曾经出过一个，为防止广告嫌疑，这里就不多说，如果真有兴趣可以联系我。

### 3. Redis下线沙龙，CRUG和鹏程组织过的

可以在IT大咖说里搜索：http://www.itdks.com/ActivityC/search?keyWord=redis

## 四、相关源码
### 1. Redis源码(35000 star)

https://github.com/antirez/redis 

### 2. Redis3源码注释(4500 star)

https://github.com/huangz1990/redis-3.0-annotated

### 3. Codis (9000 star)

https://github.com/CodisLabs/codis

基于proxy实现的Redis分布式架构，支持水平扩容，在很多公司使用，但近期不太维护了，对于Redis4 5不太支持。

### 4.Twemproxy (8800 star)

https://github.com/twitter/twemproxy

Twitter开源的基于proxy实现的Redis|memcache分布式架构，静态路由，不支持水平扩容，但我实际使用过程中非常稳定。

### 5.CacheCloud (4000 star)

https://github.com/sohutv/cachecloud

我们团队之前开源的Redis私有云平台，在很多公司都有使用，对于Redis的规模化管理非常有帮助。

### 6.Redisson(8300 star)



https://github.com/redisson/redisson 

Redisson是架设在Redis基础上的一个Java驻内存数据网格（In-Memory Data Grid），支持：Set, Multimap, SortedSet, Map, List, Queue, Deque, Semaphore, Lock, AtomicLong, Map Reduce, Publish / Subscribe, Bloom filter, Spring Cache, Tomcat, Scheduler, JCache API, Hibernate。

### 7.Pika（2600 star）

https://github.com/Qihoo360/pika

360开源的，至于Rocksdb实现的，支持Redis协议（支持Redis几乎所有的命令）的数据库，对于大容量低成本有需求的团队是个不错的选择。

### 8.阿里云开源的Redis（2600 star）

https://github.com/alibaba/ApsaraCache

阿里云Redis团队基于Redis4.0实现的，支持memcache协议，同时在很多方面（例如性能优化）做了很多改善，后续还在改善中。

### 9. redis-migrate-tool（550 star）


https://github.com/vipshop/redis-migrate-too

唯品会开源的Redis的数据迁移工具，支持twemproxy、redis cluster、aof、rdb之间实时互转，我个人非常喜欢的一个工具，但目前不支持Redis 4和5，我们团队做了一些相关改造支持这些特性，之后会开源出来。

### 10.envoy（8800 star）

https://github.com/envoyproxy/envoy

最近很火的一个代理，不过我怎么用过，支持很多协议，后续可能使用起来。

### 11.redis-replicator（410 star）

https://github.com/leonchen83/redis-replicator

Redis Replicator是一款RDB解析以及AOF解析的工具，支持SYNC, PSYNC, PSYNC2等三种同步命令. 还支持远程RDB文件备份以及数据同步等功能（支持Redis2.6~5）

### 12.corvus（600 star）

https://github.com/eleme/corvus

饿了吗团队开源的，基于Redis cluster的代理（就是在Redis cluster上架设了代理），Redis cluster对于client有一些要求，如果你想用官方集群，但要支持多语言，基于代理也是个不错的选择，但该项目最近貌似不维护了。

### 13.redis-faina（1400 star）
https://github.com/facebookarchive/redis-faina

facebook开源的一个小工具，其实就是利用monitor查找热点，你自己也可以实现一把。
