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

构造方法做的工作：
1、校验
2、初始化loadFactor和根据容量计算阈值

构造函数中并没有给 table 数组分配空间的语句，
因为这里采用了延迟加载的方式，直到第一次调用 put 方法时才会真正地分配数组空间。具体见后面关于 resize() 方法的分析。

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

```
public V put(K key, V value) {
        return putVal(hash(key), key, value, false, true);
    }
```
1、先看下hash(Key)的方法,
```
static final int hash(Object key) {
        int h;
        return (key == null) ? 0 : (h = key.hashCode()) ^ (h >>> 16);
    }
```
其实不管是增加、删除、查找第一步都需要定位的桶的位置
很简单吧，就这么简单的代码

h = key.hashCode()  key键值类型自带的哈希函数，返回int型散列值。
h >>> 16
这里的Hash算法本质上就是三步：取key的hashCode值、高位运算、取模运算。

^异或运算符顾名思义，异就是不同，其运算规则为1^0 = 1 , 1^1 = 0 , 0^1 = 1 , 0^0 = 0

2、看下putVal
```
/**
* 实现 Map.put 和相关方法
*
* @param hash hash for key
* @param key the key
* @param value the value to put
* @param onlyIfAbsent 如果为 true，则不要更改现有值
* @param evict 如果为 false，则表处于创建模式
* @return 上一个值，或空
*/
final V putVal(int hash, K key, V value, boolean onlyIfAbsent,
                   boolean evict) {
        // tab 是桶 使用局部变量tab而不是类成员，方法栈上访问更快
        //  p 一个node节点
        Node<K,V>[] tab; Node<K,V> p; int n, i;
        // table没有分配空间，或大小为0，要先用resize()初始化
        if ((tab = table) == null || (n = tab.length) == 0)
            n = (tab = resize()).length;
        if ((p = tab[i = (n - 1) & hash]) == null)
            tab[i] = newNode(hash, key, value, null);
        else {
            Node<K,V> e; K k;
            if (p.hash == hash &&
                ((k = p.key) == key || (key != null && key.equals(k))))
                e = p;
            else if (p instanceof TreeNode)
                e = ((TreeNode<K,V>)p).putTreeVal(this, tab, hash, key, value);
            else {
                for (int binCount = 0; ; ++binCount) {
                    if ((e = p.next) == null) {
                        p.next = newNode(hash, key, value, null);
                        if (binCount >= TREEIFY_THRESHOLD - 1) // -1 for 1st
                            treeifyBin(tab, hash);
                        break;
                    }
                    if (e.hash == hash &&
                        ((k = e.key) == key || (key != null && key.equals(k))))
                        break;
                    p = e;
                }
            }
            if (e != null) { // existing mapping for key
                V oldValue = e.value;
                if (!onlyIfAbsent || oldValue == null)
                    e.value = value;
                afterNodeAccess(e);
                return oldValue;
            }
        }
        ++modCount;
        if (++size > threshold)
            resize();
        afterNodeInsertion(evict);
        return null;
    }
```


### get
### resize

