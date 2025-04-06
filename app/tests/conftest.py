# tests/conftest.py
import os
from dotenv import load_dotenv

# 루트 디렉토리 기준으로 .env 로드
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
load_dotenv(dotenv_path=os.path.join(BASE_DIR, ".env"))
