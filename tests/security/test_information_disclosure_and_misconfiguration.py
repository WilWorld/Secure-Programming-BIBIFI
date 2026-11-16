"""Information disclosure and security misconfiguration checks."""
import app as app_module


def test_login_error_does_not_leak_user_existence(client):
    known = client.post("/login", data={"username": "guest1", "password": "wrong"})
    unknown = client.post("/login", data={"username": "no_such_user", "password": "wrong"})

    assert known.status_code == unknown.status_code == 401
    assert known.get_data(as_text=True) == unknown.get_data(as_text=True)
    assert b"traceback" not in known.data.lower()


def test_404_does_not_reflect_path_or_stack_trace(guest_client):
    response = guest_client.get("/<script>alert(1)</script>")
    body = response.get_data(as_text=True).lower()

    assert response.status_code == 404
    assert "<script>alert(1)</script>" not in body
    assert "traceback" not in body
    assert "exception" not in body


def test_500_handler_hides_exception_details(app):
    @app.route("/boom")
    def boom():
        raise RuntimeError("SECRET_STACK_DETAIL")

    app.config["PROPAGATE_EXCEPTIONS"] = False
    client = app.test_client()
    client.post("/login", data={"username": "guest1", "password": "CorrectHorse1"})

    response = client.get("/boom")
    body = response.get_data(as_text=True)

    assert response.status_code == 500
    assert "SECRET_STACK_DETAIL" not in body
    assert "RuntimeError" not in body


def test_security_configuration_defaults(app):
    assert app.config["SESSION_COOKIE_HTTPONLY"] is True
    assert app.config["SESSION_COOKIE_SAMESITE"] == "Lax"
    assert app.config["MAX_CONTENT_LENGTH"] == 16 * 1024


def test_app_requires_secret_key(monkeypatch):
    monkeypatch.delenv("SECRET_KEY", raising=False)
    try:
        app_module.create_app({"TESTING": True, "SECRET_KEY": None})
    except RuntimeError as exc:
        assert "SECRET_KEY" in str(exc)
    else:
        raise AssertionError("Expected RuntimeError when SECRET_KEY is missing")
