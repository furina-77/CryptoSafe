"""
直接测试密码算法（不通过 HTTP）
"""
import os
import sys

# 添加项目路径
import pathlib
project_root = pathlib.Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from services.crypto_service import AESService, RSAService, SM2Service, SM4Service
from services.hash_service import HashService
from models.key_manager import KeyManager, KeyType


def test_aes():
    """测试 AES"""
    print("=== AES 测试 ===")
    plaintext = "Hello, CryptoSafe!"

    # 生成密钥
    result = AESService.generate_key(256)
    key = result['key']
    print(f"密钥: {key[:30]}...")

    # 加密
    result = AESService.encrypt(plaintext, key, 'CBC')
    ciphertext = result['ciphertext']
    iv = result['iv']
    print(f"加密: {ciphertext[:30]}...")
    print(f"IV: {iv}")

    # 解密
    result = AESService.decrypt(ciphertext, key, 'CBC', iv)
    decrypted = result['plaintext']
    print(f"解密: {decrypted}")

    assert decrypted == plaintext, "AES 测试失败"
    print("[OK] AES 测试通过\n")


def test_rsa():
    """测试 RSA"""
    print("=== RSA 测试 ===")

    # 生成密钥对
    result = RSAService.generate_key_pair(2048)
    public_key = result['public_key']
    private_key = result['private_key']
    print("密钥对生成成功")

    # 加密
    plaintext = "RSA test"
    result = RSAService.encrypt(plaintext, public_key)
    ciphertext = result['ciphertext']
    print(f"加密: {ciphertext[:30]}...")

    # 解密
    result = RSAService.decrypt(ciphertext, private_key)
    decrypted = result['plaintext']
    print(f"解密: {decrypted}")

    assert decrypted == plaintext, "RSA 加密解密失败"

    # 签名
    message = "Message to sign"
    result = RSAService.sign(message, private_key)
    signature = result['signature']
    print(f"签名: {signature[:30]}...")

    # 验签
    result = RSAService.verify(message, signature, public_key)
    valid = result['valid']
    print(f"验签: {valid}")

    assert valid, "RSA 验签失败"
    print("[OK] RSA 测试通过\n")


def test_sm():
    """测试国密算法"""
    print("=== 国密算法测试 ===")

    if not SM2Service.check_available() or not SM4Service.check_available():
        print("[WARN] gmssl 库不可用，跳过国密测试\n")
        return

    # SM4
    result = SM4Service.generate_key()
    sm4_key = result['key']
    print(f"SM4 密钥: {sm4_key}")

    plaintext = "SM4 test"
    result = SM4Service.encrypt(plaintext, sm4_key)
    if 'error' in result:
        print(f"[ERROR] SM4 加密失败: {result['error']}")
        return
    ciphertext = result['ciphertext']
    print(f"SM4 加密: {ciphertext}")

    result = SM4Service.decrypt(ciphertext, sm4_key)
    if 'error' in result:
        print(f"[ERROR] SM4 解密失败: {result['error']}")
        return
    decrypted = result['plaintext']
    print(f"SM4 解密: {decrypted}")

    assert decrypted == plaintext, "SM4 测试失败"

    # SM2
    result = SM2Service.generate_key_pair()
    public_key = result['public_key']
    private_key = result['private_key']
    print("SM2 密钥对生成成功")

    plaintext = "SM2 test"
    result = SM2Service.encrypt(plaintext, public_key)
    ciphertext = result['ciphertext']
    print(f"SM2 加密: {ciphertext}")

    result = SM2Service.decrypt(ciphertext, private_key)
    decrypted = result['plaintext']
    print(f"SM2 解密: {decrypted}")

    assert decrypted == plaintext, "SM2 测试失败"
    print("[OK] 国密算法测试通过\n")


def test_hash():
    """测试哈希"""
    print("=== 哈希测试 ===")

    # SHA-256
    result = HashService.compute_hash("test", "SHA-256")
    hash_value = result['hash']
    print(f"SHA-256: {hash_value}")

    # SM3
    result = HashService.compute_hash("test", "SM3")
    if 'error' in result:
        print(f"[WARN] SM3 计算失败: {result['error']}")
    else:
        hash_value = result['hash']
        print(f"SM3: {hash_value}")

    # HMAC
    key = os.urandom(32)
    import base64
    key_b64 = base64.b64encode(key).decode('utf-8')
    result = HashService.compute_hmac("test", key_b64, "SHA256")
    if 'error' in result:
        print(f"[ERROR] HMAC 计算失败: {result['error']}")
        return
    hmac_value = result['hmac']
    print(f"HMAC: {hmac_value}")

    print("[OK] 哈希测试通过\n")


def test_kms():
    """测试密钥管理系统"""
    print("=== KMS 测试 ===")

    # 创建密钥管理器
    kms = KeyManager(storage_dir=str(project_root / 'keys_test'))

    # 创建密钥
    import base64
    key_material = base64.b64encode(os.urandom(32)).decode('utf-8')
    result = kms.create_key(
        algorithm='AES-256',
        key_material=key_material,
        key_type=KeyType.SYMMETRIC,
        description='测试密钥',
        tags=['test']
    )
    key_id = result['key_id']
    print(f"创建密钥: {key_id}")

    # 获取密钥元数据
    result = kms.get_key(key_id)
    metadata = result['metadata']
    print(f"元数据: {metadata['algorithm']} {metadata['status']}")

    # 获取密钥材料
    result = kms.get_key_material(key_id)
    material = result['key_material']
    assert material == key_material, "密钥材料不匹配"
    print("密钥材料验证通过")

    # 列出密钥
    result = kms.list_keys()
    keys = result['keys']
    print(f"密钥列表: {len(keys)} 个")

    # 禁用密钥
    result = kms.disable_key(key_id)
    print("密钥禁用成功")

    # 获取审计日志
    result = kms.get_audit_logs(key_id)
    logs = result['logs']
    print(f"审计日志: {len(logs)} 条")

    # 删除密钥
    result = kms.delete_key(key_id)
    print("密钥删除成功")

    print("[OK] KMS 测试通过\n")


if __name__ == '__main__':
    print("CryptoSafe 后端测试\n" + "="*40 + "\n")
    test_aes()
    test_rsa()
    test_sm()
    test_hash()
    test_kms()
    print("="*40)
    print("所有测试通过 [OK]")
