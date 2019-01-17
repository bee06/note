## Netty基础相关问题
讲讲Netty的特点？
BIO、NIO和AIO的区别？
NIO的组成是什么？
如何使用 Java NIO 搭建简单的客户端与服务端实现网络通讯？
如何使用 Netty 搭建简单的客户端与服务端实现网络通讯？
讲讲Netty 底层操作与 Java NIO 操作对应关系？
Channel 与 Socket是什么关系，Channel 与 EventLoop是什么关系，Channel 与 ChannelPipeline是什么关系？
EventLoop与EventLoopGroup 是什么关系？
说说Netty 中几个重要的对象是什么，它们之间的关系是什么？
Netty 的线程模型是什么？

## 粘包与半包和分隔符相关问题
什么是粘包与半包问题?
粘包与半包为何会出现?
如何避免粘包与半包问题？
如何使用包定长 FixedLengthFrameDecoder 解决粘包与半包问题？原理是什么？
如何使用包分隔符 DelimiterBasedFrameDecoder 解决粘包与半包问题？原理是什么？
Dubbo 在使用 Netty 作为网络通讯时候是如何避免粘包与半包问题？
Netty框架本身存在粘包半包问题？
什么时候需要考虑粘包与半包问题？
## WebSocket 协议开发相关问题
讲讲如何实现 WebSocket 长连接？

讲讲WebSocket 帧结构的理解？

浏览器、服务器对 WebSocket 的支持情况

如何使用 WebSocket 接收和发送广本信息？

如何使用 WebSocket 接收和发送二进制信息？

## Netty源码分析相关问题
服务端如何进行初始化？

何时接受客户端请求？

何时注册接受 Socket 并注册到对应的 EventLoop 管理的 Selector ？

客户端如何进行初始化？

何时创建的 DefaultChannelPipeline ？

讲讲Netty的零拷贝？
