"""
密码算法核心服务
实现 AES、RSA、SM2、SM4 等算法的加密解密
"""
import os
import base64
from typing import Tuple, Dict, Any
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, serialization, padding
from cryptography.hazmat.primitives.asymmetric import rsa, padding as asym_padding
from cryptography.hazmat.primitives.asymmetric import utils as asym_utils
from cryptography.hazmat.backends import default_backend

try:
    from gmssl import sm2, sm4, func
    GMSSL_AVAILABLE = True
except ImportError:
    GMSSL_AVAILABLE = False


class AESService:
    """AES 对称加密服务"""

    @staticmethod
    def encrypt(plaintext: str, key: str, mode: str = 'CBC', iv: str = None) -> Dict[str, Any]:
        """
        AES 加密
        Args:
            plaintext: 明文
            key: Base64 编码的密钥（16/24/32 字节对应 AES-128/192/256）
            mode: 模式（CBC/ECB/CTR）
            iv: Base64 编码的初始向量（CBC/CTR 需要）
        Returns:
            {'ciphertext': base64密文, 'iv': base64初始向量}
        """
        try:
            key_bytes = base64.b64decode(key)
            data = plaintext.encode('utf-8')

            # CBC 模式
            if mode.upper() == 'CBC':
                if iv is None:
                    iv_bytes = os.urandom(16)
                else:
                    iv_bytes = base64.b64decode(iv)

                cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
                encryptor = cipher.encryptor()

                # PKCS7 填充
                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()

                ciphertext = encryptor.update(padded_data) + encryptor.finalize()
                return {
                    'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                    'iv': base64.b64encode(iv_bytes).decode('utf-8'),
                    'mode': 'CBC'
                }

            # ECB 模式
            elif mode.upper() == 'ECB':
                cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
                encryptor = cipher.encryptor()

                padder = padding.PKCS7(128).padder()
                padded_data = padder.update(data) + padder.finalize()

                ciphertext = encryptor.update(padded_data) + encryptor.finalize()
                return {
                    'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                    'mode': 'ECB'
                }

            # CTR 模式
            elif mode.upper() == 'CTR':
                if iv is None:
                    nonce = os.urandom(16)
                else:
                    nonce = base64.b64decode(iv)

                cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
                encryptor = cipher.encryptor()

                ciphertext = encryptor.update(data) + encryptor.finalize()
                return {
                    'ciphertext': base64.b64encode(ciphertext).decode('utf-8'),
                    'iv': base64.b64encode(nonce).decode('utf-8'),
                    'mode': 'CTR'
                }

            else:
                return {'error': f'不支持的 AES 模式: {mode}'}

        except Exception as e:
            return {'error': f'AES 加密失败: {str(e)}'}

    @staticmethod
    def decrypt(ciphertext: str, key: str, mode: str, iv: str = None) -> Dict[str, Any]:
        """
        AES 解密
        Args:
            ciphertext: Base64 编码的密文
            key: Base64 编码的密钥
            mode: 模式（CBC/ECB/CTR）
            iv: Base64 编码的初始向量（CBC/CTR 需要）
        Returns:
            {'plaintext': 解密后的明文}
        """
        try:
            key_bytes = base64.b64decode(key)
            ct = base64.b64decode(ciphertext)

            if mode.upper() == 'CBC':
                if iv is None:
                    return {'error': 'CBC 模式需要 IV'}
                iv_bytes = base64.b64decode(iv)

                cipher = Cipher(algorithms.AES(key_bytes), modes.CBC(iv_bytes), backend=default_backend())
                decryptor = cipher.decryptor()

                padded_data = decryptor.update(ct) + decryptor.finalize()

                # 去除 PKCS7 填充
                unpadder = padding.PKCS7(128).unpadder()
                data = unpadder.update(padded_data) + unpadder.finalize()

                return {'plaintext': data.decode('utf-8')}

            elif mode.upper() == 'ECB':
                cipher = Cipher(algorithms.AES(key_bytes), modes.ECB(), backend=default_backend())
                decryptor = cipher.decryptor()

                padded_data = decryptor.update(ct) + decryptor.finalize()

                unpadder = padding.PKCS7(128).unpadder()
                data = unpadder.update(padded_data) + unpadder.finalize()

                return {'plaintext': data.decode('utf-8')}

            elif mode.upper() == 'CTR':
                if iv is None:
                    return {'error': 'CTR 模式需要 nonce'}
                nonce = base64.b64decode(iv)

                cipher = Cipher(algorithms.AES(key_bytes), modes.CTR(nonce), backend=default_backend())
                decryptor = cipher.decryptor()

                data = decryptor.update(ct) + decryptor.finalize()

                return {'plaintext': data.decode('utf-8')}

            else:
                return {'error': f'不支持的 AES 模式: {mode}'}

        except Exception as e:
            return {'error': f'AES 解密失败: {str(e)}'}

    @staticmethod
    def generate_key(key_size: int = 256) -> Dict[str, Any]:
        """
        生成 AES 密钥
        Args:
            key_size: 密钥位数（128/192/256）
        Returns:
            {'key': base64编码的密钥}
        """
        try:
            key_bytes = os.urandom(key_size // 8)
            return {
                'key': base64.b64encode(key_bytes).decode('utf-8'),
                'size': key_size,
                'algorithm': f'AES-{key_size}'
            }
        except Exception as e:
            return {'error': f'密钥生成失败: {str(e)}'}


class RSAService:
    """RSA 非对称加密服务"""

    @staticmethod
    def generate_key_pair(key_size: int = 2048) -> Dict[str, Any]:
        """
        生成 RSA 密钥对
        Args:
            key_size: 密钥位数（1024/2048/4096）
        Returns:
            {'public_key': 公钥PEM, 'private_key': 私钥PEM}
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=key_size,
                backend=default_backend()
            )
            public_key = private_key.public_key()

            # 导出为 PEM 格式
            pem_private = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )

            pem_public = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )

            return {
                'public_key': pem_public.decode('utf-8'),
                'private_key': pem_private.decode('utf-8'),
                'key_size': key_size
            }
        except Exception as e:
            return {'error': f'RSA 密钥对生成失败: {str(e)}'}

    @staticmethod
    def encrypt(plaintext: str, public_key_pem: str) -> Dict[str, Any]:
        """
        RSA 加密（OAEP 填充）
        Args:
            plaintext: 明文
            public_key_pem: 公钥 PEM 格式
        Returns:
            {'ciphertext': base64密文}
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )

            data = plaintext.encode('utf-8')
            ciphertext = public_key.encrypt(
                data,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            return {'ciphertext': base64.b64encode(ciphertext).decode('utf-8')}
        except Exception as e:
            return {'error': f'RSA 加密失败: {str(e)}'}

    @staticmethod
    def decrypt(ciphertext: str, private_key_pem: str) -> Dict[str, Any]:
        """
        RSA 解密（OAEP 填充）
        Args:
            ciphertext: Base64 编码的密文
            private_key_pem: 私钥 PEM 格式
        Returns:
            {'plaintext': 解密后的明文}
        """
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )

            ct = base64.b64decode(ciphertext)
            plaintext = private_key.decrypt(
                ct,
                asym_padding.OAEP(
                    mgf=asym_padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            return {'plaintext': plaintext.decode('utf-8')}
        except Exception as e:
            return {'error': f'RSA 解密失败: {str(e)}'}

    @staticmethod
    def sign(message: str, private_key_pem: str) -> Dict[str, Any]:
        """
        RSA 签名（PSS 填充）
        Args:
            message: 待签名消息
            private_key_pem: 私钥 PEM 格式
        Returns:
            {'signature': base64签名}
        """
        try:
            private_key = serialization.load_pem_private_key(
                private_key_pem.encode('utf-8'),
                password=None,
                backend=default_backend()
            )

            data = message.encode('utf-8')
            signature = private_key.sign(
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return {'signature': base64.b64encode(signature).decode('utf-8')}
        except Exception as e:
            return {'error': f'RSA 签名失败: {str(e)}'}

    @staticmethod
    def verify(message: str, signature: str, public_key_pem: str) -> Dict[str, Any]:
        """
        RSA 验签
        Args:
            message: 原始消息
            signature: Base64 编码的签名
            public_key_pem: 公钥 PEM 格式
        Returns:
            {'valid': bool}
        """
        try:
            public_key = serialization.load_pem_public_key(
                public_key_pem.encode('utf-8'),
                backend=default_backend()
            )

            data = message.encode('utf-8')
            sig = base64.b64decode(signature)

            public_key.verify(
                sig,
                data,
                asym_padding.PSS(
                    mgf=asym_padding.MGF1(hashes.SHA256()),
                    salt_length=asym_padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )

            return {'valid': True}
        except Exception as e:
            return {'valid': False, 'error': str(e)}


class SM2Service:
    """SM2 国密算法服务（需要 gmssl 库）"""

    @staticmethod
    def check_available() -> bool:
        """检查 gmssl 是否可用"""
        return GMSSL_AVAILABLE

    @staticmethod
    def generate_key_pair() -> Dict[str, Any]:
        """生成 SM2 密钥对"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM2'}

        try:
            sm2_key = sm2.CryptSM2(
                public_key='',
                private_key='',
                mode=sm2.CRYPT_MODE_CBC
            )

            # 生成私钥
            private_key = sm2_key.private_key_generate()

            # 从私钥导出公钥
            sm2_key.private_key = private_key
            public_key = sm2_key.public_key

            return {
                'public_key': public_key,
                'private_key': private_key
            }
        except Exception as e:
            return {'error': f'SM2 密钥对生成失败: {str(e)}'}

    @staticmethod
    def encrypt(plaintext: str, public_key: str) -> Dict[str, Any]:
        """SM2 加密"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM2'}

        try:
            sm2_crypt = sm2.CryptSM2(
                public_key=public_key,
                private_key='',
                mode=sm2.CRYPT_MODE_CBC
            )

            ciphertext = sm2_crypt.encrypt(plaintext.encode('utf-8'))
            return {'ciphertext': ciphertext.hex()}
        except Exception as e:
            return {'error': f'SM2 加密失败: {str(e)}'}

    @staticmethod
    def decrypt(ciphertext_hex: str, private_key: str) -> Dict[str, Any]:
        """SM2 解密"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM2'}

        try:
            sm2_crypt = sm2.CryptSM2(
                public_key='',
                private_key=private_key,
                mode=sm2.CRYPT_MODE_CBC
            )

            ciphertext = bytes.fromhex(ciphertext_hex)
            plaintext = sm2_crypt.decrypt(ciphertext)
            return {'plaintext': plaintext.decode('utf-8')}
        except Exception as e:
            return {'error': f'SM2 解密失败: {str(e)}'}

    @staticmethod
    def sign(message: str, private_key: str, user_id: str = '1234567812345678') -> Dict[str, Any]:
        """
        SM2 签名
        Args:
            message: 待签名消息
            private_key: SM2 私钥
            user_id: 用户标识（16进制字符串，默认为空）
        Returns:
            {'signature': 签名(hex)}
        """
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM2'}

        try:
            sm2_key = sm2.CryptSM2(
                public_key='',
                private_key=private_key
            )

            # 先用 SM3 计算摘要
            sm3_digest = func.sm3_hash(message.encode('utf-8'))

            signature = sm2_key.sign(sm3_digest, user_id.encode('utf-8'))
            return {'signature': signature.hex()}
        except Exception as e:
            return {'error': f'SM2 签名失败: {str(e)}'}

    @staticmethod
    def verify(message: str, signature_hex: str, public_key: str, user_id: str = '1234567812345678') -> Dict[str, Any]:
        """
        SM2 验签
        Args:
            message: 原始消息
            signature_hex: 签名(hex)
            public_key: SM2 公钥
            user_id: 用户标识
        Returns:
            {'valid': bool}
        """
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM2'}

        try:
            sm2_key = sm2.CryptSM2(
                public_key=public_key,
                private_key=''
            )

            sm3_digest = func.sm3_hash(message.encode('utf-8'))
            signature = bytes.fromhex(signature_hex)

            valid = sm2_key.verify(signature, sm3_digest, user_id.encode('utf-8'))
            return {'valid': valid}
        except Exception as e:
            return {'valid': False, 'error': str(e)}


class SM4Service:
    """SM4 国密对称加密服务"""

    @staticmethod
    def check_available() -> bool:
        """检查 gmssl 是否可用"""
        return GMSSL_AVAILABLE

    @staticmethod
    def generate_key() -> Dict[str, Any]:
        """生成 SM4 密钥（128位）"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM4'}

        try:
            key = os.urandom(16)
            return {
                'key': key.hex(),
                'algorithm': 'SM4'
            }
        except Exception as e:
            return {'error': f'SM4 密钥生成失败: {str(e)}'}

    @staticmethod
    def encrypt(plaintext: str, key_hex: str) -> Dict[str, Any]:
        """SM4 加密（ECB 模式）"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM4'}

        try:
            key = bytes.fromhex(key_hex)
            sm4_crypt = sm4.CryptSM4(key, sm4.SM4_ENCRYPT)

            # PKCS7 填充
            data = plaintext.encode('utf-8')
            block_size = 16
            padding_len = block_size - (len(data) % block_size)
            padded_data = data + bytes([padding_len] * padding_len)

            ciphertext = sm4_crypt.crypt_ecb(padded_data)
            return {'ciphertext': ciphertext.hex()}
        except Exception as e:
            return {'error': f'SM4 加密失败: {str(e)}'}

    @staticmethod
    def decrypt(ciphertext_hex: str, key_hex: str) -> Dict[str, Any]:
        """SM4 解密（ECB 模式）"""
        if not GMSSL_AVAILABLE:
            return {'error': 'gmssl 库未安装，无法使用 SM4'}

        try:
            key = bytes.fromhex(key_hex)
            ciphertext = bytes.fromhex(ciphertext_hex)

            sm4_crypt = sm4.CryptSM4(key, sm4.SM4_DECRYPT)
            padded_data = sm4_crypt.crypt_ecb(ciphertext)

            # 去除 PKCS7 填充
            padding_len = padded_data[-1]
            data = padded_data[:-padding_len]

            return {'plaintext': data.decode('utf-8')}
        except Exception as e:
            return {'error': f'SM4 解密失败: {str(e)}'}
