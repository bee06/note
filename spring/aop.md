## aop命名空间
AopNamespaceHandler
* AspectJAutoProxyBeanDefinitionParser#parse
  - 注册AspectJAnnotationAutoProxyCreator


### 知识点
  - vmstat
  - JMC(Java Mission Control)来查找热点
  - 并行计算

计算得分
scoreCalculateTask 定时任务，通过spring-schedule调用 5分钟执行一次
同步全部或者增量
计算酒店的评分和子项评分任务V2
  - 拿到seq列表
  - 获取酒店下所有点评id
    - 试睡员 有内容 权重 1.2 无内容 0.8
    - 交易用户 有内容 1.2  无 0.8
    - 绑定用户 有内容 1  无 0.5
    - 默认用户 0.5 无内容 0
  -
  只计算可显示的
  不是去哪的也不计算
  普通点评
    不是新点评并且是去哪的


cms和g1老年代都在后台线程执行，缺点就是消耗cpu的

初始young区的大小=初始heap/ 1+newratio（“设置新生代与老年代的空间占用比率。”）



-XX:+UnlockCommercialFeatures -XX:+FlightRecorder -XX:StartFlightRecording=delay=20s,duration=60s,name=MyRecording,filename=/tmp/myrecording.jfr,settings=profile

jmc是一套监控、性能分析和诊断在生成中运行的应用的工具，这个工具当前只能运行在Hotspot JVM
jmc主要有两个任务组成
  jmx 基于 JMX来监视应用程序解决方案。
  jfr java Flight Recorder 非常低开销分析和诊断工具

有一些插件可以扩展 Java 任务控件的功能, 例如 堆dump分析和基于 DTrace 的分析
我们重点放在 Java 飞行记录器上。使用堆转储分析工具和DTrace 分析工具

如何安装
已经内嵌到jdk8u25

我们使用jmc命令来创建文件
-XX:+UnlockCommercialFeatures -XX:+FlightRecorder -
XX:StartFlightRecording=delay=20s,duration=60s,name=MyRecording,filename=/tmp/javaFlightRecoder.jfr,settings=profile
然后将生成的
