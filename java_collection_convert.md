## 使用Java libraries, Guava or Apache Commons Collections转各个集合类
### List to Array
#### Using plain Java
```
@Test
public void givenUsingCoreJava_whenListConvertedToArray_thenCorrect() {
    List<Integer> sourceList = Arrays.asList(0, 1, 2, 3, 4, 5);
    Integer[] targetArray = sourceList.toArray(new Integer[sourceList.size()]);
}
```

#### Using  Guava
```
@Test
public void givenUsingGuava_whenListConvertedToArray_thenCorrect() {
    List<Integer> sourceList = Lists.newArrayList(0, 1, 2, 3, 4, 5);
    int[] targetArray = Ints.toArray(sourceList);
}
```
### Array to List
#### Using plain Java
```
@Test
public void givenUsingCoreJava_whenArrayConvertedToList_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    List<Integer> targetList = Arrays.asList(sourceArray);
}
```
or
```
List<Integer> targetList = new ArrayList<Integer>(Arrays.asList(sourceArray));
```
#### Using guava
```
@Test
public void givenUsingGuava_whenArrayConvertedToList_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    List<Integer> targetList = Lists.newArrayList(sourceArray);
}
```
#### Using commons
```
@Test
public void givenUsingCommonsCollections_whenArrayConvertedToList_thenCorrect() { 
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 }; 
    List<Integer> targetList = new ArrayList<>(6); 
    CollectionUtils.addAll(targetList, sourceArray); 
}
```

