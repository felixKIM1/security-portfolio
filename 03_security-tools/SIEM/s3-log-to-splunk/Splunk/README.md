📦 Splunk x Elasticsearch 연동 구성 (S3 기반 로그 수집)

이 디렉토리는 AWS S3에 저장된 로그 데이터를 Elasticsearch(ES)에 적재하고, Splunk를 통해 검색/정제/시각화하는 전체 파이프라인 구성

📁 구성 파일 요약

🔹 Config Explorer.py (Splunk External Command)

Splunk 사용자 정의 명령어

Elasticsearch REST API를 직접 호출하여 인덱스, 쿼리, 시간 범위 기반 로그 검색 수행

응답 결과를 _raw 필드로 반환하여 Splunk 인덱싱 구조에 맞게 출력

주요 기능:

@timestamp 기준 시간 정렬

search_et, search_lt 기반 시간 범위 자동 계산

Splunk 필드 구조로 변환 후 출력

예시 사용법:

| generateelk index="security_cflog-*" query="status:403" size=100

🔹 collect_cloudfront_logs.spl

Elasticsearch에서 수집된 CloudFront 로그 중 불필요 리소스를 제거하고 의미 있는 요청만 필터링

Splunk의 별도 인덱스(sec_cf_log)에 수집

기능 흐름:

spath로 JSON 필드 파싱

.js, .png 등 정적 자원 URI 필터링

핵심 필드(IP, URI, 응답코드 등) 추출

collect 명령어로 sec_cf_log 인덱스에 저장

사용 목적:

보안 탐지 목적의 로그 정제

후속 대시보드/경고 쿼리 연계용 데이터 가공

🔹 Dashboard (CloudFront 이상 탐지용)

sec_cf_log 인덱스를 기반으로 비정상 IP 요청 급증 현상 시각화

index=sec_cf_log
| bin _time span=10m
| stats count by _time, ip
| where count >= 100
| timechart span=10m sum(count) by ip

사용 목적:

특정 IP의 과도한 요청 탐지

timechart를 통한 이상행위 추이 분석

🔄 데이터 흐름 요약

[S3 로그] 
   ↓
[Logstash (cf.conf)]
   ↓
[Elasticsearch] → [Kibana 확인]
   ↓
[Splunk (Config Explorer.py)] → [필터링 쿼리] → [sec_cf_log 인덱스 저장] → [Dashboard 탐지]
