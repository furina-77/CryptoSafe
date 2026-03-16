"""
密钥管理模型（KMS）
实现密钥的生成、存储、生命周期管理
"""
import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from enum import Enum


class KeyStatus(Enum):
    """密钥状态枚举"""
    ACTIVE = 'active'      # 激活状态
    DISABLED = 'disabled'  # 禁用状态
    DELETED = 'deleted'    # 已删除
    EXPIRED = 'expired'    # 已过期


class KeyType(Enum):
    """密钥类型枚举"""
    SYMMETRIC = 'symmetric'  # 对称密钥（AES/SM4）
    ASYMMETRIC_PUBLIC = 'asymmetric_public'  # 非对称公钥（RSA/SM2）
    ASYMMETRIC_PRIVATE = 'asymmetric_private'  # 非对称私钥（RSA/SM2）
    HMAC = 'hmac'  # HMAC 密钥


class KeyMetadata:
    """密钥元数据"""

    def __init__(
        self,
        key_id: str,
        key_type: KeyType,
        algorithm: str,
        status: KeyStatus = KeyStatus.ACTIVE,
        description: str = '',
        tags: List[str] = None,
        expires_at: Optional[datetime] = None
    ):
        self.key_id = key_id
        self.key_type = key_type
        self.algorithm = algorithm
        self.status = status
        self.description = description
        self.tags = tags or []
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.expires_at = expires_at
        self.rotation_days = 90  # 密钥轮换周期（天）

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'key_id': self.key_id,
            'key_type': self.key_type.value,
            'algorithm': self.algorithm,
            'status': self.status.value,
            'description': self.description,
            'tags': self.tags,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'rotation_days': self.rotation_days
        }


class AuditLog:
    """审计日志"""

    def __init__(
        self,
        key_id: str,
        operation: str,
        operator: str = 'system',
        details: str = ''
    ):
        self.log_id = str(uuid.uuid4())
        self.key_id = key_id
        self.operation = operation  # CREATE, ENABLE, DISABLE, DELETE, EXPORT, ROTATE
        self.operator = operator
        self.details = details
        self.timestamp = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'log_id': self.log_id,
            'key_id': self.key_id,
            'operation': self.operation,
            'operator': self.operator,
            'details': self.details,
            'timestamp': self.timestamp.isoformat()
        }


