"""Session/token and authentication attack defenses.

Covers session fixation, token tampering/revocation, cookie hardening, and
abuse controls that complement tests/security/test_auth.py.
"""
from datetime import datetime, timedelta, timezone

import auth


PASSWORD = "CorrectHorse1"


def test_login_clears_existing_session_and_rotates_sid(client, fake):
    with client.session_transaction() as sess:
        sess["sid"] = "attacker-controlled-token"
        sess["foo"] = "bar"

    response = client.post("/login", data={"username": "guest1", "password": PASSWORD})

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "foo" not in sess
        assert sess.get("sid")
        assert sess["sid"] != "attacker-controlled-token"
    assert len(fake.sessions) == 1


def test_logout_clears_flask_session(client):
    client.post("/login", data={"username": "guest1", "password": PASSWORD})

    response = client.post("/logout")

    assert response.status_code == 302
    with client.session_transaction() as sess:
        assert "sid" not in sess
        assert "_user_id" not in sess


def test_forged_sid_is_rejected(client, fake):
    client.post("/login", data={"username": "guest1", "password": PASSWORD})
    with client.session_transaction() as sess:
        sess["sid"] = "forged-session-token"

    assert client.get("/").status_code == 302
    assert client.get("/protected-should-not-exist").status_code in (302, 404)
    assert all(not s["revoked"] for s in fake.sessions.values())


def test_session_for_inactive_user_is_rejected(client, fake):
    client.post("/login", data={"username": "guest1", "password": PASSWORD})
    fake.users[fake.usernames["guest1"]]["is_active"] = False

    assert client.get("/").status_code == 302
    assert client.get("/api/whoami").status_code == 401


def test_only_bearer_token_hash_is_stored(fake):
    token = fake.create_session(1, 30)
    record = list(fake.sessions.values())[0]

    assert record["token"] == token
    assert token not in fake.sessions
    assert len(next(iter(fake.sessions.keys()))) == 64
