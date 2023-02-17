### 下面我看看大多数与CMS收集器调优相关的JVM标志参数。

* -XX：+UseConcMarkSweepGC
> 该标志首先是激活CMS收集器。默认HotSpot JVM使用的是并行收集器。

* -XX：UseParNewGC
当使用CMS收集器时，该标志激活年轻代使用多线程并行执行垃圾回收。这令人很惊讶，我们不能简单在并行收集器中重用-XX：UserParNewGC标志，因为概念上年轻代用的算法是一样的。然而，对于CMS收集器，年轻代GC算法和老年代GC算法是不同的，因此年轻代GC有两种不同的实现，并且是两个不同的标志。

注意最新的JVM版本，当使用-XX：+UseConcMarkSweepGC时，-XX：UseParNewGC会自动开启。因此，如果年轻代的并行GC不想开启，可以通过设置-XX：-UseParNewGC来关掉。

* -XX：+CMSConcurrentMTEnabled
当该标志被启用时，并发的CMS阶段将以多线程执行(因此，多个GC线程会与所有的应用程序线程并行工作)。该标志已经默认开启，如果顺序执行更好，这取决于所使用的硬件，多线程执行可以通过-XX：-CMSConcurremntMTEnabled禁用。

 -XX：ConcGCThreads
标志-XX：ConcGCThreads=<value>(早期JVM版本也叫-XX:ParallelCMSThreads)定义并发CMS过程运行时的线程数。比如value=4意味着CMS周期的所有阶段都以4个线程来执行。尽管更多的线程会加快并发CMS过程，但其也会带来额外的同步开销。因此，对于特定的应用程序，应该通过测试来判断增加CMS线程数是否真的能够带来性能的提升。

如果还标志未设置，JVM会根据并行收集器中的-XX：ParallelGCThreads参数的值来计算出默认的并行CMS线程数。该公式是ConcGCThreads = (ParallelGCThreads + 3)/4。因此，对于CMS收集器， -XX:ParallelGCThreads标志不仅影响“stop-the-world”垃圾收集阶段，还影响并发阶段。

总之，有不少方法可以配置CMS收集器的多线程执行。正是由于这个原因,建议第一次运行CMS收集器时使用其默认设置, 然后如果需要调优再进行测试。只有在生产系统中测量(或类生产测试系统)发现应用程序的暂停时间的目标没有达到 , 就可以通过这些标志应该进行GC调优。

-XX:CMSInitiatingOccupancyFraction
当堆满之后，并行收集器便开始进行垃圾收集，例如，当没有足够的空间来容纳新分配或提升的对象。对于CMS收集器，长时间等待是不可取的，因为在并发垃圾收集期间应用持续在运行(并且分配对象)。因此，为了在应用程序使用完内存之前完成垃圾收集周期，CMS收集器要比并行收集器更先启动。

因为不同的应用会有不同对象分配模式，JVM会收集实际的对象分配(和释放)的运行时数据，并且分析这些数据，来决定什么时候启动一次CMS垃圾收集周期。为了引导这一过程， JVM会在一开始执行CMS周期前作一些线索查找。该线索由 -XX:CMSInitiatingOccupancyFraction=<value>来设置，该值代表老年代堆空间的使用率。比如，value=75意味着第一次CMS垃圾收集会在老年代被占用75%时被触发。通常CMSInitiatingOccupancyFraction的默认值为68(之前很长时间的经历来决定的)。

-XX：+UseCMSInitiatingOccupancyOnly
我们用-XX+UseCMSInitiatingOccupancyOnly标志来命令JVM不基于运行时收集的数据来启动CMS垃圾收集周期。而是，当该标志被开启时，JVM通过CMSInitiatingOccupancyFraction的值进行每一次CMS收集，而不仅仅是第一次。然而，请记住大多数情况下，JVM比我们自己能作出更好的垃圾收集决策。因此，只有当我们充足的理由(比如测试)并且对应用程序产生的对象的生命周期有深刻的认知时，才应该使用该标志。

-XX:+CMSClassUnloadingEnabled
相对于并行收集器，CMS收集器默认不会对永久代进行垃圾回收。如果希望对永久代进行垃圾回收，可用设置标志-XX:+CMSClassUnloadingEnabled。在早期JVM版本中，要求设置额外的标志-XX:+CMSPermGenSweepingEnabled。注意，即使没有设置这个标志，一旦永久代耗尽空间也会尝试进行垃圾回收，但是收集不会是并行的，而再一次进行Full GC。

-XX:+CMSIncrementalMode
该标志将开启CMS收集器的增量模式。增量模式经常暂停CMS过程，以便对应用程序线程作出完全的让步。因此，收集器将花更长的时间完成整个收集周期。因此，只有通过测试后发现正常CMS周期对应用程序线程干扰太大时，才应该使用增量模式。由于现代服务器有足够的处理器来适应并发的垃圾收集，所以这种情况发生得很少。

