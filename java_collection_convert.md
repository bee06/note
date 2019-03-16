# 使用Java libraries, Guava or Apache Commons Collections转各个集合类
## List to Array
### Using plain Java
```
@Test
public void givenUsingCoreJava_whenListConvertedToArray_thenCorrect() {
    List<Integer> sourceList = Arrays.asList(0, 1, 2, 3, 4, 5);
    Integer[] targetArray = sourceList.toArray(new Integer[sourceList.size()]);
}
```

### Using  Guava
```
@Test
public void givenUsingGuava_whenListConvertedToArray_thenCorrect() {
    List<Integer> sourceList = Lists.newArrayList(0, 1, 2, 3, 4, 5);
    int[] targetArray = Ints.toArray(sourceList);
}
```
## Array to List
### Using plain Java
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
### Using guava
```
@Test
public void givenUsingGuava_whenArrayConvertedToList_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    List<Integer> targetList = Lists.newArrayList(sourceArray);
}
```
### Using commons
```
@Test
public void givenUsingCommonsCollections_whenArrayConvertedToList_thenCorrect() { 
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 }; 
    List<Integer> targetList = new ArrayList<>(6); 
    CollectionUtils.addAll(targetList, sourceArray); 
}
```

## Array to  Set
### Using plain Java
```
@Test
public void givenUsingCoreJavaV1_whenArrayConvertedToSet_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    Set<Integer> targetSet = new HashSet<Integer>(Arrays.asList(sourceArray));
}
```
or
```
@Test
public void givenUsingCoreJavaV2_whenArrayConvertedToSet_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    Set<Integer> targetSet = new HashSet<Integer>();
    Collections.addAll(targetSet, sourceArray);
}
```

### Using Google Guava
```
@Test
public void givenUsingGuava_whenArrayConvertedToSet_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    Set<Integer> targetSet = Sets.newHashSet(sourceArray);
}
```
### Using Apache Commons Collections
```
@Test
public void givenUsingCommonsCollections_whenArrayConvertedToSet_thenCorrect() {
    Integer[] sourceArray = { 0, 1, 2, 3, 4, 5 };
    Set<Integer> targetSet = new HashSet<>(6);
    CollectionUtils.addAll(targetSet, sourceArray);
}

```
## Set to Array
### Using plain Java
```
@Test
public void givenUsingCoreJava_whenSetConvertedToArray_thenCorrect() {
    Set<Integer> sourceSet = Sets.newHashSet(0, 1, 2, 3, 4, 5);
    Integer[] targetArray = sourceSet.toArray(new Integer[sourceSet.size()]);
}
```
### Using Guava
```
@Test
public void givenUsingGuava_whenSetConvertedToArray_thenCorrect() {
    Set<Integer> sourceSet = Sets.newHashSet(0, 1, 2, 3, 4, 5);
    int[] targetArray = Ints.toArray(sourceSet);
}
```
### Using Commons Collections

```
@Test
public void givenUsingCommonsCollections_whenSetConvertedToArray_thenCorrect() {
    Set<Integer> sourceSet = Sets.newHashSet(0, 1, 2, 3, 4, 5);
    Integer[] targetArray = sourceSet.toArray(new Integer[sourceSet.size()]);
}
```
## Array to String
### Arrays.toString()  
```
String[] strArray = { "one", "two", "three" };
String joinedString = Arrays.toString(strArray);
```
###  StringBuilder.append()
```
String[] strArray = { "Convert", "Array", "With", "Java" };
StringBuilder stringBuilder = new StringBuilder();
for (int i = 0; i < strArray.length; i++) {
    stringBuilder.append(strArray[i]);
}
String joinedString = stringBuilder.toString();
```
### Java Streams API
```
String joinedString = Arrays
    .stream(new String[]{ "Convert", "With", "Java", "Streams" })
    .collect(Collectors.joining());
```

### StringUtils.join()

```
String joinedString = StringUtils.join(new String[]{ "Convert", "With", "Apache", "Commons" });

```

### Joiner.join()
```
String joinedString = Joiner.on("")
        .skipNulls()
        .join(new String[]{ "Convert", "With", "Guava", null });
```
## Array of Strings
### String.split()
```
String[] strArray = "loremipsum".split("");
```

### StringUtils.split()
```
String[] splitted = StringUtils.split("lorem ipsum dolor sit amet");
```

### Splitter.split()
```
List<String> resultList = Splitter.on(' ')
    .trimResults()
    .omitEmptyStrings()
    .splitToList("lorem ipsum dolor sit amet");   
String[] strArray = resultList.toArray(new String[0]);
```

## ArrayList  to Constructor
### Using the ArrayList Constructor
```
ArrayList<Foo> newList = new ArrayList<>(srcCollection);
```
### Stream Api
```
ArrayList<Foo> newList = srcCollection.stream().collect(toCollection(ArrayList::new));
```
