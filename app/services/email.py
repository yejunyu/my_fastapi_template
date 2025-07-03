# app/services/email.py
import smtplib
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from loguru import logger

from app.core.config import settings


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        # 这里可以配置SMTP设置，目前先用日志模拟
        self.smtp_server = getattr(settings, "SMTP_SERVER", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 587)
        self.smtp_username = getattr(settings, "SMTP_USERNAME", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)

    def generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return "".join(random.choices(string.digits, k=6))

    async def send_verification_code(self, email: str, code: str) -> bool:
        """发送邮箱验证码"""
        subject = "邮箱验证码"
        body = f"""
        您的邮箱验证码是：{code}
        
        验证码有效期为10分钟，请及时使用。
        如果这不是您的操作，请忽略此邮件。
        """

        return await self._send_email(email, subject, body)

    async def send_password_reset_link(self, email: str, reset_token: str) -> bool:
        """发送密码重置链接"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        subject = "密码重置"
        body = f"""
        您请求重置密码。
        
        点击以下链接重置您的密码：
        {reset_url}
        
        此链接有效期为30分钟。
        如果这不是您的操作，请忽略此邮件。
        """

        return await self._send_email(email, subject, body)

    async def _send_email(self, to_email: str, subject: str, body: str) -> bool:
        """发送邮件（目前用日志模拟）"""
        try:
            # 目前用日志模拟邮件发送，实际项目中需要配置真实的SMTP
            logger.info(f"发送邮件到 {to_email}")
            logger.info(f"主题: {subject}")
            logger.info(f"内容: {body}")
            logger.info("=" * 50)

            # TODO: 实际的SMTP发送逻辑
            if self.smtp_server and self.smtp_username and self.smtp_password:
                # 实际的SMTP发送代码
                pass

            return True
        except Exception as e:
            logger.error(f"发送邮件失败: {e}")
            return False


# 创建全局实例
email_service = EmailService()
