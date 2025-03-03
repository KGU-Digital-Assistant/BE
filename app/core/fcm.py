from cryptography.fernet import Fernet

from config import get_settings

# 키 생성 (애플리케이션에서 한번만 생성하고 안전한 곳에 저장)
setting = get_settings()
cipher = Fernet(setting.FERNET_KEY)


def encrypt_token(token: str) -> str:
    """암호화"""
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """복호화"""
    return cipher.decrypt(encrypted_token.encode()).decode()

