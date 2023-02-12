## 定义
- MVCC全称(Multi-version concurrency control)，多版本并发控制，是数据库管理系统常用的一种并发的策略;
- MVCC是通过数据行的多个版本来管理数据库的并发控制;
- Mvcc在InnoDB引擎的事务隔离级别下执行一致性读操作有了保证

## 解决的问题
- MVCC在innodb中的实现是为了提升数据库并发性能，主要更好的处理【读-写】的冲突。

## 准备知识
学习之前，我们先复习下数据的事务相关知识
### 当前读和快照读

* 快照读
  * 快照读又叫一致性读，也就是利用MVCC机制读取快照中的数据。不加锁的简单的SELECT 都属于快照读，比如这样：
  ```SELECT * FROM user WHERE ...```
    
* 当前读
  * 当前读读取的是记录的最新版本，读取时会对读取的记录进行加锁, 其他事务就有可能阻塞。加锁的 SELECT，或者对数据进行增删改都会进行当前读。
    
  ```
  SELECT * FROM user LOCK IN SHARE MODE; # 共享锁
    SELECT * FROM user FOR UPDATE; # 排他锁
    INSERT INTO user values ... # 排他锁
    DELETE FROM user WHERE ... # 排他锁
    UPDATE user SET ... # 排他锁
  ```

### 数据库的事务
##### 事务的4种隔离级别

|  隔离级别   | 描述 | 问题 |
|  ----  |--|---|
| 读未提交  | 一个事务读取了另外一个未提交事务修改的数据 |脏读 |
| 读已提交  | 单元格 |不可重复读 |
| 可重复读  | 单元格 |幻读 |
| 串行化  | 单元格 |问题 |

* mysql的默认级别是可重复读

## 是如何实现
### 版本链
* MVCC 使用了数据库行记录的“三个隐藏字段”来实现版本并发控制
  |  rowid   | db_trx_id | db_roll_pointer |
  |  ----  |---|---|
  | 自增id  | 事务id |回滚指针 |

### readView

