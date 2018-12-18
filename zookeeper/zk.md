paxos
 三个角色
 	提案者 proposal
 	接受者 accept
 	选定   chose
 	学习者  learner



basic paxos
两次提交
	两个节点
		1、准备阶段
		2、回答阶段

mutil paxos

raft



假设我们


对于这个示例，您可以将我们的节点看作一个存储单个值的数据库服务器。


我们也有一个客户端可以向服务器发送一个值

在一个节点上达成一致或共识就很容易

但如果我们有多个节点，我们如何达成共识

这是分布式共识的问题

raft是实施分布式共识的协议

我们来看一下它的工作原理
	1、一个节点可以在3个状态中的1个 follower状态 candidate 状态 或者leader
	2、我们所有的节点都是从跟随者状态开始的
	3、如果追随者没有听到领导者的消息，他们可以成为候选人
	4、候选人然后请求其他节点的投票
	5、节点将回复他们的投票
	6、如果从多数节点获得选票，候选人就成为领导者。
	7、这个过程被称为领导者选举
	8、现在系统的所有变化都通过领导
	9、每个更改都添加为节点日志中的条目
	10、此日志条目当前未提交，因此它不会更新节点的值
	11、为了提交条目，节点首先将它复制到跟随者节点
	12、这时领导等待，直到大多数节点已经写入条目
	13、该条目现在在领导者节点上提交并且节点状态为“5”
	14、领导者然后通知追随者该条目已经落实
	15、该集群现在已经就系统状态达成共识
	16、这个过程叫日志复制

raft 领导人选举
1、在raft里有两个超时设置来控制选举
2、首先是选举超时
	2.1 选举超时是一个追随者在成为候选人之前等待的时间。
	2.2 这选举超时是在150ms和300ms之间的随机数
3.在选举超时之后，追随者成为候选人并开始新的选举任期
4、选举自己
5、并发送请求投票消息给其他节点。
6、如果接收节点尚未在此期间投票，那么它会为候选人投票
7、并且该节点重置其选举超时
8、一旦候选人获得多数选票，它就成为领导者。
9、领导者开始向追随者发送附加条目消息。
10.这些消息以心跳超时指定的间隔发送。	
11、追随者然后回应每个追加条目消息
12、这个选举任期将持续到跟随者停止接受心跳并成为候选人


让我们停止领导人，并观看重新选举
1、Node B现在是第2任期的领导人
2、要求多数选票保证每个任期只能选举一名领导人
3、如果两个节点同时成为候选，则可能发生分裂投票。
4、让我们来看看一个分割投票的例子...
	4.1 两个节点都开始选举相同的期限..
	4.2 并且每个都在另一个节点之前到达单个跟随器节点
	4.3 现在每个候选人有2票，并且不能再收到这个任期
	4.4 节点将等待新的选举并再次尝试
日志复制
	1.一旦我们选出了一个领导者，我们就需要把我们的系统的所有变化复制到所有节点上
	2、这是通过使用用于心跳的相同附加条目消息来完成的
	3、首先客户端发送变化给leader
	4、这一变化被加到领导的日志上。
	5、然后在下一次心跳中将变化发送给追随者。
	6、一旦大多数追随者承认，就提交一个条目。
	7、并将响应发送给客户端
	8、现在让我们发送一个命令，通过“2”来增加值

面对网络分区，Raft甚至可以保持一致
1、让我们添加一个分区来分离abcde（a&b）{cde}
2、由于我们的分割，我们现在有两个不同的领导者
3、让我们添加另一个客户端并尝试更新两个领导者
4、一个客户端将尝试将节点B的值设置为“3”。
5、节点B不能复制到多数，所以它的日志条目保持未提交
6、另一个客户端将尝试将节点C的值设置为“8”
7、这将成功，因为它可以复制到多数。
8、现在我们来修复网络分区
9、Node B将看到更高的选举期限并下台
10、两个节点A和B将回滚未提交的条目并匹配新的领导日志
11、我们的日志现在在我们的集群中是一致的。



因为raft比zab出来晚点,可能raft 里面的有些东西会借鉴zab协议.其实两个协议差不到哪里去,本质上都是维护一个replicated log.
相同点(不全,没有实现过zab):
都使用timeout来重新选择leader.
采用quorum来确定整个系统的一致性(也就是对某一个值的认可),
这个quorum一般实现是集群中半数以上的服务器,
zookeeper里还提供了带权重的quorum实现.都由leader来发起写操作.都采用心跳检测存活性.
leader election都采用先到先得的投票方式.

不同点(不全,没有实现过zab):
zab用的是epoch和count的组合来唯一表示一个值, 
而raft用的是term和index.zab的follower在投票给一个leader之前必须和leader的日志达成一致,
而raft的follower则简单地说是谁的term高就投票给谁.
raft协议的心跳是从leader到follower, 而zab协议则相反.  
raft协议数据只有单向地从leader到follower(成为leader的条件之一就是拥有最新的log), 

而zab协议在discovery阶段, 
一个prospective leader需要将自己的log更新为quorum里面最新的log,然后才好在synchronization阶段将quorum里的其他机器的log都同步到一致.

zab