## centos
yum install perf -y
yum install gcc -y
yum install gcc-c++
yum install cmake -y
## ubuntu
apt install linux-tools-generic
apt install linux-tools-common
## FlameGraph
# 参考 http://www.brendangregg.com/FlameGraphs/cpuflamegraphs.html#Java
export JAVA_HOME=/root/jdk1.8.0_181
export PATH=$JAVA_HOME/bin:$PATH
git clone --depth=1 https://github.com/jrudolph/perf-map-agent
cd perf-map-agent
cmake .
make
bin/create-links-in /usr/bin

git clone https://github.com/brendangregg/FlameGraph.git
export FLAMEGRAPH_DIR=/root/git/FlameGraph
# jvm启动参数需要增加
-XX:+PreserveFramePointer

perf-java-flames 进程号
