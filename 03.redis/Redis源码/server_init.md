
## 背景
* 我们通过源码来看看redis的server启动的时候会初始化哪些参数或者对象，以及都做了哪些工作？

## 说明
> * 源码分析基于redis的6.2版本
> * 源码分析主要是在server.h和server.c
> * 本次主要是分析启动过程的流程，一些细节等后续分章节分析

## 流程图

![redis-server-init.png](https://p6-juejin.byteimg.com/tos-cn-i-k3u1fbpfcp/b6b2353fa8514aa7b7f9f711d4891589~tplv-k3u1fbpfcp-watermark.image?)

## 源码解析

### 预备知识
### redisServer
* server.h中定义了一个redisServer全局变量,存储 Redis 服务器信.包括服务器配置项和运行时数据:
    * 网络连接信息
    * 数据库
    * redisDb
    * 命令表
    * 客户端信息
    * 从服务器信息
    * 统计信息等数据


 
### 代码启动入口

* Redis的Server实例启动是从server.c这个文件的main开始执行的

```
int main(int argc, char **argv) {
    struct timeval tv;
    int j;
    char config_from_stdin = 0;
    // 删除了代码中的#ifdef
    
    // 设置时区
    setlocale(LC_COLLATE,"");
    tzset(); /* Populates 'timezone' global. */
    //Redis中对内存的管理功能由 zmalloc 完成,表示在内存不足（out of memory，缩写oom）的时候所采取的操作
    zmalloc_set_oom_handler(redisOutOfMemoryHandler);
    //以getpid()为随机序列的种子，即将系统返回的进程ID作为随机序列的种子
    srand(time(NULL)^getpid());
    srandom(time(NULL)^getpid());
    gettimeofday(&tv,NULL);
    init_genrand64(((long long) tv.tv_sec * 1000000 + tv.tv_usec) ^ getpid());
    crc64_init();

    umask(server.umask = umask(0777));
    // 设置随机种子
    uint8_t hashseed[16];
    getRandomBytes(hashseed,sizeof(hashseed));
    dictSetHashFunctionSeed(hashseed);
    // 检查是否是哨兵模式
    server.sentinel_mode = checkForSentinelMode(argc,argv);
    // 初始服务端的默认配置
    initServerConfig();
    //ACL子系统必须尽快初始化，因为基本的网络代码和客户端创建都依赖于它
    ACLInit();

    // 初始化模块系统
    moduleInitModulesSystem();
    tlsInit();

    // 将可执行路径和参数存储在一个安全的地方，以便以后能够重新启动服务器
    server.executable = getAbsolutePath(argv[0]);
    //保存执行的参数分配内存
    server.exec_argv = zmalloc(sizeof(char*)*(argc+1));
    server.exec_argv[argc] = NULL;
    // 保存执行的参数
    for (j = 0; j < argc; j++) server.exec_argv[j] = zstrdup(argv[j]);


    // 如果是哨兵模式，就初始化哨兵的配置以及哨兵模式的参数
    if (server.sentinel_mode) {
        initSentinelConfig();
        initSentinel();
    }

    /*
     * 检查是否要执行 RDB 检测或 AOF 检查，这对应了实际运行的程序是 redis-check-rdb 或 redis-check-aof
     * */
    // 如果运行的是redis-check-rdb程序 调用redis_check_rdb_main
    if (strstr(argv[0],"redis-check-rdb") != NULL)
        redis_check_rdb_main(argc,argv,NULL);
        // 如果运行的是redis-check-aof程序 调用redis_check_aof_main
    else if (strstr(argv[0],"redis-check-aof") != NULL)
        redis_check_aof_main(argc,argv);

    if (argc >= 2) {
       
        /* 解析命令行的选项 */
        
        // 解析命令行参数  解析配置文件
        loadServerConfig(server.configfile, config_from_stdin, options);
        if (server.sentinel_mode) loadSentinelConfigFromQueue();
        //释放一个sds字符串
        sdsfree(options);
    }
    // 哨兵模式，检查配置文件
    if (server.sentinel_mode) sentinelCheckConfigFile();
    // 守护进程后台运行
    server.supervised = redisIsSupervised(server.supervised_mode);
    int background = server.daemonize && !server.supervised;
    if (background) daemonize();


    // 初始化服务端
    initServer();
    serverLog(LL_WARNING,"初始化");
    if (background || server.pidfile) createPidFile();
    if (server.set_proc_title) redisSetProcTitle(NULL);
    redisAsciiArt();
    checkTcpBacklogSettings();

    // 如果不是哨兵模式
    if (!server.sentinel_mode) {
    
        moduleInitModulesSystemLast();
        moduleLoadFromQueue();
        ACLLoadUsersAtStartup();
        InitServerLast();
        // 从磁盘上load AOF 或者是 RDB 文件，以便恢复之前的数据。
        loadDataFromDisk();
     
    } 

    /* 警告可疑的max-memory设置. */
    if (server.maxmemory > 0 && server.maxmemory < 1024*1024) {
        serverLog(LL_WARNING,"WARNING: You specified a maxmemory value that is less than 1MB (current value is %llu bytes). Are you sure this is what you really want?", server.maxmemory);
    }

    redisSetCpuAffinity(server.server_cpulist);
    setOOMScoreAdj(-1);

    // 进入事件驱动框架，开始循环处理各种事件
    aeMain(server.el);
    aeDeleteEventLoop(server.el);
    return 0;
}
```
#### 关键的代码
* 初始服务端的默认配置  initServerConfig();
* 初始化服务端 initServer();
* 进入事件驱动框架，开始循环处理各种触发的事件 aeMain(server.el);

#### 重点分析initServer函数

```
void initServer(void) {
    int j;

    //开启了 Unix 系统日志，则调用 openlog()与 Unix 系统日志建立输出连接，以便输出系统日志
    if (server.syslog_enabled) {
        openlog(server.syslog_ident, LOG_PID | LOG_NDELAY | LOG_NOWAIT,
            server.syslog_facility);
    }


    // 创建共享对象集合，这些数据可在各场景中共享使用,
    // 如小数字 0～9999、常用字符串+OK\r\n（命令处理成功响应字符串）、+PONG\r\n（ping 命令响应字符串）
    createSharedObjects();
    // 尝试修改环境变量，提高系统允许打开的文件描述符上限，避免由于大量客户端连接（Socket 文件描述符）导致错误。
    adjustOpenFilesLimit();
    const char *clk_msg = monotonicInit();
    serverLog(LL_NOTICE, "monotonic clock: %s", clk_msg);
    // 创建事件驱动框架
    server.el = aeCreateEventLoop(server.maxclients+CONFIG_FDSET_INCR);
    if (server.el == NULL) {
        serverLog(LL_WARNING,
            "Failed creating the event loop. Error message: '%s'",
            strerror(errno));
        exit(1);
    }
    // 分配db内存
    server.db = zmalloc(sizeof(redisDb)*server.dbnum);

    /* 监听端口 */
    if (server.port != 0 &&
        listenToPort(server.port,&server.ipfd) == C_ERR) {
        serverLog(LL_WARNING, "Failed listening on port %u (TCP), aborting.", server.port);
        exit(1);
    }
    /* 配置了 server.tls_ port，则开启 TLS Socket 服务，Redis 6.0 开始支持 TLS 连接. */
    if (server.tls_port != 0 &&
        listenToPort(server.tls_port,&server.tlsfd) == C_ERR) {
        serverLog(LL_WARNING, "Failed listening on port %u (TLS), aborting.", server.tls_port);
        exit(1);
    }

    /* 配置了 server.unixsocket，则开启 UNIX Socket 服务. */
    if (server.unixsocket != NULL) {
        unlink(server.unixsocket); /* don't care if this fails */
        server.sofd = anetUnixServer(server.neterr,server.unixsocket,
            server.unixsocketperm, server.tcp_backlog);
        if (server.sofd == ANET_ERR) {
            serverLog(LL_WARNING, "Opening Unix socket: %s", server.neterr);
            exit(1);
        }
        anetNonBlock(NULL,server.sofd);
        anetCloexec(server.sofd);
    }

    /* 如果根本没有监听套接字，则中止. */
    if (server.ipfd.count == 0 && server.tlsfd.count == 0 && server.sofd < 0) {
        serverLog(LL_WARNING, "Configured to not listen anywhere, exiting.");
        exit(1);
    }

    /* 创建Redis数据库，初始化其他内部状态。 */
    for (j = 0; j < server.dbnum; j++) {
        // 创建全局哈希表
        server.db[j].dict = dictCreate(&dbDictType,NULL);
        //创建过期key的信息表
        server.db[j].expires = dictCreate(&dbExpiresDictType,NULL);
        //为被BLPOP阻塞的key创建信息表
        server.db[j].expires_cursor = 0;
        //为被BLPOP阻塞的key创建信息表
        server.db[j].blocking_keys = dictCreate(&keylistDictType,NULL);
        //为将执行PUSH的阻塞key创建信息表
        server.db[j].ready_keys = dictCreate(&objectKeyPointerValueDictType,NULL);
        //为被MULTI/WATCH操作监听的key创建信息表
        server.db[j].watched_keys = dictCreate(&keylistDictType,NULL);
        server.db[j].id = j;
        server.db[j].avg_ttl = 0;
        server.db[j].defrag_later = listCreate();
        listSetFreeMethod(server.db[j].defrag_later,(void (*)(void*))sdsfree);
    }
    //初始化LRU 池
    evictionPoolAlloc(); /* Initialize the LRU keys pool. */
    

    /* 创建一个时间事件，执行函数为 serverCron，
     * 这是我们增量处理许多后台操作的方法，比如客户端超时，清除未访问的过期键等等. */
    if (aeCreateTimeEvent(server.el, 1, serverCron, NULL, NULL) == AE_ERR) {
        serverPanic("Can't create event loop timers.");
        exit(1);
    }

    /* 创建一个事件处理程序，用于接受TCP和Unix域套接字中的新连接. */
    if (createSocketAcceptHandler(&server.ipfd, acceptTcpHandler) != C_OK) {
        serverPanic("Unrecoverable error creating TCP socket accept handler.");
    }

    if (createSocketAcceptHandler(&server.tlsfd, acceptTLSHandler) != C_OK) {
        serverPanic("Unrecoverable error creating TLS socket accept handler.");
    }

    //创建文件事件，并注册相应的事件处理函数
    if (server.sofd > 0 && aeCreateFileEvent(server.el,server.sofd,AE_READABLE,
        acceptUnixHandler,NULL) == AE_ERR) serverPanic("Unrecoverable error creating server.sofd file event.");

    /*  注册一个可读事件，用于在模块中阻塞的客户端需要注意时唤醒事件循环。*/
    if (aeCreateFileEvent(server.el, server.module_blocked_pipe[0], AE_READABLE,
        moduleBlockedClientPipeReadable,NULL) == AE_ERR) {
            serverPanic(
                "Error registering the readable event for the module "
                "blocked clients subsystem.");
    }

    /* 注册事件驱动框架的钩子函数，事件循环器在每次阻塞前后都会调用钩子函数*/
    aeSetBeforeSleepProc(server.el,beforeSleep);
    aeSetAfterSleepProc(server.el,afterSleep);

    /* 如果需要，打开AOF文件. */
    if (server.aof_state == AOF_ON) {
        server.aof_fd = open(server.aof_filename,
                               O_WRONLY|O_APPEND|O_CREAT,0644);
        if (server.aof_fd == -1) {
          
            exit(1);
        }
    }

    /* 如果 Redis 运行在 32 位操作系统上，由于 32 位操作系统内存空间限制为 4GB，所以将 Redis 使用内存限制为 3GB，避免 Redis 服务器因内存不足而崩溃。. */
    if (server.arch_bits == 32 && server.maxmemory == 0) {
        serverLog(LL_WARNING,"Warning: 32 bit instance detected but no memory limit set. Setting 3 GB maxmemory limit with 'noeviction' policy now.");
        server.maxmemory = 3072LL*(1024*1024); /* 3 GB */
        server.maxmemory_policy = MAXMEMORY_NO_EVICTION;
    }
    // 如果是Cluster 模式启动则初始化集群相关的
    if (server.cluster_enabled) clusterInit();
    replicationScriptCacheInit();
    // 初始化LUA机制
    scriptingInit(1);
    // 初始化慢日志机制
    slowlogInit();
    //初始化延迟监控机制
    latencyMonitorInit();
    
    ACLUpdateDefaultUserPassword(server.requirepass);
}
```

## 总结
* RedisServer的整体启动流程:
    *  初始化默认配置
    *  解析启动命令
    *  初始化server
    *  启动事件驱动框架
    *  循环处理各种事件
* RedisServer结构体存储服务端配置项、运行时数据

## 参考文献
* *[极客时间-Redis源码剖析与实战](https://time.geekbang.org/column/article/406556)* </br>
*  *[Redis启动过程源码分析](https://xie.infoq.cn/article/751e23bb966aca71ba789b41c)* </br>

