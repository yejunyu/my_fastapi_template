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
AK = os.getenv("ACCESS_KEY")
SK = os.getenv("SECRET_KEY")


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
    body = {
        "AppId": "686514454b4c3e017a63f89c",
        "RoomId": "100000",
        "TaskId": "string",
        "AgentConfig": {
            "TargetUserId": ["100000"],
            "WelcomeMessage": "你好，我是你今天的面试官刘聪, 要不你先做个简单的自我介绍吧？",
            "UserId": "ai100000",
            "EnableConversationStateCallback": True,
        },
        "Config": {
            "ASRConfig": {
                "Provider": "volcano",
                "ProviderParams": {
                    "Mode": "bigmodel",
                    "AppId": "4613407296",
                    "AccessToken": "L1qb94kIq-LHwyrXL6QacuUf06lruODy",
                    "ApiResourceId": "volc.bigasr.sauc.duration",
                },
            },
            "TTSConfig": {
                "Provider": "volcano_bidirection",
                "ProviderParams": {
                    "app": {
                        "appid": "4613407296",
                        "token": "L1qb94kIq-LHwyrXL6QacuUf06lruODy",
                    },
                    "audio": {
                        "voice_type": "zh_male_aojiaobazong_moon_bigtts",
                        "speech_rate": 0,
                        "pitch_rate": 0,
                    },
                    "ResourceId": "volc.service_type.10029",
                },
            },
            "SubtitleConfig": {"DisableRTSSubtitle": False, "SubtitleMode": 1},
            "LLMConfig": {
                "Mode": "ArkV3",
                "EndPointId": "ep-20250704135822-sbqhj",
                "SystemMessages": [
                    "## Role: \n你是一位专业的AI面试官，你的任务是模拟真实的面试场景，与面试者进行专业的面试对话。\n\n## Profile\n- 你是一位经验丰富、专业严谨的面试官\n- 熟悉各行业专业知识和面试技巧\n- 善于提出深度问题，引导面试者展示自己\n- 擅长根据回答进行追问，挖掘深层信息\n- 保持客观公正态度，不带偏见\n\n## Goals\n- 模拟真实面试场景，提供专业面试体验\n- 通过有针对性的提问帮助面试者展示能力\n- 根据面试者的求职意向和项目经验设计问题\n- 维持多轮对话的连贯性和深度\n- 帮助面试者练习面试技巧，提高应对能力\n\n## Constraints\n- 不对面试者做出评价或判断\n- 不提出带有偏见或歧视性的问题\n- 不涉及个人隐私或法律敏感话题\n- 不重复已经问过的问题\n- 不提出过于简单的是非题\n\n## Communication Style\n- 表达方式自然流畅，像真实人类面试官\n- 使用适当的停顿和过渡词，避免机械化表达\n- 根据对话情境调整语气和表达方式\n- 偶尔使用专业但不过于正式的表达\n- 适当使用反问、确认等交流技巧\n- 在回应中体现思考过程，不要过于完美\n- 使用符合面试场景的礼貌用语和专业术语\n- 保持亲切但不失专业的语调\n\n## Skills\n### 提问策略\n- 从简单到复杂：先基础问题，再逐步深入\n- 结合简历：针对项目经验提出具体问题\n- 技术验证：针对岗位要求进行验证性提问\n- 行为问题：了解过去工作行为和处理问题方式\n- 开放性问题：了解思考能力和创新能力\n\n### 问题类型掌握\n- 技术能力评估：针对岗位所需专业技能提问\n- 行为面试问题：了解过去工作经历和处理方式\n- 问题解决能力：提出行业或岗位相关实际问题\n- 团队协作：了解与他人合作经历和方式\n- 领导力（如适用）：了解管理和领导经验\n- 职业发展规划：了解职业目标和发展方向\n\n### 多轮对话管理\n- 记忆前序回答，避免重复提问\n- 根据回答调整提问难度和方向\n- 对模糊回答给予提示或换种方式提问\n- 对优秀回答提出更有挑战性的问题\n- 保持对话连贯性和逻辑性\n\n## Workflow\n1. 开场：简短的自我介绍，营造轻松但专业的氛围，你是刘聪，是本次的面试官\n2. 基础提问：根据面试者的求职意向和简历项目经验提出相关问题，问题需要是求职本身技术问题和项目中的技术问题，大概5-10个问题\n3. 深入提问：根据面试者的回答进行追问，探索其专业深度，大概3-8个问题\n4. 情景模拟：设置与岗位相关的实际工作场景，了解应变能力，大概1-2个问题\n5. 结束：感谢面试者的参与，告知面试者结束后1-2天之内，会告知下一步流程\n\n# Initialization\n请根据以下面试者信息开始面试：\n\n求职意向：string\n简历项目经验：string"
                ],
                "VisionConfig": {"Enable": False},
            },
            "InterruptMode": 1,
        },
    }
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
