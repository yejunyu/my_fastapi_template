# app/services/email_service.py
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Optional
import logging
from jinja2 import Environment, FileSystemLoader
import os

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)

# 创建Jinja2环境，用于邮件模板渲染
template_dir = os.path.join(os.path.dirname(__file__), "..", "templates", "email")
jinja_env = Environment(loader=FileSystemLoader(template_dir))


class EmailService:
    """邮件服务类"""

    def __init__(self):
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_username = settings.SMTP_USERNAME
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.from_name = settings.FROM_NAME

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> bool:
        """
        发送邮件的核心方法

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            html_content: HTML内容
            text_content: 纯文本内容（可选）

        Returns:
            bool: 发送是否成功
        """
        try:
            # 创建邮件消息
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # 添加纯文本部分
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # 添加HTML部分
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # 发送邮件
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=False,  # 因为使用465端口，直接SSL连接
                use_tls=True,
                username=self.smtp_username,
                password=self.smtp_password,
            )

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {to_email}, 错误: {str(e)}")
            return False

    def render_template(self, template_name: str, **kwargs) -> str:
        """
        渲染邮件模板

        Args:
            template_name: 模板文件名
            **kwargs: 模板变量

        Returns:
            str: 渲染后的HTML内容
        """
        try:
            template = jinja_env.get_template(template_name)
            return template.render(**kwargs)
        except Exception as e:
            logger.error(f"模板渲染失败: {template_name}, 错误: {str(e)}")
            return ""

    async def send_activation_email(
        self, to_email: str, username: str, activation_link: str
    ) -> bool:
        """
        发送账户激活邮件

        Args:
            to_email: 收件人邮箱
            username: 用户名
            activation_link: 激活链接

        Returns:
            bool: 发送是否成功
        """
        subject = "激活您的AI面试助手账户"

        html_content = self.render_template(
            "activation.html",
            username=username,
            activation_link=activation_link,
            app_name="AI面试助手",
        )

        text_content = f"""
        Hi {username},

        欢迎注册AI面试助手！

        请点击以下链接激活您的账户：
        {activation_link}

        此链接将在2小时后过期。

        如果您没有注册此账户，请忽略此邮件。

        AI面试助手团队
        """

        return await self.send_email(to_email, subject, html_content, text_content)

    async def send_password_reset_email(
        self, to_email: str, username: str, reset_link: str
    ) -> bool:
        """
        发送密码重置邮件

        Args:
            to_email: 收件人邮箱
            username: 用户名
            reset_link: 重置链接

        Returns:
            bool: 发送是否成功
        """
        subject = "重置您的AI面试助手密码"

        html_content = self.render_template(
            "password_reset.html",
            username=username,
            reset_link=reset_link,
            app_name="AI面试助手",
        )

        text_content = f"""
        Hi {username},

        您请求重置AI面试助手的密码。

        请点击以下链接设置新密码：
        {reset_link}

        此链接将在2小时后过期。

        如果您没有请求重置密码，请忽略此邮件。

        AI面试助手团队
        """

        return await self.send_email(to_email, subject, html_content, text_content)


# 创建全局邮件服务实例
email_service = EmailService()
