# SSL 证书说明

生产环境需要使用真实的 SSL 证书。

## 生成自签名证书（仅用于测试）

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem \
  -out cert.pem
```

## 使用 Let's Encrypt（推荐）

```bash
# 安装 certbot
sudo apt-get install certbot

# 获取证书
sudo certbot certonly --nginx -d your-domain.com

# 证书位置
# /etc/letsencrypt/live/your-domain.com/fullchain.pem (cert.pem)
# /etc/letsencrypt/live/your-domain.com/privkey.pem (key.pem)
```

## 更新 docker-compose.yml

将证书挂载到容器：

```yaml
volumes:
  - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
  - /etc/letsencrypt/live/your-domain.com/fullchain.pem:/etc/nginx/ssl/cert.pem:ro
  - /etc/letsencrypt/live/your-domain.com/privkey.pem:/etc/nginx/ssl/key.pem:ro
```
