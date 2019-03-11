## 简介
Redis Sentinel为Redis提供更高性能性，实际上，这意味着是用Sentinel能够创建一个Redis部署，可以在没有人工干预的情况下抵御某些故障。



## 其他
Sentinel本质上就是一个运行在特殊模式下的Redis服务器
和普通服务器不同的是，sentinel不使用数据库，所以初始化时不会载入RDB文件或者AOF文件
