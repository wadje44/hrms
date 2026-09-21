import jwt
from fastapi.testclient import TestClient

from app.core.config import settings
from app.main import app

client = TestClient(app)


def test_invalid_role_in_jwt_is_rejected():
    token = jwt.encode(
        {"sub": "EMP008", "role": "not-a-real-role", "exp": 9999999999},
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM,
    )

    resp = client.get("/api/v1/dashboard/today", headers={"Authorization": f"Bearer {token}"})

    assert resp.status_code == 401
    assert "credentials" in resp.json()["detail"].lower()
