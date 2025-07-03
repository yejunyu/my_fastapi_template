import subprocess
import sys


def main():
    if len(sys.argv) < 2:
        print("用法: python scripts/alembic_migrate.py <迁移描述>")
        sys.exit(1)
    msg = sys.argv[1]

    # 1. 生成迁移文件
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", msg], check=True)

    # 2. 执行升级
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    print("数据库迁移已完成")


if __name__ == "__main__":
    main()
