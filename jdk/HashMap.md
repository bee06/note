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

/**
* Constructs a new <tt>HashMap</tt> with the same mappings as the
* specified <tt>Map</tt>.  The <tt>HashMap</tt> is created with
* default load factor (0.75) and an initial capacity sufficient to
* hold the mappings in the specified <tt>Map</tt>.
*
* @param   m the map whose mappings are to be placed in this map
* @throws  NullPointerException if the specified map is null
*/
public HashMap(Map<? extends K, ? extends V> m) {
    this.loadFactor = DEFAULT_LOAD_FACTOR;
    putMapEntries(m, false);
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
### 计算容器大小
```
/**
* Returns a power of two size for the given target capacity.
*/
static final int tableSizeFor(int cap) {
    int n = cap - 1;
    n |= n >>> 1;
    n |= n >>> 2;
    n |= n >>> 4;
    n |= n >>> 8;
    n |= n >>> 16;
    return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
}
```
* >>>是无符号右移操作，  无符号右移，忽略符号位，空位都以0补齐   
* |是位或操作 0|0=0 1|0=1 0|1=1 1|1=0

栗子：
    cap=4
    int n = cap - 1;  // n=3


## 问题
* 为什么会采用链表+红黑树
使用了基于数组的哈希表的结构，数组中每一个元素都是一个链表，把数组中的每一格称为一个桶(bin或bucket)。当数组中已经被使用的桶的数量超过容量和装填因子的积，会进行扩容操作。

由于每一个桶中都是一个单向链表，hash 相同的键值对都会作为一个节点被加入这个链表，当桶中键值对数量过多时会将桶中的单向链表转化为一个树。通过TREEIFY_THRESHOLD、UNTREEIFY_THRESHOLD和MIN_TREEIFY_CAPACITY来控制转换需要的阈值。

在JDK 8之前的 HashMap 中都只是采取了单向链表的方式，哈希碰撞会给查找带来灾难性的影响。在最差的情况下，HashMap 会退化为一个单链表，查找时间由 O(1) 退化为 O(n) 。而在JDK 8中，如果单链表过长则会转换为一颗红黑树，使得最坏情况下查找的时间复杂度为 O(log n) 。红黑树节点的空间占用相较于普通节点要高出许多，通常只有在比较极端的情况下才会由单链表转化为红黑树。

* 什么时候转换红黑树
* hashmap是如何解决哈希碰撞
* hashmap是如何计算hash


