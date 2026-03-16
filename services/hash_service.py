"""
哈希摘要服务
实现 MD5、SHA-256、SHA-512、SM3、HMAC
"""
import hashlib
import hmac
import base64
from typing import Dict, Any

try:
    from gmssl import func
    GMSSL_AVAILABLE = True
except ImportError:
    GMSSL_AVAILABLE = False


class HashService:
    """通用哈希服务"""

    @staticmethod
    def compute_hash(data: str, algorithm: str) -> Dict[str, Any]:
        """
        计算哈希值
        Args:
            data: 输入数据
            algorithm: 算法（MD5/SHA-256/SHA-512/SM3）
        Returns:
            {'hash': 哈希值(hex)}
        """
        try:
            data_bytes = data.encode('utf-8')

            if algorithm.upper() == 'MD5':
                hash_obj = hashlib.md5(data_bytes)
            elif algorithm.upper() in ['SHA256', 'SHA-256']:
                hash_obj = hashlib.sha256(data_bytes)
            elif algorithm.upper() in ['SHA512', 'SHA-512']:
                hash_obj = hashlib.sha512(data_bytes)
            elif algorithm.upper() == 'SM3':
                if not GMSSL_AVAILABLE:
                    return {'error': 'gmssl 库未安装，无法使用 SM3'}
                hash_hex = func.sm3_hash(data_bytes)
                return {'hash': hash_hex}
            else:
                return {'error': f'不支持的哈希算法: {algorithm}'}

            return {'hash': hash_obj.hexdigest()}
        except Exception as e:
            return {'error': f'哈希计算失败: {str(e)}'}

    @staticmethod
    def compute_hmac(data: str, key: str, algorithm: str = 'SHA256') -> Dict[str, Any]:
        """
        计算 HMAC
        Args:
            data: 输入数据
            key: Base64 编码的密钥
            algorithm: 算法（SHA256/SHA512）
        Returns:
            {'hmac': HMAC值(hex)}
        """
        try:
            data_bytes = data.encode('utf-8')
            key_bytes = base64.b64decode(key)

            if algorithm.upper() in ['SHA256', 'SHA-256']:
                hash_obj = hashlib.sha256
            elif algorithm.upper() in ['SHA512', 'SHA-512']:
                hash_obj = hashlib.sha512
            else:
                return {'error': f'HMAC 不支持该算法: {algorithm}'}

            hmac_obj = hmac.new(key_bytes, data_bytes, hash_obj)
            return {'hmac': hmac_obj.hexdigest()}
        except Exception as e:
            return {'error': f'HMAC 计算失败: {str(e)}'}

    @staticmethod
    def verify_hash(data: str, expected_hash: str, algorithm: str) -> Dict[str, Any]:
        """
        验证哈希值
        Args:
            data: 原始数据
            expected_hash: 期望的哈希值
            algorithm: 算法
        Returns:
            {'valid': bool}
        """
        result = HashService.compute_hash(data, algorithm)
        if 'error' in result:
            return result

        return {'valid': result['hash'].lower() == expected_hash.lower()}

    @staticmethod
    def verify_hmac(data: str, key: str, expected_hmac: str, algorithm: str = 'SHA256') -> Dict[str, Any]:
        """
        验证 HMAC 值
        Args:
            data: 原始数据
            key: Base64 编码的密钥
            expected_hmac: 期望的 HMAC 值
            algorithm: 算法
        Returns:
            {'valid': bool}
        """
        result = HashService.compute_hmac(data, key, algorithm)
        if 'error' in result:
            return result

        return {'valid': result['hmac'].lower() == expected_hmac.lower()}

    @staticmethod
    def compare_hashes(hash1: str, hash2: str) -> Dict[str, Any]:
        """
        安全比较两个哈希值（防止时序攻击）
        Args:
            hash1: 哈希值1
            hash2: 哈希值2
        Returns:
            {'equal': bool}
        """
        try:
            equal = hmac.compare_digest(hash1.encode('utf-8'), hash2.encode('utf-8'))
            return {'equal': equal}
        except Exception as e:
            return {'error': f'哈希比较失败: {str(e)}'}
