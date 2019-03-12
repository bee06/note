## 命令
### SREM
#### 格式 
SREM key member [member ...]
#### 定义
从集合中删除指定的成员，不包含此集合成员的指定成员将被忽略，
如果key不存在，它被视为空集，此命令返回0
#### Examples
```
redis> SADD myset "one"
(integer) 1
redis> SADD myset "two"
(integer) 1
redis> SADD myset "three"
(integer) 1
redis> SREM myset "one"
(integer) 1
redis> SREM myset "four"
(integer) 0
redis> SMEMBERS myset
1) "three"
2) "two"
redis> 
```

### Hset
#### 定义
返回key中存储的哈希中的所有字段名称
