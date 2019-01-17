## 定义
封装Java类型，提供对超类型，接口和通用参数的访问，以及最终解析为类的能力。
ResolvableTypes可以从字段，方法参数，方法返回或类中获得。此类上的大多数方法本身都会返回ResolvableTypes，从而可以轻松导航。

## 例子
```
public class ResolvableTypesLearn {

    private HashMap<Integer, List<String>> myMap;

    public static void main(String[] args) throws NoSuchFieldException {
        ResolvableType t = ResolvableType.forField(ResolvableTypesLearn.class.getDeclaredField("myMap"));

        System.out.println(t.getSuperType());
        System.out.println(t.asMap());
        System.out.println(t.getGeneric(0).resolve());
        System.out.println(t.getGeneric(1).resolve());
        System.out.println(t.getGeneric(1));
        System.out.println(t.resolveGeneric(1, 0));
    }
}


```
### 输出
```
java.util.AbstractMap<java.lang.Integer, java.util.List<java.lang.String>>
java.util.Map<java.lang.Integer, java.util.List<java.lang.String>>
class java.lang.Integer
interface java.util.List
java.util.List<java.lang.String>
class java.lang.String
```

## 源码分析
### 成员变量
```
/**
	 * {@code ResolvableType} returned when no value is available. {@code NONE} is used
	 * in preference to {@code null} so that multiple method calls can be safely chained.
	 */
	public static final ResolvableType NONE = new ResolvableType(null, null, null, null);

	private static final ResolvableType[] EMPTY_TYPES_ARRAY = new ResolvableType[0];

	private static final ConcurrentReferenceHashMap<ResolvableType, ResolvableType> cache =
			new ConcurrentReferenceHashMap<ResolvableType, ResolvableType>(256);


	/**
	 * The underlying Java type being managed (only ever {@code null} for {@link #NONE}).
	 */
	private final Type type;

	/**
	 * Optional provider for the type.
	 */
	private final TypeProvider typeProvider;

	/**
	 * The {@code VariableResolver} to use or {@code null} if no resolver is available.
	 */
	private final VariableResolver variableResolver;

	/**
	 * The component type for an array or {@code null} if the type should be deduced.
	 */
	private final ResolvableType componentType;

	/**
	 * Copy of the resolved value.
	 */
	private final Class<?> resolved;

	private ResolvableType superType;

	private ResolvableType[] interfaces;

	private ResolvableType[] generics;
```

### 构造方法
```
/**
	 * Private constructor used to create a new {@link ResolvableType} for resolution purposes.
	 */
	private ResolvableType(
			Type type, TypeProvider typeProvider, VariableResolver variableResolver, ResolvableType componentType) {

		this.type = type;
		this.typeProvider = typeProvider;
		this.variableResolver = variableResolver;
		this.componentType = componentType;
		this.resolved = resolveClass();
	}

	/**
	 * Private constructor used to create a new {@link ResolvableType} for cache key purposes.
	 */
	private ResolvableType(Type type, TypeProvider typeProvider, VariableResolver variableResolver) {
		this.type = type;
		this.typeProvider = typeProvider;
		this.variableResolver = variableResolver;
		this.componentType = null;
		this.resolved = null;
	}

```

