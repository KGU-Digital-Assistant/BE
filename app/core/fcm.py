from cryptography.fernet import Fernet

from config import get_settings

# 키 생성 (애플리케이션에서 한번만 생성하고 안전한 곳에 저장)
setting = get_settings()
cipher = Fernet(setting.FERNET_KEY)


# 암호화
def encrypt_token(token: str) -> str:
    return cipher.encrypt(token.encode()).decode()


# 복호화
def decrypt_token(encrypted_token: str) -> str:
    return cipher.decrypt(encrypted_token.encode()).decode()


# 사용 예제
fcm_token = "your-fcm-token"
encrypted_token = encrypt_token(fcm_token)
print(f"Encrypted Token: {encrypted_token}")
decrypted_token = decrypt_token(encrypted_token)
print(f"Decrypted Token: {decrypted_token}")
