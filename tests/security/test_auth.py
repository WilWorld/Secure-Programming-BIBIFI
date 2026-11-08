"""Login/logout security tests. Run from the project root:  pytest tests/security/test_auth.py
Uses an in-memory fake store, so no database is needed."""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest
from flask import Flask
from flask_login import login_required

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src", "backend"))
sys.path.insert(0, ROOT)  # inside the container the backend files live directly in /app

import auth  # noqa: E402
import auth_store  # noqa: E402
from fakes import PASSWORD, patch_store  # noqa: E402

def make_app(csrf=False):
    frontend = next(d for d in (os.path.join(ROOT, "src", "frontend"), os.path.join(ROOT, "frontend"))
                    if os.path.isdir(d))
    app = Flask(__name__, template_folder=os.path.join(frontend, "templates"),
                static_folder=os.path.join(frontend, "static"))
    app.config.update(SECRET_KEY="test-secret", TESTING=True,
                      WTF_CSRF_ENABLED=csrf, RATELIMIT_ENABLED=False)
    auth.init_auth(app)

    @app.route("/protected")
    @login_required
    def protected():
        return "secret page"

    @app.route("/")
    def home():
        return "home"

    return app


@pytest.fixture
def fake(monkeypatch):
    return patch_store(monkeypatch, auth_store)


@pytest.fixture
def client(fake):
    return make_app().test_client()


def login(client, user="alice", pw=PASSWORD):
    return client.post("/login", data={"username": user, "password": pw})


def test_login_success_redirects_and_audits(client, fake):
    r = login(client)
    assert r.status_code == 302
    assert (1, "LOGIN", "alice", "success") in fake.audit
    assert client.get("/protected").status_code == 200


def test_protected_page_requires_login(client):
    r = client.get("/protected")
    assert r.status_code == 302 and "/login" in r.headers["Location"]


def test_wrong_password_and_unknown_user_look_identical(client):
    a = login(client, "alice", "wrong-password")
    b = login(client, "nobody", "wrong-password")
    assert a.status_code == b.status_code == 401
    assert auth.GENERIC_ERROR.encode() in a.data
    assert auth.GENERIC_ERROR.encode() in b.data


def test_lockout_after_repeated_failures(client, fake):
    for _ in range(auth.MAX_FAILED_LOGINS):
        assert login(client, "alice", "wrong").status_code == 401
    assert login(client).status_code == 401  # correct password, still locked
    assert any(a[3] == "locked" for a in fake.audit)


def test_inactive_account_cannot_log_in(client):
    assert login(client, "bob").status_code == 401


def test_invalid_username_characters_rejected(client, fake):
    r = login(client, "alice' OR '1'='1", "x")
    assert r.status_code == 401
    assert any(a[3] == "invalid_input" for a in fake.audit)


def test_logout_requires_post(client):
    login(client)
    assert client.get("/logout").status_code == 405


def test_logout_revokes_session(client, fake):
    login(client)
    r = client.post("/logout")
    assert r.status_code == 302
    assert all(s["revoked"] for s in fake.sessions.values())
    assert client.get("/protected").status_code == 302


def test_revoked_session_is_rejected(client, fake):
    login(client)
    for s in fake.sessions.values():
        s["revoked"] = True
    assert client.get("/protected").status_code == 302


def test_session_cookie_flags(client):
    r = login(client)
    cookie = r.headers.get("Set-Cookie", "")
    assert "HttpOnly" in cookie and "SameSite=Lax" in cookie
    expires = cookie.split("Expires=")[1].split(";")[0]
    delta = datetime.strptime(expires, "%a, %d %b %Y %H:%M:%S GMT").replace(tzinfo=timezone.utc) - datetime.now(timezone.utc)
    assert timedelta(minutes=25) < delta < timedelta(minutes=35)


def test_csrf_token_required(fake):
    c = make_app(csrf=True).test_client()
    r = c.post("/login", data={"username": "alice", "password": PASSWORD})
    assert r.status_code == 400