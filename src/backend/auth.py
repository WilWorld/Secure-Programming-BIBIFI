"""Login and logout. Call init_auth(app) once from your Flask app."""
import os
import re
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from flask import Blueprint, redirect, render_template, request, session, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFProtect

import auth_store as store

MAX_FAILED_LOGINS = 5
LOCK_MINUTES = 15
SESSION_MINUTES = 30
GENERIC_ERROR = "Incorrect username or password."
USERNAME_RE = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")

ph = PasswordHasher()
_DUMMY_HASH = ph.hash("not-a-real-password")

bp = Blueprint("auth", __name__)
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address)
csrf = CSRFProtect()


class User(UserMixin):
    def __init__(self, row):
        self.id = row["id"]
        self.username = row["username"]
        self.role = row["role"]
        self._active = row["is_active"]

    @property
    def is_active(self):
        return self._active

    def get_id(self):
        return str(self.id)


@login_manager.user_loader
def load_user(user_id):
    token = session.get("sid")
    if not token:
        return None
    try:
        uid = int(user_id)
    except (TypeError, ValueError):
        return None
    if not store.session_is_valid(token, uid):
        return None
    row = store.get_user_by_id(uid)
    if row is None or not row["is_active"]:
        return None
    return User(row)


def _dummy_verify(password):
    """Spend the same time as a real check so timing does not reveal valid usernames."""
    try:
        ph.verify(_DUMMY_HASH, password)
    except (VerificationError, InvalidHashError):
        pass


def _is_locked(row):
    locked_until = row.get("locked_until")
    if locked_until is None:
        return False
    if locked_until.tzinfo is None:
        locked_until = locked_until.replace(tzinfo=timezone.utc)
    return locked_until > datetime.now(timezone.utc)


def _audit(user_id, action, target, outcome):
    store.write_audit(user_id, action, target, outcome, request.remote_addr)


def _fail(user_id, username, reason):
    _audit(user_id, "LOGIN", username, reason)
    return render_template("login.html", error=GENERIC_ERROR), 401


@bp.route("/login", methods=["GET", "POST"])
@limiter.limit("10 per minute", methods=["POST"])
def login():
    if request.method == "GET":
        return render_template("login.html", error=None)

    username = (request.form.get("username") or "").strip()
    password = request.form.get("password") or ""

    if not USERNAME_RE.match(username) or not password or len(password) > 128:
        _dummy_verify(password[:128])
        return _fail(None, username, "invalid_input")

    row = store.get_user_by_username(username)
    if row is None:
        _dummy_verify(password)
        return _fail(None, username, "unknown_user")

    if _is_locked(row):
        _dummy_verify(password)
        return _fail(row["id"], username, "locked")

    if row.get("locked_until") is not None:
        store.reset_failed_logins(row["id"])

    if not row["is_active"]:
        _dummy_verify(password)
        return _fail(row["id"], username, "inactive")

    try:
        ph.verify(row["password_hash"], password)
    except (VerificationError, InvalidHashError):
        store.record_failed_login(row["id"], MAX_FAILED_LOGINS, LOCK_MINUTES)
        return _fail(row["id"], username, "bad_password")

    session.clear()
    token = store.create_session(row["id"], SESSION_MINUTES)
    login_user(User(row))
    session["sid"] = token
    session.permanent = True
    store.reset_failed_logins(row["id"])
    _audit(row["id"], "LOGIN", username, "success")
    return redirect("/")


@bp.post("/logout")
@login_required
def logout():
    user_id, username = current_user.id, current_user.username
    store.revoke_session(session.get("sid"))
    _audit(user_id, "LOGOUT", username, "success")
    logout_user()
    session.clear()
    return redirect(url_for("auth.login"))


def init_auth(app):
    # Flask ships its own defaults for these keys, so set them directly (setdefault would do nothing).
    app.config["SESSION_COOKIE_HTTPONLY"] = True
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
    app.config["SESSION_COOKIE_SECURE"] = bool(app.config.get("SESSION_COOKIE_SECURE")) or \
        os.environ.get("FORCE_HTTPS", "false").lower() == "true"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(minutes=SESSION_MINUTES)
    app.config.setdefault("RATELIMIT_STORAGE_URI", "memory://")
    login_manager.login_view = "auth.login"
    login_manager.session_protection = "strong"
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    app.register_blueprint(bp)