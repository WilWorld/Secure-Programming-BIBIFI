"""In-memory fakes for the database access modules.

The real ``auth_store`` and ``gallery_store`` talk to PostgreSQL with
SQL that SQLite cannot run (``DISTINCT ON``, ``make_interval``, ``FOR
UPDATE`` ...).  These fakes reproduce the *behaviour* the Flask routes
rely on, so security tests can run without a database.

``patch_store(monkeypatch, auth_store)`` swaps every store function for
its fake counterpart and returns the ``FakeStore`` instance.  Tests can
then inspect ``fake.audit``, ``fake.sessions``, ``fake.events`` and seed
data with ``fake.add_room()`` / ``fake.add_art()`` / ``fake.add_event()``.

All fake users share the password ``PASSWORD``.  This file is test-only.
"""
import hashlib
import secrets
from datetime import datetime, timedelta, timezone

from argon2 import PasswordHasher

PASSWORD = "CorrectHorse1"

_hasher = PasswordHasher()
_PASSWORD_HASH = _hasher.hash(PASSWORD)

AUTH_FUNCTIONS = [
    "engine",
    "get_user_by_username",
    "get_user_by_id",
    "record_failed_login",
    "reset_failed_logins",
    "create_session",
    "session_is_valid",
    "revoke_session",
    "write_audit",
    "create_user",
]

GALLERY_FUNCTIONS = [
    "display_rooms",
    "get_room",
    "list_art",
    "current_visitors",
    "is_inside",
    "record_event",
    "current_room",
    "room_name",
    "list_rooms",
    "list_users",
    "add_user_rows",
    "get_events",
    "filter_gallery_events",
    "update_role",
]

GALLERY_EXCEPTIONS = ["RecordRejected", "InRoom", "InDifferentRoom", "NotInThisRoom"]


class RecordRejected(Exception):
    pass


class InRoom(RecordRejected):
    pass


class InDifferentRoom(RecordRejected):
    pass


class NotInThisRoom(RecordRejected):
    pass


def _now():
    return datetime.now(timezone.utc)


def _hash_token(token):
    return hashlib.sha256(token.encode()).hexdigest()


class _Result:
    """Minimal stand-in for a SQLAlchemy Result."""

    def mappings(self):
        return self

    def all(self):
        return []

    def first(self):
        return None

    def scalar_one_or_none(self):
        return None


class _Connection:
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def execute(self, statement, params=None):
        return _Result()


class _Engine:
    """Engine that satisfies the /health check without a database."""

    def connect(self):
        return _Connection()

    def begin(self):
        return _Connection()


