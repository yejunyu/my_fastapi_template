import base64
import struct
import json


def unpack_subtitle_message(encoded_msg: str) -> dict:
    """
    解码经过特定二进制格式封装的字幕消息。

    这个函数是 Go Unpack 函数的 Python 实现。
    它执行以下操作：
    1. Base64 解码输入字符串。
    2. 校验 "subv" 协议头。
    3. 解析数据体长度。
    4. 校验总长度。
    5. 将数据体解析为 JSON (Python 字典)。

    Args:
        encoded_msg: 经过 Base64 编码的二进制消息。

    Returns:
        一个包含字幕数据的字典。

    Raises:
        ValueError: 如果消息格式无效（如长度、协议头或大小不匹配）。
        json.JSONDecodeError: 如果 JSON 数据本身格式错误。
        base64.binascii.Error: 如果 Base64 字符串无效。
    """
    # 1. Base64 解码
    try:
        binary_data = base64.b64decode(encoded_msg)
    except base64.binascii.Error as e:
        raise ValueError(f"Base64 解码失败: {e}")

    # 校验最小长度 (header 4 bytes + size 4 bytes)
    if len(binary_data) < 8:
        raise ValueError("数据无效：总长度不足8字节")

    # 2. 读取并校验协议头
    header = binary_data[:4]
    if header != b"subv":  # 在 Python 中，二进制数据与 bytes 对象进行比较
        # raise ValueError(f"协议头不匹配：期望 b'subv'，实际为 {header}")
        # print(f"协议头不匹配：期望 b'subv'，实际为 {header}")
        return {}
    # 3. 读取数据长度 (大端序, 4字节无符号整数)
    #    struct.unpack 返回一个元组，所以我们取第一个元素 [0]
    data_size_tuple = struct.unpack(">I", binary_data[4:8])
    data_size = data_size_tuple[0]

    # 4. 校验总长度
    if data_size + 8 != len(binary_data):
        raise ValueError(f"大小不匹配：声明的数据长度为 {data_size}，但实际不符")

    # 5. 提取并解析 JSON 数据
    json_payload_bytes = binary_data[8:]
    subtitle_data = json.loads(json_payload_bytes.decode("utf-8"))

    return subtitle_data


# --- 主程序示例 ---
def generate_test_message() -> str:
    """辅助函数：创建一个有效的测试消息并进行编码"""
    # 构造一个符合 Subv 结构的 Python 字典
    payload = {
        "type": "final_paragraph",
        "data": [
            {
                "definite": True,
                "paragraph": True,
                "language": "zh-CN",
                "sequence": 101,
                "text": "你好，这是一个测试。",
                "userId": "user-001",
            }
        ],
    }

    # 将字典转为 JSON 字符串，再编码为 bytes
    json_payload_bytes = json.dumps(payload, ensure_ascii=False).encode("utf-8")

    # 获取 JSON 数据长度
    data_size = len(json_payload_bytes)

    # 按照 "header (4) + size (4) + data" 的格式构建二进制消息
    # '>I' 表示 Big-Endian Unsigned Integer
    binary_message = b"subv" + struct.pack(">I", data_size) + json_payload_bytes

    # 对整个二进制消息进行 Base64 编码
    encoded_string = base64.b64encode(binary_message).decode("ascii")

    return encoded_string


if __name__ == "__main__":
    # 1. 生成一个用于测试的、格式正确的编码后消息
    test_message = generate_test_message()
    print(f"生成的测试消息 (Base64): {test_message}\n")

    # 2. 调用解码函数进行解码
    try:
        test_message = "c3VidgAAASh7CgkiZGF0YSIgOiAKCVsKCQl7CgkJCSJkZWZpbml0ZSIgOiB0cnVlLAoJCQkibGFuZ3VhZ2UiIDogIiIsCgkJCSJtb2RlIiA6IDAsCgkJCSJwYXJhZ3JhcGgiIDogZmFsc2UsCgkJCSJyb3VuZElkIiA6IDEsCgkJCSJzZXF1ZW5jZSIgOiAyLAoJCQkidGV4dCIgOiAiXHU0ZjYwXHU1MTQ4XHU3ODZlXHU4YmE0XHU1OTdkXHU3NmY4XHU1MTczXHU0ZmUxXHU2MDZmXHUzMDAyIiwKCQkJInRpbWVzdGFtcCIgOiAxNzUxOTc2MDk2Njc4LAoJCQkidXNlcklkIiA6ICJhaTIiCgkJfQoJXSwKCSJ0eXBlIiA6ICJzdWJ0aXRsZSIKfQ=="
        unpacked_data = unpack_subtitle_message(test_message)
        print("解码成功!")
        # 使用 json.dumps 美化打印输出
        print(json.dumps(unpacked_data, indent=2, ensure_ascii=False))
    except ValueError as e:
        print(f"解码失败: {e}")

    # --- 错误处理示例 ---
    # print("\n--- 测试无效的协议头 ---")
    # try:
    #     # 创建一个 header 错误的 base64 字符串
    #     invalid_header_message = base64.b64encode(
    #         b"oops" + b"\x00\x00\x00\x05" + b"hello"
    #     ).decode("ascii")
    #     unpack_subtitle_message(invalid_header_message)
    # except ValueError as e:
    #     print(f"捕获到预期的错误: {e}")
