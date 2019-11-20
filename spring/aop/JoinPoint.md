## JoinPoint
### 目的
### 功能
* toString
//连接点所在位置的相关信息  
* toShortString
//连接点所在位置的简短相关信息  
* toLongString
//连接点所在位置的全部相关信息 
* getThis
//返回AOP代理对象，也就是com.sun.proxy.$Proxy18
* getTarget
//返回目标对象，一般我们都需要它或者（也就是定义方法的接口或类，为什么会是接口呢？
* getArgs
//返回被通知方法参数列表  
* getSignature
//返回当前连接点签名
* getSourceLocation
//返回连接点方法所在类文件中的位置  
* getKind
连接点类型  
* getStaticPart
返回连接点静态部分  
### 实现
### 缺点