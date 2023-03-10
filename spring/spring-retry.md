## what
该项目为Spring应用程序提供声明式重试支持
## how
### maven引用

```
<dependency>
    <groupId>org.springframework.retry</groupId>
    <artifactId>spring-retry</artifactId>
    <version>1.3.1</version>
</dependency>
```


```

 private RetryTemplate getRetryTemplate() {
        // 重试策略
        SimpleRetryPolicy retryPolicy = new SimpleRetryPolicy();
        // 最大重试次数
        retryPolicy.setMaxAttempts(5);
        ExponentialBackOffPolicy backOffPolicy = new ExponentialBackOffPolicy();
        // 初始等待时间(单位：毫秒)
        backOffPolicy.setInitialInterval(1000);
        // 时间等待倍数
        backOffPolicy.setMultiplier(2);
        // 最大等待时间(10秒)
        backOffPolicy.setMaxInterval(10000);
        RetryTemplate template = new RetryTemplate();
        template.setRetryPolicy(retryPolicy);
        template.setBackOffPolicy(backOffPolicy);
        return template;
    }

RetryTemplate retryTemplate = getRetryTemplate();


retryTemplate.execute(new RetryCallback<Response, RuntimeException>() {
    @Override
    public Response doWithRetry(RetryContext retryContext) throws RuntimeException {
        // 重试的代码
        ;
    }
}, new RecoveryCallback<Response>() {
    @Override
    public Response recover(RetryContext retryContext) throws Exception {
        // 重试失败后执行的代码
        ;
    }
});
```
## 功能
## 实现
## 缺点
