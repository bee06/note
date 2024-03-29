# 数据类型
## 介绍
redis不是一个普通的kv存储，它实际上是一个数据结构服务器，支持不同类型的值;这意味着，而在传统键值存储中, 您将字符串键与字符串值相关联;在redis中，该值不局限于简单的字符串，但也可以容纳更复杂的数据结构，以下就是 redis 支持的所有数据结构的列表:
* String
* list：根据插入顺序排序的字符串元素的集合。它们基本上是链接列表
* set：唯一的、未排序的字符串元素的集合
* Sorted sets
* Hashes 它是由与值关联的字段组成的映射。字段和值都是字符串
* Streams

## keys
键是二进制安全，这意味着可以使用任何二进制序列作为健，像”foo“ 字符串到到 jpeg 文件的内容，空字符串也是有效的键，下面是设置key的建议：
* 非常长的key不是好想法，比如1024 字节的键不仅是坏主意而是不方便记忆，因为在数据集中查找键可能需要几个代价高昂的键进行比较，即使手头的任务是查找一个大的值的存在，是用hash算法（sha1）是一个比较好的注意，特别是从内存和带宽的角度来考虑。
* 非常短的key同样也不是好想法，使用 "u1000flw" 是没有什么意义的, 你可以改为写 "user: 1000:desp",后者可读性更强，与键对象本身和值对象使用的空间相比, 增加的空间较小，虽然短键显然会消耗更少的内存，需要在占用更少内存和可读性找到平衡。
* 尝试坚持使用模式，例如 "object-type:id" 是一个好的想法，如 "user: 1000" "."或"-"通常用于多字段,如 "comment: 1234 : reply.to" 或者 "comment : 1234 : reply-to"
* 最大允许512M
## Strings
* String类型是最简单的类型、它是Memcached唯一的数据类型，所以新人非常自然的使用的类型。
* redis键可以使是字符串，当我们也使用字符串类型作为值时, 我们将一个字符串映射到另一个字符串，字符串数据类型对于许多用例都很有用，如缓存 html 片段或页面
，让我们用字符串来演示下，使用redis-cli
```
> set mykey somevalue
OK
> get mykey
"somevalue"
```
* 正如你看到的使用set和get命令是我们设置和检索字符串的方式，请注意，set会覆盖缓存中存在的值，在key已存在的情况下，即使键与非字符串值关联。
* 值可以是各种字符串 (包括二进制数据)，例如, 可以将 jpeg 图像存储在值中。值不能大于 512 mb，
* set命令是一个有趣的操作。提供了附加参数，例如 如果key已存在, 我会要求 set 失败或者相反，只有当key已经存在时, 它才会成功。
```
> set mykey newval nx
(nil)
> set mykey newval xx
OK
```
* incr 命令将字符串值解析为整数，递增一个.最后将获得的值设置为新值.还有其他类似的命令, 如 incrby、decr 和 decrby.实际上在内部，他们使用是相同的命令
incr是原子的？即使多个客户端对同一密钥发出 incr 命令也永远不会进入竞争条件，例如 他永远不会发生，在同一个时间 客户端1读取是10，客户端2读完也是10，两次自增是11，并且将新值更新成11
最终值始终为 12, 并在所有其他客户端不同时执行命令的情况下执行读取增量集操作。

有许多用于在字符串上操作的命令，getset 设置新值且返回老值作为结果。
你可以使用此命令。

例如, 如果给定的键存在或不在数据库中, 则 exists 命令返回1或0以发出信号

redis 过期: key应该控制生存时间
在继续使用更复杂的数据结构之前,我们需要讨论另一个特性值的有效性，并称为Redis expires。
你可以给key设置失效时间，限制生存时间，当生存时间过去时，key会自动销毁，正如用户调用 del 命令。
对Redis expires一些信息：
* 它们可以使用秒或毫秒精度进行设置
* 但是, 过期时间始终设置为1毫秒
* 有关过期的信息将被复制并保存在磁盘上，时间几乎过去了，当redis服务器保持停止。
```
> set key some-value
OK
> expire key 5
(integer) 1
> get key (immediately)
"some-value"
> get key (after some time)
(nil)
```
key在两次调用之间消失，因为第二次调用超过5秒。在上面的示例中, 我们使用 expire 来设置过期
persist 可以用来删除过期, 并使key永远持久;
但是, 我们也可以使用其他 redis 命令创建过期的密钥.比如使用set命令。

