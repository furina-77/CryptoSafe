# CryptoSafe 后端部署指南

## 开发环境

### 前置要求

- Python 3.10+
- pip

### 快速启动

```bash
cd E:\crypto
E:\Anaconda\python.exe -m pip install -r requirements.txt
E:\Anaconda\python.exe app.py
```

服务将在 `http://localhost:5000` 启动

### 环境变量

创建 `.env` 文件：

```
FLASK_ENV=development
FLASK_APP=app.py
FLASK_DEBUG=1
SECRET_KEY=your-secret-key-change-this-in-production
```

## 生产环境部署

### 使用 Gunicorn

```bash
E:\Anaconda\Scripts\gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

参数说明：
- `-w 4`: 使用 4 个工作进程
- `-b 0.0.0.0:5000`: 绑定到所有网卡的 5000 端口
- `app:app`: 模块名:应用对象

### 使用 Supervisor（推荐）

创建 `/etc/supervisor/conf.d/cryptosafe.conf`:

```ini
[program:cryptosafe]
command=/path/to/python /path/to/app.py
directory=/path/to/crypto
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/cryptosafe.err.log
stdout_logfile=/var/log/cryptosafe.out.log
```

启动：
```bash
supervisorctl update
supervisorctl start cryptosafe
```

### 使用 Docker

创建 `Dockerfile`:

```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

创建 `docker-compose.yml`:

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
    volumes:
      - ./keys:/app/keys
```

启动：
```bash
docker-compose up -d
```

## 安全建议

1. **密钥存储**：使用专门的密钥管理服务（如 AWS KMS、Hashicorp Vault）
2. **HTTPS**：在生产环境使用 TLS/SSL
3. **认证**：添加 JWT 或 OAuth2 认证
4. **速率限制**：防止 API 滥用
5. **日志审计**：记录所有敏感操作

## 监控

### 健康检查

```bash
curl http://localhost:5000/health
```

### 日志查看

```bash
tail -f /var/log/cryptosafe.out.log
```

## 性能优化

1. **缓存**：使用 Redis 缓存常用密钥
2. **数据库**：改用 PostgreSQL 替代 SQLite 存储密钥元数据
3. **负载均衡**：使用 Nginx 反向代理多个 Gunicorn 实例
