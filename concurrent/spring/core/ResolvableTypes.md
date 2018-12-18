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
