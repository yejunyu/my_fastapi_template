# app/models/__init__.py
# 这个文件是为了让 Alembic 能够发现所有的模型
# 确保你创建的每个模型都在这里被导入

from app.db.session import engine  # 虽然未使用，但保留它以备将来使用或明确表示引擎来源
from app.models.base import Base

# 导入所有你希望 Alembic 管理的模型
from app.models.user import User, UserStatus
from app.models.todo import Todo
from app.models.email_verification import EmailVerificationCode
from app.models.password_reset import PasswordReset
from app.models.user_file import UserFile
from app.models.base import BaseModel
from app.models.interview import Interview, Order
from app.models.product import Product

# 导出 Base 供 Alembic 使用
__all__ = [
    "Base",
    "User",
    "UserStatus",
    "Todo",
    "EmailVerificationCode",
    "PasswordReset",
    "BaseModel",
    "UserFile",
    "Interview",
    "Order",
    "Product",
]
