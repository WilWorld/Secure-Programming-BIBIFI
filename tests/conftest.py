"""Shared pytest fixtures for the test suite.

The Flask app and its stores need PostgreSQL, so for tests we swap the
store modules for the in-memory fakes in ``tests/fakes.py``.  No database
or Docker is required.
"""
import importlib
import os
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, os.path.join(ROOT, "tests"))
sys.path.insert(0, os.path.join(ROOT, "src", "backend"))
sys.path.insert(0, ROOT)

import auth_store  # noqa: E402
import gallery_store  # noqa: E402,F401
from fakes import PASSWORD, patch_store  # noqa: E402

app_module = importlib.import_module("app")

TEST_CONFIG = {
    "TESTING": True,
    "SECRET_KEY": "test-secret",
    "WTF_CSRF_ENABLED": False,
    "RATELIMIT_ENABLED": False,
    "SESSION_COOKIE_SECURE": False,
}


@pytest.fixture
def fake(monkeypatch):
    return patch_store(monkeypatch, auth_store)


@pytest.fixture
def app(fake):
    return app_module.create_app(dict(TEST_CONFIG))


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def login():
    def _login(test_client, username="guest1", password=PASSWORD):
        return test_client.post(
            "/login", data={"username": username, "password": password}
        )

    return _login


def _logged_in(app, username):
    test_client = app.test_client()
    response = test_client.post(
        "/login", data={"username": username, "password": PASSWORD}
    )
    assert response.status_code == 302, f"login as {username} failed"
    return test_client


@pytest.fixture
def guest_client(app):
    return _logged_in(app, "guest1")


@pytest.fixture
def employee_client(app):
    return _logged_in(app, "employee1")


@pytest.fixture
def admin_client(app):
    return _logged_in(app, "administrator1")
