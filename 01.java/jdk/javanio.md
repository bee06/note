## 定义
《Scalable IO in Java》 是Doug Lea关于分析与构建可伸缩的高性能IO服务的经典文章。
原文地址: https://gee.cs.oswego.edu/dl/cpjslides/nio.pdf
## 目录
* 可扩展的网络服务 
* 事件驱动处理
* 反应堆模式 
  * 基本版本 
  * 多线程版本 
  * 其他变体 
* java.nio非阻塞IO API演示

### 网络服务
* Web服务、分布式对象等大多具有相同的基本结构：
  * 读取请求
  * 解码请求
  * 处理服务
  * 编码回复
  * 发送回复。
* 但每个步骤的成本不同，包括XML解析、文件传输、网页生成和计算服务等。
  
* 每个处理程序可以在自己的线程中启动。
  
```
class Server implements Runnable {
    public void run() {
        try {
            ServerSocket ss = new ServerSocket(PORT);
            while (!Thread.interrupted())
                new Thread(new Handler(ss.accept())).start();

            or, single-threaded, or a thread pool
        } catch (IOException ex) { 
        }
    }

    static class Handler implements Runnable {
        final Socket socket;

        Handler(Socket s) {
            socket = s;
        }

        public void run() {
            try {
                byte[] input = new byte[MAX_INPUT];
                socket.getInputStream().read(input);

                byte[] output = process(input);
                socket.getOutputStream().write(output);
            } catch (IOException ex) { 
            }
        }

        private byte[] process(byte[] cmd) { 
        }
    }
}

```

### 可扩展性目标
* 在负载增加（更多客户端）的情况下优雅降级 持续改进
* 随着资源的增加（CPU、内存、磁盘、带宽） 
* 同时满足可用性和性能目标 
  * 低延迟 
  * 满足峰值需求 
  * 可调整服务质量 
* "分而治之"通常是实现任何可扩展性目标的最佳方法

### 分而治之
* 将处理过程分成小任务，
  * 每个任务执行一个操作而不会阻塞。
* 当启用每个任务时执行它。在这里，通常使用IO事件作为触发器。
* Java.nio支持的基本机制
  * 非阻塞读写，
  * 分派与感知IO事件相关的任务。
* 无尽的变化可能性构成了
  * 一系列事件驱动设计。
  
## 事件驱动设计
* 通常比其他选择更有效率。
  * 更少的资源
    * 通常不需要为每个客户端创建一个线程
  * 更少的开销
    * 较少的上下文切换，通常意味着较少的锁定
  * 但分派可能会更慢。
    * 必须手动将操作绑定到事件

* 通常更难编程
  * 必须分解成简单的非阻塞动作。
    * 类似于图形用户界面事件驱动的操作
    * 无法消除所有阻塞：GC、页面错误等。
    * 必须跟踪服务的逻辑状态

## 反应器模式
* 反应堆通过分派处理程序来响应IO事件
  * 类似于 AWT 线程
* 处理程序执行非阻塞操作
  * 类似于 AWT 的 ActionListeners
* 通过将处理程序绑定到事件来管理
  * 类似于 AWT addActionListener

### 基本反应堆设计
* 单线程版本

### java.nio 支持
* 通道----支持非阻塞读取的文件、套接字等连接。
* 缓存区---类似数组的对象，可以直接被通道读取或写入
* 选择器---告诉我哪些通道有IO事件。
* 选择键集合---保持IO事件状态和绑定

#### 反应堆1：设置

```
class Reactor implements Runnable {
    final Selector selector;
    final ServerSocketChannel serverSocket;

    Reactor(int port) throws IOException {
        selector = Selector.open();
        serverSocket = ServerSocketChannel.open();
        serverSocket.socket().bind(new InetSocketAddress(port));
        serverSocket.configureBlocking(false);

        SelectionKey sk = serverSocket.register(selector, SelectionKey.OP_ACCEPT);
        sk.attach(new Acceptor());
    }
}

```

#### 反应堆2：循环调度

```
public void run() { //通常在一个新的线程中
    try {
        while (!Thread.interrupted()) {
            selector.select();
            Set selected = selector.selectedKeys();
            Iterator it = selected.iterator();
            while (it.hasNext())
                dispatch((SelectionKey)(it.next());
            selected.clear();
        }
    } catch (IOException ex) { 

     }
}
    
void dispatch(SelectionKey k) {
    Runnable r = (Runnable)(k.attachment());
    if (r != null)
        r.run();
}
```

### 反应堆3：接受者
```
class Acceptor implements Runnable { // inner
    public void run() {
        try {
            SocketChannel c = serverSocket.accept();

            if (c != null) {
                new Handler(selector, c);
            }
        } catch (IOException ex) { /* ... */
        }
    }
}
```

### 反应堆4：处理程序设置

