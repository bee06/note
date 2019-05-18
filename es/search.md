## 查询
* matchAllQuery()方法用来匹配全部文档
* matchQuery("filedname","value")匹配单个字段，匹配字段名为filedname,值为value的文档
* multiMatchQuery(Object text, String... fieldNames)
* wildcardQuery()模糊查询
> 模糊查询，?匹配单个字符，*匹配多个字符
* 使用BoolQueryBuilder进行复合查询
