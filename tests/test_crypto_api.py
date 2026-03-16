"""
API 测试脚本
测试所有密码算法接口的正确性
"""
import requests
import base64
import json

BASE_URL = 'http://localhost:5000/api'


def test_aes():
    """测试 AES 加密解密"""
    print("=== 测试 AES ===")

    # 生成密钥
    resp = requests.post(f'{BASE_URL}/crypto/aes/generate-key', json={'key_size': 256})
    key = resp.json()['key']
    print(f"✓ AES 密钥生成: {key[:20]}...")

    # 加密
    plaintext = "Hello, CryptoSafe!"
    resp = requests.post(f'{BASE_URL}/crypto/aes/encrypt', json={
        'plaintext': plaintext,
        'key': key,
        'mode': 'CBC'
    })
    ciphertext = resp.json()['ciphertext']
    iv = resp.json()['iv']
    print(f"✓ AES 加密: {ciphertext[:20]}...")

    # 解密
    resp = requests.post(f'{BASE_URL}/crypto/aes/decrypt', json={
        'ciphertext': ciphertext,
        'key': key,
        'mode': 'CBC',
        'iv': iv
    })
    decrypted = resp.json()['plaintext']
    assert decrypted == plaintext, "AES 解密失败"
    print(f"✓ AES 解密验证通过: {decrypted}")
    print()


def test_rsa():
    """测试 RSA 加密解密和签名验签"""
    print("=== 测试 RSA ===")

    # 生成密钥对
    resp = requests.post(f'{BASE_URL}/crypto/rsa/generate-key-pair', json={'key_size': 2048})
    public_key = resp.json()['public_key']
    private_key = resp.json()['private_key']
    print("✓ RSA 密钥对生成")

    # 加密
    plaintext = "RSA test message"
    resp = requests.post(f'{BASE_URL}/crypto/rsa/encrypt', json={
        'plaintext': plaintext,
        'public_key': public_key
    })
    ciphertext = resp.json()['ciphertext']
    print(f"✓ RSA 加密: {ciphertext[:20]}...")

    # 解密
    resp = requests.post(f'{BASE_URL}/crypto/rsa/decrypt', json={
        'ciphertext': ciphertext,
        'private_key': private_key
    })
    decrypted = resp.json()['plaintext']
    assert decrypted == plaintext, "RSA 解密失败"
    print(f"✓ RSA 解密验证通过: {decrypted}")

    # 签名
    message = "Message to sign"
    resp = requests.post(f'{BASE_URL}/sign/rsa/sign', json={
        'message': message,
        'private_key': private_key
    })
    signature = resp.json()['signature']
    print(f"✓ RSA 签名: {signature[:20]}...")

    # 验签
    resp = requests.post(f'{BASE_URL}/sign/rsa/verify', json={
        'message': message,
        'signature': signature,
        'public_key': public_key
    })
    valid = resp.json()['valid']
    assert valid, "RSA 验签失败"
    print("✓ RSA 验签通过")
    print()


def test_hash():
    """测试哈希计算"""
    print("=== 测试哈希 ===")

    # SHA-256
    resp = requests.post(f'{BASE_URL}/hash/compute', json={
        'message': 'test',
        'algorithm': 'SHA-256'
    })
    hash_value = resp.json()['hash']
    print(f"✓ SHA-256: {hash_value}")

    # HMAC
    key = base64.b64encode(b'secret_key').decode('utf-8')
    resp = requests.post(f'{BASE_URL}/hash/hmac', json={
        'message': 'test',
        'key': key,
        'algorithm': 'SHA256'
    })
    hmac_value = resp.json()['hmac']
    print(f"✓ HMAC-SHA256: {hmac_value}")

    # 验证哈希
    resp = requests.post(f'{BASE_URL}/hash/verify', json={
        'message': 'test',
        'expected_hash': hash_value,
        'algorithm': 'SHA-256'
    })
    valid = resp.json()['valid']
    assert valid, "哈希验证失败"
    print("✓ 哈希验证通过")
    print()


def test_kms():
    """测试密钥管理系统"""
    print("=== 测试密钥管理系统 (KMS) ===")

    # 创建密钥
    key_material = base64.b64encode(os.urandom(32)).decode('utf-8')
    resp = requests.post(f'{BASE_URL}/keys/create', json={
        'algorithm': 'AES-256',
        'key_material': key_material,
        'key_type': 'symmetric',
        'description': '测试密钥',
        'tags': ['test'],
        'expires_in_days': 365
    })
    key_id = resp.json()['key_id']
    print(f"✓ 创建密钥: {key_id}")

    # 列出密钥
    resp = requests.get(f'{BASE_URL}/keys/')
    keys = resp.json()['keys']
    assert len(keys) > 0, "未找到密钥"
    print(f"✓ 密钥列表: 共 {len(keys)} 个")

    # 获取密钥元数据
    resp = requests.get(f'{BASE_URL}/keys/{key_id}')
    metadata = resp.json()['metadata']
    assert metadata['key_id'] == key_id, "密钥 ID 不匹配"
    print(f"✓ 密钥元数据: {metadata['algorithm']} {metadata['status']}")

    # 获取密钥材料
    resp = requests.get(f'{BASE_URL}/keys/{key_id}/material')
    material = resp.json()['key_material']
    assert material == key_material, "密钥材料不匹配"
    print("✓ 密钥材料获取成功")

    # 禁用密钥
    resp = requests.post(f'{BASE_URL}/keys/{key_id}/disable')
    assert resp.json()['success'], "禁用密钥失败"
    print("✓ 密钥禁用成功")

    # 获取审计日志
    resp = requests.get(f'{BASE_URL}/keys/{key_id}/audit')
    logs = resp.json()['logs']
    print(f"✓ 审计日志: 共 {len(logs)} 条")

    # 清理：删除密钥
    resp = requests.delete(f'{BASE_URL}/keys/{key_id}')
    assert resp.json()['success'], "删除密钥失败"
    print("✓ 密钥删除成功")
    print()


def run_all_tests():
    """运行所有测试"""
    try:
        print("开始测试 CryptoSafe API\n")
        test_aes()
        test_rsa()
        test_hash()
        test_kms()
        print("=" * 50)
        print("所有测试通过 ✓")
        print("=" * 50)
    except requests.exceptions.ConnectionError:
        print("错误: 无法连接到服务器，请确保 Flask 服务已启动")
        print("启动命令: E:\\Anaconda\\python.exe app.py")
    except AssertionError as e:
        print(f"测试失败: {e}")
    except Exception as e:
        print(f"未知错误: {e}")


if __name__ == '__main__':
    import os
    run_all_tests()
