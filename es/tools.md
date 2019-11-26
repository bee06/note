## 创建索引
curl -X PUT "localhost:9200/user_order_short?pretty" -H 'Content-Type: application/json' -d'
{
    "settings": {
        "number_of_shards" :   3,
        "number_of_replicas" : 2
    }
}
'
## 删除索引
curl -X DELETE "http://localhost:9201/user_order_short

## 创建动态索引
curl -X PUT "http://localhost:9201/user_order_short?pretty"  -d'
{
  "mappings": {
    "user_orders": {
      "_routing": {
        "required": true
      },
      "dynamic_date_formats": [
        "yyyy-MM-dd",
        "yyyy-MM-dd HH:mm:ss",
        "date_optional_time"
      ],
      "dynamic_templates": [
        {
          "anglyzed_stringType": {
            "mapping": {
              "fields": {
                "raw": {
                  "type": "keyword"
                }
              },
              "type": "text"
            },
            "match_mapping_type": "string",
            "match": "analyze_*"
          }
        },
        {
          "not_analyzed_stringType": {
            "mapping": {
              "ignore_above": 255,
              "type": "keyword"
            },
            "match_mapping_type": "string",
            "match": "*"
          }
        }
      ],
      "properties": {}
    }
  }
}
'


