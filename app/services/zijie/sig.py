import datetime
import hashlib
import hmac
import os
from urllib.parse import quote
import httpx
import json

from dotenv import load_dotenv

load_dotenv()

# 以下参数视服务不同而不同，一个服务内通常是一致的
Service = "rtc"
Version = "2024-12-01"
Region = "cn-beijing"
Host = "rtc.volcengineapi.com"
ContentType = "application/json"  # 使用JSON格式

# 请求的凭证
AK = os.getenv("HUOSHAN_ACCESS_KEY")
SK = os.getenv("HUOSHAN_SECRET_KEY")


# 辅助函数: sha256 HMAC加密
def hmac_sha256(key: bytes, content: str):
    return hmac.new(key, content.encode("utf-8"), hashlib.sha256).digest()


# 辅助函数: sha256 hash
def hash_sha256(content: str):
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


# 查询参数的正规化
def norm_query(params):
    query = ""
    for key in sorted(params.keys()):
        query += f"{quote(key, safe='-_.~')}={quote(str(params[key]), safe='-_.~')}&"
    return query.rstrip("&")


# 正规化请求头
def get_canonical_headers(headers):
    signed_headers_str = ";".join(sorted([k.lower() for k in headers.keys()]))
    canonical_headers_str = "\n".join(
        [f"{k.lower()}:{v.strip()}" for k, v in sorted(headers.items())]
    )
    return signed_headers_str, canonical_headers_str


# 正规化请求体
def get_body_sha(body):
    return hash_sha256(body)


# 构建并发送请求
def request_rtc_api(action: str, body: dict):
    now = datetime.datetime.now(datetime.UTC)
    x_date = now.strftime("%Y%m%dT%H%M%SZ")
    short_x_date = x_date[:8]

    # 请求体 (Body)

    body_json = json.dumps(body)
    body_sha256 = get_body_sha(body_json)

    # 请求头
    headers = {
        "Content-Type": ContentType,
        "Host": Host,
        "X-Date": x_date,
        "X-Content-Sha256": body_sha256,
    }

    # 查询参数
    query = {
        "Version": Version,
        "Action": action,
    }

    # 获取规范化的请求头和签名
    signed_headers_str, canonical_headers_str = get_canonical_headers(headers)

    # 计算签名
    canonical_request_str = "\n".join(
        [
            "POST",
            "/",
            norm_query(query),
            canonical_headers_str + "\n",
            signed_headers_str,
            body_sha256,
        ]
    )

    hashed_canonical_request = hash_sha256(canonical_request_str)
    credential_scope = f"{short_x_date}/{Region}/{Service}/request"
    string_to_sign = "\n".join(
        ["HMAC-SHA256", x_date, credential_scope, hashed_canonical_request]
    )

    # 计算最终签名
    k_date = hmac_sha256(SK.encode("utf-8"), short_x_date)
    k_region = hmac_sha256(k_date, Region)
    k_service = hmac_sha256(k_region, Service)
    k_signing = hmac_sha256(k_service, "request")
    signature = hmac_sha256(k_signing, string_to_sign).hex()

    # Authorization头部
    authorization = f"HMAC-SHA256 Credential={AK}/{credential_scope}, SignedHeaders={signed_headers_str}, Signature={signature}"
    headers["Authorization"] = authorization

    # 发送POST请求
    response = httpx.post(
        url=f"https://{Host}/", headers=headers, params=query, data=body_json
    )

    print(response.text)
    return response.json()


def start_voice_chat(body: dict):
    response = request_rtc_api("StartVoiceChat", body)
    return response


def stop_voice_chat(body: dict):
    body = {
        "AppId": "686514454b4c3e017a63f89c",
        "RoomId": "100000",
        "TaskId": "string",
    }
    response = request_rtc_api("StopVoiceChat", body)
    return response


if __name__ == "__main__":
    # response = request_rtc_api()
    # print(response)
    response = stop_voice_chat({})
    print(response)
