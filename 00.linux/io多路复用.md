## 同步阻塞网络IO
### 介绍
简称BIO
```
int main()
{
 int sk = socket(AF_INET, SOCK_STREAM, 0);
 connect(sk, ...)
 recv(sk, ...)
}
```
1.进程在 recv 的时候大概率会被阻塞掉，导致一次进程切换
2.当连接上数据就绪的时候进程又会被唤醒，又是一次进程切换
3.一个进程同时只能等待一条连接，如果有很多并发，则需要很多进程
