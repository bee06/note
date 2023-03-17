## 什么是PageCache
* 是内核管理的内存
* 属于内核态不属于用户态
## 为什么需要PageCache
* 减少IO，提升应用的IO速度
## pageCache的产生和回收是什么样
* 控制脏页
  * sar -r