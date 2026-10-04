"""Database access for authentication. Every query is parameterized.

Targets database/schema.sql:
  users(id PK, username UNIQUE, password_hash, role, is_active BOOL,
        failed_attempts INT, locked_until TIMESTAMPTZ NULL, created_at)
  sessions(session_hash PK, user_id FK, created_at, expires_at, revoked BOOL)
  audit_log(id PK, actor_id FK NULL, action, target, outcome, ip_address, created_at)
Column names follow schema.sql; the primary key is `id`, not `user_id`.
"""
import hashlib
import os
import secrets

from sqlalchemy import create_engine, text

_engine = None


def engine():
    global _engine
    if _engine is None:
        url = os.environ.get("DATABASE_URL") or (
            "postgresql+psycopg://{u}:{p}@db:5432/{d}".format(
                u=os.environ["POSTGRES_USER"],
                p=os.environ["POSTGRES_PASSWORD"],
                d=os.environ["POSTGRES_DB"],
            )
        )
        _engine = create_engine(url, pool_pre_ping=True)
    return _engine


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


def get_user_by_username(username):
    with engine().connect() as c:
        row = c.execute(
            text("SELECT id, username, password_hash, role, is_active, "
                 "failed_attempts, locked_until FROM users WHERE username = :u"),
            {"u": username},
        ).mappings().first()
    return dict(row) if row else None


def get_user_by_id(user_id):
    with engine().connect() as c:
        row = c.execute(
            text("SELECT id, username, role, is_active FROM users WHERE id = :i"),
            {"i": user_id},
        ).mappings().first()
    return dict(row) if row else None


def record_failed_login(user_id, max_attempts, lock_minutes):
    with engine().begin() as c:
        c.execute(
            text("UPDATE users SET failed_attempts = failed_attempts + 1, "
                 "locked_until = CASE WHEN failed_attempts + 1 >= :mx "
                 "THEN now() + make_interval(mins => :mins) ELSE locked_until END "
"WHERE id = :i"),
             {"mx": max_attempts, "mins": lock_minutes, "i": user_id},
        )


def reset_failed_logins(user_id):
    with engine().begin() as c:
        c.execute(
            text("UPDATE users SET failed_attempts = 0, locked_until = NULL WHERE id = :i"),
            {"i": user_id},
        )


def create_session(user_id, ttl_minutes):
    token = secrets.token_urlsafe(32)
    with engine().begin() as c:
        c.execute(
            text("INSERT INTO sessions (session_hash, user_id, created_at, expires_at, revoked) "
                 "VALUES (:h, :u, now(), now() + make_interval(mins => :m), false)"),
            {"h": _hash_token(token), "u": user_id, "m": ttl_minutes},
        )
    return token


def session_is_valid(token, user_id):
    with engine().connect() as c:
        row = c.execute(
            text("SELECT 1 FROM sessions WHERE session_hash = :h AND user_id = :u "
                 "AND revoked = false AND expires_at > now()"),
            {"h": _hash_token(token), "u": user_id},
        ).first()
    return row is not None


def revoke_session(token):
    if not token:
        return
    with engine().begin() as c:
        c.execute(
            text("UPDATE sessions SET revoked = true WHERE session_hash = :h"),
            {"h": _hash_token(token)},
        )


def write_audit(user_id, action, target, outcome, ip):
    with engine().begin() as c:
        c.execute(
            text("INSERT INTO audit_log (actor_id, action, target, outcome, ip_address, created_at) "
                 "VALUES (:u, :a, :t, :o, :ip, now())"),
            {"u": user_id, "a": action, "t": (target or "")[:64], "o": outcome, "ip": ip},
        )