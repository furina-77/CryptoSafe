"""
哈希摘要 API 路由
"""
from flask import Blueprint, request, jsonify

from services.hash_service import HashService

hash_bp = Blueprint('hash', __name__)


@hash_bp.route('/compute', methods=['POST'])
def compute_hash():
    """计算哈希值"""
    data = request.get_json()
    message = data.get('message')
    algorithm = data.get('algorithm', 'SHA-256')

    if not message:
        return jsonify({'error': '缺少必需参数: message'}), 400

    result = HashService.compute_hash(message, algorithm)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@hash_bp.route('/hmac', methods=['POST'])
def compute_hmac():
    """计算 HMAC"""
    data = request.get_json()
    message = data.get('message')
    key = data.get('key')
    algorithm = data.get('algorithm', 'SHA256')

    if not message or not key:
        return jsonify({'error': '缺少必需参数: message, key'}), 400

    result = HashService.compute_hmac(message, key, algorithm)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@hash_bp.route('/verify', methods=['POST'])
def verify_hash():
    """验证哈希值"""
    data = request.get_json()
    message = data.get('message')
    expected_hash = data.get('expected_hash')
    algorithm = data.get('algorithm', 'SHA-256')

    if not message or not expected_hash:
        return jsonify({'error': '缺少必需参数: message, expected_hash'}), 400

    result = HashService.verify_hash(message, expected_hash, algorithm)

    return jsonify(result)


@hash_bp.route('/hmac/verify', methods=['POST'])
def verify_hmac():
    """验证 HMAC"""
    data = request.get_json()
    message = data.get('message')
    key = data.get('key')
    expected_hmac = data.get('expected_hmac')
    algorithm = data.get('algorithm', 'SHA256')

    if not message or not key or not expected_hmac:
        return jsonify({'error': '缺少必需参数: message, key, expected_hmac'}), 400

    result = HashService.verify_hmac(message, key, expected_hmac, algorithm)

    return jsonify(result)


@hash_bp.route('/compare', methods=['POST'])
def compare_hashes():
    """安全比较两个哈希值"""
    data = request.get_json()
    hash1 = data.get('hash1')
    hash2 = data.get('hash2')

    if not hash1 or not hash2:
        return jsonify({'error': '缺少必需参数: hash1, hash2'}), 400

    result = HashService.compare_hashes(hash1, hash2)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)
