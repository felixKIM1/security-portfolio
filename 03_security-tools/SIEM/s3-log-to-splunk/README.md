# 📊 S3 로그 기반 SIEM 분석 파이프라인 구축

## 📝 개요

이 프로젝트는 AWS S3에 저장된 로그 데이터를 Logstash로 수집하고,  
Elasticsearch에 적재한 후, Splunk의 collect 기능을 통해 인덱싱하여 시각화한 **보안 로그 분석 파이프라인**입니다.
---

## 🔧 구성 아키텍처
[S3] → [Logstash] → [Elasticsearch] → [Splunk (collect input)] → [Splunk Index]
