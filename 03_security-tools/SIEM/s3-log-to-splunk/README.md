# 📊 S3 로그 기반 SIEM 분석 파이프라인 구축

## 📝 개요

이 프로젝트는 AWS S3에 저장된 로그 데이터를 Logstash로 수집하고,  
Elasticsearch에 적재한 후, Splunk의 collect 기능을 통해 인덱싱하여 시각화한 **보안 로그 분석 파이프라인**입니다.

---

## 🔧 구성 아키텍처

```
[S3]  
  ↓  
[Logstash]  
  ↓  
[Elasticsearch]  
  ↓  
[Splunk generateelk.py → collect]  
  ↓  
[Splunk Index + Dashboard]
```



### 주요 목적

- AWS S3에 저장된 로그를 활용해 보안 데이터 흐름 구성
- Logstash를 통해 로그를 Elasticsearch에 적재
- Splunk에서 Elasticsearch 데이터를 수집하여 추가 분석
- Splunk Dashboard를 통해 보안 이벤트 시각화

---

## ⚙️ 구성 요소

| 구성 요소         | 설명 |
|------------------|------|
| **AWS S3**       | 로그 원본 저장소 |
| **Logstash**     | 로그 전달 도구 (Elasticsearch 전송 역할) |
| **Elasticsearch**| 로그 저장 및 검색용 데이터베이스 |
| **Splunk (collect)** | Elasticsearch 데이터를 수집해 인덱싱 |
| **Splunk Dashboard** | 수집된 데이터를 기반으로 이벤트 시각화 구성 |

---

## 📁 구성 파일 및 설정

### 🔧 Logstash – `cf.conf`

- `proxy_uri`: S3 접근 시 사용하는 프록시 서버 주소 (내부망 환경)
- `sincedb_path`: 수집 지점 기록용 파일 경로
- `interval`: S3 수집 주기 (초 단위, 기본 60)

---

### 🗂️ Elasticsearch

- 수집된 로그가 저장되는 NoSQL 기반 검색 엔진
- 인덱스 형식: `security_cflog-%{+YYYY.MM}`
- Kibana에서 시각화 또는 Splunk에서 직접 수집 가능

---

### 📊 Splunk 구성 요소

#### ✅ `Config Explorer.py`
- Splunk External Search Command
- Elasticsearch에 직접 `_search` 요청 후 결과를 Splunk에 `_raw` 형태로 인덱싱
- 시간 필터, 쿼리, 인덱스 지정 가능



#### ✅ 'collect_cloudfront_logs.spl'
정적 자원 제외 필터링

중요한 필드(ip, uri, status, 등)만 추출

collect 명령어로 sec_cf_log 인덱스에 저장

#### ✅ 'Dashboard'
특정 시간 내 IP 요청량 이상 감지

index=sec_cf_log
| bin _time span=10m
| stats count by _time, ip
| where count >= 100
| timechart span=10m sum(count) by ip
