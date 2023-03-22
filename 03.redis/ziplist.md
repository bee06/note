## 压缩列表
* 压缩列表和数组差不多，数组中每一个元素都对应保存一个数据，和数据不同的是
* 压缩列表在表头上有三个字段zlbytes、zltail 和 zllen，分别表示列表长度、列表尾的偏移量和列表中的 entry 个数；压缩列表在表尾还有一个 zlend，表示列表结束。
* 压缩列表之所以能节省内存，就是用每个entry保存数据
  * prev_len
  * len
  * encoding
  * content

