## 偏向锁
## 轻量锁
## 重量锁
## 重入锁
## 读写锁

## sychronized
## volatile
## reentrankLock


## Lock

java.util.concurrent.locks public interface Lock

Lock implementations provide more extensive locking operations than can be obtained using synchronized methods and statements.

锁定实现提供了比使用同步方法和语句可以获得的更广泛的锁定操作


They allow more flexible structuring, may have quite different properties, and may support multiple associated Condition objects.
它们允许更灵活的结构, 可能具有相当不同的属性, 并支持多个关联的条件对象

A lock is a tool for controlling access to a shared resource by multiple threads.
锁是通过多个线程控制对共享资源的访问的工具。

Commonly, a lock provides exclusive access to a shared resource: only one thread at a time can acquire the lock and all access to the shared resource requires that the lock be acquired first.

通常 锁提供对共享资源的独占访问权限，一次只有一个线程可以获取锁, 并且对共享资源的所有访问都要求首先获取锁

However, some locks may allow concurrent access to a shared resource, such as the read lock of a ReadWriteLock.
然而,某些锁可能允许对共享资源进行并发访问,如 ReadWriteLock 的读锁定

The use of synchronized methods or statements provides access to the implicit monitor lock associated with every object, but forces all lock acquisition and release to occur in a block-structured way:
when multiple locks are acquired they must be released in the opposite order, and all locks must be released in the same lexical scope in which they were acquired.
使用同步方法或语句提供对与每个对象关联的隐式监视器锁的访问,但强制所有锁获取和释放以块结构的方式发生
当获取多个锁时, 它们必须以相反的顺序释放, 并且所有锁必须在获取它们的同一词法范围内释放。

While the scoping mechanism for synchronized methods and statements makes it much easier to program with monitor locks, and helps avoid many common programming errors involving locks, there are occasions where you need to work with locks in a more flexible way.

虽然同步方法和语句的作用域机制使使用监视器锁编程更容易,并且帮助避免许多涉及锁的常见编程错误, 有时需要用更灵活的方式处理锁

For example, some algorithms for traversing concurrently accessed data structures require the use of "hand-over-hand" or "chain locking": you acquire the lock of node A, then node B, then release A and acquire C, then release B and acquire D and so on. Implementations of the Lock interface enable the use of such techniques by allowing a lock to be acquired and released in different scopes, and allowing multiple locks to be acquired and released in any order.
例如, 一些遍历并发访问数据结构的算法需要使用 "手动" 或 "链锁"。获取节点 A、节点 B 的锁, 然后释放 a 并获取 C, 然后释放 B 并获取 D 等。锁接口的实现允许在不同的范围内获取和释放锁, 并允许以任何顺序获取和释放多个锁, 从而使用此类技术。


With this increased flexibility comes additional responsibility. The absence of block-structured locking removes the automatic release of locks that occurs with synchronized methods and statements. In most cases, the following idiom should be used:
随着这一增加的灵活性来额外的责任,缺少块结构化锁定会删除同步方法和语句所发生的锁的自动释放。在大多数情况下, 应使用以下成语

   Lock l = ...;
  l.lock();
  try {
    // access the resource protected by this lock
  } finally {
    l.unlock();
  }

When locking and unlocking occur in different scopes, care must be taken to ensure that all code that is executed while the lock is held is protected by try-finally or try-catch to ensure that the lock is released when necessary.
当锁定和解锁发生在不同的范围内时,必须注意确保在锁被持有时执行的所有代码都通过尝试-最终或尝试捕获来保护, 以确保在必要时释放锁

Lock implementations provide additional functionality over the use of synchronized methods and statements by providing a non-blocking attempt to acquire a lock (tryLock()),
an attempt to acquire the lock that can be interrupted (lockInterruptibly, and an attempt to acquire the lock that can timeout (tryLock(long, TimeUnit)).

通过提供非阻塞尝试获取锁 (tryLock ()), 锁实现通过使用同步方法和语句提供了附加功能,尝试获取可以中断的锁 (lockInterruptibly, 并尝试获取可以超时的锁 (tryLock (long, TimeUnit))

A Lock class can also provide behavior and semantics that is quite different from that of the implicit monitor lock, such as guaranteed ordering, non-reentrant usage, or deadlock detection.

锁类还可以提供与隐式监视器锁完全不同的行为和语义,例如保证排序、不可重入使用或死锁检测。

If an implementation provides such specialized semantics then the implementation must document those semantics.
Note that Lock instances are just normal objects and can themselves be used as the target in a synchronized statement.
如果实现提供了这样的专门化语义, 则实现必须记录这些语义
请注意, 锁定实例只是普通对象, 并且可以在同步语句中用作目标

Acquiring the monitor lock of a Lock instance has no specified relationship with invoking any of the lock methods of that instance.
获取锁实例的监视器锁与调用该实例的任何锁方法没有指定关系


It is recommended that to avoid confusion you never use Lock instances in this way, except within their own implementation.
建议避免混淆, 您从来没有这样使用锁实例, 除非在他们自己的实现中

Except where noted, passing a null value for any parameter will result in a NullPointerException being thrown.
Memory Synchronization

除非注意到, 为任何参数传递 null 值将导致而当前被抛出.
Memory 同步

All Lock implementations must enforce the same memory synchronization semantics as provided by the built-in monitor lock, as described in The Java Language Specification (17.4 Memory Model) :
所有锁实现都必须按照 Java 语言规范 (17.4 内存模型) 中所述, 强制执行内置监视器锁提供的相同内存同步语义。
A successful lock operation has the same memory synchronization effects as a successful Lock action
成功的锁操作与成功的锁定操作具有相同的内存同步效果。
A successful unlock operation has the same memory synchronization effects as a successful Unlock action.
成功的解锁操作与成功的解锁操作具有相同的内存同步效果
Unsuccessful locking and unlocking operations, and reentrant locking/unlocking operations, do not require any memory synchronization effects.
不成功的锁定和解锁操作, 以及重入锁定/解锁操作, 不需要任何内存同步效果

Implementation Considerations
实施注意事项

The three forms of lock acquisition (interruptible, non-interruptible, and timed) may differ in their performance characteristics, ordering guarantees, or other implementation qualities.

Further, the ability to interrupt the ongoing acquisition of a lock may not be available in a given Lock class.
此外, 在给定的锁类中, 中断正在进行的锁的获取的能力可能不可用

Consequently, an implementation is not required to define exactly the same guarantees or semantics for all three forms of lock acquisition, nor is it required to support interruption of an ongoing lock acquisition.
因此, 不需要实现为所有三种形式的锁获取定义完全相同的保证或语义, 也不需要支持正在进行的锁捕获中断

An implementation is required to clearly document the semantics and guarantees provided by each of the locking methods.
需要一个实现来清楚地记录每个锁定方法提供的语义和保证

It must also obey the interruption semantics as defined in this interface, to the extent that interruption of lock acquisition is supported: which is either totally, or only on method entry.

As interruption generally implies cancellation, and checks for interruption are often infrequent, an implementation can favor responding to an interrupt over normal method return. This is true even if it can be shown that the interrupt occurred after another action may have unblocked the thread. An implementation should document this behavior.
