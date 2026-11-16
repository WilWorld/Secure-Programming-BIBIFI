"""Input validation and bypass defenses.

Verifies server-side validation, type enforcement, and safe handling of
malformed or oversized input.
"""
PAYLOADS = {
    "username": "<script>alert(1)</script>",
    "password": "Password1",
    "passwordMatch": "Password1",
}


def test_signup_rejects_short_and_overlong_usernames(client, fake):
    for username in ("ab", "a" * 33):
        response = client.post(
            "/signup",
            data={"username": username, "password": "Password123", "passwordMatch": "Password123"},
        )
        assert response.status_code == 400
        assert username not in fake.usernames


def test_signup_rejects_overlong_password(client, fake):
    password = "A" * 129
    response = client.post(
        "/signup",
        data={"username": "validuser1", "password": password, "passwordMatch": password},
    )

    assert response.status_code == 400
    assert "validuser1" not in fake.usernames


def test_login_rejects_whitespace_only_username(client):
    response = client.post("/login", data={"username": "   ", "password": "whatever"})

    assert response.status_code == 401
    assert b"Incorrect username or password." in response.data


def test_visit_action_bypass_is_rejected(employee_client, fake):
    response = employee_client.post("/rooms/1/visit", data={"action": "ENTER"})

    assert response.status_code == 400
    assert fake.events == []


def test_admin_rejects_invalid_action_choice(admin_client):
    response = admin_client.post("/admin", data={"action": "drop_table"})

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/admin")


def test_large_form_payload_is_rejected(client):
    response = client.post(
        "/login",
        data={"username": "guest1", "password": "x" * 20000},
        content_type="application/x-www-form-urlencoded",
    )

    assert response.status_code in (400, 413, 429)
