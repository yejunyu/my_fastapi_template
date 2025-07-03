# 用户认证与账户管理 API 文档

## 概述

本系统提供基于邮箱验证码的用户注册和密码重置功能，支持安全的用户认证。

## API 接口

### 1. 发送验证码

**POST** `/api/v1/users/send-verification-code`

发送6位数字验证码到指定邮箱，用于注册验证。

**请求体：**
```json
{
  "email": "user@example.com"
}
```

**限制：**
- 同一邮箱60秒内只能发送一次
- 验证码有效期10分钟

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "msg": "验证码已发送至您的邮箱，请注意查收"
  }
}
```

### 2. 用户注册

**POST** `/api/v1/users/register`

使用邮箱、密码和验证码完成用户注册。

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!",
  "verification_code": "123456"
}
```

**密码要求：**
- 至少8位
- 包含大写字母
- 包含小写字母
- 包含数字
- 包含特殊字符

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "status": "active",
    "is_superuser": false
  }
}
```

### 3. 用户登录

**POST** `/api/v1/users/login`

使用邮箱和密码登录。

**请求体：**
```json
{
  "email": "user@example.com",
  "password": "SecurePassword123!"
}
```

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer"
  }
}
```

### 4. 忘记密码

**POST** `/api/v1/users/forgot-password`

发送密码重置链接到用户邮箱。

**请求体：**
```json
{
  "email": "user@example.com"
}
```

**限制：**
- 同一邮箱5分钟内只能发送一次

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "msg": "密码重置邮件已发送至您的邮箱，请注意查收"
  }
}
```

### 5. 重置密码

**POST** `/api/v1/users/reset-password`

使用重置token设置新密码。

**请求体：**
```json
{
  "token": "reset_token_from_email",
  "new_password": "NewSecurePassword123!"
}
```

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "msg": "密码修改成功，请使用新密码登录"
  }
}
```

### 6. 获取当前用户信息

**GET** `/api/v1/users/me`

获取当前登录用户的信息。

**请求头：**
```
Authorization: Bearer <access_token>
```

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "email": "user@example.com",
    "status": "active",
    "is_superuser": false
  }
}
```

### 7. 更新用户信息

**PUT** `/api/v1/users/me`

更新当前用户的信息。

**请求头：**
```
Authorization: Bearer <access_token>
```

**请求体：**
```json
{
  "email": "newemail@example.com",
  "password": "NewPassword123!"
}
```

**响应：**
```json
{
  "code": 0,
  "msg": "success",
  "data": {
    "id": 1,
    "email": "newemail@example.com",
    "status": "active",
    "is_superuser": false
  }
}
```

## 错误处理

所有接口使用统一的错误响应格式：

```json
{
  "code": 400,
  "msg": "错误描述",
  "data": null
}
```

### 常见错误码

- `400` - 请求参数错误
- `401` - 认证失败
- `404` - 资源不存在
- `422` - 数据验证错误
- `429` - 请求过于频繁
- `500` - 服务器内部错误

## 认证流程

### 注册流程

1. 调用发送验证码接口
2. 用户收到邮箱验证码
3. 使用邮箱、密码、验证码完成注册
4. 注册成功，用户状态为已激活

### 登录流程

1. 使用邮箱和密码登录
2. 获取访问令牌
3. 在后续请求中携带令牌

### 密码重置流程

1. 调用忘记密码接口
2. 用户收到重置链接邮件
3. 点击链接，使用token重置密码
4. 重置成功，使用新密码登录

## 安全特性

- **密码强度校验**：确保密码符合安全要求
- **频率限制**：防止验证码和重置邮件滥用
- **Token有效期**：访问令牌8天有效期
- **一次性使用**：验证码和重置token使用后立即失效
- **用户状态管理**：支持用户激活/禁用状态

## 扩展性设计

系统采用策略模式设计认证框架，当前支持邮箱密码认证，未来可轻松扩展：

- 手机验证码登录
- 第三方OAuth登录（Google、GitHub等）
- 多因素认证（2FA）

## 管理功能

系统提供管理员功能：

```bash
# 创建超级用户
python scripts/create_superuser.py
```

超级用户可以访问所有用户管理功能。 