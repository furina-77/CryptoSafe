import sys
sys.path.insert(0, 'E:/crypto')
from services.crypto_service import AESService
print(AESService.generate_key(256))
