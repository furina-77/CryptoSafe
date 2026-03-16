#!/bin/bash

# CryptoSafe 生产环境部署脚本

set -e

echo "=== CryptoSafe 部署脚本 ==="

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "错误: Docker 未安装"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "错误: Docker Compose 未安装"
    exit 1
fi

# 检查环境变量文件
if [ ! -f .env.production ]; then
    echo "错误: .env.production 文件不存在"
    exit 1
fi

# 复制生产环境配置
cp .env.production .env

# 创建 SSL 证书（如果不存在）
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "生成自签名 SSL 证书..."
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout nginx/ssl/key.pem \
        -out nginx/ssl/cert.pem \
        -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
    echo "SSL 证书已生成"
fi

# 构建并启动服务
echo "构建 Docker 镜像..."
docker-compose build

echo "启动服务..."
docker-compose up -d

# 等待服务启动
echo "等待服务启动..."
sleep 10

# 健康检查
echo "执行健康检查..."
if curl -f http://localhost/health; then
    echo "✓ 服务启动成功"
    echo ""
    echo "访问地址："
    echo "  HTTP:  http://localhost"
    echo "  HTTPS: https://localhost"
    echo "  API:   http://localhost/api"
else
    echo "✗ 服务启动失败"
    echo "查看日志: docker-compose logs"
    exit 1
fi

echo ""
echo "常用命令："
echo "  查看日志: docker-compose logs -f"
echo "  停止服务: docker-compose down"
echo "  重启服务: docker-compose restart"
echo "  查看状态: docker-compose ps"
