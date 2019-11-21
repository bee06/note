## 目的
该项目为Spring应用程序提供声明式重试支持
## 如何做
```
RetryTemplate template = RetryTemplate.builder()
                .maxAttempts(3)
                .fixedBackoff(1000)
                .retryOn(RemoteAccessException.class)
                .build();

template.execute(ctx -> {
    // ... do something
});
```
## 功能
## 实现
## 缺点
