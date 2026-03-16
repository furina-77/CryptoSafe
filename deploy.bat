@echo off
REM CryptoSafe 生产环境部署脚本 (Windows)

echo === CryptoSafe 部署脚本 ===

REM 检查 Docker 是否安装
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker 未安装
    exit /b 1
)

docker-compose --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: Docker Compose 未安装
    exit /b 1
)

REM 检查环境变量文件
if not exist .env.production (
    echo 错误: .env.production 文件不存在
    exit /b 1
)

REM 复制生产环境配置
copy /Y .env.production .env >nul

REM 创建 SSL 证书目录
if not exist nginx\ssl mkdir nginx\ssl

REM 检查 SSL 证书
if not exist nginx\ssl\cert.pem (
    echo 生成自签名 SSL 证书...
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout nginx\ssl\key.pem -out nginx\ssl\cert.pem -subj "/C=CN/ST=State/L=City/O=Organization/CN=localhost"
    echo SSL 证书已生成
)

REM 构建并启动服务
echo 构建 Docker 镜像...
docker-compose build

echo 启动服务...
docker-compose up -d

REM 等待服务启动
echo 等待服务启动...
timeout /t 10 /nobreak >nul

REM 健康检查
echo 执行健康检查...
curl -f http://localhost/health
if %errorlevel% equ 0 (
    echo.
    echo 服务启动成功
    echo.
    echo 访问地址：
    echo   HTTP:  http://localhost
    echo   HTTPS: https://localhost
    echo   API:   http://localhost/api
) else (
    echo.
    echo 服务启动失败
    echo 查看日志: docker-compose logs
    exit /b 1
)

echo.
echo 常用命令：
echo   查看日志: docker-compose logs -f
echo   停止服务: docker-compose down
echo   重启服务: docker-compose restart
echo   查看状态: docker-compose ps
