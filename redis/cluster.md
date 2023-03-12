## 是什么
* redis的集群模式
* redis cluster不采用把key直接映射到实例的方式，而是采用哈希槽的方式
* redis cluster 采用无中心化的模式
* redis cluster没有proxy，是客户端和服务器直连



## 为什么
* 服务器的内存有限

## 难点
* 请求路由
* 数据迁移

## 如何做
* 采用crc16算法计算一个key的16bit的值，并将这值对16384取模