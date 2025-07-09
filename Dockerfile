# 1. 使用官方的 Python 3.13 slim 版本作为基础镜像
FROM python:3.13-slim

# 2. 设置环境变量
#    - PYTHONDONTWRITEBYTECODE: 防止 Python 写入 .pyc 文件
#    - PYTHONUNBUFFERED: 确保容器日志直接输出，不被缓冲
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. 设置工作目录
WORKDIR /app

# 4. 更新包管理器并安装系统依赖 (如果需要)
# RUN apt-get update && apt-get install -y --no-install-recommends gcc

# 5. 安装 Python 依赖
#    首先复制 requirements.txt，以便利用 Docker 的层缓存机制
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 6. 复制应用代码到工作目录
COPY . .

# 7. 暴露应用运行的端口
EXPOSE 8000

# 8. 定义容器启动时运行的命令
#    使用 uvicorn 启动 FastAPI 应用
#    --host 0.0.0.0 使其可以从容器外部访问
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 