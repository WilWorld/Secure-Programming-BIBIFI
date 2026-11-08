"""Flask application factory.  Run with:  gunicorn -b 0.0.0.0:8000 "app:create_app()" """
import os

from flask import Flask, jsonify, redirect, render_template, request, url_for
from flask_login import current_user
from flask_talisman import Talisman
from sqlalchemy import text
from werkzeug.exceptions import HTTPException

import auth_store
import gallery_store
from auth import init_auth
from flask import abort
from roles import enforce_login_by_default, require_role

# These pages can be accessed without logging in
PUBLIC_ENDPOINTS = {"health", "auth.login", "auth.signup", "static"}

# Custom outputs so the error messagess make some sense
ERROR_TEXT = {
    400: "The request could not be processed.",
    401: "Please sign in.",
    403: "You do not have access to this page.",
    404: "Page not found.",
    405: "That action is not allowed here.",
    409: "That movement is not allowed",
    413: "That request is too large.",
    429: "Too many requests. Try again shortly.",
}

# Locates the templates folder and throws an error if not found
def _frontend_dir():
    here = os.path.dirname(os.path.abspath(__file__))
    for candidate in (os.path.join(here, "frontend"), os.path.join(here, "..", "frontend")):
        if os.path.isdir(os.path.join(candidate, "templates")):
            return os.path.abspath(candidate)
    raise RuntimeError("Could not find frontend/templates next to or above src/backend")

# This is where all of the endpoints and other stuff lives
def create_app(test_config=None):
    frontend = _frontend_dir()                                                              # Creates filepath helper
    app = Flask(__name__,                                                                   # Finds templates and static folders
                template_folder=os.path.join(frontend, "templates"),
                static_folder=os.path.join(frontend, "static"))
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024                                            # Form size limit
    if test_config:
        app.config.update(test_config)                                                      # ???
    if not app.config.get("SECRET_KEY"):
        app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")                             # Checks if key was set and pull .env "SECRET_KEY" if missing
    if not app.config["SECRET_KEY"]:
        raise RuntimeError("SECRET_KEY is not set. Fill it in your .env file.")             # Throw error if .env "SECRET_KEY" is also missing

    force_https = os.environ.get("FORCE_HTTPS", "false").lower() == "true"
    Talisman(app, force_https=force_https, session_cookie_secure=force_https,               # Adds protective headers
             content_security_policy={"default-src": "'self'"}, frame_options="DENY")
    init_auth(app)                                                                          # ???
    enforce_login_by_default(app, PUBLIC_ENDPOINTS)                                         # ???

    # Gallery
    @app.get("/")
    def home():
        return render_template("home.html", displays=gallery_store.display_rooms())

    # Rooms
    @app.get("/room/<int:room_id>")
    def room_detail(room_id):
        room = gallery_store.get_room(room_id)
        if room is None:
            abort(404)
        if current_user.role in ("employee", "administrator"): 
            visitorsList=gallery_store.current_visitors(room_id)
        else: 
            visitorsList = []
        return render_template(
            "room.html",
            room=room,
            art=gallery_store.list_art(room_id),
            visitors=visitorsList,
            inside=gallery_store.is_inside(room_id, current_user.id),
        )

    # Handles users entering/leaving pages
    @app.post("/rooms/<int:room_id>/visit")
    def visit(room_id):
        action = request.form.get("action")
        subject_id = current_user.id
        
        # If recording move on someone else's behalf
        if request.form.get("user_id"):
            if current_user.role not in ("employee", "administrator"):
                auth_store.write_audit(current_user.id, "record_event", f"room={room_id} attempted_subject={request.form.get('user_id', '')[:50]}", "denied", request.remote_addr)
                abort(403)
            try:
                subject_id = int(request.form["user_id"])
            except (TypeError, ValueError):
                abort(400)
            if auth_store.get_user_by_id(subject_id) is None:   # Check if user exists
                abort(404)
        
        # Failsafe if room_id doesn't exist
        if gallery_store.get_room(room_id) is None:
            abort(404)
        
        # Attempt to record the movement
        try:
            gallery_store.record_event(room_id, subject_id, action, current_user.id)
            
        except ValueError:
            auth_store.write_audit(current_user.id, "record_event", f"room={room_id} attempted_subject={request.form.get('user_id', '')[:50]}", "denied", request.remote_addr)
            abort(400)
        except gallery_store.RecordRejected:
            auth_store.write_audit(current_user.id, "record_event", f"room={room_id} subject={subject_id} requested={action}", "denied", request.remote_addr)
            abort(409)
        auth_store.write_audit(current_user.id, "record_event", f"room={room_id} subject={subject_id} requested={action}", "success", request.remote_addr)
        
        return redirect(url_for("room_detail", room_id=room_id))

    @app.get("/api/rooms")
    def api_rooms():
        return jsonify(rooms=gallery_store.list_rooms())

    @app.get("/health")
    def health():
        try:
            with auth_store.engine().connect() as conn:
                conn.execute(text("SELECT 1"))
            return jsonify(status="ok")
        except Exception:
            app.logger.exception("health check failed")
            return jsonify(status="error"), 503

    @app.get("/api/whoami")
    def whoami():
        return jsonify(username=current_user.username, role=current_user.role)

    @app.get("/admin")
    @require_role("administrator")
    def admin_home():
        return render_template("admin.html", users=gallery_store.list_users())

    def _error(code):
        message = ERROR_TEXT.get(code, "Something went wrong.")
        if request.path.startswith("/api/"):
            return jsonify(error=message), code
        return render_template("error.html", code=code, message=message), code

    @app.errorhandler(HTTPException)
    def http_error(e):
        return _error(e.code)

    @app.errorhandler(Exception)
    def unhandled_error(e):
        app.logger.exception("unhandled error")
        return _error(500)

    return app


def __getattr__(name):
    # Lets an existing "gunicorn app:app" command keep working.
    if name == "app":
        return create_app()
    raise AttributeError(name)