为了设置和检查以毫秒为单位过期，检查 pexpire 和 pttl 命令
```
> set key 100 ex 10
OK
> ttl key
(integer) 9
```
上面的示例设置了一个字符串值为100的键,过期10秒,调用 ttl 命令是为了检查key剩余的生存时间
## Lists
* 要解释 list 数据类型, 最好从一点点的理论开始,由于术语列表经常使用
  * 例如, "python 列表" 不是名链接列表, 而是数组,列表只是一个无序元素序列:10、20、1、2、3，但是, 使用数组实现的 list 的属性与使用链接列表实现的列表的属性有很大的不同。这意味着, 即使您的列表中包含数以百万计的元素，在列表的头部或尾部添加新元素的操作是在恒定的时间内执行的，将 lpush 命令的新元素添加到列表头部，具有十个元素与在列表的前面添加一个包含 1, 000万个元素的元素是相同的。

* 在使用 array 实现的列表中, 按索引访问元素的速度非常快，在由链接列表实现的列表中访问速度不是那么快。
redis list 是通过链接列表实现的, 因为对于数据库系统来说, 能够以非常快的方式将元素添加到很长的列表中至关重要
另一个强大的优势，有一个不同的数据结构, 可以使用, 称为排序集。

* 使用 redis 列表的第一步
  * 命令将一个新元素添加到列表中，在左边 (在头)，当rpush命令添加新元素到列表，在右边（在尾部）
最后, lrange 命令从列表中提取元素的范围

```
> rpush mylist A
(integer) 1
> rpush mylist B
(integer) 2
> lpush mylist first
(integer) 3
> lrange mylist 0 -1
1) "first"
2) "A"
3) "B"
```

> 请注意, lrange 采用两个索引，要返回的范围的第一个和最后一个元素，两个索引都是负数，告诉redis从最后开始计数
所以-1 是最后一个元素，-2 是列表的倒数第二个元素, 依此类推.
真如你看到rpush 命令在list右边追加元素，而最后的 lpush 附加了左边的元素
这两个命令都是可变命令，这意味着您可以在一次调用中将多个元素推送到列表中
```
> rpush mylist 1 2 3 4 5 "foo bar"
(integer) 9
> lrange mylist 0 -1
1) "first"
2) "A"
3) "B"
4) "1"
5) "2"
6) "3"
7) "4"
8) "5"
9) "foo bar"
```
* 在redis list有个重要操作 有能力pop操作。弹出元素是从列表中检索元素的操作，并且从list排除，您可以从左、右弹出元素
类似于如何推送列表两侧的元素。
```
> rpush mylist a b c
(integer) 3
> rpop mylist
"c"
> rpop mylist
"b"
> rpop mylist
"a"
```
* 我们添加三个元素并且拿走三个元素，因此, 在这个命令序列的末尾, 列表是空的, 没有更多的元素可以弹出
如果list是null的，我们试图弹出一个元素，结果如下：
```
> rpop mylist
(nil)
```
redis 返回一个 null 值, 以表示列表中没有元素。
列表的常见用例,列表对于许多任务都很有用，两个非常具有代表性的用例如下:
* 记住用户发布到社交网络中的最新更新
* 两个进程之间通讯，使用消费者生产者模式, 其中生产者推送项目到列表。
和消费者 (通常是工人) 使用这些项目和执行的操作。redis 有特殊的列表命令, 使这种用例更可靠、更高效。
这个受欢迎的推特社交网络将用户发布的最新推特纳入了 redis list中。
在许多用例中, 我们只想使用列表来存储最新的项目，无论他们是: 社交网络更新, 日志, 或任何其他

