# 数据类型和抽象简介
## 介绍
redis不是一个普通的k-v存储，它实际上是一个数据结构服务器，支持不同类型的值，这意味着，而在传统键值存储中, 您将字符串键与字符串值相关联，在redis中，
该值不局限于简单的字符串，但也可以容纳更复杂的数据结构，以下就是 redis 支持的所有数据结构的列表:
* 字符串
* list：根据插入顺序排序的字符串元素的集合。它们基本上是链接列表
* set：唯一的、未排序的字符串元素的集合
* Sorted sets
* Hashes 它是由与值关联的字段组成的映射。字段和值都是字符串
* 字符串

## keys
键是二进制安全，这意味着可以使用任何二进制序列作为健，像”foo“ 字符串到到 jpeg 文件的内容，空字符串也是有效的键，下面是设置key的建议：
* 非常长的key不是好主意，比如1024 字节的键不仅是坏主意而是不方便记忆，因为在数据集中查找键可能需要几个代价高昂的键进行比较，即使手头的任务是查找一个大的值的存在，是用hash算法（sha1）是一个比较好的注意，特别是从内存和带宽的角度来考虑。
* 最大允许512M
## Strings
## Lists
