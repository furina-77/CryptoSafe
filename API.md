# CryptoSafe API 接口文档

## 基础信息

- **Base URL**: `http://localhost:5000/api`
- **Content-Type**: `application/json`
- **字符编码**: `UTF-8`

## 通用响应格式

### 成功响应
```json
{
  "data": {},
  "message": "操作成功"
}
```

### 错误响应
```json
{
  "error": "错误描述",
  "code": "ERROR_CODE"
}
```

---

## 1. 加密/解密 (`/crypto`)

### 1.1 AES 加密

**请求**
```http
POST /crypto/aes/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "key": "base64编码的密钥",
  "mode": "CBC",
  "iv": "base64编码的IV（可选）"
}
```

**响应**
```json
{
  "ciphertext": "base64编码的密文",
  "iv": "base64编码的IV",
  "mode": "CBC"
}
```

### 1.2 AES 解密

**请求**
```http
POST /crypto/aes/decrypt
Content-Type: application/json

{
  "ciphertext": "base64编码的密文",
  "key": "base64编码的密钥",
  "mode": "CBC",
  "iv": "base64编码的IV"
}
```

**响应**
```json
{
  "plaintext": "解密后的明文"
}
```

### 1.3 AES 生成密钥

**请求**
```http
POST /crypto/aes/generate-key
Content-Type: application/json

{
  "key_size": 256
}
```

**响应**
```json
{
  "key": "base64编码的密钥",
  "size": 256,
  "algorithm": "AES-256"
}
```

### 1.4 RSA 加密

**请求**
```http
POST /crypto/rsa/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "public_key": "PEM格式的公钥"
}
```

**响应**
```json
{
  "ciphertext": "base64编码的密文"
}
```

### 1.5 RSA 解密

**请求**
```http
POST /crypto/rsa/decrypt
Content-Type: application/json

{
  "ciphertext": "base64编码的密文",
  "private_key": "PEM格式的私钥"
}
```

**响应**
```json
{
  "plaintext": "解密后的明文"
}
```

### 1.6 RSA 生成密钥对

**请求**
```http
POST /crypto/rsa/generate-key-pair
Content-Type: application/json

{
  "key_size": 2048
}
```

**响应**
```json
{
  "public_key": "PEM格式的公钥",
  "private_key": "PEM格式的私钥",
  "key_size": 2048
}
```

### 1.7 SM2 加密

**请求**
```http
POST /crypto/sm2/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "public_key": "SM2公钥(hex)"
}
```

**响应**
```json
{
  "ciphertext": "hex格式的密文"
}
```

### 1.8 SM2 解密

**请求**
```http
POST /crypto/sm2/decrypt
Content-Type: application/json

{
  "ciphertext": "hex格式的密文",
  "private_key": "SM2私钥(hex)"
}
```

**响应**
```json
{
  "plaintext": "解密后的明文"
}
```

---

## 2. 数字签名 (`/sign`)

### 2.1 RSA 签名

**请求**
```http
POST /sign/rsa/sign
Content-Type: application/json

{
  "message": "待签名消息",
  "private_key": "PEM格式的私钥"
}
```

**响应**
```json
{
  "signature": "base64编码的签名"
}
```

### 2.2 RSA 验签

**请求**
```http
POST /sign/rsa/verify
Content-Type: application/json

{
  "message": "原始消息",
  "signature": "base64编码的签名",
  "public_key": "PEM格式的公钥"
}
```

**响应**
```json
{
  "valid": true
}
```

### 2.3 SM2 签名

**请求**
```http
POST /sign/sm2/sign
Content-Type: application/json

{
  "message": "待签名消息",
  "private_key": "SM2私钥(hex)",
  "user_id": "1234567812345678"
}
```

**响应**
```json
{
  "signature": "hex格式的签名"
}
```

### 2.4 SM2 验签

**请求**
```http
POST /sign/sm2/verify
Content-Type: application/json

{
  "message": "原始消息",
  "signature": "hex格式的签名",
  "public_key": "SM2公钥(hex)",
  "user_id": "1234567812345678"
}
```

**响应**
```json
{
  "valid": true
}
```

---

## 3. 哈希摘要 (`/hash`)

### 3.1 计算哈希

