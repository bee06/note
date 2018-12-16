## 源码分析
### 设计模式
  - Proxy设计模式
  - Factory设计模式
  - Singleton 单例模式
  - Delegate
  - strategy
  - prototype
  - template
### Spring5
### mybatis
### dubbo

## 工程化

## 分布式
## 微服务

## 性能优化
## 并发编程
### jmm

### Synchronized
- 理解什么是线程安全。
- Synchronized、ReentrantLock 等机制的基本使用与案例。

- 掌握 Synchronized、ReentrantLock 底层实现；理解锁膨胀、降级；理解偏斜锁、自旋锁、轻量级锁、重量级锁等概念。

- 掌握并发包中 java.util.concurrent.lock 各种不同实现和案例分析

线程安全需要保证几个基本特性：

- 原子性，简单说就是相关操作不会中途被其他线程干扰，一般通过同步机制实现。
- 可见性，是一个线程修改了某个共享变量，其状态能够立即被其他线程知晓，通常被解释为将线程本地状态反映到主内存上，volatile 就是负责保证可见性的。
- 有序性，是保证线程内串行语义，避免指令重排等。
-
### volatile
### 单例
### 并发基础
- aqs
- cas
### 锁
### 开发工具类
### 并发集合
### 原子操作
### 引用模型
### 线程池
### 其他

## 运维
- perf查看cpu占用
- greys-anatomy
- hystrix降级
