[문제 개요]

업무 중 VPN을 통해 특정 서버에 접속해야 했으나, 도메인 입력 시 "도메인을 찾을 수 없음"이라는 메시지가 출력되며 접속이 불가능한 문제가 발생했다.
같은 VPN 네트워크를 사용하는 신청자는 정상적으로 접속이 가능했지만, 나는 접속할 수 없었고, 다른 일부 사용자들도 동일한 현상을 겪고 있었다.

[초기 분석]

1. DNS 서버 문제를 의심하여 nslookup으로 도메인 조회 결과 확인 → 응답 없음
2. 신청자 또한 nslookup으로 도메인 조회 시 응답을 받지 못함
3. 그러나 신청자는 해당 도메인으로 정상 접속이 가능함

이상하다고 판단하여 신청자의 PC에서 hosts 파일을 확인한 결과, 해당 도메인과 IP가 직접 매핑되어 있었다.

[문제 원인]

신청자의 hosts 파일에는 다음과 같이 도메인과 IP가 직접 설정되어 있었다.

예시:
10.10.10.123 myserver.internal.local

이는 DNS 서버를 거치지 않고도 해당 도메인에 접근 가능하도록 설정한 것이다.

반면 나는 hosts 파일에 해당 도메인 설정이 없었기 때문에, DNS를 통해 도메인을 조회하려 했고, DNS 응답이 없자 접속에 실패한 것이다.


[1차 조치]

문제를 해결하기 위해 내 PC의 hosts 파일에 해당 도메인과 IP를 추가하였다.

hosts 파일 경로 (Windows):
C:\Windows\System32\drivers\etc\hosts

예시 추가 내용:
10.10.10.123 myserver.internal.local

하지만 추가 후에도 접속이 되지 않았다.


[2차 점검]

1. VPN 설정 점검
   - VPN ACL 및 Route Table 확인 → 정상

2. AWS 구성 점검
   - 대상 서버가 AWS 환경이라, NACL, Security Group, Route Table 등 점검 → 문제 없음

3. 클라이언트 측 점검
   - curl 명령어로 해당 도메인 접속 시 여전히 "도메인을 찾을 수 없음" 오류 발생
   - ipconfig /displaydns 명령어로 DNS 캐시 확인 결과, 추가한 도메인이 반영되지 않음

   원인: hosts 파일이 올바르게 저장되지 않았음


[최종 해결]

- hosts 파일을 관리자 권한으로 열고 정확한 형식으로 저장
- 저장 후 ipconfig /flushdns로 DNS 캐시 초기화
- 다시 접속 시 정상적으로 도메인 인식 및 접속 가능


[인사이트]

- 도메인 조회 순서: hosts 파일 -> 로컬 DNS 캐시 -> DNS 서버
- DNS 이슈 발생 시, hosts 파일 우선순위를 반드시 확인할 것
- hosts 파일은 반드시 정확한 형식과 관리자 권한으로 저장해야 정상 반영됨
- displaydns 명령어는 DNS 캐시 상태 확인에 매우 유용함
