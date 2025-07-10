# AI-Interview

## 本地部署

### 1. 配置环境

首先，复制环境文件模板，并根据你的本地环境或从你的云服务提供商那里获取的凭证填写其中的值。

```bash
cp .env_template .env
```

### 2. 安装依赖

本项目使用 `uv` 进行包管理。如果你尚未安装 `uv`，请先安装它：

```bash
pip install uv
```

然后，使用 `uv sync` 来安装 `pyproject.toml` 中锁定的所有依赖项：

```bash
uv sync
```

### 3. 运行数据库迁移

在首次启动应用或数据库模型有任何变更后，你需要运行数据库迁移来创建或更新数据表。

```bash
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### 4. 启动应用

一切准备就绪后，使用 `uvicorn` 来启动 FastAPI 应用。

```bash
uvicorn app.main:app --reload
```

应用将在 `http://127.0.0.1:8000` 上运行。