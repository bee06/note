## 背景
redis实例运行时，是从server.c这个文件的main开始执行的，main方法其实负责启动redis的server的
，我们自己在写程序的时候，服务启动的时候会初始化一些参数或者对象，那么redis在启动时候都做了哪些工作？
## 问题
* Redis server 启动后具体会做哪些初始化操作？
* Redis server 初始化时有哪些关键配置项？
* Redis server 如何开始处理客户端请求？

## 步骤
1. 初始化基本信息
   1. 完成一些基本的初始化的工作，包括server的时区、设置哈希函数的随机种子等
    
   ```
    设置时区
    setlocale(LC_COLLATE,"");
    tzset(); 
    //Redis中对内存的管理功能由 zmalloc 完成,表示在内存不足（out of memory，缩写oom）的时候所采取的操作
    zmalloc_set_oom_handler(redisOutOfMemoryHandler);
    ......
     // 设置随机种子
    uint8_t hashseed[16];
    getRandomBytes(hashseed,sizeof(hashseed));
    dictSetHashFunctionSeed(hashseed);
    
   ```

2. 检查哨兵
   1. // 检查是否是哨兵模式
    server.sentinel_mode = checkForSentinelMode(argc,argv);
3. 初始服务端的配置
   1.  默认端口
   2.  定时任务频率
   3.  数据库数量
   4.  AOF 刷盘策略
   5.  淘汰策略
   6.  数据结构转换阈值
   7.  主从复制参数
4. 初始化module
5. 解析运行参数
6. 
7. 执行rdb和aof检测
   1. 检查是否需要以redis-check-rdb aof模式启动
8. 解析参数
9. 初始化server
10. 加载ACL
11. 服务器初始化中的一些步骤需要在最后完成(在加载模块之后)
12. 当服务器处于Sentinel模式、启动、加载配置并准备好进行正常操作时，将调用此函数
13. 设置cpu的亲和力
14. 创建事件驱动
15. 执行事件驱动


