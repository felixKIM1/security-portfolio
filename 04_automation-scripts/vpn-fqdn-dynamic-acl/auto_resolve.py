import requests
import json
import yaml
import re
import socket
import base64
from datetime import datetime
import ipaddress
import os
from typing import Dict, List, Tuple, Optional

# 상수 정의
CONFIG_FILE_PATH = "/경로/config.yaml"
YAML_FILE_PATH = "/경로/yaml.yaml"

# YAML 파일 관련 함수들
def read_yaml() -> Dict:
    """기본 설정 파일(yaml.yaml)을 읽어오는 함수"""
    try:
        with open(YAML_FILE_PATH) as y:
            return yaml.safe_load(y)
    except Exception as e:
        print(f"Error reading yaml file: {e}")
        raise

def read_multi_document_yaml(file_path: str = CONFIG_FILE_PATH) -> Dict:
    """설정 파일(config.yaml)을 읽어오는 함수"""
    try:
        with open(file_path, "r") as file:
            documents = list(yaml.safe_load_all(file))
            return {k: v for doc in documents for k, v in doc.items()}
    except Exception as e:
        print(f"Error reading config file: {e}")
        raise

# 도메인 정보 처리 함수들
def get_acl_names(yaml_data: Dict) -> List[str]:
    """YAML 데이터에서 ACL 이름들을 추출"""
    try:
        acl_names = []
        for section in yaml_data.values():
            if isinstance(section, dict):
                acl_names.extend(section.keys())
        return sorted(list(set(acl_names)))
    except Exception as e:
        print(f"Error extracting ACL names: {e}")
        return []

def get_domain_list(config_data: Dict, target_acl_name: str) -> List[Tuple[str, str]]:
    domain_info = []
    try:
        for section in config_data.values():
            if isinstance(section, dict):
                # 특정 ACL 이름에 해당하는 도메인 리스트만 처리
                if target_acl_name in section:
                    for domain in section[target_acl_name]:
                        parts = domain.strip().split(':')
                        if len(parts) == 2:
                            domain_info.append((parts[0], parts[1]))
        return domain_info
    except Exception as e:
        print(f"Error in get_domain_list for {target_acl_name}: {e}")
        return []

# API 인증 관련 함수들
def get_api_key(config_data: Dict) -> requests.Response:
    """API 키 획득"""
    try:
        credentials = f"{config_data['USER_NAME']}:{config_data['USER_PASSWD']}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Basic {encoded_credentials}"
        }
        data = {"realm": "Admin Users"}

        return requests.post(
            config_data['API_KEY_URL'],
            headers=headers,
            json=data,
            verify=False
        )
    except Exception as e:
        print(f"Error getting API key: {e}")
        raise

def get_config_key(config_data: Dict, api_key: str) -> str:
    """설정 키 획득"""
    try:
        headers = {"Content-Type": "application/json"}
        auth = (api_key, "")

        response = requests.get(
            config_data['BASIC_KEY_URL'],
            auth=auth,
            headers=headers,
            verify=False
        )
        return response.request.headers.get("Authorization")
    except Exception as e:
        print(f"Error getting config key: {e}")
        raise

