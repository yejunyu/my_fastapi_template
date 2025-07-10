# --- Build Stage ---
FROM python:3.13-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 安装构建依赖，例如gcc (如果您的Python包需要编译)
# 如果您发现某些包（如psycopg-binary, cryptography, lxml等）需要C编译器，请取消注释下一行
# RUN apt-get update && apt-get install -y --no-install-recommends gcc build-essential

# 安装 uv
RUN pip install --no-cache-dir -i https://pypi.tuna.tsinghua.edu.cn/simple uv

COPY requirements.txt ./

# 用 uv 安装依赖到虚拟环境或指定目录
# 使用 --target 参数将包安装到特定目录，而不是系统site-packages
RUN uv pip install --prefix /install --system -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# --- Runtime Stage ---
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app


# 从构建阶段复制安装好的依赖
COPY --from=builder /install /usr/local
# 或者 COPY --from=builder /install /app/venv # 如果安装到虚拟环境

# 复制应用代码
COPY . .

# 复制并设置启动脚本权限
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0", "--port", "8000"]