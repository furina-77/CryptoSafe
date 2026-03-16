# CryptoSafe 密码安全服务平台

> 一个完整的密码技术工程化落地项目，包含前端演示平台和 Python 后端 API 服务，支持国际标准（AES/RSA/SHA）和国密算法（SM2/SM3/SM4）。

---

## 项目架构

CryptoSafe 采用前后端分离架构：

| 组件 | 技术栈 | 说明 |
|------|--------|------|
| **前端** | HTML/CSS/JS + CryptoJS | 浏览器端密码算法演示 |
| **后端** | Flask + cryptography | RESTful API 服务 |
| **数据库** | SQLite / PostgreSQL | 密钥存储（可选） |
| **部署** | Docker + Gunicorn + Nginx | 生产环境容器化部署 |

---

## 📁 项目目录

```
CryptoSafe/
├── frontend/              # 前端项目（浏览器端演示）
│   ├── index.html         # 主页面
│   ├── crypto.js          # 密码算法实现
│   ├── keymgr.js          # 密钥管理系统
│   ├── api-client.js      # 后端 API 客户端
│   └── style.css          # 样式文件
├── backend/               # 后端项目（Flask API）
│   ├── app.py             # Flask 应用主入口
│   ├── requirements.txt   # Python 依赖
│   ├── routes/            # API 路由
│   ├── services/          # 业务逻辑
│   ├── models/            # 数据模型（KMS）
│   ├── database/          # 数据库脚本
│   ├── docker/            # Docker 配置
│   └── nginx/             # Nginx 配置
└── README.md              # 本文件
```

---

## 功能模块

### 1. 对称加密

| 算法 | 前端实现 | 后端实现 | 用途 |
|------|----------|----------|------|
| AES-128/256 | ✅ CryptoJS | ✅ cryptography | 数据加密 |
| SM4 | ✅ sm-crypto | ✅ gmssl | 国密对称加密 |

### 2. 非对称加密

| 算法 | 前端实现 | 后端实现 | 用途 |
|------|----------|----------|------|
| RSA-2048 | ✅ node-forge | ✅ cryptography | 密钥交换、签名 |
| SM2 | ✅ sm-crypto | ✅ gmssl | 国密非对称 |

### 3. 数字签名

| 算法 | 前端实现 | 后端实现 | 用途 |
|------|----------|----------|------|
| RSA-PSS | ✅ node-forge | ✅ cryptography | 代码签名、TLS |
| SM2-SM3 | ✅ sm-crypto | ✅ gmssl | 国密签名 |

### 4. 哈希摘要

| 算法 | 前端实现 | 后端实现 | 用途 |
|------|----------|----------|------|
| SHA-256/512 | ✅ CryptoJS | ✅ cryptography | 数据完整性 |
| SM3 | ✅ sm-crypto | ✅ gmssl | 国密哈希 |
| HMAC | ✅ CryptoJS | ✅ cryptography | 消息认证 |

### 5. 密钥管理系统（KMS）

**前端特性：**
- 密钥生成与存储（localStorage）
- 密钥状态管理（启用/禁用/删除）
- 操作审计日志

**后端特性：**
- 密钥生命周期管理（符合 NIST SP 800-57）
- 密钥轮换机制
- 数据库持久化（PostgreSQL）
- RESTful API 接口

---

## 快速开始

### 前端运行

```bash
# 直接用浏览器打开 index.html
# 或使用本地服务器
python -m http.server 8000
# 访问 http://localhost:8000/index.html
```

### 后端运行

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动服务（开发模式）
python backend/app.py

# 访问 http://localhost:5000
```

### Docker 部署

```bash
# 使用 docker-compose 部署
cd backend
docker-compose up -d

# 访问 http://localhost
```

---

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

#### RSA 加密
```bash
POST /api/crypto/rsa/encrypt
Content-Type: application/json

{
  "plaintext": "Hello, World!",
  "public_key": "PEM格式的公钥"
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

---

## 技术亮点

### 密码工程标准
- AES 使用 PKCS7 填充
- RSA 使用 OAEP 和 PSS 填充
- SM2/SM4 符合 GM/T 国密标准
- KMS 遵循 NIST SP 800-57 规范

### 安全性设计
- 前端使用 `SubtleCrypto` 或 WebCrypto API（浏览器支持）
- 后端使用 `hmac.compare_digest()` 防止时序攻击
- 密钥轮换机制（默认 90 天）
- 完整的审计日志

### 架构设计
- 前后端分离
- RESTful API 规范
- 模块化设计
- 支持容器化部署

---

## 部署建议

### 开发环境
```bash
# 前端
python -m http.server 8000

# 后端
python backend/app.py
```

### 生产环境

#### 方式一：Gunicorn
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 方式二：Docker
```bash
docker build -t cryptosafe-backend .
docker run -p 5000:5000 cryptosafe-backend
```

#### 方式三：Docker Compose（推荐）
```bash
docker-compose up -d
```

---

## 环境变量配置

创建 `.env` 文件：

```env
# Flask 配置
FLASK_ENV=production
FLASK_DEBUG=0
SECRET_KEY=your-secret-key-here

# 数据库配置（可选）
DATABASE_URL=postgresql://user:password@localhost:5432/cryptosafe

# 密钥存储配置
KEY_STORAGE_PATH=./keys
KEY_ROTATION_DAYS=90
```

---

## 测试

### 前端测试
直接在浏览器中打开 index.html，测试各项功能。

### 后端测试
```bash
# 运行单元测试
python backend/run_tests.py

# API 测试
python backend/tests/test_crypto_api.py
```

---

## 安全说明

⚠️ **重要提醒：**

- 本项目为演示用途，生产环境应使用 HSM（硬件安全模块）
- 前端私钥存储在 localStorage，仅适合演示
- 后端密钥应存储在专用密钥管理服务（如 AWS KMS、HashiCorp Vault）
- 所有密码操作在服务端执行，不上传任何敏感数据

---

## 面试要点

1. **密码算法实现**
   - 详细讲解 AES/RSA/SM2/SM4 的工程实现细节
   - 区分浏览器端和服务端的不同实现方式

2. **密钥管理**
   - 阐述 KMS 的设计理念
   - NIST SP 800-57 标准遵循情况

3. **安全性**
   - 强调安全编码实践（防时序攻击、密钥轮换、审计日志）
   - 前后端分离的安全考虑

4. **架构设计**
   - RESTful API 设计原则
   - 模块化架构和可扩展性

---

## 许可证

MIT License

---

## 作者

CryptoSafe Team · 2026

---

## 项目链接

- 前端演示：https://github.com/furina-77/CryptoSafe
- 后端 API：https://github.com/furina-77/CryptoSafe/tree/main/backend
