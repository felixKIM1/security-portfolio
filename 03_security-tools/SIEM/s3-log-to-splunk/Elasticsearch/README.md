## 📦 Elasticsearch & Kibana 구조 개요

### 🔎 데이터 수집 확인

- Kibana의 **Stack Management → Index Management**에서  
  Elasticsearch에 로그 데이터가 정상적으로 쌓이고 있는지 확인할 수 있습니다.  
  Logstash가 데이터를 잘 전달하고 있는지 검증하는 데 유용합니다.

- Kibana의 **Index Patterns** 기능은  
  다양한 인덱스를 패턴(`security_cflog-*`)으로 묶어  
  Discover, Dashboard 등에서 분석할 수 있도록 도와줍니다.

---

### 🔄 Splunk와 Elasticsearch 연동

- Splunk는 Elasticsearch에 직접 **REST API 요청**을 보내어 데이터를 수집합니다.
- 이때 사용하는 경로는 실제 **Elasticsearch 인덱스 API** (`/_search`)이며,  
  Kibana의 Index Management에서 보이는 인덱스 목록과 **동일한 위치를 참조**합니다.

```http
GET http://<ES_IP>:9200/security_cflog-*/_search
