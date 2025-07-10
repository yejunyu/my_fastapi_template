#!/bin/bash
set -e

echo "=== Starting AI Interview Application ==="

# 1. 等待远程 PostgreSQL 数据库可用
echo "Waiting for PostgreSQL to be ready..."
# while ! pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER"; do
#   echo "PostgreSQL is unavailable - sleeping"
#   sleep 1
# done
echo "PostgreSQL is up - executing commands"

# 2. 执行 Alembic 迁移
echo "Running Alembic migrations..."
if [ -f "scripts/alembic_migrate.py" ]; then
    python scripts/alembic_migrate.py "init"
else
    # 如果没有自定义脚本，直接用 alembic 命令
    alembic upgrade head
fi

# 3. 执行 SQL 初始化（如果文件存在）
# if [ -f "scripts/sql/init.sql" ]; then
#     echo "Running SQL init script..."
#     PGPASSWORD=$POSTGRES_PASSWORD psql -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB" -f scripts/sql/init.sql
# else
#     echo "No init.sql found, skipping SQL initialization"
# fi

# 4. 启动主应用
echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 