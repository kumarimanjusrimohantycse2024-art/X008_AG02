from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, hash_password, verify_password
from app.db.session import SessionLocal
from app.main import app
from app.models import Job, JobStatus, User, UserRole

client = TestClient(app)


@pytest.fixture
def auth_records() -> dict[str, object]:
    session = SessionLocal()
    suffix = uuid4().hex
    password = "correct-horse-battery"
    users = {
        "recruiter_a": User(email=f"recruiter-a-{suffix}@example.test", password_hash=hash_password(password), name="Recruiter A", role=UserRole.RECRUITER),
        "recruiter_b": User(email=f"recruiter-b-{suffix}@example.test", password_hash=hash_password(password), name="Recruiter B", role=UserRole.RECRUITER),
        "admin": User(email=f"admin-{suffix}@example.test", password_hash=hash_password(password), name="Admin", role=UserRole.ADMIN),
    }
    session.add_all(users.values())
    session.flush()
    jobs = {
        "job_a": Job(title="Job A", description="A", status=JobStatus.DRAFT, created_by=users["recruiter_a"].id),
        "job_b": Job(title="Job B", description="B", status=JobStatus.DRAFT, created_by=users["recruiter_b"].id),
    }
    session.add_all(jobs.values())
    session.commit()
    records = {**users, **jobs, "password": password}
    try:
        yield records
    finally:
        session.delete(jobs["job_a"])
        session.delete(jobs["job_b"])
        session.flush()
        for user in users.values():
            session.delete(user)
        session.commit()
        session.close()


def login(email: str, password: str) -> dict[str, object]:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()


def auth_header(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_password_hashing_and_verification() -> None:
    password_hash = hash_password("a-secure-password")
    assert password_hash != "a-secure-password"
    assert verify_password("a-secure-password", password_hash)
    assert not verify_password("wrong-password", password_hash)
    with pytest.raises(ValueError):
        hash_password("short")


def test_login_success_and_safe_response(auth_records: dict[str, object]) -> None:
    user = auth_records["recruiter_a"]
    response = login(user.email, auth_records["password"])
    assert response["token_type"] == "bearer"
    assert response["expires_in"] > 0
    assert response["user"]["role"] == "RECRUITER"
    assert "password_hash" not in response["user"]
    claims = jwt.decode(response["access_token"], get_settings().jwt_secret, algorithms=["HS256"])
    assert set(claims) == {"sub", "role", "type", "iat", "exp"}


def test_login_failure_is_generic(auth_records: dict[str, object]) -> None:
    user = auth_records["recruiter_a"]
    bad_password = client.post("/api/auth/login", json={"email": user.email, "password": "wrong-password"})
    missing_user = client.post("/api/auth/login", json={"email": "missing@example.test", "password": "wrong-password"})
    assert bad_password.status_code == 401
    assert missing_user.status_code == 401
    assert bad_password.json() == missing_user.json() == {"detail": "Invalid email or password."}


def test_me_and_missing_or_invalid_tokens(auth_records: dict[str, object]) -> None:
    user = auth_records["recruiter_a"]
    token = login(user.email, auth_records["password"])["access_token"]
    response = client.get("/api/auth/me", headers=auth_header(token))
    assert response.status_code == 200
    assert response.json()["email"] == user.email
    assert "password_hash" not in response.json()
    assert client.get("/api/auth/me").status_code == 401
    assert client.get("/api/auth/me", headers=auth_header("not-a-token")).status_code == 401


def test_expired_token_is_rejected(auth_records: dict[str, object]) -> None:
    user = auth_records["recruiter_a"]
    now = datetime.now(timezone.utc)
    token = jwt.encode({"sub": str(user.id), "role": "RECRUITER", "type": "access", "iat": now - timedelta(hours=2), "exp": now - timedelta(minutes=1)}, get_settings().jwt_secret, algorithm="HS256")
    assert client.get("/api/auth/me", headers=auth_header(token)).status_code == 401


def test_token_for_missing_user_is_rejected() -> None:
    token, _ = create_access_token(uuid4(), "RECRUITER")
    assert client.get("/api/auth/me", headers=auth_header(token)).status_code == 401


def test_admin_endpoint_and_role_denial(auth_records: dict[str, object]) -> None:
    admin = auth_records["admin"]
    recruiter = auth_records["recruiter_a"]
    admin_token = login(admin.email, auth_records["password"])["access_token"]
    recruiter_token = login(recruiter.email, auth_records["password"])["access_token"]
    assert client.get("/api/admin/users", headers=auth_header(admin_token)).status_code == 200
    assert client.get("/api/admin/users", headers=auth_header(recruiter_token)).status_code == 403


def test_cross_recruiter_job_ownership(auth_records: dict[str, object]) -> None:
    recruiter_a = auth_records["recruiter_a"]
    recruiter_b = auth_records["recruiter_b"]
    admin = auth_records["admin"]
    token_a = login(recruiter_a.email, auth_records["password"])["access_token"]
    token_b = login(recruiter_b.email, auth_records["password"])["access_token"]
    admin_token = login(admin.email, auth_records["password"])["access_token"]
    assert client.get(f"/api/jobs/{auth_records['job_a'].id}", headers=auth_header(token_a)).status_code == 200
    assert client.get(f"/api/jobs/{auth_records['job_b'].id}", headers=auth_header(token_a)).status_code == 404
    assert client.get(f"/api/jobs/{auth_records['job_a'].id}", headers=auth_header(token_b)).status_code == 404
    assert client.get(f"/api/jobs/{auth_records['job_a'].id}", headers=auth_header(admin_token)).status_code == 200


def test_recruiter_can_create_owned_job(auth_records: dict[str, object]) -> None:
    recruiter = auth_records["recruiter_a"]
    token = login(recruiter.email, auth_records["password"])["access_token"]
    response = client.post("/api/jobs", headers=auth_header(token), json={"title": "Owned job", "description": "Owned"})
    assert response.status_code == 201
    assert response.json()["created_by"] == str(recruiter.id)
    with SessionLocal() as session:
        created = session.get(Job, response.json()["id"])
        assert created is not None
        session.delete(created)
        session.commit()
