FROM python:3.10-slim

# 시스템 패키지 설치
RUN apt update && apt install -y \
    build-essential \
    gcc \
    libpq-dev \
    libffi-dev \
    libssl-dev \
    rustc \
    curl \
    && apt clean

WORKDIR /app

COPY requirements.txt .
COPY ${FIREBASE_PATH} /app

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY app .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
