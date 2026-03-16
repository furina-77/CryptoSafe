"""
数字签名 API 路由
"""
from flask import Blueprint, request, jsonify

from services.crypto_service import RSAService, SM2Service

sign_bp = Blueprint('sign', __name__)


@sign_bp.route('/rsa/sign', methods=['POST'])
def rsa_sign():
    """RSA 签名"""
    data = request.get_json()
    message = data.get('message')
    private_key = data.get('private_key')

    if not message or not private_key:
        return jsonify({'error': '缺少必需参数: message, private_key'}), 400

    result = RSAService.sign(message, private_key)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@sign_bp.route('/rsa/verify', methods=['POST'])
def rsa_verify():
    """RSA 验签"""
    data = request.get_json()
    message = data.get('message')
    signature = data.get('signature')
    public_key = data.get('public_key')

    if not message or not signature or not public_key:
        return jsonify({'error': '缺少必需参数: message, signature, public_key'}), 400

    result = RSAService.verify(message, signature, public_key)

    return jsonify(result)


@sign_bp.route('/sm2/sign', methods=['POST'])
def sm2_sign():
    """SM2 签名"""
    data = request.get_json()
    message = data.get('message')
    private_key = data.get('private_key')
    user_id = data.get('user_id', '1234567812345678')

    if not message or not private_key:
        return jsonify({'error': '缺少必需参数: message, private_key'}), 400

    if not SM2Service.check_available():
        return jsonify({'error': 'gmssl 库未安装，无法使用 SM2'}), 500

    result = SM2Service.sign(message, private_key, user_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@sign_bp.route('/sm2/verify', methods=['POST'])
def sm2_verify():
    """SM2 验签"""
    data = request.get_json()
    message = data.get('message')
    signature = data.get('signature')
    public_key = data.get('public_key')
    user_id = data.get('user_id', '1234567812345678')

    if not message or not signature or not public_key:
        return jsonify({'error': '缺少必需参数: message, signature, public_key'}), 400

    if not SM2Service.check_available():
        return jsonify({'error': 'gmssl 库未安装，无法使用 SM2'}), 500

    result = SM2Service.verify(message, signature, public_key, user_id)

    return jsonify(result)