-XX:+ExplicitGCInvokesConcurrent and -XX:+ExplicitGCInvokesConcurrentAndUnloadsClasses
如今,被广泛接受的最佳实践是避免显式地调用GC(所谓的“系统GC”)，即在应用程序中调用system.gc()。然而，这个建议是不管使用的GC算法的，值得一提的是，当使用CMS收集器时，系统GC将是一件很不幸的事，因为它默认会触发一次Full GC。幸运的是，有一种方式可以改变默认设置。标志-XX:+ExplicitGCInvokesConcurrent命令JVM无论什么时候调用系统GC，都执行CMS GC，而不是Full GC。第二个标志-XX:+ExplicitGCInvokesConcurrentAndUnloadsClasses保证当有系统GC调用时，永久代也被包括进CMS垃圾回收的范围内。因此，通过使用这些标志，我们可以防止出现意料之外的”stop-the-world”的系统GC。

-XX:+DisableExplicitGC
然而在这个问题上…这是一个很好提到- XX:+ DisableExplicitGC标志的机会，该标志将告诉JVM完全忽略系统的GC调用(不管使用的收集器是什么类型)。对于我而言，该标志属于默认的标志集合中，可以安全地定义在每个JVM上运行，而不需要进一步思考。




2018-06-12T22:05:33.678+0800: 19.252: [GC (CMS Initial Mark) [1 CMS-initial-mark: 85194K(7094272K)] 1113994K(9306112K), 0.1282654 secs] [Times: user=0.39 sys=0.00, real=0.13 secs]
时间+时区                                 开始使用CMS回收器进行老年代回收，这个阶段标记由根可以直接到达的对象，标记期间整个应用线程会暂停。
2018-06-12T22:05:33.807+0800: 19.380: [CMS-concurrent-mark-start]
开始并发标记(concurrent-mark-start) 阶段
2018-06-12T22:05:33.888+0800: 19.461: [CMS-concurrent-mark: 0.081/0.081 secs] [Times: user=0.12 sys=0.02, real=0.08 secs]
并发标记阶段结束
2018-06-12T22:05:33.888+0800: 19.461: [CMS-concurrent-preclean-start]
开始预清理
2018-06-12T22:05:33.906+0800: 19.479: [CMS-concurrent-preclean: 0.018/0.018 secs] [Times: user=0.03 sys=0.00, real=0.02 secs]
预清理结束

2018-06-12T22:05:33.906+0800: 19.479: [CMS-concurrent-abortable-preclean-start] CMS: abort preclean due to time 2018-06-12T22:05:38.947+0800: 24.520: [CMS-concurrent-abortable-preclean: 4.381/5.041 secs] [Times: user=13.31 sys=0.73, real=5.04 secs]
2018-06-12T22:05:38.947+0800: 24.520: [GC (CMS Final Remark)[YG occupancy: 1922909 K (2211840 K)]2018-06-12T22:05:38.947+0800: 24.520:
[GC (CMS Final Remark)

2018-06-12T22:05:38.947+0800: 24.520: [ParNew: 1922909K->188209K(2211840K), 0.2647720 secs] 2008104K->308808K(9306112K), 0.2663288 secs] [Times: user=0.88 sys=0.01, real=0.27 secs]
2018-06-12T22:05:39.214+0800: 24.787: [Rescan (parallel) , 0.0446848 secs]
2018-06-12T22:05:39.258+0800: 24.831: [weak refs processing, 0.0000548 secs]
2018-06-12T22:05:39.258+0800: 24.832: [class unloading, 0.0076217 secs]2
018-06-12T22:05:39.266+0800: 24.839:  [scrub symbol table, 0.0066305 secs]
2018-06-12T22:05:39.273+0800: 24.846: [scrub string table, 0.0058460 secs]

[1 CMS-remark: 120599K(7094272K)] 308808K(9306112K), 0.3331970 secs] [Times: user=1.08 sys=0.01, real=0.34 secs]

2018-06-12T22:05:39.281+0800: 24.854: [CMS-concurrent-sweep-start]
开始并发清理阶段，在清理阶段，应用线程还在运行
2018-06-12T22:05:39.334+0800: 24.907: [CMS-concurrent-sweep: 0.049/0.054 secs] [Times: user=0.20 sys=0.01, real=0.05 secs]
并发清理阶段费时0.126秒
2018-06-12T22:05:39.334+0800: 24.907: [CMS-concurrent-reset-start]
开始并发重置
2018-06-12T22:05:39.351+0800: 24.924: [CMS-concurrent-reset: 0.016/0.016 secs] [Times: user=0.07 sys=0.00, real=0.02 secs]
重新初始化CMS内部数据结构，以备下一轮 GC 使用


我强烈建议大家去创建一个学习英语的环境，自觉养成一个看英语、读英语、写英语、听英语的习惯
