## Programming with Redis
Redis实现的完整 **[命令列表](https://redis.io/commands)**，以及每个命令的完整文档

### 协议

set name value
redis会转换为：
```
*3\r\n
$3\r\n
SET\r\n
$4\r\n
name\r\n
$5\r\n
value\r\n
```

get name

### 数据结构
string----sds
list------deque
hash------hash table
set-------intest +dict
zset------skip list+hash table

#### string

struct sdshdr{
    int len;
    int free;
    char buf[];
}
获取字符串长度、常量复杂度
增加时空间预分配
惰性回收

栗子：
    ```
    sdshdr
        free--->0
        len---->len
        buf----->[r,e,d,i,s,\O]
    ```