redis 允许我们使用列表作为上限集合, 只记住最新的 n 项, 并使用 ltrim 命令丢弃所有最早的项目
ltrim命令有点想lrange，但它没有显示指定的元素范围, 而是将此范围设置为新的列表值。在给定范围之外的所有元素都将被删除

```
> rpush mylist 1 2 3 4 5
(integer) 5
> ltrim mylist 0 2
OK
> lrange mylist 0 -1
1) "1"
2) "2"
3) "3"
```
上面的 ltrim 命令告诉 redis 只获取索引0到2中的元素列表,其他一切都会被丢弃

## Redis Hashes
redis 哈希看起来正是人们所期望的 "哈希", 并带有字段值对
```
> hmset user:1000 username antirez birthyear 1977 verified 1
OK
> hget user:1000 username
"antirez"
> hget user:1000 birthyear
"1977"
> hgetall user:1000
1) "username"
2) "antirez"
3) "birthyear"
4) "1977"
5) "verified"
6) "1"
```
虽然哈希很容易表示对象, 但实际上可以放在哈希中的字段数量没有实际限制 (可用内存除外)，因此, 您可以在应用程序中以许多不同的方式使用哈希， hmset命令 设置哈希的多个字段，hget命令检索单个字段，hmget命令 类似于 hget, 返回了一组值.


