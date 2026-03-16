"""
密钥管理 API 路由
"""
from flask import Blueprint, request, jsonify

from models.key_manager import KeyManager, KeyType

# 创建全局密钥管理器实例
key_manager = KeyManager(storage_dir='E:/crypto/keys')

key_bp = Blueprint('keys', __name__)


@key_bp.route('/create', methods=['POST'])
def create_key():
    """创建密钥"""
    data = request.get_json()
    algorithm = data.get('algorithm')
    key_material = data.get('key_material')
    key_type = data.get('key_type')
    description = data.get('description', '')
    tags = data.get('tags', [])
    expires_in_days = data.get('expires_in_days')

    if not algorithm or not key_material or not key_type:
        return jsonify({'error': '缺少必需参数: algorithm, key_material, key_type'}), 400

    try:
        key_type_enum = KeyType(key_type)
    except ValueError:
        return jsonify({'error': f'无效的密钥类型: {key_type}'}), 400

    result = key_manager.create_key(
        algorithm=algorithm,
        key_material=key_material,
        key_type=key_type_enum,
        description=description,
        tags=tags,
        expires_in_days=expires_in_days
    )

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/<key_id>', methods=['GET'])
def get_key(key_id):
    """获取密钥元数据"""
    result = key_manager.get_key(key_id)

    if 'error' in result:
        return jsonify(result), 404

    return jsonify(result)


@key_bp.route('/<key_id>/material', methods=['GET'])
def get_key_material(key_id):
    """获取密钥材料"""
    result = key_manager.get_key_material(key_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/', methods=['GET'])
def list_keys():
    """列出所有密钥"""
    status = request.args.get('status')
    algorithm = request.args.get('algorithm')

    result = key_manager.list_keys(status=status, algorithm=algorithm)

    return jsonify(result)


@key_bp.route('/<key_id>/disable', methods=['POST'])
def disable_key(key_id):
    """禁用密钥"""
    result = key_manager.disable_key(key_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/<key_id>/enable', methods=['POST'])
def enable_key(key_id):
    """启用密钥"""
    result = key_manager.enable_key(key_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/<key_id>', methods=['DELETE'])
def delete_key(key_id):
    """删除密钥"""
    result = key_manager.delete_key(key_id)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/<key_id>/rotate', methods=['POST'])
def rotate_key(key_id):
    """密钥轮换"""
    data = request.get_json()
    new_key_material = data.get('new_key_material')

    if not new_key_material:
        return jsonify({'error': '缺少必需参数: new_key_material'}), 400

    result = key_manager.rotate_key(key_id, new_key_material)

    if 'error' in result:
        return jsonify(result), 400

    return jsonify(result)


@key_bp.route('/<key_id>/audit', methods=['GET'])
def get_audit_logs(key_id):
    """获取密钥审计日志"""
    result = key_manager.get_audit_logs(key_id)

    return jsonify(result)


@key_bp.route('/audit', methods=['GET'])
def get_all_audit_logs():
    """获取所有审计日志"""
    result = key_manager.get_audit_logs()

    return jsonify(result)
