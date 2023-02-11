## 
1. 服务的socket在哪里初始化？ 
2. 在哪里accept连接？ 
3. 理顺服务端启动流程 
4. ServerBootstrap外观，NioServerSocketChannel创建，初始化，注册selector，绑定端口，接受新连接

## 
1. 默认情况下，Netty服务端启动多少线程？何时启动？
2. Netty如何解决JDK空轮询bug？ 
3. Netty如何保证异步串行无锁化？ 
4. 吃透高并发线程模型 
5. 深入理解Netty无锁化串行设计，精心设计的reactor线程模型将 
6. 榨干你的cpu，打满你的网卡，让你的应用程序性能爆表

##
1. Netty在哪里检测有新连接接入的？
2. 新连接是怎样注册到NioEventLoop线程的？
3. 通晓新连接接入流程
4. boos reactor线程，监测新连接，创建NioSocketChannel，IO线程分配，selector注册事件

##
1. Netty是如何判断ChannelHandler类型的？
2. 对于ChannelHandler的添加应遵循什么顺序？
3. 用户手动触发事件传播，不同触发方式的区别？
4. 明晰事件传播机制脉络
5. 大动脉pipeline，处理器channelHandler，inbound、outbound事件传播，异常传播

## 
1. Netty内存类别有哪些？
2. 如何减少多线程内存分配之间的竞争？
3. 不同大小的内存是如何进行分配的？
4. 攻破内存分配机制
5. ByteBufAllocator分类，ByteBuf分类，堆内堆外，池化非池化，
6. Unsafe非Unsafe，area、chunk、page、subpage，内存分级，
7. 内存缓存片段等概念一网打尽

## 
1. 解码器抽象的解码过程是什么样的？
2. Netty里面有哪些拆箱即用的解码器？
3. 如何把对象变成字节流，最终写到Socket底层？
4. 掌握编解码原理
5. 编解码顶层抽象，定长解码器，行解码器，分隔符解码器，基于 长度域解码器全面分析，编码抽象，writeAndFlush深入分析
