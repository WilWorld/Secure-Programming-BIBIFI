"""Authorization helpers. Every check runs on the server."""
from functools import wraps

from flask import abort, current_app, jsonify, request
from flask_login import current_user


def require_role(*roles):
    """Allow only the listed roles. Anonymous users are sent to login; others get 403."""
    allowed = set(roles)

    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                return current_app.login_manager.unauthorized()
            if current_user.role not in allowed:
                abort(403)
            return view(*args, **kwargs)

        return wrapped

    return decorator


def enforce_login_by_default(app, public_endpoints):
    """Deny by default: any route not listed as public requires a signed-in user."""

    @app.before_request
    def _gate():
        endpoint = request.endpoint
        if endpoint is None or endpoint in public_endpoints:
            return None
        if current_user.is_authenticated:
            return None
        if request.path.startswith("/api/"):
            return jsonify(error="Please sign in."), 401
        return app.login_manager.unauthorized()