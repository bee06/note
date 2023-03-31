## 是什么
codis实现redis的集群，在redis cluster发布之前

## 整体架构
1. codis server:二次开发的redis实例
2. codis proxy:接收客户端的请求
3. zk:保存元数据
4. codis dashboard和codis fe：共同组成了集群管理工具

## 流程

## 难点
* 数据如何在集群里分布
  1. 第一步，codis有1024个slot，把这些slot手动分配给codis server, 每个server上包含一部分slot
  2. 第二步  当客户端要读写数据时候，会使用crc32算法计算key的哈希值 ,将hash值对1023取模，计算对应的slot的编号

我们把 Slot 和 codis server 的映射关系称为数据路由表（简称路由表）。
我们在 codis dashboard 上分配好路由表后，dashboard 会把路由表发送给 codis proxy，同时，dashboard 也会把路由表保存在 Zookeeper 中。
codis-proxy 会把路由表缓存在本地，当它接收到客户端请求后，直接查询本地的路由表，就可以完成正确的请求转发了。
* 集群扩容
* 数据迁移
* 集群客户端需要重新开发
* 怎么保证集群可靠性？
* 切片集群方案选择建议