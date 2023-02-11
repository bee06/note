
数组实现的有界阻塞队列  队列元素先进先出  队列头元素是对列最长元素。队列尾元素是最短的元素。新的元素在队列的尾部插入，队列检索操作在队列的头部获取元素。


这是一个经典的“有界缓冲区”。其中固定大小的数组包含由生产者插入并由消费者提取的元素
一旦创建，容量就不能修改了
尝试将元素放入完整队列将导致操作阻塞
尝试从空队列获取对象将导致操作阻塞

支持用于订购等待生产者和使用者线程的可选公平性策略，
默认情况下，不保证排序。
由公平设置为true的队列，以FIFO顺序授予线程访问权，公平通常降低吞吐量，但减少变异性，避免饥饿


源码分析
    实现了BlockingQueue接口

    成员变量
    /** 队列数组 */
    final Object[] items;

    /** 用于进行、轮训、查看和删除索引项 */
    int takeIndex;

    /** 增加存放的所有项 */
    int putIndex;

    /** 队列个数 */
    int count;

    /*
     * Concurrency control uses the classic two-condition algorithm
     * found in any textbook.
     */

    /** Main lock guarding all access */
    final ReentrantLock lock;

    /** 获取等待的条件 */
    private final Condition notEmpty;

    /** 放入等待的条件 */
    private final Condition notFull;

    /**
     * Shared state for currently active iterators, or null if there
     * are known not to be any.  Allows queue operations to update
     * iterator state.
     */
    transient Itrs itrs = null;


    构造函数

    capacity 容量
    fair 公平锁
    public ArrayBlockingQueue(int capacity, boolean fair) {
        if (capacity <= 0)
            throw new IllegalArgumentException();
        this.items = new Object[capacity];
        lock = new ReentrantLock(fair);
        notEmpty = lock.newCondition();
        notFull =  lock.newCondition();
    }
