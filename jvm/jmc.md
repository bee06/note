


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
