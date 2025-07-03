#!/usr/bin/env python3
"""
创建超级用户脚本
用法: python scripts/create_superuser.py
"""

import asyncio
import sys
from getpass import getpass

# 添加项目根目录到路径
sys.path.append(".")

from app.db.session import AsyncSessionFactory
from app.services.user_admin import user_admin_service
from app.core.password_validator import validate_password_strength
from loguru import logger


async def create_superuser():
    """交互式创建超级用户"""
    logger.info("=== 创建超级用户 ===")

    # 获取邮箱
    while True:
        email = input("请输入管理员邮箱: ").strip()
        if "@" in email and "." in email:
            break
        logger.error("请输入有效的邮箱地址")

    # 获取密码
    while True:
        password = getpass("请输入密码: ")
        confirm_password = getpass("请确认密码: ")

        if password != confirm_password:
            logger.error("两次输入的密码不一致，请重新输入")
            continue

        # 验证密码强度
        is_valid, errors = validate_password_strength(password)
        if not is_valid:
            logger.error(f"密码强度不足: {'; '.join(errors)}")
            continue

        break

    # 创建超级用户
    try:
        async with AsyncSessionFactory() as db:
            user = await user_admin_service.create_superuser(
                db, email=email, password=password
            )
            logger.success(f"超级用户创建成功！")
            logger.info(f"邮箱: {user.email}")
            logger.info(f"用户ID: {user.id}")

            # 显示用户统计
            stats = await user_admin_service.get_user_stats(db)
            logger.info(f"系统用户统计: {stats}")

    except Exception as e:
        logger.error(f"创建超级用户失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(create_superuser())
