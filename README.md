# CryptoSafe 密码安全服务平台（Python 后端版本）

## 项目介绍

基于 Flask + cryptography 库实现的密码算法工程化后端服务，提供 AES、RSA、SM2、SM4 等密码算法的 API 接口，并包含完整的密钥管理系统（KMS）。

## 技术栈

- **Web 框架**: Flask 3.0
- **密码库**:
  - `cryptography`: 实现 AES、RSA、SHA
  - `gmssl`: 实现国密 SM2、SM3、SM4
- **环境管理**: python-dotenv
- **部署**: gunicorn

## 功能模块

### 1. 对称加密
- AES-128/192/256 (CBC/ECB/CTR 模式)
- SM4 (国密对称算法)

### 2. 非对称加密
- RSA-2048 (OAEP 填充)
- SM2 (国密非对称算法)

### 3. 数字签名
- RSA-PSS 签名
- SM2-SM3 签名

### 4. 哈希摘要
- MD5、SHA-256、SHA-512
- SM3 (国密哈希)
- HMAC-SHA256/512

### 5. 密钥管理系统（KMS）
- 密钥生成与存储
- 密钥生命周期管理（启用/禁用/删除）
- 密钥轮换
- 操作审计日志

## 快速开始

### 1. 安装依赖

```bash
cd E:\crypto
E:\Anaconda\python.exe -m pip install -r requirements.txt
```

### 2. 启动服务

```bash
E:\Anaconda\python.exe app.py
```

服务将在 `http://localhost:5000` 启动

### 3. 测试 API

访问 http://localhost:5000 查看可用接口

## API 接口文档

### 加密/解密 (`/api/crypto`)

#### AES 加密
```bash
POST /api/crypto/aes/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "key": "base64编码的密钥",
  "mode": "CBC",
  "iv": "base64编码的IV（可选）"
}
```

#### AES 解密
```bash
POST /api/crypto/aes/decrypt
Content-Type: application/json

{
  "ciphertext": "base64编码的密文",
  "key": "base64编码的密钥",
  "mode": "CBC",
  "iv": "base64编码的IV"
}
```

#### RSA 加密
```bash
POST /api/crypto/rsa/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "public_key": "PEM格式的公钥"
}
```

#### SM2 加密
```bash
POST /api/crypto/sm2/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "public_key": "SM2公钥(hex)"
}
```

### 密钥管理 (`/api/keys`)

#### 创建密钥
```bash
POST /api/keys/create
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

#### 列出密钥
```bash
GET /api/keys/?status=active&algorithm=AES-256
```

#### 获取密钥元数据
```bash
GET /api/keys/{key_id}
```

#### 获取密钥材料
```bash
GET /api/keys/{key_id}/material
```

#### 禁用密钥
```bash
POST /api/keys/{key_id}/disable
```

#### 密钥轮换
```bash
POST /api/keys/{key_id}/rotate
Content-Type: application/json

{
  "new_key_material": "base64编码的新密钥"
}
```

### 数字签名 (`/api/sign`)

#### RSA 签名
```bash
POST /api/sign/rsa/sign
Content-Type: application/json

{
  "message": "待签名消息",
  "private_key": "PEM格式的私钥"
}
```

#### SM2 签名
```bash
POST /api/sign/sm2/sign
Content-Type: application/json

{
  "message": "待签名消息",
  "private_key": "SM2私钥(hex)"
}
```

### 哈希摘要 (`/api/hash`)

#### 计算哈希
```bash
POST /api/hash/compute
Content-Type: application/json

{
  "message": "Hello, World!",
  "algorithm": "SHA-256"
}
```

#### 计算 HMAC
```bash
POST /api/hash/hmac
Content-Type: application/json

{
  "message": "Hello, World!",
  "key": "base64编码的密钥",
  "algorithm": "SHA256"
}
```

## 项目结构

```
E:\crypto/
├── app.py                 # Flask 应用主入口
├── requirements.txt       # Python 依赖
├── .env                   # 环境变量配置
├── routes/               # API 路由
│   ├── crypto_routes.py  # 加密/解密
│   ├── key_routes.py     # 密钥管理
│   ├── sign_routes.py    # 数字签名
│   └── hash_routes.py    # 哈希摘要
├── services/             # 业务逻辑
│   ├── crypto_service.py # 密码算法实现
│   └── hash_service.py  # 哈希服务
├── models/               # 数据模型
│   └── key_manager.py    # 密钥管理模型（KMS）
├── keys/                 # 密钥存储目录（自动创建）
└── tests/                # 单元测试
```

## 密钥管理（KMS）特性

1. **密钥生命周期管理**
   - 创建、启用、禁用、删除
   - 自动过期时间设置
   - 密钥轮换机制

2. **安全存储**
   - 密钥材料加密存储
   - 支持标签和描述
   - 软删除机制

3. **审计日志**
   - 记录所有密钥操作
   - 可追溯操作历史
   - 支持按密钥 ID 筛选

## 技术亮点

1. **符合密码工程标准**
   - AES/CBC/CTR 使用 PKCS7 填充
   - RSA 使用 OAEP 和 PSS 填充
   - SM2/SM4 符合 GM/T 国密标准

2. **安全性设计**
   - 使用 `hmac.compare_digest()` 防止时序攻击
   - 密钥轮换机制
   - 完整的审计日志

3. **生产级架构**
   - 模块化设计
   - RESTful API
   - 支持横向扩展

## 部署建议

### 开发环境
```bash
E:\Anaconda\python.exe app.py
```

### 生产环境
使用 gunicorn 部署：
```bash
E:\Anaconda\Scripts\gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## 测试

运行单元测试：
```bash
E:\Anaconda\python.exe -m pytest tests/
```

## 许可证

MIT License

## 面试要点

1. **密码算法实现**: 详细讲解 AES/RSA/SM2/SM4 的工程实现细节
2. **密钥管理**: 阐述 KMS 的设计理念和 NIST SP 800-57 标准遵循情况
3. **安全性**: 强调安全编码实践（防时序攻击、密钥轮换、审计日志）
4. **架构设计**: 说明 RESTful API 设计原则和模块化架构

---

作者: [你的名字]
日期: 2026
