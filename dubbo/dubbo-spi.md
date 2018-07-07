## 为什么要设计adaptive？注解在类上和注解在方法上的区别？
  - adaptive设计的目的是为了识别固定已知类和扩展未知类。
  - 注解在类上：代表人工实现，实现一个装饰类（设计模式中的装饰模式），它主要作用于固定已知类，
  目前整个系统只有2个，AdaptiveCompiler、AdaptiveExtensionFactory。
  a.为什么AdaptiveCompiler这个类是固定已知的？因为整个框架仅支持Javassist和JdkCompiler。
  b.为什么AdaptiveExtensionFactory这个类是固定已知的？因为整个框架仅支持2个objFactory,一个是spi,另一个是spring
2.注解在方法上：代表自动生成和编译一个动态的Adpative类，它主要是用于SPI，因为spi的类是不固定、未知的扩展类，所以设计了动态$Adaptive类.
例如 Protocol的spi类有 injvm dubbo registry filter listener等等 很多扩展未知类，
它设计了Protocol$Adaptive的类，通过ExtensionLoader.getExtensionLoader(Protocol.class).getExtension(spi类);来提取对象


## 为什么dubbo要自己设计一套SPI？
这是原始JDK spi的代码
  ServiceLoader<Command> serviceLoader=ServiceLoader.load(Command.class);
  for(Command command:serviceLoader){  
      command.execute();  
  }  
dubbo在原来的基础上设计了以下功能
1.原始JDK spi不支持缓存；dubbo设计了缓存对象：spi的key与value 缓存在 cachedInstances对象里面，它是一个ConcurrentMap
2.原始JDK spi不支持默认值，dubbo设计默认值：@SPI("dubbo") 代表默认的spi对象，例如Protocol的@SPI("dubbo")就是 DubboProtocol，
  通过 ExtensionLoader.getExtensionLoader(Protocol.class).getDefaultExtension()那默认对象
3.jdk要用for循环判断对象，dubbo设计getExtension灵活方便，动态获取spi对象，
  例如 ExtensionLoader.getExtensionLoader(Protocol.class).getExtension(spi的key)来提取对象
4.原始JDK spi不支持 AOP功能，dubbo设计增加了AOP功能,在cachedWrapperClasses，在原始spi类，包装了XxxxFilterWrapper XxxxListenerWrapper
5.原始JDK spi不支持 IOC功能，dubbo设计增加了IOC,通过构造函数注入,代码为：wrapperClass.getConstructor(type).newInstance(instance),





dubbo spi 的目的：获取一个指定实现类的对象。
途径：ExtensionLoader.getExtension(String name)
实现路径：
getExtensionLoader(Class<T> type) 就是为该接口new 一个ExtensionLoader，然后缓存起来。
getAdaptiveExtension() 获取一个扩展类，如果@Adaptive注解在类上就是一个装饰类；如果注解在方法上就是一个动态代理类，例如Protocol$Adaptive对象。
getExtension(String name) 获取一个指定对象。


-----------------------ExtensionLoader.getExtensionLoader(Class<T> type)
ExtensionLoader.getExtensionLoader(Container.class)
  -->this.type = type;
  -->objectFactory = (type == ExtensionFactory.class ? null : ExtensionLoader.getExtensionLoader(ExtensionFactory.class).getAdaptiveExtension());
     -->ExtensionLoader.getExtensionLoader(ExtensionFactory.class).getAdaptiveExtension()
       -->this.type = type;
       -->objectFactory =null;

执行以上代码完成了2个属性的初始化
1.每个一个ExtensionLoader都包含了2个值 type 和 objectFactory
  Class<?> type；//构造器  初始化时要得到的接口名
  ExtensionFactory objectFactory//构造器  初始化时 AdaptiveExtensionFactory[SpiExtensionFactory,SpringExtensionFactory]
2.new 一个ExtensionLoader 存储在ConcurrentMap<Class<?>, ExtensionLoader<?>> EXTENSION_LOADERS

关于这个objectFactory的一些细节：
1.objectFactory就是ExtensionFactory，它也是通过ExtensionLoader.getExtensionLoader(ExtensionFactory.class)来实现的，但是它的objectFactory=null
2.objectFactory作用，它就是为dubbo的IOC提供所有对象。


-----------------------getAdaptiveExtension()


-->getAdaptiveExtension()//为cachedAdaptiveInstance赋值
  -->createAdaptiveExtension()
    -->getAdaptiveExtensionClass()
      -->getExtensionClasses()//为cachedClasses 赋值
        -->loadExtensionClasses()
          -->loadFile
      -->createAdaptiveExtensionClass()//自动生成和编译一个动态的adpative类，这个类是一个代理类
        -->ExtensionLoader.getExtensionLoader(com.alibaba.dubbo.common.compiler.Compiler.class).getAdaptiveExtension()
        -->compiler.compile(code, classLoader)
    -->injectExtension()//作用：进入IOC的反转控制模式，实现了动态入注


关于loadfile的一些细节
目的：通过把配置文件META-INF/dubbo/internal/com.alibaba.dubbo.rpc.Protocol的内容，存储在缓存变量里面。
cachedAdaptiveClass//如果这个class含有adative注解就赋值，例如ExtensionFactory，而例如Protocol在这个环节是没有的。
cachedWrapperClasses//只有当该class无adative注解，并且构造函数包含目标接口（type）类型，
                                                                 例如protocol里面的spi就只有ProtocolFilterWrapper和ProtocolListenerWrapper能命中
cachedActivates//剩下的类，包含Activate注解
cachedNames//剩下的类就存储在这里。



-----------------------getExtension(String name)
getExtension(String name) //指定对象缓存在cachedInstances；get出来的对象wrapper对象，例如protocol就是ProtocolFilterWrapper和ProtocolListenerWrapper其中一个。
  -->createExtension(String name)
    -->getExtensionClasses()
    -->injectExtension(T instance)//dubbo的IOC反转控制，就是从spi和spring里面提取对象赋值。
      -->objectFactory.getExtension(pt, property)
        -->SpiExtensionFactory.getExtension(type, name)
          -->ExtensionLoader.getExtensionLoader(type)
          -->loader.getAdaptiveExtension()
        -->SpringExtensionFactory.getExtension(type, name)
          -->context.getBean(name)
    -->injectExtension((T) wrapperClass.getConstructor(type).newInstance(instance))//AOP的简单设计