```
    /**
    * 初始化或加倍表大小.  如果为 null，则根据字段阈值中保持的初始容量目标进行分配。.
    * 否则，因为我们使用的是二次扩展, the
    * 每个 bin 中的元素必须保持相同的索引, 或在新表中以两个偏移量移动 。
    *
    * @return the table
    */
    final Node<K,V>[] resize() {
        //使用oldTab指向原来的hash表
        //通常方法内都使用局部变量，局部变量在方法栈上，而对象的成员在堆上
        //方法栈的访问比堆更高效
        Node<K,V>[] oldTab = table;
        // oldTab的大小
        int oldCap = (oldTab == null) ? 0 : oldTab.length;
        // 老的tab阈值
        int oldThr = threshold;
        // 新的tab大小和阈值
        int newCap, newThr = 0;
        // old不为空
        if (oldCap > 0) {
            // 如果oldtable打到最大值，则不进行扩容
            if (oldCap >= MAXIMUM_CAPACITY) {
                threshold = Integer.MAX_VALUE;
                return oldTab;
            }
            // 如果新（老的2倍）小于最大容量 & 老的容量大于等于16（默认的）
            else if ((newCap = oldCap << 1) < MAXIMUM_CAPACITY &&
                     oldCap >= DEFAULT_INITIAL_CAPACITY)
                // 新的阈值=老的阈值*2
                newThr = oldThr << 1; // double threshold
        }
        // oldCap <= 0 table空间尚未分配，初始化分配空间
        else if (oldThr > 0) // initial capacity was placed in threshold
            newCap = oldThr;
        // 使用零初始阈值表示使用默认值。
        else {               // zero initial threshold signifies using defaults
            newCap = DEFAULT_INITIAL_CAPACITY;
            newThr = (int)(DEFAULT_LOAD_FACTOR * DEFAULT_INITIAL_CAPACITY);
        }
        if (newThr == 0) {
            float ft = (float)newCap * loadFactor;
            newThr = (newCap < MAXIMUM_CAPACITY && ft < (float)MAXIMUM_CAPACITY ?
                      (int)ft : Integer.MAX_VALUE);
        }
        threshold = newThr;
        @SuppressWarnings({"rawtypes","unchecked"})
            Node<K,V>[] newTab = (Node<K,V>[])new Node[newCap];
        // 分配新table
        table = newTab;
        // table != null，说明这是一次扩容，需要将Entry散列到新的位置
        if (oldTab != null) {
            // 遍历所有的桶
            for (int j = 0; j < oldCap; ++j) {
                Node<K,V> e;
                if ((e = oldTab[j]) != null) {
                    oldTab[j] = null;
                    // 桶里面只有一个节点
                    if (e.next == null)
                        newTab[e.hash & (newCap - 1)] = e;
                        // 桶中是一颗红黑树，通过红黑树的split方法处理
                    else if (e instanceof TreeNode)
                        ((TreeNode<K,V>)e).split(this, newTab, j, oldCap);
                        //单向链表，从新散列，但要保证Entry原来的顺序
                        //因为容量加倍了，散列时使用的位数扩展了一位
                       //该链表中Entry散列后可能有两个位置，通过新扩展位为0或1区分
                     else { // preserve order
                        //原链表分成两个链表，一高一低，通过新扩展的位来确定
                        Node<K,V> loHead = null, loTail = null;
                        Node<K,V> hiHead = null, hiTail = null;
                        Node<K,V> next;
                        do {
                            next = e.next;
                            //新扩展位为0(oldCap为2^k)，低链表
                            if ((e.hash & oldCap) == 0) {
                                if (loTail == null)
                                    loHead = e;
                                else
                                    loTail.next = e;
                                loTail = e;
                            }
                             //高链表
                            else {
                                if (hiTail == null)
                                    hiHead = e;
                                else
                                    hiTail.next = e;
                                hiTail = e;
                            }
                        } while ((e = next) != null);
                        if (loTail != null) {
                            loTail.next = null;
                            //低链表在数组中仍在原来的位置
                            newTab[j] = loHead;
                        }
                        if (hiTail != null) {
                            hiTail.next = null;
                            //高链表的位置相对于低链表的偏移为oldCap
                            newTab[j + oldCap] = hiHead;
                        }
                    }
                }
            }
        }
        return newTab;
    }
```

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

```
public class Test {
    static final int MAXIMUM_CAPACITY = 1 << 30;
    public static void main(String[] args) {
        System.out.println(tableSizeFor(4));
        System.out.println(10<<1);
        System.out.println(1 << 30);
        System.out.println(Integer.MAX_VALUE/2);
    }

    static final int tableSizeFor(int cap) {
        int n = cap - 1;
        n |= n >>> 1;
        n |= n >>> 2;

        n |= n >>> 4;
        n |= n >>> 8;
        n |= n >>> 16;
        return (n < 0) ? 1 : (n >= MAXIMUM_CAPACITY) ? MAXIMUM_CAPACITY : n + 1;
    }
}
```


