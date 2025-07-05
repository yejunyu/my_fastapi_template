# Prompt加载工具

这是一个简单的prompt文件读取工具，支持通过文件名快速加载和格式化prompt内容，使用Jinja2模板引擎。

## 功能特性

- ✅ 简单的文件名读取（无需扩展名）
- ✅ 自动支持多种文件格式（无扩展名、.txt、.md、.prompt）
- ✅ 支持Jinja2模板格式化（`{{variable}}`语法）
- ✅ 错误处理和日志记录
- ✅ 列出所有可用prompt文件

## 使用方法

### 1. 基本加载

```python
from app.utils import load_prompt

# 加载interview prompt
prompt_content = load_prompt("interview")
if prompt_content:
    print(prompt_content)
```

### 2. 参数格式化

```python
from app.utils import format_prompt

# 格式化prompt，替换模板中的参数
formatted_prompt = format_prompt(
    "interview",
    job_intention="Python后端开发工程师",
    resume_experience="3年Python开发经验，熟悉FastAPI、Django等框架"
)
```

### 3. 列出所有prompt文件

```python
from app.utils import list_prompts

# 获取所有可用的prompt文件名
available_prompts = list_prompts()
print(available_prompts)  # ['interview', 'ranking', 'resume_extract', 'score_weight']
```

### 4. 直接使用PromptLoader类

```python
from app.utils import PromptLoader

# 创建自定义实例
loader = PromptLoader(prompt_dir="custom/prompt/dir")

# 加载prompt
content = loader.load_prompt("my_prompt")
```

## 文件结构

```
app/
├── prompt/
│   ├── interview          # 面试prompt
│   ├── ranking           # 评分prompt
│   ├── resume_extract    # 简历提取prompt
│   └── score_weight      # 权重评分prompt
└── utils/
    ├── __init__.py
    ├── prompt_loader.py  # 工具实现
    └── README.md         # 本文档
```

## Prompt文件格式

prompt文件支持以下格式：

1. **纯文本文件**（推荐）：无扩展名
2. **Markdown文件**：.md扩展名
3. **文本文件**：.txt扩展名
4. **自定义格式**：.prompt扩展名

## 参数格式化

prompt文件使用Jinja2模板语法进行参数替换：

```
## Role: 
你是一位专业的AI面试官...

# Initialization
请根据以下面试者信息开始面试：

求职意向：{{job_intention}}
简历项目经验：{{resume_experience}}
```

使用时：

```python
formatted = format_prompt("interview", 
    job_intention="Python开发工程师",
    resume_experience="3年经验，熟悉Django"
)
```

## 错误处理

工具会自动处理以下错误情况：

- 文件不存在：返回None并记录错误日志
- 读取失败：返回None并记录错误日志
- 格式化参数缺失：返回原始内容并记录警告
- 格式化失败：返回原始内容并记录错误

## 示例

运行示例代码：

```bash
python examples/prompt_usage_example.py
```

这将展示工具的基本用法、格式化功能和错误处理。 