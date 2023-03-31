## 是什么
codis实现redis的集群，在redis cluster发布之前

## 整体架构
1. codis server:二次开发的redis实例
2. codis proxy:接收客户端的请求
3. zk:保存元数据
4. codis dashboard和codis fe：共同组成了集群管理工具