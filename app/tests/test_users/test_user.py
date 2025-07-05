import uuid
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


# Helper - 테스트용 유저 생성
def create_test_user(username=None, password="securepassword123"):
    if not username:
        username = f"user_{uuid.uuid4().hex[:8]}"
    nickname = f"nick_{uuid.uuid4().hex[:8]}"
    email = f"{uuid.uuid4().hex[:8]}@example.com"
    cellphone = f"010{str(abs(hash(username)))[0:8]}"

    response = client.post("/api/v1/user/create", json={
        "username": username,
        "name": "Test User",
        "nickname": nickname,
        "cellphone": cellphone,
        "email": email,
        "password1": password,
        "password2": password,
        "gender": "MALE",
        "birth": "2000-01-01",
        "profile_picture": None,
    })
    assert response.status_code == 200, f"Failed to create user: {response.json()}"
    return username, password  # 로그인 때 username, password 리턴


# ---------------- 테스트 시작 ----------------

def test_create_user():
    username, password = create_test_user()
    response = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login():
    username, password = create_test_user()
    response = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    })
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_get_user_info():
    username, password = create_test_user()
    token = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/user/info", headers=headers)
    assert response.status_code == 200
    assert response.json()["username"] == username


def test_save_fcm_token():
    username, password = create_test_user()
    token = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/v1/user/fcm-token?token=test_fcm_token", headers=headers)
    assert response.status_code == 200
    # 저장된 fcm_token 값은 암호화돼 있으니 비교하지 말고 성공만 확인


def test_get_users_by_username():
    username, password = create_test_user()
    token = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.get(f"/api/v1/user/username?username={username}", headers=headers)  # 잘리지 말고 전체 검색
    assert response.status_code == 200
    assert any(u["username"] == username for u in response.json())


def test_update_user():
    username, password = create_test_user()
    token = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    new_nickname = f"updated_{uuid.uuid4().hex[:6]}"
    response = client.put("/api/v1/user/update", headers=headers, json={
        "nickname": new_nickname
    })
    assert response.status_code == 200
    assert response.json()["nickname"] == new_nickname


def test_delete_user():
    username, password = create_test_user()
    token = client.post("/api/v1/user/login", data={
        "username": username,
        "password": password,
    }).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}
    response = client.delete("/api/v1/user/delete", headers=headers)
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted"
