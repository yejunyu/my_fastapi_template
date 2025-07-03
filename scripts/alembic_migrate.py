import subprocess
import sys
from loguru import logger


def main():
    if len(sys.argv) < 2:
        logger.error("用法: python scripts/alembic_migrate.py <迁移描述>")
        sys.exit(1)
    msg = sys.argv[1]

    # 1. 生成迁移文件
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", msg], check=True)

    # 2. 执行升级
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    logger.success("数据库迁移已完成")


if __name__ == "__main__":
    main()
