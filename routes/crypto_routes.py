"""
加密/解密 API 路由
"""
from flask import Blueprint, request, jsonify
import base64

from services.crypto_service import AESService, RSAService, SM2Service, SM4Service

crypto_bp = Blueprint('crypto', __name__)


@crypto_bp.route('/aes/encrypt', methods=['POST'])
def aes_encrypt():
    """AES 加密"""
    data = request.get_json()
    plaintext = data.get('plaintext')
    key = data.get('key')
    mode = data.get('mode', 'CBC')
    iv = data.get('iv')

    if not plaintext or not key:
        return jsonify({'error': '缺少必需参数: plaintext, key'}), 400

    result = AESService.encrypt(plaintext, key, mode, iv)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/aes/decrypt', methods=['POST'])
def aes_decrypt():
    """AES 解密"""
    data = request.get_json()
    ciphertext = data.get('ciphertext')
    key = data.get('key')
    mode = data.get('mode')
    iv = data.get('iv')

    if not ciphertext or not key or not mode:
        return jsonify({'error': '缺少必需参数: ciphertext, key, mode'}), 400

    result = AESService.decrypt(ciphertext, key, mode, iv)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/aes/generate-key', methods=['POST'])
def aes_generate_key():
    """生成 AES 密钥"""
    data = request.get_json()
    key_size = data.get('key_size', 256)

    result = AESService.generate_key(key_size)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/rsa/generate-key-pair', methods=['POST'])
def rsa_generate_key_pair():
    """生成 RSA 密钥对"""
    data = request.get_json()
    key_size = data.get('key_size', 2048)

    result = RSAService.generate_key_pair(key_size)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/rsa/encrypt', methods=['POST'])
def rsa_encrypt():
    """RSA 加密"""
    data = request.get_json()
    plaintext = data.get('plaintext')
    public_key = data.get('public_key')

    if not plaintext or not public_key:
        return jsonify({'error': '缺少必需参数: plaintext, public_key'}), 400

    result = RSAService.encrypt(plaintext, public_key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/rsa/decrypt', methods=['POST'])
def rsa_decrypt():
    """RSA 解密"""
    data = request.get_json()
    ciphertext = data.get('ciphertext')
    private_key = data.get('private_key')

    if not ciphertext or not private_key:
        return jsonify({'error': '缺少必需参数: ciphertext, private_key'}), 400

    result = RSAService.decrypt(ciphertext, private_key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm2/generate-key-pair', methods=['POST'])
def sm2_generate_key_pair():
    """生成 SM2 密钥对"""
    if not SM2Service.check_available():
        return jsonify({'error': 'gmssl 库未安装，无法使用 SM2'}), 500

    result = SM2Service.generate_key_pair()

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm2/encrypt', methods=['POST'])
def sm2_encrypt():
    """SM2 加密"""
    data = request.get_json()
    plaintext = data.get('plaintext')
    public_key = data.get('public_key')

    if not plaintext or not public_key:
        return jsonify({'error': '缺少必需参数: plaintext, public_key'}), 400

    result = SM2Service.encrypt(plaintext, public_key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm2/decrypt', methods=['POST'])
def sm2_decrypt():
    """SM2 解密"""
    data = request.get_json()
    ciphertext = data.get('ciphertext')
    private_key = data.get('private_key')

    if not ciphertext or not private_key:
        return jsonify({'error': '缺少必需参数: ciphertext, private_key'}), 400

    result = SM2Service.decrypt(ciphertext, private_key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm4/generate-key', methods=['POST'])
def sm4_generate_key():
    """生成 SM4 密钥"""
    if not SM4Service.check_available():
        return jsonify({'error': 'gmssl 库未安装，无法使用 SM4'}), 500

    result = SM4Service.generate_key()

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm4/encrypt', methods=['POST'])
def sm4_encrypt():
    """SM4 加密"""
    data = request.get_json()
    plaintext = data.get('plaintext')
    key = data.get('key')

    if not plaintext or not key:
        return jsonify({'error': '缺少必需参数: plaintext, key'}), 400

    result = SM4Service.encrypt(plaintext, key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@crypto_bp.route('/sm4/decrypt', methods=['POST'])
def sm4_decrypt():
    """SM4 解密"""
    data = request.get_json()
    ciphertext = data.get('ciphertext')
    key = data.get('key')

    if not ciphertext or not key:
        return jsonify({'error': '缺少必需参数: ciphertext, key'}), 400

    result = SM4Service.decrypt(ciphertext, key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)
