# 📊 S3 로그 기반 SIEM 분석 파이프라인 구축

## 📝 개요

이 프로젝트는 AWS S3에 저장된 로그 데이터를 Logstash로 수집하고,  
Elasticsearch에 적재한 후, Splunk의 collect 기능을 통해 인덱싱하여 시각화한 **보안 로그 분석 파이프라인**입니다.
---

## 🔧 구성 아키텍처
[S3] → [Logstash] → [Elasticsearch] → [Splunk (collect input)] → [Splunk Index]

### 주요 목적

- AWS S3에 저장된 로그를 활용해 보안 데이터 흐름 구성
- Logstash를 통해 로그를 Elasticsearch에 적재
- Splunk에서 Elasticsearch 데이터를 수집하여 추가 분석
- Splunk Dashboard를 통해 보안 이벤트 시각화

## ⚙️ 구성 요소

| 구성 요소 | 설명 |
|-----------|------|
| **AWS S3** | 로그 원본 저장소 |
| **Logstash** | 로그 전달 도구 (Elasticsearch 전송 역할) |
| **Elasticsearch** | 로그 저장 및 검색용 데이터베이스 |
| **Splunk (collect)** | Elasticsearch 데이터를 수집해 인덱싱 |
| **Splunk Dashboard** | 수집된 데이터를 기반으로 이벤트 시각화 구성 |

## 📁 파일 및 주요 설정 설명

### 🔧 Logstash

**`cf.conf`** – S3 로그 수집용 Logstash 파이프라인 설정

| 설정 항목 | 설명 |
|-----------|------|
| `proxy_uri` | S3 접근 시 사용하는 프록시 서버 주소 (내부망 환경에서 외부 통신용) |
| `sincedb_path` | 마지막 수집 지점 정보를 저장하는 로컬 경로 (재시작 시 이어서 수집 가능) |
| `interval` | S3 수집 주기 (초 단위, 기본: 60초) |

---

### 🗂️ Elasticsearch

- 수집된 로그가 저장되는 NoSQL 기반 데이터 저장소
- 인덱스 명: `security_cflog-%{+YYYY.MM}`
- 로그 탐색 및 연동 대상

---

### 📊 Splunk

- Elasticsearch 데이터를 **collect input** 기능으로 가져와 분석/시각화
- 인덱스에 저장 후, Dashboard를 통해 시각화 구성
  - 예: Source IP Top 10, 요청 경로 분포, 응답 코드 등