```
final class Handler implements Runnable {
    static final int READING = 0;
    static final int SENDING = 1;
    final SocketChannel socket;
    final SelectionKey sk;
    ByteBuffer input = ByteBuffer.allocate(MAXIN);
    ByteBuffer output = ByteBuffer.allocate(MAXOUT);
    int state = READING;

    Handler(Selector sel, SocketChannel c) throws IOException {
        socket = c;
        c.configureBlocking(false);
        // Optionally try first read now
        sk = socket.register(sel, 0);
        sk.attach(this);
        sk.interestOps(SelectionKey.OP_READ);
        sel.wakeup();
    }
    boolean inputIsComplete() { /* ... */ }
    boolean outputIsComplete() { /* ... */ }
    void process() { /* ... */ }
}


```

### 反应堆5：请求处理

```
public void run() {
    try {
        if (state == READING)read();
        else if (state == SENDING) send();
    } catch (IOException ex) { /* ... */ }
}

void read() throws IOException {
    socket.read(input);
    if (inputIsComplete()) {
        process();
        state = SENDING;
    // Normally also do first write now
        sk.interestOps(SelectionKey.OP_WRITE);
    }
}

void send() throws IOException {
    socket.write(output);
    if (outputIsComplete()) sk.cancel();
}

```

### Per-State 处理程序
* GoF状态对象模式的简单使用
  * 将适当的处理程序重新绑定为附件
  
```
class Handler {
    // ...
    public void run() {
        // initial state is reader
        socket.read(input);
        if (inputIsComplete()) {
            process();
            sk.attach(new Sender());
            sk.interest(SelectionKey.OP_WRITE);
            sk.selector().wakeup();
        }
    }
     class Sender implements Runnable {
        public void run() {
            // ...
            socket.write(output);
            if (outputIsComplete())
                sk.cancel();
        }
    }
}
```

### 多线程设计
* 为了可扩展性而战略性地添加线程
  * 主要适用于多处理器
* 工作线程
  * 反应器应该快速触发处理程序,处理程序的处理会减慢反应器的速度,将非IO处理卸载到其他线程上
* 多个反应器线程
  * 反应器线程可能会因为IO操作而饱和,
  * 将负载分配到其他反应器上
  * "负载均衡以匹配CPU和IO速率
  
### 工作线程
* 将非I/O处理卸载以加速反应器线程
* “比重新设计计算绑定处理为事件驱动形式更简单
  * 应该仍然是纯非阻塞计算,“足够的处理能够超过开销,“但是与IO重叠处理更加困难
* 最好的方法是先将所有输入读入缓冲区
* “使用线程池以进行调整和控制
* 通常需要的线程比客户端少得多

### 使用线程池处理
```
class Handler implements Runnable {
    // uses util.concurrent thread pool
    static PooledExecutor pool = new PooledExecutor(...);
    static final int PROCESSING = 3;
    // ...
    synchronized void read() { // ...
        socket.read(input);
        if (inputIsComplete()) {
            state = PROCESSING;
            pool.execute(new Processer());
        }
    }
    synchronized void processAndHandOff() {
        process();
        state = SENDING; // or rebind attachment
        sk.interest(SelectionKey.OP_WRITE);
    }
    class Processer implements Runnable {
        public void run() { processAndHandOff(); }
    }
}
```

### 协调任务
* 转移
  * 每个任务都会启用、触发或调用下一个任务,通常是最快的，但可能不够稳定
* 回调到每个处理程序分发器
  * 设置状态
* 队列
  * 例如，在不同阶段之间传递缓冲区
* Futures

### 使用 PooledExecutor
* 可调节的工作线程池
* 主方法执行(Runnable r)
* 控制项：
  * 任务队列类型
  * 最大线程数
  * 最小线程数
  * 按需分配线程
  * 保持活动状态的时间间隔，直到空闲线程死亡
  * 饱和度策略
  
### 多个反应器线程

* 使用反应堆池
  * 用于匹配CPU和IO速率
  * 静态或动态构造
    * 每个都有自己的选择器、线程和调度循环
    * 主接受器分配给其他反应器

    ```
    Selector[] selectors;
    int next = 0;
    class Acceptor {
        // ...
        public synchronized void run() {
            // ...
            Socket connection = serverSocket.accept();
            if (connection != null)
                new Handler(selectors[next], connection);
            if (++next == selectors.length)
                next = 0;
        }
    }
    ```
### 使用其他的java.nio功能
* 每个反应器多个选择器
  * 将不同的处理程序绑定到不同的IO事件可能需要仔细协调以进行同步。
* 文件传输
  * 自动文件到网络或网络到文件的复制
* 内存映射文件
  * 通过缓冲区访问文件
* 直接缓冲区
  
### 基于连接的扩展
* 不是单一的服务请求
  * 客户端连接
  * 客户端发送一系列消息/请求
  * 客户端断开连接
* 范例
  * 数据库和事务监控器
  * 多参与者游戏、聊天等
* 可以扩展基本网络服务模式
  * 处理许多相对长期的客户端
  * 跟踪客户端和会话状态（包括掉线）
  * 将服务分布在多个主机上

