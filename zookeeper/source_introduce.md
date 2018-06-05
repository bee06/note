##  客户端API介绍
org.apache.zookeeper.ZooKeeper

## 序列化
org.apache.jute 这个包下面就是专门做序列化
## 网络通信
### 客户端通讯
org.apache.zookeeper.ClientCnxn
    1. 包括SendThread和EventThread
org.apache.zookeeper.ClientCnxnSocket(抽象类)
org.apache.zookeeper.ClientCnxnSocketNio
org.apache.zookeeper.ClientCnxnSocketNetty
### 服务端通信
org.apache.zookeeper.server.ServerCnxn
org.apache.zookeeper.server.NIOServerCnxn
org.apache.zookeeper.server.NettyServerCnxn

## watcher机制
org.apache.zookeeper.Watcher
org.apache.zookeeper.WatchedEvent
org.apache.zookeeper.ClientWatchManager
org.apache.zookeeper.ZooKeeper.ZKWatchManager

## 数据存储
org.apache.zookeeper.server.persistence  该包下面就是做数据持久化
## 请求处理链
实现该接口 org.apache.zookeeper.server.RequestProcessor

## leader选取
接口定义
org.apache.zookeeper.server.quorum.Election
接口实现
org.apache.zookeeper.server.quorum.FastLeaderElection
看着一个就可以，其他的都类都过期了
## 服务端
org.apache.zookeeper.server.ZooKeeperServer
org.apache.zookeeper.server.quorum.QuorumZooKeeperServer
org.apache.zookeeper.server.quorum.ObserverZooKeeperServer
## zab协议
org.apache.zookeeper.server.quorum.Leader
org.apache.zookeeper.server.quorum.Follower
org.apache.zookeeper.server.quorum.LeaderHandler
## 权限认证
org.apache.zookeeper.server.auth
## JMX
org.apache.zookeeper.jmx.
## 其他
### 静态变量定义
org.apache.zookeeper.ZooDefs
