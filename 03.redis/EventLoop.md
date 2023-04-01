## 前言
* 上面我们分析了redis服务端启动过程,这篇文章我们分析下redis的事件框架，这个也是redis高性能方面的关键实现
  
## 结构图
## 入口
### 创建事件框架
* 代码位置  void initServer(void);
  ```
  // 创建事件驱动框架
    server.el = aeCreateEventLoop(server.maxclients+CONFIG_FDSET_INCR);
  ```

  在配置服务器eventloop时，我们将其设置为可以处理的文件描述符的总数为服务器。maxclients + RESERVED_FDS +一些以保持安全。由于RESERVED_FDS默认为32，我们添加96以确保不超过128个fds
  #define CONFIG_MIN_RESERVED_FDS 32
  #define CONFIG_FDSET_INCR (CONFIG_MIN_RESERVED_FDS+96)
  入参是 配置的服务器最大客户端数据+CONFIG_FDSET_INCR（32+96）

  ```
  // 创建 eventLoop
aeEventLoop *aeCreateEventLoop(int setsize) {
    aeEventLoop *eventLoop;
    int i;

    monotonicInit();    /* 以防调用程序没有初始化 */

    if ((eventLoop = zmalloc(sizeof(*eventLoop))) == NULL) goto err;
    eventLoop->events = zmalloc(sizeof(aeFileEvent)*setsize);
    eventLoop->fired = zmalloc(sizeof(aeFiredEvent)*setsize);
    if (eventLoop->events == NULL || eventLoop->fired == NULL) goto err;
    eventLoop->setsize = setsize;
    eventLoop->timeEventHead = NULL;
    eventLoop->timeEventNextId = 0;
    eventLoop->stop = 0;
    eventLoop->maxfd = -1;
    eventLoop->beforesleep = NULL;
    eventLoop->aftersleep = NULL;
    eventLoop->flags = 0;
    if (aeApiCreate(eventLoop) == -1) goto err;
    /* Events with mask == AE_NONE are not set. So let's initialize the
     * vector with it. */
    for (i = 0; i < setsize; i++)
        eventLoop->events[i].mask = AE_NONE;
    return eventLoop;

err:
    if (eventLoop) {
        zfree(eventLoop->events);
        zfree(eventLoop->fired);
        zfree(eventLoop);
    }
    return NULL;
}
  ```