# 概述


# 名词解释


# 代码入口

```
  public void subscribe(Collection<String> topics, ConsumerRebalanceListener listener) {
        acquireAndEnsureOpen();
        try {
            maybeThrowInvalidGroupIdException();
            if (topics == null)
                throw new IllegalArgumentException("Topic collection to subscribe to cannot be null");
            if (topics.isEmpty()) {
                // 将订阅的空主题列表视为取消订阅
                this.unsubscribe();
            } else {
                for (String topic : topics) {
                    if (Utils.isBlank(topic))
                        throw new IllegalArgumentException("Topic collection to subscribe to cannot contain null or empty topic");
                }

                throwIfNoAssignorsConfigured();
                fetcher.clearBufferedDataForUnassignedTopics(topics);
                
                if (this.subscriptions.subscribe(new HashSet<>(topics), listener))
                    metadata.requestUpdateForNewTopics();
            }
        } finally {
            release();
        }
    }
```