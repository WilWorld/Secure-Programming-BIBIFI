"""SQL injection tests.

Two layers:

* ``test_*_is_parameterized`` / ``test_*_allowlist`` call the real store
  functions with a recording "engine" and assert the attacker payload is
  sent as a bound parameter (or dropped by an allowlist), never pasted
  into the SQL text.  This is the actual defence; it needs no database.

* ``test_route_*`` drive the HTTP endpoints with the in-memory fake store
  to prove malicious input is rejected before it reaches the store.
"""
import pytest

import auth_store
import gallery_store

PAYLOADS = [
    "' OR '1'='1",
    "'; DROP TABLE users;--",
    "1); DROP TABLE users;--",
    "admin'--",
]


class _Result:
    def mappings(self):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def scalar_one_or_none(self):
        return None


class _RecordingConnection:
    def __init__(self, log):
        self._log = log

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, statement, params=None):
        self._log.append((str(statement), params))
        return _Result()


class _RecordingEngine:
    def __init__(self):
        self.log = []

    def connect(self):
        return _RecordingConnection(self.log)

    def begin(self):
        return _RecordingConnection(self.log)


def install_recording_engine(monkeypatch):
    engine = _RecordingEngine()
    monkeypatch.setattr(auth_store, "engine", lambda: engine)
    return engine


# --------------------------------------------------------------- parameterized
@pytest.mark.parametrize("payload", PAYLOADS)
def test_username_lookup_is_parameterized(monkeypatch, payload):
    engine = install_recording_engine(monkeypatch)
    auth_store.get_user_by_username(payload)

    sql, params = engine.log[-1]
    assert payload not in sql
    assert payload in params.values()


@pytest.mark.parametrize("payload", PAYLOADS)
def test_room_lookup_is_parameterized(monkeypatch, payload):
    engine = install_recording_engine(monkeypatch)
    gallery_store.get_room(payload)

    sql, params = engine.log[-1]
    assert payload not in sql
    assert payload in params.values()


@pytest.mark.parametrize("payload", PAYLOADS)
def test_art_lookup_is_parameterized(monkeypatch, payload):
    engine = install_recording_engine(monkeypatch)
    gallery_store.list_art(payload)

    sql, params = engine.log[-1]
    assert payload not in sql
    assert payload in params.values()


@pytest.mark.parametrize("payload", PAYLOADS)
def test_update_role_is_parameterized(monkeypatch, payload):
    engine = install_recording_engine(monkeypatch)
    gallery_store.update_role(payload, "guest")

    sql, params = engine.log[-1]
    assert payload not in sql
    assert payload in params.values()


@pytest.mark.parametrize("payload", PAYLOADS)
def test_create_user_is_parameterized(monkeypatch, payload):
    engine = install_recording_engine(monkeypatch)
    auth_store.create_user(payload, "argon2-hash")

    sql, params = engine.log[-1]
    assert payload not in sql
    assert payload in params.values()


# ------------------------------------------------------------------- allowlist
def test_event_sort_column_allowlist_blocks_injection(monkeypatch):
    engine = install_recording_engine(monkeypatch)
    gallery_store.filter_gallery_events("user_id; DROP TABLE users;--", "ASC")

    sql, _ = engine.log[-1]
    assert "DROP" not in sql.upper()
    assert "ORDER BY occurred_at ASC" in sql  # unsafe column fell back to the default


def test_event_sort_direction_allowlist_blocks_injection(monkeypatch):
    engine = install_recording_engine(monkeypatch)
    gallery_store.filter_gallery_events("user_id", "ASC; DROP TABLE users;--")

    sql, _ = engine.log[-1]
    assert "DROP" not in sql.upper()
    assert "ORDER BY user_id DESC" in sql  # anything not "ASC" becomes "DESC"


def test_record_event_rejects_injected_action():
    with pytest.raises(ValueError):
        gallery_store.record_event(1, 1, "enter'; DROP TABLE gallery_event;--", 1)


# ----------------------------------------------------------------- route level
@pytest.mark.parametrize("payload", PAYLOADS)
def test_login_rejects_sql_injection_payload(client, fake, payload):
    response = client.post(
        "/login", data={"username": payload, "password": "whatever"}
    )

    assert response.status_code == 401
    assert b"Incorrect username or password." in response.data
    assert any(record[3] == "invalid_input" for record in fake.audit)
    assert client.get("/").status_code == 302  # still signed out


@pytest.mark.parametrize("payload", PAYLOADS)
def test_signup_rejects_sql_injection_payload(client, fake, payload):
    response = client.post(
        "/signup",
        data={"username": payload, "password": "Password1", "passwordMatch": "Password1"},
    )

    assert response.status_code == 400
    assert payload not in fake.usernames


def test_room_id_path_is_typed_as_integer(guest_client):
    response = guest_client.get("/room/1%27%20OR%20%271%27%3D%271")

    assert response.status_code == 404


@pytest.mark.parametrize("user_id", ["1 OR 1=1", "1); DROP TABLE users;--", "abc"])
def test_visit_rejects_non_integer_subject(employee_client, fake, user_id):
    response = employee_client.post(
        "/rooms/1/visit", data={"action": "enter", "user_id": user_id}
    )

    assert response.status_code == 400
    assert fake.events == []


def test_admin_event_filter_injection_does_not_crash(admin_client, fake):
    response = admin_client.post(
        "/admin",
        data={
            "action": "events",
            "filter_for": "user_id; DROP TABLE users;--",
            "filter_by": "ASC",
        },
    )

    assert response.status_code == 200
    assert b"Event History" in response.data
