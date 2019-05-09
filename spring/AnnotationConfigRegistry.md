## 功能
注释配置应用程序上下文的通用配置，定义了注册和扫描方法
## 实现类
### AnnotationConfigApplicationContext
#### 父类
GenericApplicationContext
#### 成员变量
* AnnotatedBeanDefinitionReader
* ClassPathBeanDefinitionScanner
#### 构造方法
```
public AnnotationConfigApplicationContext() {
	this.reader = new AnnotatedBeanDefinitionReader(this);
	this.scanner = new ClassPathBeanDefinitionScanner(this);
}
public AnnotationConfigApplicationContext(DefaultListableBeanFactory beanFactory) {
	super(beanFactory);
	this.reader = new AnnotatedBeanDefinitionReader(this);
	this.scanner = new ClassPathBeanDefinitionScanner(this);
}
public AnnotationConfigApplicationContext(Class<?>... annotatedClasses) {
	this();
	register(annotatedClasses);
	refresh();
}
public AnnotationConfigApplicationContext(String... basePackages) {
	this();
	scan(basePackages);
	refresh();
}
```
#### 方法
```
setEnvironment(ConfigurableEnvironment environment)
setBeanNameGenerator(BeanNameGenerator beanNameGenerator) 
setScopeMetadataResolver(ScopeMetadataResolver scopeMetadataResolver)
register(Class<?>... annotatedClasses)
scan(String... basePackages) 
registerBean(Class<T> annotatedClass, Object... constructorArguments)
registerBean(@Nullable String beanName, Class<T> annotatedClass, Object... constructorArguments)
registerBean(@Nullable String beanName, Class<T> beanClass, @Nullable Supplier<T> supplier,
			BeanDefinitionCustomizer... customizers)
```
