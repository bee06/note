## Collection as Value

```
Map<String, List<String>> map = new HashMap<>();
List<String> list = new ArrayList<>();
map.put("key1", list);
map.get("key1").add("value1");
map.get("key1").add("value2");
```

## With Commons Collections
```
MultiMap<String, String> map = new MultiValueMap<>();
map.put("key1", "value1");
map.put("key1", "value2");
assertThat((Collection<String>) map.get("key1"))
  .contains("value1", "value2");
```
or
```
MultiValuedMap<String, String> map = new HashSetValuedHashMap<>();
map.put("key1", "value1");
map.put("key1", "value1");
assertThat((Collection<String>) map.get("key1"))
  .containsExactly("value1");
```

## With Guava
```
Multimap<String, String> map = ArrayListMultimap.create();
map.put("key1", "value2");
map.put("key1", "value1");
assertThat((Collection<String>) map.get("key1"))
  .containsExactly("value2", "value1");
```

