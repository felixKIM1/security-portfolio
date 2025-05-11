# 🛠️ 대상지 IP 변경을 자동 반영하는 VPN 장비 스크립트 
- **FQDN 이슈와 LB와 같이 IP가 변경되는 대상지**에 대해 IP를 자동으로 변경하는 스크립트 작성 

## 📝 개요
VPN에서 FQDN 기반 접근 제어 정책을 설정할 경우,  
제조사에서는 문제없다는 답변을 받았지만 접속 지연 현상이 발생하는 것으로 확인됐습니다.

이 스크립트는 해당 문제들을 자동으로 대응하기 위해 작성되었습니다.
**nslookup을 통해 IP를 동적으로 조회하여 ACL과 Routing Table을 갱신**합니다.

---

## 🔧 구성 요소
auto_resolve.py #메인 자동화 스크립트
config.yaml #대상 도메인 및 포트 정의 (멀티 YAML 형식)
yaml.yaml #계정 및 API URL 등 인증/환경 정보
failure_logs.json #정책 업데이트 실패 or DNS 실패 시 기록되는 자동 생성 로그 파일
dns_fail.txt #도메인 → IP 변환 실패 시 DNS 실패 내역을 텍스트로 기록 (디버깅용)

---

## 🔐 인증 흐름

1. `yaml.yaml` 파일에서 `username:password` 조합 → Base64 인코딩
2. 인증 요청 URL(API_KEY_URL)에 POST → API 키 발급
3. 해당 키를 사용하여 BASIC 키 획득 → 모든 정책 요청 시 헤더에 포함

---

## 🔁 작동 순서 요약

1. `config.yaml` → 도메인 및 포트 정보 로드 (멀티 문서 YAML)
2. 각 도메인에 대해 `socket.getaddrinfo()`로 IP 목록 수집
3. 사설 IP / 공인 IP / 도메인 주소 분리 및 정리
4. ACL 정책 업데이트 (`PUT /acl/...`)
5. 공인 IP가 존재할 경우 → SP 정책도 함께 업데이트 (`PUT /sp/...`)
6. 모든 실패 내역은 `failure_logs.json` 및 `dns_fail.txt`에 기록

---
