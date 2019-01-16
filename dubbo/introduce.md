
* proxyFactory:就是为了获取一个接口的代理类，例如获取一个远程接口的代理。
它有2个方法，代表2个作用
  ** getInvoker:针对server端，将服务对象，如DemoServiceImpl包装成一个Invoker对象。
  ** getProxy  :针对client端，创建接口的代理对象，例如DemoService的接口。
* Wrapper:它类似spring的BeanWrapper,它就是包装了一个接口或一个类，可以通过wrapper对实例对象进行赋值 取值以及制定方法的调用。
* Invoker：它是一个可执行的对象，能够根据方法的名称、参数得到相应的执行结果。
       它里面有一个很重要的方法 Result invoke(Invocation invocation)，
  Invocation是包含了需要执行的方法和参数等重要信息，目前它只有2个实现类RpcInvocation MockInvocation
      它有3种类型的Invoker
    ** 本地执行类的Invoker
      server端：要执行 demoService.sayHello，就通过InjvmExporter来进行反射执行demoService.sayHello就可以了。
      
    ** 远程通信类的Invoker
        client端：要执行 demoService.sayHello，它封装了DubboInvoker进行远程通信，发送要执行的接口给server端。
        server端：采用了AbstractProxyInvoker执行了DemoServiceImpl.sayHello,然后将执行结果返回发送给client.
        
    ** 多个远程通信执行类的Invoker聚合成集群版的Invoker
        client端：要执行 demoService.sayHello，就要通过AbstractClusterInvoker来进行负载均衡，DubboInvoker进行远程通信，发送要执行的接口给server端。
        server端：采用了AbstractProxyInvoker执行了DemoServiceImpl.sayHello,然后将执行结果返回发送给client.
        
* Protocol
  1.export：暴露远程服务（用于服务端），就是将proxyFactory.getInvoker创建的代理类 invoker对象，通过协议暴露给外部。
  2.refer：引用远程服务（用于客户端）, 通过proxyFactory.getProxy来创建远程的动态代理类，例如DemoService的远程动态接口。
  
* exporter：维护invoder的生命周期。

* exchanger：信息交换层，封装请求响应模式，同步转异步。

* transporter：网络传输层，用来抽象netty和mina的统一接口。

* Directory：目录服务
  StaticDirectory：静态目录服务，他的Invoker是固定的。
  RegistryDirectory：注册目录服务，他的Invoker集合数据来源于zk注册中心的，他实现了NotifyListener接口，并且实现回调notify(List<URL> urls),整个过程有一个重要的map变量，methodInvokerMap（它是数据的来源；同时也是notify的重要操作对象，重点是写操作。）
  
                                                           


  
    
       
       