```
> hmget user:1000 username birthyear no-such-field
1) "antirez"
2) "1977"
3) (nil)
```
有一些命令也可以对单个字段执行操作, 例如 hinccrby:
```
> hincrby user:1000 birthyear 10
(integer) 1987
> hincrby user:1000 birthyear 10
(integer) 1997
```
您可以在 **[hash命令](https://redis.io/commands#hash)** 查看完整的hash命令
值得注意的是, 小哈希 (即, 几个具有小值的元素) 在内存中以特殊的方式进行编码, 使它们具有很高的内存效率。


## set
redis 集是无序的字符串集合,sadd 命令将新元素添加到集合中,如果给定的元素已经存在, 也可以对集执行许多其他操作, 如测试,多个集合之间的交集、联合或差异, 依此类推
```
> sadd myset 1 2 3
(integer) 3
> smembers myset
1. 3
2. 1
3. 2
```
在这里, 我已经添加了三个元素到我的集合, 并告诉 redis 返回所有的元素,正如你所看到的, 它们没有排序,redis 可以在每次调用时按任意顺序返回元素
redis 有用于测试成员的命令,例如, 检查元素是否存在
```
> sismember myset 3
(integer) 1
> sismember myset 30
(integer) 0
```
"3" 是集合的成员, 而 "30" 不是,集很好地表示对象之间的关系,例如, 我们可以很容易地使用集来实现标记

对这个问题建模的一个简单方法是为我们要标记的每个对象设置一个集，该集合包含与对象关联的标记的 id


## Redis Sorted sets
排序集是一种数据类型, 类似于 "集" 和 "哈希" 之间的混合，有序集由唯一的，非重复的字符串元素组成，
所以在某种意义上，排序集也是一个集合

但是，内部集合中的元素不是有序的，排序集中的每个元素都与浮点值相关联，称为得分（这就是为什么类型也类似于散列，因为每个元素都映射到一个值），此外，排序集合中的元素按顺序排列，它们按照以下规则排序：
* 如果A和B是两个具有不同分数的元素，那么A> B，如果A.score是> B.score。
* 如果A和B具有完全相同的分数，则A> B，如果A字符串按字典顺序大于B字符串。 A和B字符串不能相等，因为有序集只有唯一元素
让我们从一个简单的例子开始，添加一些选定的黑客名称作为排序的集合元素，他们的出生年份为“得分”
```
> zadd hackers 1940 "Alan Kay"
(integer) 1
> zadd hackers 1957 "Sophie Wilson"
(integer) 1
> zadd hackers 1953 "Richard Stallman"
(integer) 1
> zadd hackers 1949 "Anita Borg"
(integer) 1
> zadd hackers 1965 "Yukihiro Matsumoto"
(integer) 1
> zadd hackers 1914 "Hedy Lamarr"
(integer) 1
> zadd hackers 1916 "Claude Shannon"
(integer) 1
> zadd hackers 1969 "Linus Torvalds"
(integer) 1
> zadd hackers 1912 "Alan Turing"
(integer) 1
```
如您所见，ZADD与SADD类似,但需要一个额外的参数（放在要添加的元素之前）这是得分,ZADD也是可变的
所以你可以自由指定多个得分 - 值对,即使上面例子没有使用他
对于排序集，返回按出生年份排序的黑客列表是微不足道的，因为实际上它们已经排序了。
实现说明：
 排序集通过包含跳过列表和散列表的双数据结构实现  ，因此，每次添加元素时，Redis都会执行O（log（N））操作 
 这很好，但是当我们要求排序的元素时，Redis根本不需要做任何工作，它已经全部排序。
 ```
 > zrange hackers 0 -1
1) "Alan Turing"
2) "Hedy Lamarr"
3) "Claude Shannon"
4) "Alan Kay"
5) "Anita Borg"
6) "Richard Stallman"
7) "Sophie Wilson"
8) "Yukihiro Matsumoto"
9) "Linus Torvalds"
 ```
说明：0和-1表示从元素索引0到最后一个元素（1就像在LRANGE命令中一样工作）
如果我想以相反的方式进行排序，最小到最老的怎么办？使用ZREVRANGE而不是ZRANGE：
```
> zrevrange hackers 0 -1
1) "Linus Torvalds"
2) "Yukihiro Matsumoto"
3) "Sophie Wilson"
4) "Richard Stallman"
5) "Anita Borg"
6) "Alan Kay"
7) "Claude Shannon"
8) "Hedy Lamarr"
9) "Alan Turing"
```
使用WITHSCORES参数也可以返回分数：
```
> zrange hackers 0 -1 withscores
1) "Alan Turing"
2) "1912"
3) "Hedy Lamarr"
4) "1914"
5) "Claude Shannon"
6) "1916"
7) "Alan Kay"
8) "1940"
9) "Anita Borg"
10) "1949"
11) "Richard Stallman"
12) "1953"
13) "Sophie Wilson"
14) "1957"
15) "Yukihiro Matsumoto"
16) "1965"
17) "Linus Torvalds"
18) "1969"
```
Operating on ranges
排序集比这更强大,他们可以在范围内操作。让我们得到所有出生到1950年的人,我们使用ZRANGEBYSCORE命令来执行此操作
```
> zrangebyscore hackers -inf 1950
1) "Alan Turing"
2) "Hedy Lamarr"
3) "Claude Shannon"
4) "Alan Kay"
5) "Anita Borg"
```
我们要求Redis以负无穷大和1950之间的分数返回所有元素（包括两个极值）。
也可以删除元素范围。让我们从排序集中删除1940年到1960年间出生的所有黑客：
```
> zremrangebyscore hackers 1940 1960
(integer) 4
```
ZREMRANGEBYSCORE可能不是最好的命令名，但它可能非常有用，并返回已删除元素的数量。
为有序集元素定义的另一个非常有用的操作是get-rank操作。可以询问有序元素集中元素的位置。
```
> zrank hackers "Anita Borg"
(integer) 4
```
考虑到按降序排序的元素，ZREVRANK命令也可用于获得排名。
### Lexicographical scores
随着新版本2.8，引入了一项新功能，允许按字典顺序获取范围，假设排序集中的元素都插入了相同的相同分数，所以保证没有排序规则，每个Redis实例都会回复相同的输出）。

使用词典范围操作的主要命令是ZRANGEBYLEX，ZREVRANGEBYLEX，ZREMRANGEBYLEX和ZLEXCOUNT。
例如，让我们再次添加我们的着名黑客列表，但这次使用所有元素的得分为零
```
> zadd hackers 0 "Alan Kay" 0 "Sophie Wilson" 0 "Richard Stallman" 0
  "Anita Borg" 0 "Yukihiro Matsumoto" 0 "Hedy Lamarr" 0 "Claude Shannon"
  0 "Linus Torvalds" 0 "Alan Turing"
```
由于排序集排序规则，它们已经按字典顺序排序：
```
> zrange hackers 0 -1
1) "Alan Kay"
2) "Alan Turing"
3) "Anita Borg"
4) "Claude Shannon"
5) "Hedy Lamarr"
6) "Linus Torvalds"
7) "Richard Stallman"
8) "Sophie Wilson"
9) "Yukihiro Matsumoto"
```
使用ZRANGEBYLEX我们可以要求词典范围：
```
> zrangebylex hackers [B [P
1) "Claude Shannon"
2) "Hedy Lamarr"
3) "Linus Torvalds"
```
范围可以是包容性的或排他性的（取决于第一个字符），字符串无限和负无限分别用+和 - 字符串指定。有关更多信息，请参阅文档。
此功能很重要，因为它允许我们使用有序集作为通用索引。
例如，如果要通过128位无符号整数参数索引元素，您需要做的就是将元素添加到具有相同分数的排序集中（例如0）但是有一个16字节前缀，由大端的128位数组成，因为大端的数字，按字典顺序排序（按原始字节顺序）实际上也是按数字顺序排序的，您可以在128位空间中询问范围，并获取元素的值以丢弃前缀。
更新分数：排行榜
## Bitmaps
bitmaps不是一个真实的数据类型，但是在String类型上定义了一组面向位的操作，
由于字符串是二进制安全blob，并且它们的最大长度为512 MB，因此它们适合设置232个不同的位。
位操作分为两组：恒定时间单位操作，例如将位设置为1或0 或者获得它的价值，以及对比特组的操作
例如，计算给定比特范围内的设定比特数（例如，人口计数）
位图的最大优势之一是它们在存储信息时通常可以节省大量空间。
例如，在通过增量用户ID表示不同用户的系统中，可以使用仅512MB的存储器记住40亿用户的单个位信息（例如，知道用户是否想要接收新闻通讯）。
使用SETBIT和GETBIT命令设置和检索位：
```
> setbit key 10 1
(integer) 1
> getbit key 10
(integer) 1
> getbit key 11
(integer) 0
```
* SETBIT命令将位数作为其第一个参数,并将该位设置为第二个参数，即1或0,如果寻址位超出当前字符串长度，该命令会自动放大字符串
* GETBIT只返回指定索引处的位值,超出范围的位（寻址存储在目标密钥中的字符串长度之外的位）始终被认为是零。
* 有三组命令在一组位上运行：
  * BITOP在不同的字符串之间执行逐位操作。提供的操作是AND，OR，XOR和NOT。
  * BITCOUNT执行填充计数，报告设置为1的位数。
  * BITPOS查找具有指定值0或1的第一个位。

## HyperLogLogs

* HyperLogLog是用于计算唯一事物的概率数据结构（从技术上讲，这被称为估计集合的基数）
* 通常计算唯一项目需要使用与您要计算的项目数量成比例的内存量
* 因为你需要记住过去已经看过的元素，以避免多次计算它们,然而，有一组算法可以交换内存以获得精确度,您以标准错误的估计度量结束
* 在Redis实施的情况下，小于1％,此算法的神奇之处在于您不再需要使用与计数项目数成比例的内存量
而是可以使用恒定的内存量！在最坏的情况下12k字节，或者如果您的HyperLogLog（我们从现在开始称它们为HLL）少了很多元素



## 其他值得注意的功能
* Redis API中还有其他重要内容无法在本文档的上下文中进行探讨，但值得您关注：</br>
  * **[可以递增地迭代大集合的key空间](https://redis.io/commands/scan)** </br>
  * **[可以运行Lua脚本服务器端来改善延迟和带宽。](https://redis.io/commands/eval)** </br>
  * **[Redis也是Pub-Sub服务器](https://redis.io/topics/pubsub)**

## 学到更多
本教程并非完整，仅涵盖了API的基础知识。阅读命令参考以发现 **[更多命令](https://redis.io/commands)**
感谢阅读，并与Redis玩得开心！
