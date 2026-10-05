import os

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError
from flask import Flask, jsonify, redirect, render_template, url_for
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from flask_sqlalchemy import SQLAlchemy
from flask_talisman import Talisman
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import text, select, MetaData, Table
from wtforms import PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Length

db = SQLAlchemy()
csrf = CSRFProtect()
login_manager = LoginManager()
limiter = Limiter(key_func=get_remote_address, default_limits=["200/hour"])

ph = PasswordHasher()

# Prevents attackers from detecting users that don't exist
DUMMY_HASH = ph.hash("not-a-real-password")

# Maps a class to the users table
class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, nullable=False)

# Used to verify login information
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired(), Length(max=150)])
    password = PasswordField("Password", validators=[DataRequired(), Length(max=1024)])
    submit = SubmitField("Log in")

# Checks if a user is logged in
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Checks if a password is valid
def password_is_valid(user, password):
    stored = user.password_hash if user else DUMMY_HASH
    try:
        ph.verify(stored, password)
    except (VerificationError, InvalidHashError):
        return False
    return user is not None

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

    login_manager.login_view = "login"          # where to send logged-out users
    login_manager.session_protection = "strong" # invalidate session if client fingerprint changes

    @app.get("/")
    @login_required
    def index():
        return render_template("index.html")

    @app.route("/login", methods=["GET", "POST"])
    @limiter.limit("5 per minute", methods=["POST"])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for("index"))

        form = LoginForm()
        error = None
        if form.validate_on_submit():
            user = db.session.execute(select(User).where(User.username == form.username.data)).scalar_one_or_none()

            if password_is_valid(user, form.password.data):
                login_user(user)
                return redirect(url_for("index"))
            
            error = "Invalid username or password."

        return render_template("login.html", form=form, error=error)

    @app.post("/logout")
    @login_required
    def logout():
        logout_user()
        return redirect(url_for("login"))

    @app.get("/health")
    @login_required
    @limiter.exempt
    def health():
        try:
            db.session.execute(text("SELECT 1"))
            return jsonify(status="ok"), 200
        except Exception:
            app.logger.exception("Health check DB query failed")
            return jsonify(status="unavailable"), 503

    @app.get("/database")
    @login_required
    def database_test():
        try:
            t = Table("art", MetaData(), autoload_with=db.engine)
            rows = db.session.execute(select(t)).mappings().all()
            return jsonify([dict(r) for r in rows]), 200
        except Exception:
            app.logger.exception("/database check failed")
            return jsonify(error="database error"), 500

    return app