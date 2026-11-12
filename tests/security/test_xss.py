"""Cross-site scripting (XSS) tests.

The app relies on Jinja2 auto-escaping plus a strict Content-Security-Policy.
These tests feed script payloads into every place user/DB data is rendered and
assert the data comes out HTML-escaped, never as live markup.
"""
SCRIPT_PAYLOAD = "<script>alert('xss')</script>"


def _body(response):
    return response.get_data(as_text=True)


def test_jinja_autoescape_is_enabled(app):
    assert app.jinja_env.autoescape("room.html") is True


def test_room_name_is_escaped(guest_client, fake):
    fake.rooms[1]["name"] = SCRIPT_PAYLOAD

    response = guest_client.get("/room/1")
    body = _body(response)

    assert response.status_code == 200
    assert SCRIPT_PAYLOAD not in body
    assert "&lt;script&gt;" in body


def test_art_title_and_artist_are_escaped(guest_client, fake):
    fake.art[1]["title"] = "<img src=x onerror=alert(1)>"
    fake.art[1]["artist"] = SCRIPT_PAYLOAD

    response = guest_client.get("/room/1")
    body = _body(response)

    assert response.status_code == 200
    assert "<img src=x onerror=alert(1)>" not in body
    assert "&lt;img src=x onerror=alert(1)&gt;" in body
    assert SCRIPT_PAYLOAD not in body
    assert "&lt;script&gt;" in body


def test_home_display_fields_are_escaped(guest_client, fake):
    fake.rooms[1]["name"] = SCRIPT_PAYLOAD
    fake.art[1]["title"] = SCRIPT_PAYLOAD
    fake.art[1]["artist"] = SCRIPT_PAYLOAD

    response = guest_client.get("/")
    body = _body(response)

    assert response.status_code == 200
    assert SCRIPT_PAYLOAD not in body
    assert "&lt;script&gt;" in body


def test_admin_user_table_escapes_username(admin_client, fake):
    fake.users[6]["username"] = SCRIPT_PAYLOAD

    response = admin_client.get("/admin")
    body = _body(response)

    assert response.status_code == 200
    assert SCRIPT_PAYLOAD not in body
    assert "&lt;script&gt;" in body


def test_admin_event_filter_reflection_is_escaped(admin_client):
    response = admin_client.post(
        "/admin",
        data={"action": "events", "filter_for": SCRIPT_PAYLOAD, "filter_by": "DESC"},
    )
    body = _body(response)

    assert response.status_code == 200
    assert SCRIPT_PAYLOAD not in body
    assert "&lt;script&gt;" in body


def test_signup_rejects_script_in_username(client, fake):
    response = client.post(
        "/signup",
        data={
            "username": SCRIPT_PAYLOAD,
            "password": "Password1",
            "passwordMatch": "Password1",
        },
    )

    assert response.status_code == 400
    assert SCRIPT_PAYLOAD not in _body(response)
    assert SCRIPT_PAYLOAD not in fake.usernames


def test_login_rejects_script_in_username(client):
    response = client.post(
        "/login", data={"username": SCRIPT_PAYLOAD, "password": "whatever"}
    )

    assert response.status_code == 401
    assert SCRIPT_PAYLOAD not in _body(response)
    assert b"Incorrect username or password." in response.data


def test_csp_blocks_inline_and_external_scripts(client):
    response = client.get("/login")

    csp = response.headers.get("Content-Security-Policy", "")
    assert "default-src 'self'" in csp
    assert "script-src" not in csp  # falls back to default-src 'self'


def test_security_headers_are_present(client):
    response = client.get("/login")

    assert response.headers.get("X-Frame-Options") == "DENY"
    assert response.headers.get("X-Content-Type-Options") == "nosniff"