class KeyManager:
    """密钥管理系统（KMS）"""

    def __init__(self, storage_dir: str = 'keys'):
        self.storage_dir = storage_dir
        self.keys: Dict[str, KeyMetadata] = {}
        self.key_materials: Dict[str, str] = {}  # key_id -> key_value
        self.audit_logs: List[AuditLog] = []

        # 创建存储目录
        os.makedirs(storage_dir, exist_ok=True)

        # 加载已有密钥
        self._load_keys()

    def _get_key_path(self, key_id: str) -> str:
        """获取密钥存储路径"""
        return os.path.join(self.storage_dir, f'{key_id}.json')

    def _load_keys(self):
        """从磁盘加载密钥"""
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(self.storage_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        data = json.load(f)

                    # 恢复元数据
                    metadata = KeyMetadata(
                        key_id=data['key_id'],
                        key_type=KeyType(data['key_type']),
                        algorithm=data['algorithm'],
                        status=KeyStatus(data['status']),
                        description=data.get('description', ''),
                        tags=data.get('tags', [])
                    )
                    metadata.created_at = datetime.fromisoformat(data['created_at'])
                    metadata.updated_at = datetime.fromisoformat(data['updated_at'])
                    if data.get('expires_at'):
                        metadata.expires_at = datetime.fromisoformat(data['expires_at'])

                    self.keys[metadata.key_id] = metadata
                    self.key_materials[metadata.key_id] = data['key_material']

        except Exception as e:
            print(f'加载密钥失败: {e}')

    def _save_key(self, key_id: str):
        """保存密钥到磁盘"""
        if key_id not in self.keys:
            return

        metadata = self.keys[key_id]
        key_material = self.key_materials.get(key_id, '')

        data = metadata.to_dict()
        data['key_material'] = key_material

        filepath = self._get_key_path(key_id)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _add_audit_log(self, key_id: str, operation: str, details: str = ''):
        """添加审计日志"""
        log = AuditLog(key_id, operation, details=details)
        self.audit_logs.append(log)

        # 保存审计日志
        self._save_audit_logs()

    def _save_audit_logs(self):
        """保存审计日志到磁盘"""
        filepath = os.path.join(self.storage_dir, 'audit_logs.json')
        with open(filepath, 'w', encoding='utf-8') as f:
            logs_data = [log.to_dict() for log in self.audit_logs]
            json.dump(logs_data, f, ensure_ascii=False, indent=2)

    def create_key(
        self,
        algorithm: str,
        key_material: str,
        key_type: KeyType,
        description: str = '',
        tags: List[str] = None,
        expires_in_days: int = None
    ) -> Dict[str, Any]:
        """
        创建密钥
        Args:
            algorithm: 算法（AES-256, RSA-2048, SM4, SM2 等）
            key_material: 密钥材料（Base64 或 PEM 格式）
            key_type: 密钥类型
            description: 描述
            tags: 标签
            expires_in_days: 过期天数
        Returns:
            {'key_id': 密钥ID, 'metadata': 元数据}
        """
        try:
            key_id = str(uuid.uuid4())

            # 计算过期时间
            expires_at = None
            if expires_in_days:
                expires_at = datetime.now() + timedelta(days=expires_in_days)

            # 创建元数据
            metadata = KeyMetadata(
                key_id=key_id,
                key_type=key_type,
                algorithm=algorithm,
                description=description,
                tags=tags,
                expires_at=expires_at
            )

            self.keys[key_id] = metadata
            self.key_materials[key_id] = key_material
            self._save_key(key_id)
            self._add_audit_log(key_id, 'CREATE', f'创建 {algorithm} 密钥')

            return {
                'key_id': key_id,
                'metadata': metadata.to_dict()
            }
        except Exception as e:
            return {'error': f'创建密钥失败: {str(e)}'}

    def get_key(self, key_id: str) -> Dict[str, Any]:
        """
        获取密钥（不包括密钥材料）
        Args:
            key_id: 密钥ID
        Returns:
            {'metadata': 元数据}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        metadata = self.keys[key_id]
        return {'metadata': metadata.to_dict()}

    def get_key_material(self, key_id: str) -> Dict[str, Any]:
        """
        获取密钥材料（敏感操作，会记录审计）
        Args:
            key_id: 密钥ID
        Returns:
            {'key_material': 密钥材料}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        if key_id not in self.key_materials:
            return {'error': '密钥材料不可用'}

        metadata = self.keys[key_id]
        if metadata.status != KeyStatus.ACTIVE:
            return {'error': '密钥未激活'}

        self._add_audit_log(key_id, 'EXPORT', '导出密钥材料')

        return {'key_material': self.key_materials[key_id]}

    def list_keys(self, status: str = None, algorithm: str = None) -> Dict[str, Any]:
        """
        列出所有密钥（不包括密钥材料）
        Args:
            status: 筛选状态
            algorithm: 筛选算法
        Returns:
            {'keys': 密钥元数据列表}
        """
        keys = []
        for key_id, metadata in self.keys.items():
            # 跳过已删除的密钥
            if metadata.status == KeyStatus.DELETED:
                continue

            # 状态筛选
            if status and metadata.status.value != status:
                continue

            # 算法筛选
            if algorithm and metadata.algorithm != algorithm:
                continue

            keys.append(metadata.to_dict())

        return {'keys': keys}

    def disable_key(self, key_id: str) -> Dict[str, Any]:
        """
        禁用密钥
        Args:
            key_id: 密钥ID
        Returns:
            {'success': bool}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        metadata = self.keys[key_id]
        if metadata.status == KeyStatus.DISABLED:
            return {'error': '密钥已禁用'}

        metadata.status = KeyStatus.DISABLED
        metadata.updated_at = datetime.now()
        self._save_key(key_id)
        self._add_audit_log(key_id, 'DISABLE', '禁用密钥')

        return {'success': True}

    def enable_key(self, key_id: str) -> Dict[str, Any]:
        """
        启用密钥
        Args:
            key_id: 密钥ID
        Returns:
            {'success': bool}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        metadata = self.keys[key_id]
        if metadata.status != KeyStatus.DISABLED:
            return {'error': '只能启用已禁用的密钥'}

        metadata.status = KeyStatus.ACTIVE
        metadata.updated_at = datetime.now()
        self._save_key(key_id)
        self._add_audit_log(key_id, 'ENABLE', '启用密钥')

        return {'success': True}

    def delete_key(self, key_id: str) -> Dict[str, Any]:
        """
        删除密钥（软删除）
        Args:
            key_id: 密钥ID
        Returns:
            {'success': bool}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        metadata = self.keys[key_id]
        metadata.status = KeyStatus.DELETED
        metadata.updated_at = datetime.now()
        self._save_key(key_id)
        self._add_audit_log(key_id, 'DELETE', '删除密钥')

        # 从内存中删除密钥材料
        if key_id in self.key_materials:
            del self.key_materials[key_id]

        return {'success': True}

    def rotate_key(self, key_id: str, new_key_material: str) -> Dict[str, Any]:
        """
        密钥轮换
        Args:
            key_id: 密钥ID
            new_key_material: 新密钥材料
        Returns:
            {'success': bool}
        """
        if key_id not in self.keys:
            return {'error': '密钥不存在'}

        metadata = self.keys[key_id]
        if metadata.status != KeyStatus.ACTIVE:
            return {'error': '只能轮换激活状态的密钥'}

        # 更新密钥材料
        self.key_materials[key_id] = new_key_material
        metadata.updated_at = datetime.now()
        self._save_key(key_id)
        self._add_audit_log(key_id, 'ROTATE', '密钥轮换')

        return {'success': True}

    def get_audit_logs(self, key_id: str = None) -> Dict[str, Any]:
        """
        获取审计日志
        Args:
            key_id: 可选，筛选特定密钥的日志
        Returns:
            {'logs': 审计日志列表}
        """
        if key_id:
            logs = [log.to_dict() for log in self.audit_logs if log.key_id == key_id]
        else:
            logs = [log.to_dict() for log in self.audit_logs]

        return {'logs': logs}
