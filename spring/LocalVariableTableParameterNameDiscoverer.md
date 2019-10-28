
实现了ParameterNameDiscoverer
查找方法和构造函数的参数名称的接口

栗子🌰

```
/**
 * 通过ASM方式获得方法参数信息
 * @param apiMethod
 * @return
 */
private static ApiParamMeta[] getApiParamMetaByASM(Method apiMethod) {
	LocalVariableTableParameterNameDiscoverer parameterNameDiscoverer = 
			new LocalVariableTableParameterNameDiscoverer();
	String[] names = parameterNameDiscoverer.getParameterNames(apiMethod);
	
	if (names != null) {
		ApiParamMeta[] apiParamMetas = new ApiParamMeta[names.length];
		for (int i = 0; i < names.length; i++) {
			apiParamMetas[i] = new ApiParamMeta(names[i]);
		}
		return apiParamMetas;
	}
	return null;
}
```
DefaultParameterNameDiscoverer

AutowireCandidateResolver

Aware
ApplicationContextAware：获取容器上下文
BeanClassLoaderAware：获取加载当前Bean的类加载器
BeanNameAware：获取当前Bean的名称
LoadTimeWeaverAware：可以接收一个指向载入时（编译时）时织入实例的引用，实现编译时代理，属于比较高端的。可参见AspectJWeavingEnabler
BootstrapContextAware：拿到资源适配器BootstrapContext上下文，如JCA,CCI
ServletConfigAware：获取到ServletConfig
ImportAware：获取到AnnotationMetadata等信息。这个挺重要的，比如AbstractCachingConfiguration、AbstractTransactionManagementConfiguration都通过实现这个接口来获取到了注解的属性们。比如@EnableAsync、EnableCaching等注解上的属性值  参考：Spring的@Import注解与ImportAware接口
EmbeddedValueResolverAware：能让我们拿到StringValueResolver这个处理器，这样我们就可以很好的处理配置文件的值了。我们可以做个性化处理（比如我们自己要书写一个属性获取的工具类之类的。。。）
EnvironmentAware：拿到环境Environment
BeanFactoryAware：获取Bean Factory
NotificationPublisherAware：和JMX有关
ResourceLoaderAware：获取资源加载器ResourceLoader可以获得外部资源文件  比如它的：ResourceLoader#getResource方法
MessageSourceAware：获取国际化文本信息
ServletContextAware：获取ServletContext
ApplicationEventPublisher：拿到事件发布器


ResolvableType
提供的方法举例：

getSuperType()：获取直接父类型
getInterfaces()：获取接口类型们
getGenerics()：获取类型携带的泛型类型
resolve()：Type对象到Class对象的转换（使用得非常多）
isInstance、isAssignableFrom。。。
.ResolvableType.forInstance 获取指定的实例的泛型信息