class FakeStore:
    def __init__(self):
        self.users = {}          # id -> user dict
        self.usernames = {}      # username -> id
        self.rooms = {}          # id -> {"id", "name"}
        self.art = {}            # id -> art dict
        self.events = []         # list of event dicts
        self.sessions = {}       # token hash -> session dict
        self.audit = []          # (actor_id, action, target, outcome)
        self.audit_records = []  # dicts with the same data plus ip

        self._next_user_id = 1
        self._next_room_id = 1
        self._next_art_id = 1
        self._next_event_id = 1

        # id 1 must be "alice": tests/security/test_auth.py relies on it.
        for username, role, active in [
            ("alice", "guest", True),
            ("bob", "guest", False),
            ("guest1", "guest", True),
            ("employee1", "employee", True),
            ("administrator1", "administrator", True),
            ("guest2", "guest", True),
        ]:
            self._insert_user(username, role, active)

        first_room = self.add_room("Eudyptes")
        self.add_room("Spheniscus")
        self.add_art(
            first_room,
            "King Penguin",
            artist="N/A",
            price_cents=100000,
            image_path="assets/King Penguin.jpg",
        )

    # ------------------------------------------------------------------ helpers
    def _insert_user(self, username, role, is_active, password_hash=None):
        user_id = self._next_user_id
        self._next_user_id += 1
        row = {
            "id": user_id,
            "username": username,
            "password_hash": password_hash or _PASSWORD_HASH,
            "role": role,
            "is_active": is_active,
            "failed_attempts": 0,
            "locked_until": None,
            "created_at": _now() + timedelta(seconds=user_id),
        }
        self.users[user_id] = row
        self.usernames[username] = user_id
        return user_id

    def add_room(self, name):
        room_id = self._next_room_id
        self._next_room_id += 1
        self.rooms[room_id] = {"id": room_id, "name": name}
        return room_id

    def add_art(self, room_id, title, artist=None, price_cents=None, image_path=None):
        art_id = self._next_art_id
        self._next_art_id += 1
        self.art[art_id] = {
            "id": art_id,
            "title": title,
            "artist": artist,
            "price_cents": price_cents,
            "image_path": image_path,
            "room_id": room_id,
        }
        return art_id

    def add_event(self, room_id, user_id, action, recorded_by=None):
        event_id = self._next_event_id
        self._next_event_id += 1
        event = {
            "id": event_id,
            "user_id": user_id,
            "room_id": room_id,
            "action": action,
            "occurred_at": _now() + timedelta(seconds=event_id),
            "recorded_by": recorded_by,
        }
        self.events.append(event)
        return event

    def _latest_event(self, user_id, room_id=None):
        matches = [
            e
            for e in self.events
            if e["user_id"] == user_id
            and (room_id is None or e["room_id"] == room_id)
        ]
        if not matches:
            return None
        return max(matches, key=lambda e: (e["occurred_at"], e["id"]))

    # ------------------------------------------------------------ auth_store
    def engine(self):
        return _Engine()

    def get_user_by_username(self, username):
        user_id = self.usernames.get(username)
        return dict(self.users[user_id]) if user_id is not None else None

    def get_user_by_id(self, user_id):
        row = self.users.get(int(user_id))
        if row is None:
            return None
        return {
            "id": row["id"],
            "username": row["username"],
            "role": row["role"],
            "is_active": row["is_active"],
        }

    def record_failed_login(self, user_id, max_attempts, lock_minutes):
        row = self.users[user_id]
        row["failed_attempts"] += 1
        if row["failed_attempts"] >= max_attempts:
            row["locked_until"] = _now() + timedelta(minutes=lock_minutes)

    def reset_failed_logins(self, user_id):
        row = self.users[user_id]
        row["failed_attempts"] = 0
        row["locked_until"] = None

    def create_session(self, user_id, ttl_minutes):
        token = secrets.token_urlsafe(32)
        self.sessions[_hash_token(token)] = {
            "user_id": user_id,
            "token": token,
            "created_at": _now(),
            "expires_at": _now() + timedelta(minutes=ttl_minutes),
            "revoked": False,
        }
        return token

    def session_is_valid(self, token, user_id):
        session = self.sessions.get(_hash_token(token))
        return bool(
            session
            and session["user_id"] == user_id
            and not session["revoked"]
            and session["expires_at"] > _now()
        )

    def revoke_session(self, token):
        if not token:
            return
        session = self.sessions.get(_hash_token(token))
        if session is not None:
            session["revoked"] = True

    def write_audit(self, user_id, action, target, outcome, ip=None):
        self.audit.append((user_id, action, target, outcome))
        self.audit_records.append(
            {
                "actor_id": user_id,
                "action": action,
                "target": target,
                "outcome": outcome,
                "ip_address": ip,
            }
        )

    def create_user(self, username, password_hash):
        if username in self.usernames:
            return False
        self._insert_user(username, "guest", True, password_hash)
        return True

    # --------------------------------------------------------- gallery_store
    def display_rooms(self):
        displays = []
        for room in sorted(self.rooms.values(), key=lambda r: r["name"]):
            art = sorted(
                (a for a in self.art.values() if a["room_id"] == room["id"]),
                key=lambda a: a["id"],
            )
            if not art:
                continue
            first = art[0]
            displays.append(
                {
                    "id": room["id"],
                    "name": room["name"],
                    "title": first["title"],
                    "artist": first["artist"],
                    "image_path": first["image_path"],
                }
            )
        return displays

    def get_room(self, room_id):
        room = self.rooms.get(int(room_id))
        return dict(room) if room else None

    def list_art(self, room_id):
        rows = [a for a in self.art.values() if a["room_id"] == int(room_id)]
        return [dict(a) for a in sorted(rows, key=lambda a: a["title"])]

    def current_visitors(self, room_id):
        latest = {}
        for event in self.events:
            if event["room_id"] != int(room_id):
                continue
            current = latest.get(event["user_id"])
            if current is None or event["id"] > current["id"]:
                latest[event["user_id"]] = event
        visitors = []
        for user_id, event in latest.items():
            if event["action"] != "enter":
                continue
            user = self.users.get(user_id)
            if user is None:
                continue
            visitors.append(
                {
                    "username": user["username"],
                    "action": event["action"],
                    "occurred_at": event["occurred_at"],
                }
            )
        return visitors

    def current_room(self, user_id, connection=None):
        event = self._latest_event(int(user_id))
        if event is None or event["action"] != "enter":
            return None
        return event["room_id"]

    def is_inside(self, room_id, user_id):
        return self.current_room(user_id) == int(room_id)

    def record_event(self, room_id, user_id, action, recorded_by):
        if action not in ("enter", "leave"):
            raise ValueError("action must be 'enter' or 'leave'")

        room_id = int(room_id)
        user_id = int(user_id)
        current = self.current_room(user_id)

        if action == "enter":
            if current == room_id:
                raise InRoom("user is already in this room")
            if current is not None:
                raise InDifferentRoom("user is in a different room")
        elif action == "leave":
            if current != room_id:
                raise NotInThisRoom("user is not in this room")

        self.add_event(room_id, user_id, action, recorded_by)

    def room_name(self, room_id):
        if room_id is None:
            return None
        room = self.rooms.get(int(room_id))
        return room["name"] if room else None

    def list_rooms(self):
        latest = {}
        for event in self.events:
            current = latest.get(event["user_id"])
            if current is None or event["id"] > current["id"]:
                latest[event["user_id"]] = event

        rooms = []
        for room in sorted(self.rooms.values(), key=lambda r: r["name"]):
            visitors = sorted(
                self.users[e["user_id"]]["username"]
                for e in latest.values()
                if e["room_id"] == room["id"]
                and e["action"] == "enter"
                and e["user_id"] in self.users
            )
            rooms.append(
                {
                    "id": room["id"],
                    "name": room["name"],
                    "artwork_count": sum(
                        1 for a in self.art.values() if a["room_id"] == room["id"]
                    ),
                    "visitor_count": len(visitors),
                    "visitors": visitors,
                }
            )
        return rooms

    def list_users(self):
        return [
            dict(row)
            for row in sorted(
                self.users.values(), key=lambda r: r["created_at"], reverse=True
            )
        ]

    def add_user_rows(self, users):
        return [
            {
                "username": user["username"],
                "role": user["role"],
                "room": self.room_name(self.current_room(user["id"])),
            }
            for user in users
        ]

    def get_events(self):
        return [
            dict(event)
            for event in sorted(
                self.events,
                key=lambda e: (e["occurred_at"], e["id"]),
                reverse=True,
            )
        ]

    def filter_gallery_events(self, filter_for, filter_by):
        sort_columns = {"user_id", "room_id", "action", "occurred_at", "recorded_by"}
        column = filter_for if filter_for in sort_columns else "occurred_at"
        descending = filter_by != "ASC"
        return [
            dict(event)
            for event in sorted(
                self.events,
                key=lambda e: (e[column], e["id"]) if e[column] is not None else (None, e["id"]),
                reverse=descending,
            )
        ]

    def update_role(self, username, role):
        user_id = self.usernames.get(username)
        if user_id is None:
            return False
        self.users[user_id]["role"] = role
        return True


def patch_store(monkeypatch, auth_store_module):
    """Replace real store functions with a shared FakeStore and return it."""
    fake = FakeStore()

    for name in AUTH_FUNCTIONS:
        monkeypatch.setattr(auth_store_module, name, getattr(fake, name))

    try:
        import gallery_store as gallery_store_module
    except ImportError:  # the minimal auth-only app used by test_auth.py
        gallery_store_module = None

    if gallery_store_module is not None:
        for name in GALLERY_FUNCTIONS:
            monkeypatch.setattr(gallery_store_module, name, getattr(fake, name))
        for name in GALLERY_EXCEPTIONS:
            monkeypatch.setattr(gallery_store_module, name, globals()[name])

    return fake
