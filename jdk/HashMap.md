## 成员变量

```

/**
* 默认初始容量 - 必须是2的幂. 默认值 16
*/
static final int DEFAULT_INITIAL_CAPACITY = 1 << 4; 

/**
* 最大的容量，必须是2的幂，且小于等于  1<<30（1073741824）.
*/
static final int MAXIMUM_CAPACITY = 1 << 30;

/**
* 默认的负载因子.
*/
static final float DEFAULT_LOAD_FACTOR = 0.75f;

/**
* The bin count threshold for using a tree rather than list for a
* bin.  Bins are converted to trees when adding an element to a
* bin with at least this many nodes. The value must be greater
* than 2 and should be at least 8 to mesh with assumptions in
* tree removal about conversion back to plain bins upon
* shrinkage.
*/
static final int TREEIFY_THRESHOLD = 8;

/**
* The bin count threshold for untreeifying a (split) bin during a
* resize operation. Should be less than TREEIFY_THRESHOLD, and at
* most 6 to mesh with shrinkage detection under removal.
*/
static final int UNTREEIFY_THRESHOLD = 6;

/**
* The smallest table capacity for which bins may be treeified.
* (Otherwise the table is resized if too many nodes in a bin.)
* Should be at least 4 * TREEIFY_THRESHOLD to avoid conflicts
* between resizing and treeification thresholds.
*/
static final int MIN_TREEIFY_CAPACITY = 64;

```

## 内部类
### Node

```
    static class Node<K,V> implements Map.Entry<K,V> {
        final int hash;
        final K key;
        V value;
        Node<K,V> next;
    }

```


## 方法
### put
### get
### resize