**请求**
```http
POST /hash/compute
Content-Type: application/json

{
  "message": "Hello, World!",
  "algorithm": "SHA-256"
}
```

**响应**
```json
{
  "hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08"
}
```

支持的算法：`MD5`, `SHA-256`, `SHA-512`, `SM3`

### 3.2 计算 HMAC

**请求**
```http
POST /hash/hmac
Content-Type: application/json

{
  "message": "Hello, World!",
  "key": "base64编码的密钥",
  "algorithm": "SHA256"
}
```

**响应**
```json
{
  "hmac": "hex格式的HMAC值"
}
```

### 3.3 验证哈希

**请求**
```http
POST /hash/verify
Content-Type: application/json

{
  "message": "Hello, World!",
  "expected_hash": "9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08",
  "algorithm": "SHA-256"
}
```

**响应**
```json
{
  "valid": true
}
```

---

## 4. 密钥管理 (`/keys`)

### 4.1 创建密钥

**请求**
```http
POST /keys/create
Content-Type: application/json

{
  "algorithm": "AES-256",
  "key_material": "base64编码的密钥",
  "key_type": "symmetric",
  "description": "主加密密钥",
  "tags": ["production"],
  "expires_in_days": 365
}
```

**响应**
```json
{
  "key_id": "uuid",
  "metadata": {
    "key_id": "uuid",
    "key_type": "symmetric",
    "algorithm": "AES-256",
    "status": "active",
    "description": "主加密密钥",
    "tags": ["production"],
    "created_at": "2026-03-16T...",
    "updated_at": "2026-03-16T...",
    "expires_at": "2027-03-16T...",
    "rotation_days": 90
  }
}
```

### 4.2 列出密钥

**请求**
```http
GET /keys/?status=active&algorithm=AES-256
```

**响应**
```json
{
  "keys": [
    {
      "key_id": "uuid",
      "key_type": "symmetric",
      "algorithm": "AES-256",
      "status": "active",
      ...
    }
  ]
}
```

### 4.3 获取密钥元数据

**请求**
```http
GET /keys/{key_id}
```

**响应**
```json
{
  "metadata": {
    "key_id": "uuid",
    "key_type": "symmetric",
    "algorithm": "AES-256",
    "status": "active",
    ...
  }
}
```

### 4.4 获取密钥材料

**请求**
```http
GET /keys/{key_id}/material
```

**响应**
```json
{
  "key_material": "base64编码的密钥"
}
```

### 4.5 禁用密钥

**请求**
```http
POST /keys/{key_id}/disable
```

**响应**
```json
{
  "success": true
}
```

### 4.6 启用密钥

**请求**
```http
POST /keys/{key_id}/enable
```

**响应**
```json
{
  "success": true
}
```

### 4.7 删除密钥

**请求**
```http
DELETE /keys/{key_id}
```

**响应**
```json
{
  "success": true
}
```

### 4.8 密钥轮换

**请求**
```http
POST /keys/{key_id}/rotate
Content-Type: application/json

{
  "new_key_material": "base64编码的新密钥"
}
```

**响应**
```json
{
  "success": true
}
```

### 4.9 获取审计日志

**请求**
```http
GET /keys/{key_id}/audit
```

**响应**
```json
{
  "logs": [
    {
      "log_id": "uuid",
      "key_id": "uuid",
      "operation": "CREATE",
      "operator": "system",
      "details": "创建 AES-256 密钥",
      "timestamp": "2026-03-16T..."
    }
  ]
}
```

---

## 5. 系统接口

### 5.1 健康检查

**请求**
```http
GET /health
```

**响应**
```json
{
  "status": "ok"
}
```

### 5.2 API 信息

**请求**
```http
GET /
```

**响应**
```json
{
  "name": "CryptoSafe API",
  "version": "1.0.0",
  "description": "密码安全服务平台后端接口",
  "endpoints": {
    "crypto": "/api/crypto/* - 加密/解密",
    "keys": "/api/keys/* - 密钥管理",
    "sign": "/api/sign/* - 数字签名",
    "hash": "/api/hash/* - 哈希摘要"
  }
}
```

---

## 错误码

| 错误码 | 说明 |
|--------|------|
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 速率限制

当前版本未设置速率限制，生产环境建议添加。

## 认证

当前版本未实现认证，生产环境建议添加 JWT 或 OAuth2。
