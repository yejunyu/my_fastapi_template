# app/services/email.py
import random
import string
from loguru import logger
import asyncio
from email.mime.text import MIMEText
import aiosmtplib
import ssl  # 保持导入，以防需要自定义 SSL Context
from app.core.config import settings


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        # 从设置中获取SMTP配置
        self.smtp_server = getattr(settings, "SMTP_SERVER", None)
        self.smtp_port = getattr(settings, "SMTP_PORT", 465)  # 默认使用465端口
        self.smtp_username = getattr(settings, "SMTP_USERNAME", None)
        self.smtp_password = getattr(settings, "SMTP_PASSWORD", None)
        self.sender_email = self.smtp_username  # 通常发件人就是SMTP用户名

    def generate_verification_code(self) -> str:
        """生成6位数字验证码"""
        return "".join(random.choices(string.digits, k=6))

    async def send_verification_code(self, email: str, code: str) -> bool:
        """发送邮箱验证码"""
        subject = "您的验证码：[重要] - 请勿分享"
        body = f"""
        <html>
        <body>
            <p>尊敬的用户，</p>
            <p>您的邮箱验证码是：<strong>{code}</strong></p>
            <p>此验证码有效期为<strong>10分钟</strong>，请及时使用。请勿将此验证码分享给任何人。</p>
            <p>如果这不是您本人的操作，请立即忽略此邮件并联系客服。</p>
            <br>
            <p>祝您使用愉快！</p>
            <p>此致，</p>
            <p>您的应用团队</p>
        </body>
        </html>
        """
        return await self._send_email(email, subject, body, is_html=True)

    async def send_password_reset_link(self, email: str, reset_token: str) -> bool:
        """发送密码重置链接"""
        reset_url = f"{settings.FRONTEND_URL}/reset-password?token={reset_token}"
        subject = "密码重置请求 - 重要通知"
        body = f"""
        <html>
        <body>
            <p>尊敬的用户，</p>
            <p>我们收到一个请求，要求重置与此邮箱关联的账户密码。</p>
            <p>请点击以下链接重置您的密码：</p>
            <p><a href="{reset_url}">点击此处重置密码</a></p>
            <p>此链接有效期为<strong>30分钟</strong>，请尽快使用。</p>
            <p><strong>请注意：</strong>如果您没有请求重置密码，请忽略此邮件，您的密码将保持不变。请勿将此链接分享给任何人。</p>
            <br>
            <p>感谢您的理解与支持！</p>
            <p>此致，</p>
            <p>您的应用团队</p>
        </body>
        </html>
        """
        return await self._send_email(email, subject, body, is_html=True)

    async def _send_email(
        self, to_email: str, subject: str, body: str, is_html: bool = False
    ) -> bool:
        """
        异步发送邮件的内部方法。
        使用 aiosmtplib 实现实际的SMTP邮件发送，针对腾讯企业邮箱465端口配置。
        """
        if not self.smtp_server or not self.smtp_username or not self.smtp_password:
            logger.error(
                "SMTP配置不完整，无法发送邮件。请检查 SMTP_SERVER, SMTP_USERNAME, SMTP_PASSWORD。"
            )
            return False

        msg = MIMEText(body, "html" if is_html else "plain", "utf-8")
        msg["From"] = self.sender_email
        msg["To"] = to_email
        msg["Subject"] = subject

        # 创建默认的 SSLContext，这是推荐的做法
        ssl_context = ssl.create_default_context()
        # 如果遇到证书验证问题，可以尝试禁用证书验证（不推荐在生产环境使用）
        # ssl_context.check_hostname = False
        # ssl_context.verify_mode = ssl.CERT_NONE

        try:
            logger.info(
                f"尝试通过SMTP发送邮件到 {to_email} (服务器: {self.smtp_server}:{self.smtp_port})"
            )

            # 核心：针对465端口，直接设置 use_tls=True，aiosmtplib 会建立隐式SSL连接
            # 不再需要手动调用 starttls()
            smtp_client = aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.smtp_port,
                use_tls=True,  # 让 aiosmtplib 自动处理隐式 TLS 协商
                tls_context=ssl_context,  # 传入自定义的 SSL Context
            )

            await smtp_client.connect()
            # 移除 await smtp_client.starttls()，因为端口465已经处理了TLS

            await smtp_client.login(self.smtp_username, self.smtp_password)
            await smtp_client.send_message(msg)
            await smtp_client.quit()

            logger.info(f"邮件成功发送到 {to_email}。")
            return True

        except aiosmtplib.SMTPException as e:
            logger.error(f"SMTP邮件发送失败到 {to_email}: {e}", exc_info=True)
            return False
        except ssl.SSLError as e:
            logger.error(f"SSL/TLS 连接错误到 {to_email}: {e}", exc_info=True)
            return False
        except Exception as e:
            logger.error(f"发送邮件过程中发生未知错误到 {to_email}: {e}", exc_info=True)
            return False
        finally:
            logger.info("=" * 50)  # 日志分隔符


# 创建全局实例
email_service = EmailService()


# --- 示例用法 ---
async def main():
    # 替换为你可以接收邮件的真实邮箱
    # 并确保在Settings中配置了正确的腾讯企业邮箱SMTP信息
    test_email_verification = "liuxing_yue@126.com"
    verification_code = email_service.generate_verification_code()
    print(f"生成的验证码: {verification_code}")
    success_verification = await email_service.send_verification_code(
        test_email_verification, verification_code
    )
    print(f"验证码邮件发送结果到 {test_email_verification}: {success_verification}")

    print("\n" + "=" * 70 + "\n")

    test_email_reset = "another_email@example.com"  # 替换为另一个真实邮箱
    reset_token = "some_random_secure_token_12345"
    success_reset = await email_service.send_password_reset_link(
        test_email_reset, reset_token
    )
    print(f"密码重置邮件发送结果到 {test_email_reset}: {success_reset}")


if __name__ == "__main__":
    asyncio.run(main())
