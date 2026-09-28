import os

from flask import Flask, jsonify
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])


def create_app():
    app = Flask(
        __name__,
        template_folder="frontend/templates",
        static_folder="frontend/static",
    )

    # Fail loudly if secrets are missing. Never fall back to a default.
    app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ["DATABASE_URL"]
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    force_https = os.environ.get("FORCE_HTTPS", "false").lower() == "true"
    app.config.update(
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=force_https,
    )

    # Talisman defaults to Secure cookies + HTTPS redirect, which breaks
    # plain-http localhost, so both follow FORCE_HTTPS.
    Talisman(app, force_https=force_https, session_cookie_secure=force_https)

    db.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    limiter.init_app(app)
    @app.get("/")
    def index():
        return "Hello Charlie!"

    @app.get("/health")
    @limiter.exempt
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok"), 200
        except Exception:
            app.logger.exception("Health check DB query failed")
            return jsonify(status="unavailable"), 503

    return app