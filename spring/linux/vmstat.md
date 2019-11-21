## 定义
vmstat：一个标准的工具，它会报告 Linux 系统的虚拟内存统计。vmstat 会报告有关进程、内存、分页、块 IO、陷阱（中断）和 cpu 活动的信息。它可以帮助 Linux 管理员在解决问题时识别系统瓶颈。
## 名称解释
ram： 代表“随机访问内存Random Access Memory”，是一种计算机数据存储，它会存储经常使用的程序来提升系统性能。
虚拟内存：虚拟内存是一种内存管理方式，计算机通过临时将最近未使用的程序数据从 RAM 转移到硬盘，以平衡或管理内存的短缺
## 功能
### 如何安装
sudo yum install sysstat
>Linux 中没有独立的 vmstat 包。它与 sysstat 绑定在一起

### 如何使用
```
vmstat
procs -----------memory---------- ---swap-- -----io---- -system-- ------cpu-----
 r  b   swpd   free   buff  cache   si   so    bi    bo   in   cs us sy id wa st
 1  0      0 2651976    872 2098468    0    0    57   171  269  445  2  0 97  0  0
```



