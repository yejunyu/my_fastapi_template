# 响应格式统一化中间件

## 概述

响应格式统一化中间件自动将所有API响应包装为统一的格式：

```json
{
  "code": 0,
  "msg": "success", 
  "data": { /* 原始响应数据 */ }
}
```

## 特性

✅ **自动响应包装** - 无需修改现有代码  
✅ **异常处理** - 统一的错误响应格式  
✅ **路径跳过** - 可配置跳过特定路径  
✅ **特殊响应支持** - 文件下载、重定向等保持原样  
✅ **性能监控** - 自动添加请求处理时间  

## 响应格式说明

### 成功响应 (code: 0)
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "name": "示例数据"
  }
}
```

### 错误响应 (code: 非0)
```json
{
  "code": 400,
  "msg": "Bad request", 
  "data": null
}
```

### 验证错误响应
```json
{
  "code": 422,
  "msg": "body -> name: field required",
  "data": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

## 配置选项

### 基本配置
```python
app.add_middleware(
    ResponseWrapperMiddleware,
    success_code=0,           # 成功时的业务码
    success_msg="success",    # 成功时的消息
)
```

### 跳过路径配置
```python
app.add_middleware(
    ResponseWrapperMiddleware,
    skip_paths=["/", "/health"],                     # 跳过完整路径
    skip_prefixes=["/docs", "/static", "/openapi"], # 跳过路径前缀
)
```

## 支持的响应类型

### 1. 普通JSON响应 ✅ 会被包装
```python
@app.get("/users")
async def get_users():
    return {"users": [...]}
# 响应: {"code": 0, "msg": "success", "data": {"users": [...]}}
```

### 2. 列表响应 ✅ 会被包装
```python
@app.get("/items")
async def get_items():
    return [{"id": 1}, {"id": 2}]
# 响应: {"code": 0, "msg": "success", "data": [{"id": 1}, {"id": 2}]}
```

### 3. 文件下载 ❌ 不会被包装
```python
@app.get("/download")
async def download_file():
    return FileResponse("file.pdf")
# 响应: 直接返回文件内容
```

### 4. 重定向 ❌ 不会被包装
```python
@app.get("/redirect")
async def redirect():
    return RedirectResponse("/new-path")
# 响应: 302重定向
```

## 异常处理

所有异常都会被自动捕获并转换为统一格式：

### HTTP异常
```python
raise HTTPException(status_code=404, detail="User not found")
# 响应: {"code": 404, "msg": "User not found", "data": null}
```

### 验证错误
```python
# 请求体验证失败
# 响应: {"code": 422, "msg": "详细验证错误", "data": [...]}
```

### 未捕获异常
```python
raise ValueError("Something went wrong")
# 响应: {"code": 500, "msg": "Internal server error", "data": null}
```

## 演示端点

系统提供了演示端点来测试中间件功能：

```bash
# 成功响应
GET /api/v1/demo/success

# 错误响应
GET /api/v1/demo/error-400
GET /api/v1/demo/error-404
GET /api/v1/demo/error-500

# 验证错误
POST /api/v1/demo/validation-error
GET /api/v1/demo/query-validation?page=0  # 会触发验证错误

# 特殊响应（不被包装）
GET /api/v1/demo/file-download
GET /api/v1/demo/redirect
```

## 性能监控

每个响应会自动添加处理时间头：

```http
X-Process-Time: 0.00123456
```

## 最佳实践

### 1. 路径跳过配置
- 跳过文档路径：`/docs`, `/redoc`, `/openapi.json`
- 跳过静态文件：`/static`
- 跳过健康检查：`/health`

### 2. 业务码规范
```python
# 推荐的业务码规范
{
  "code": 0,     # 成功
  "code": 400,   # 客户端错误
  "code": 500,   # 服务器错误
  "code": 1001,  # 自定义业务错误
}
```

### 3. 错误处理
```python
# 业务逻辑中抛出HTTP异常
if not user:
    raise HTTPException(status_code=404, detail="用户不存在")
```

## 注意事项

1. **响应包装优先级**：异常处理器 > 中间件包装
2. **HTTP状态码**：所有响应统一返回200，业务状态通过`code`字段区分
3. **特殊响应**：文件下载、重定向等特殊响应不会被包装
4. **性能影响**：中间件会增加少量响应处理时间（通常<1ms）

## 常见问题

**Q: 如何跳过某个特定端点的包装？**  
A: 在中间件配置中添加该端点到`skip_paths`列表

**Q: 如何修改成功时的业务码？**  
A: 在中间件初始化时设置`success_code`参数

**Q: 文件下载接口被包装了怎么办？**  
A: 确保使用`FileResponse`类型，中间件会自动识别并跳过

**Q: 如何自定义错误消息？**  
A: 在抛出`HTTPException`时设置`detail`参数 