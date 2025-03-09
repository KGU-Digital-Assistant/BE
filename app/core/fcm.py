from cryptography.fernet import Fernet

from config import get_settings
from firebase_admin import credentials, storage, initialize_app,messaging

# 키 생성 (애플리케이션에서 한번만 생성하고 안전한 곳에 저장)
setting = get_settings()
cipher = Fernet(setting.FERNET_KEY)

# firebase json 경로
path = setting.FIREBASE_PATH

# firebase admin sdk 초기화
cred = credentials.Certificate(path)
default_app = initialize_app(cred, {'storageBucket': 'ieat-76bd6.appspot.com'})

bucket = storage.bucket()

def encrypt_token(token: str) -> str:
    """암호화"""
    return cipher.encrypt(token.encode()).decode()


def decrypt_token(encrypted_token: str) -> str:
    """복호화"""
    return cipher.decrypt(encrypted_token.encode()).decode()


#FCM 알림 보내는 함수
def send_fcm_notification(fcm_token,title, body):
    if fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            token=fcm_token,
        )
        try:
            response = messaging.send(message)
            print('Success sent msg:', response)
        except Exception as e:
            print('Fail send msg:',e)

def send_fcm_data_noti(fcm_token, title, body, data):
    if fcm_token:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body,
            ),
            data=data,
            token=fcm_token,
        )
        try:
            response = messaging.send(message)
            print('Success sent msg:', response)
        except Exception as e:
            print('Fail send msg:',e)

