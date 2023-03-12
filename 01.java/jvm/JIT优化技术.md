> 翻译地址：https://advancedweb.hu/2016/05/27/jvm_jit_optimization_techniques/
### 摘要
JVM JIT优化技术概述和有趣的测试
这是JVM JIT优化技术系列中的第一篇文章，一定也要给其他人看看。
目录
1.  JVM JIT 优化技术
2.  [JVM JIT 优化技术 - 第二章](https://advancedweb.hu/2016/06/28/jvm_jit_optimization_techniques_part_2/)
3.  [jvm基于配置文件的优化技术](https://advancedweb.hu/2017/03/01/jvm_optimistic_optimizations/)

### 开始

由于（JIT）编译的各种优化技术，JVM优化以及它如何使生产代码表现更好得到了很多关注，有很多优秀的研究资料可供选择，但我想自己看下这些在实践中是如何应用的。因此我决定深入挖掘并进行一些测量。

在测量完成之后，不同JVM实现和体系结构之间可能存在差异。
不同的jvm实现和体系结构可能得到不同的结果。所以在这篇文章中，我不打算给出精确的测量结果，只是鸟瞰平台的可能性。

### 延迟编译
