📦 Splunk x Elasticsearch 연동 구성 (S3 기반 로그 수집)

이 디렉토리는 AWS S3에 저장된 로그 데이터를 Elasticsearch(ES)에 적재하고, Splunk를 통해 검색/정제/시각화하는 전체 파이프라인의 구성 예시를 포함합니다.

📁 구성 파일 개요

1. Config Explorer.py (Splunk External Command)

Splunk 사용자 정의 명령어로, Splunk에서 직접 Elasticsearch REST API에 접속하여 데이터를 조회하는 Python 스크립트입니다.

사용자가 입력한 인덱스, 쿼리, 시간 범위 등을 바탕으로 Elasticsearch에 요청을 보내고, 결과를 _raw로 변환해 Splunk로 반환합니다.

주요 기능:

@timestamp 필드를 기준으로 시간 정렬

시간 범위 자동 계산 (search_et, search_lt 기반)

검색 결과를 Splunk 필드 구조로 파싱 및 출력

예시 사용법:

| generateelk index="security_cflog-*" query="status:403" size=100

2. collect_cloudfront_logs.spl

Elasticsearch에서 수집된 CloudFront 로그 중 정적 자원 요청을 제외하고 의미 있는 요청만 필터링하여 Splunk의 별도 인덱스(sec_cf_log)로 수집하는 쿼리입니다.

기능 흐름:

spath 명령어로 CloudFront JSON 로그 필드 파싱

.js, .png, .mp4 등 불필요 자원 URI 제거

사용자 IP, URI, 응답코드 등의 핵심 필드만 추출

collect 명령어를 사용해 sec_cf_log 인덱스로 저장

사용 목적:

보안 분석/탐지용 로그 정제

후속 대시보드 및 경고 쿼리 연계용

3. Dashboard (CloudFront 이상 탐지 예시)

sec_cf_log 인덱스를 기반으로 일정 시간 내 요청 수가 급증한 IP를 시각화하는 예시 SPL 쿼리입니다.

index=sec_cf_log
| bin _time span=10m
| stats count by _time, ip
| where count >= 100
| timechart span=10m sum(count) by ip

사용 목적:

공격 또는 비정상 요청 발생 시 이상 징후를 빠르게 탐지

timechart를 통해 시간 기반 추이 시각화 가능

🔄 전체 데이터 흐름 요약

[S3 로그]
   ↓
[Logstash (cf.conf)]
   ↓
[Elasticsearch] → [Kibana 확인용]
   ↓
[Splunk (generateelk.py)] → [필터링 쿼리] → [sec_cf_log 인덱스 저장] → [Dashboard 탐지]

✨ 실무 포인트 요약

Splunk에서 직접 ES API를 호출하는 방식으로 실시간 연동 구현

불필요 로그 제거 후 collect를 통해 탐지 최적화된 데이터만 수집

대시보드 구성으로 경고, 추세 분석까지 확장 가능

이 구성은 S3-ES-Splunk 로그 분석 파이프라인을 직접 구성해본 실습 결과로, 실제 보안 인프라 환경에서 적용 가능한 구조입니다.
