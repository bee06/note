# high performance
## 各个缓存的响应时间
---|---|---
L1 cache reference|0.5ns|
Branch mispredict|5ns|
L2 cache reference|7ns|14x L1 cache
Mutex lock/unlock|25ns|
Main memory reference|100ns|20x L2 cache, 200x L1 cache
Compress 1K bytes with Zippy|3us|
Send 1K bytes over 1 Gbps network|10us|
Read 4K randomly from SSD*|150us|1GB/sec SSD
Read 1 MB sequentially from memory|250us|
Round trip within same datacenter|500us|
Read 1 MB sequentially from SSD*|1ms|~1GB/sec SSD, 4X memory
Disk seek|10ms|20x datacenter roundtrip
Read 1 MB sequentially from disk|20ms|80x memory, 20X SSD
Send packet PEK->SHA|30ms|
Send packet CA->Netherlands->CA|150ms|
