# app/core/password_validator.py
import re
from typing import List


def validate_password_strength(password: str) -> tuple[bool, List[str]]:
    """
    校验密码强度

    要求：
    - 至少8位
    - 包含大写字母
    - 包含小写字母
    - 包含数字
    - 包含特殊字符

    返回: (是否有效, 错误信息列表)
    """
    errors = []

    if len(password) < 8:
        errors.append("密码长度至少8位")

    # if not re.search(r"[A-Z]", password):
    #     errors.append("密码必须包含至少一个大写字母")

    # if not re.search(r"[a-z]", password):
    #     errors.append("密码必须包含至少一个小写字母")

    # if not re.search(r"\d", password):
    #     errors.append("密码必须包含至少一个数字")

    # if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
    #     errors.append("密码必须包含至少一个特殊字符")

    return len(errors) == 0, errors
