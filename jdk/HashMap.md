## 摘要
> HashMap 是一种高效的实现，在通常情况可以得到常数级别的查找和插入性能。
## 类的定义&实现接口

```
public class HashMap<K,V> extends AbstractMap<K,V> implements Map<K,V>, Cloneable, Serializable
```
* AbstractMap 提供了Map接口的抽象实现，提供了一些公用的方法
* Cloneable, Serializable 这两个接口忽略


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
* 树化的阈值，使用树而不是列表的阈值，将元素添加到具有至少许多节点时，将转换成树
* 该值必须大于 2，并且应至少为 8，
* The bin count threshold for using a tree rather than list for a
* bin.  Bins are converted to trees when adding an element to a
* bin with at least this many nodes. The value must be greater
* than 2 and should be at least 8 to mesh with assumptions in
* tree removal about conversion back to plain bins upon
* shrinkage.
*/
static final int TREEIFY_THRESHOLD = 8;

/**
* 非树化的阈值，在调整大小操作期间取消树 的 bin 计数阈值。应小于TREEIFY_THRESHOLD，并且最多 6 
* The bin count threshold for untreeifying a (split) bin during a
* resize operation. Should be less than TREEIFY_THRESHOLD, and at
* most 6 to mesh with shrinkage detection under removal.
*/
static final int UNTREEIFY_THRESHOLD = 6;

/**
* 最小树化的容量，可树化的最小表容量，否则，如果 bin 中的节点太多，则调整表的大小
* 应至少为 4 *=* TREEIFY_THRESHOLD，以避免调整大小和树化阈值之间的冲突，
*/
static final int MIN_TREEIFY_CAPACITY = 64;

/**
* The table, initialized on first use, and resized as
* necessary. When allocated, length is always a power of two.
* (We also tolerate length zero in some operations to allow
* bootstrapping mechanics that are currently not needed.)
*/
transient Node<K,V>[] table;

/**
* Holds cached entrySet(). Note that AbstractMap fields are used
* for keySet() and values().
*/
transient Set<Map.Entry<K,V>> entrySet;

/**
* The number of key-value mappings contained in this map.
*/
transient int size;

/**
* The number of times this HashMap has been structurally modified
* Structural modifications are those that change the number of mappings in
* the HashMap or otherwise modify its internal structure (e.g.,
* rehash).  This field is used to make iterators on Collection-views of
* the HashMap fail-fast.  (See ConcurrentModificationException).
*/
transient int modCount;

/**
* The next size value at which to resize (capacity * load factor).
*
* @serial
*/
// (The javadoc description is true upon serialization.
// Additionally, if the table array has not been allocated, this
// field holds the initial array capacity, or zero signifying
// DEFAULT_INITIAL_CAPACITY.)
int threshold;

/**
* The load factor for the hash table.
*
* @serial
*/
final float loadFactor;

```

## 构造方法

```
/**
* Constructs an empty <tt>HashMap</tt> with the specified initial
* capacity and load factor.
*
* @param  initialCapacity the initial capacity
* @param  loadFactor      the load factor
* @throws IllegalArgumentException if the initial capacity is negative
*         or the load factor is nonpositive
*/
public HashMap(int initialCapacity, float loadFactor) {
    if (initialCapacity < 0)
        throw new IllegalArgumentException("Illegal initial capacity: " +
                                            initialCapacity);
    if (initialCapacity > MAXIMUM_CAPACITY)
        initialCapacity = MAXIMUM_CAPACITY;
    if (loadFactor <= 0 || Float.isNaN(loadFactor))
        throw new IllegalArgumentException("Illegal load factor: " +
                                            loadFactor);
    this.loadFactor = loadFactor;
    this.threshold = tableSizeFor(initialCapacity);
}

/**
* Constructs an empty <tt>HashMap</tt> with the specified initial
* capacity and the default load factor (0.75).
*
* @param  initialCapacity the initial capacity.
* @throws IllegalArgumentException if the initial capacity is negative.
*/
public HashMap(int initialCapacity) {
    this(initialCapacity, DEFAULT_LOAD_FACTOR);
}

/**
* Constructs an empty <tt>HashMap</tt> with the default initial capacity
* (16) and the default load factor (0.75).
*/
public HashMap() {
    this.loadFactor = DEFAULT_LOAD_FACTOR; // all other fields defaulted
}
```

## 内部类
### Node

```
/**
* 最基本的单元，单向链表
* 实现了Map.Entry接口
*/
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


## 问题
* 为什么会采用链表+红黑树
* 什么时候转换
* hashmap是如何解决哈希碰撞
* hashmap是如何计算hash


