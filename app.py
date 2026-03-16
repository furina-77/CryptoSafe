"""
CryptoSafe 后端服务
基于 Flask + cryptography 库实现密码算法工程化
"""
import os
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key')
app.config['JSON_AS_ASCII'] = False

# 导入路由
from routes.crypto_routes import crypto_bp
from routes.key_routes import key_bp
from routes.sign_routes import sign_bp
from routes.hash_routes import hash_bp

# 注册蓝图
app.register_blueprint(crypto_bp, url_prefix='/api/crypto')
app.register_blueprint(key_bp, url_prefix='/api/keys')
app.register_blueprint(sign_bp, url_prefix='/api/sign')
app.register_blueprint(hash_bp, url_prefix='/api/hash')


@app.route('/')
def index():
    """API 根路径"""
    return jsonify({
        'name': 'CryptoSafe API',
        'version': '1.0.0',
        'description': '密码安全服务平台后端接口',
        'endpoints': {
            'crypto': '/api/crypto/* - 加密/解密',
            'keys': '/api/keys/* - 密钥管理',
            'sign': '/api/sign/* - 数字签名',
            'hash': '/api/hash/* - 哈希摘要'
        }
    })


@app.route('/health')
def health():
    """健康检查"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