# ACL 리소스 관련 함수들
def get_resource_acl(basic_key: str, acl_name: str, yaml_data: Dict) -> Dict:
    """ACL 리소스 정보 조회"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": basic_key
        }
        response = requests.get(
            f"{yaml_data['ACL_KEY_URL']}/{acl_name}",
            headers=headers,
            verify=False
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error getting resource ACL: {e}")
        raise

# 로깅 관련 상수 추가
LOG_DIR = "/경로/Log"
FAILURE_LOG_FILE = "failure_logs.json"

def save_failure_log(acl_name: str, error_msg: str, status_code: int = None, additional_info: dict = None):
    try:
        # 로그 디렉토리 생성
        if not os.path.exists(LOG_DIR):
            os.makedirs(LOG_DIR)

        log_file_path = os.path.join(LOG_DIR, FAILURE_LOG_FILE)

        # 현재 로그 파일 읽기
        existing_logs = []
        if os.path.exists(log_file_path):
            with open(log_file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_logs = json.load(f)
                except json.JSONDecodeError:
                    existing_logs = []

        # 새 로그 엔트리 생성
        new_log_entry = {
            "timestamp": datetime.now().isoformat(),
            "acl_name": acl_name,
            "error_message": str(error_msg),
            "status_code": status_code
        }

        if additional_info:
            new_log_entry.update(additional_info)

        # 새 로그 추가
        existing_logs.append(new_log_entry)

        # 파일에 저장
        with open(log_file_path, 'w', encoding='utf-8') as f:
            json.dump(existing_logs, f, indent=2, ensure_ascii=False)

    except Exception as e:
        print(f"Error saving failure log: {e}")

def is_public_ip(ip_address: str) -> bool:
    try:
        ip = ipaddress.ip_address(ip_address)
        return not ip.is_private
    except ValueError:
        return False

def get_resource_sp(basic_key: str, sp_name: str, yaml_data: Dict) -> Dict:
    """SP 리소스 정보 조회"""
    try:
        headers = {
            "Content-Type": "application/json",
            "Authorization": basic_key
        }
        response = requests.get(
            f"{yaml_data['SP_KEY_URL']}/{sp_name}",
            headers=headers,
            verify=False
        )
        return json.loads(response.text)
    except Exception as e:
        print(f"Error getting resource SP: {e}")
        raise

def put_resource_sp(basic_key: str, sp_name: str, public_ips: List[str], public_domains: List[str], yaml_data: Dict) -> int:
    """SP 리소스 업데이트"""
    try:
        unique_domains = list(dict.fromkeys(public_domains))
        # SP 정책 조회
        sp_text = get_resource_sp(basic_key, sp_name, yaml_data)

        # **IP 주소가 아닌 도메인만 유지**
        filtered_unique_domains = [d for d in unique_domains if is_valid_domain(d.split(':')[0])]
        #print(f"filtered_unique_::::::{filtered_unique_domains}")
        # API 요청 데이터 준비
        data = {
            "action": sp_text['action'],
            "apply": sp_text['apply'],
            "description": sp_text['description'],
            "name": sp_text['name'],
            "resources": [public_ips],
            "resources-fqdn": [filtered_unique_domains],
            "resources-v6": sp_text['resources-v6'],
            "roles": sp_text['roles'],
            "rules": sp_text['rules']
        }

        # SP 정책 업데이트
        headers = {
            "Content-Type": "application/json",
            "Authorization": basic_key
        }

        response = requests.put(
            f"{yaml_data['SP_KEY_URL']}/{sp_name}",
            headers=headers,
            data=json.dumps(data),
            verify=False
        )

        return response.status_code

    except Exception as e:
        print(f"Error updating SP {sp_name}: {e}")
        return 500

def is_valid_domain(domain: str) -> bool:
    """입력값이 도메인 형식인지 확인 (IP가 아닌 경우 True 반환)"""
    try:
        # IP 주소인지 검사 (IP라면 False 반환)
        ipaddress.ip_address(domain)
        return False
    except ValueError:
        # 도메인이면 True 반환
        return True

# put_resource_acl 함수 수정
def put_resource_acl(basic_key: str, acl_name: str, config_data: Dict, yaml_data: Dict) -> int:
    """ACL 리소스 업데이트"""
    try:
        # ACL 정책 조회
        acl_text = get_resource_acl(basic_key, acl_name, yaml_data)
        all_domains = [] # 도메인 리스트
        all_ips = []  # 사설 IP 리스트
        public_ips = []   # 공인 IP 리스트
        public_domains = [] # 공인 domain 리스트트

        # 특정 ACL에 대한 도메인 목록만 가져오기
        domain_list = get_domain_list(config_data, acl_name)

        # 도메인별 IP 주소 수집
        dns_failures = []  # DNS 조회 실패 기록

        for domain, port in domain_list:
            try:
                addr_info = socket.getaddrinfo(domain, None, socket.AF_INET, socket.SOCK_STREAM)
                #print(f"addr_info::::::{addr_info}")
                for info in addr_info:
                    ip = info[4][0]
                    #print(f"ip:::::::{ip}")
                    # 공인/사설 IP 구분하여 저장
                    if is_public_ip(ip):
                        formatted_pub_ip = f"{ip}"
                        public_ips.append(formatted_pub_ip)
                        public_domains.append(domain)

                    formatted_ip = f"tcp://{ip}:{port}"
                    formatted_domain = f"{domain}:{port}"
                    #print(f"formatted_ip:::{formatted_ip}")
                    all_ips.append(formatted_ip)
                    #print(f"all_ips_append::::{all_ips}")
                all_domains.append(formatted_domain)

            except socket.gaierror as e:
                error_msg = f"DNS resolution failed for {domain}: {e}"
                print(error_msg)
                dns_failures.append({"domain": domain, "error": str(e)})

        # DNS 조회 실패가 있었다면 로깅
        if dns_failures:
            with open("/경로/dns_fail.txt", "a", encoding="utf-8") as f:
                f.write("\n=== DNS Resolution Failures ===\n")
                for failure in dns_failures:
                    f.write(f"{failure}\n")

            save_failure_log(
                acl_name,
                "DNS resolution failures",
                additional_info={"dns_failures": dns_failures}
            )

        response_codes = []  # API 응답 코드 저장 리스트
        #print(f"===================={all_ips}")

        # **IP 주소가 아닌 도메인만 유지**
        filtered_all_domains = [d for d in all_domains if is_valid_domain(d.split(':')[0])]

        # 사설 IP에 대한 ACL 정책 업데이트
        data = {
            "action": acl_text['action'],
            "apply": acl_text['apply'],
            "description": acl_text['description'],
            "name": acl_text['name'],
            "resource": [all_ips],
            "resources-fqdn": [filtered_all_domains],
            "resources-v6": acl_text['resources-v6'],
            "roles": acl_text['roles'],
            "rules": acl_text['rules']
        }

        acl_response = requests.put(
            f"{yaml_data['ACL_KEY_URL']}/{acl_name}",
            headers={"Content-Type": "application/json", "Authorization": basic_key},
            data=json.dumps(data),
            verify=False
        )
        response_codes.append(acl_response.status_code)

        # 공인 IP에 대한 SP 정책 업데이트
        if public_ips:
            # ACL 이름을 SP 이름으로 변환 (acl-* -> sp-*)
            sp_name = 'sp-' + acl_name[4:] if acl_name.startswith('acl-') else 'sp-' + acl_name

            # SP 정책 업데이트
            sp_response_code = put_resource_sp(basic_key, sp_name, public_ips, public_domains, yaml_data)
            response_codes.append(sp_response_code)

            # 공인 IP 로깅
            save_failure_log(
                sp_name,
                "Public IPs processed",
                additional_info={
                    "public_ips": public_ips,
                    "original_acl_name": acl_name
                }
            )

        # 응답 상태 확인 및 로깅
        if not all(code == 200 for code in response_codes):
            save_failure_log(
                acl_name,
                "Policy update partially failed",
                additional_info={
                    "acl_response": response_codes[0] if all_ips else None,
                    "sp_response": response_codes[-1] if public_ips else None
                }
            )

        # 모든 요청이 성공했을 때만 200 반환
        return 200 if all(code == 200 for code in response_codes) else 500

    except Exception as e:
        error_msg = f"Error updating policies for {acl_name}: {e}"
        save_failure_log(acl_name, error_msg)
        print(error_msg)
        return 500

def main():
    """메인 실행 함수"""
    try:
        print("Starting ACL update process...")

        # 설정 파일 로드
        config_data = read_multi_document_yaml()
        yaml_data = read_yaml()

        # API 인증
        api_key_response = get_api_key(yaml_data)
        api_key = re.findall(r"\"(.*?)\"", api_key_response.text)[1]
        basic_key = get_config_key(yaml_data, api_key)

        # ACL 이름 추출
        acl_names = get_acl_names(config_data)
        if not acl_names:
            print("Error: No ACL names found in config.yaml")
            return

        # ACL 업데이트 실행
        for acl_name in acl_names:
            print(f"Processing ACL: {acl_name}")
            status_code = put_resource_acl(basic_key, acl_name, config_data, yaml_data)
            print(f"Status: {'Success' if status_code == 200 else f'Failed ({status_code})'}")

    except Exception as e:
        print(f"Error in main execution: {e}")
        exit(1)

if __name__ == "__main__":
    main()

