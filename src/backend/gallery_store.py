"""Database access for rooms, artworks, and visits. Every query is parameterized.

Targets database/schema.sql:
  room(id PK, name UNIQUE)
  art(id PK, title, artist, price_cents, image_path, room_id FK)
  gallery_event(id PK, user_id FK, room_id FK, action, occurred_at, recorded_by FK)
"""
from sqlalchemy import text

# Custom error type to distinguish invalid requests vs bugs
class RecordRejected(Exception): pass
class InRoom(RecordRejected): pass
class InDifferentRoom(RecordRejected): pass
class NotInThisRoom(RecordRejected): pass

def _engine():
    import auth_store
    return auth_store.engine()

def list_users():
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT * FROM users ORDER BY created_at DESC"),
        ).mappings().all()
    return [dict(r) for r in rows]
            
def list_rooms():
    with _engine().connect() as c:
        rows = c.execute(
            text("WITH latest AS ("
                 "SELECT DISTINCT ON (user_id) user_id, room_id, action "
                 "FROM gallery_event "
                 "ORDER BY user_id, occurred_at DESC, id DESC"
                 ") "
                 "SELECT r.id, r.name, "
                 "(SELECT count(*) FROM art a WHERE a.room_id = r.id) AS artwork_count, "
                 "(SELECT count(*) FROM latest l "
                 "WHERE l.room_id = r.id AND l.action = 'enter') AS visitor_count, "
                 "COALESCE((SELECT array_agg(u.username ORDER BY u.username) "
                 "FROM latest l JOIN users u ON u.id = l.user_id "
                 "WHERE l.room_id = r.id AND l.action = 'enter'), "
                 "ARRAY[]::varchar[]) AS visitors "
                 "FROM room r ORDER BY r.name"),
        ).mappings().all()
    return [dict(r) for r in rows]

def get_events():
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT * FROM gallery_event")
        ).mappings().all()
    return [dict(r) for r in rows] if rows else None

# This is for the room displays on the homepage
def display_rooms():
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT DISTINCT ON (r.name) r.id, r.name, "
                 "       a.title, a.artist, a.image_path "
                 "FROM art a JOIN room r ON r.id = a.room_id "
                 "ORDER BY r.name, random()")
        ).mappings().all()
    return [dict(r) for r in rows]

# Looks up one room by id
def get_room(room_id):
    """Return one room, or None if it does not exist."""
    with _engine().connect() as c:
        row = c.execute(
            text("SELECT id, name FROM room WHERE id = :i"), {"i": room_id},
        ).mappings().first()
    return dict(row) if row else None

# Lists all the artwork in a room by room id
def list_art(room_id):
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT id, title, artist, price_cents, image_path "
                 "FROM art WHERE room_id = :i ORDER BY title"),
            {"i": room_id},
        ).mappings().all()
    return [dict(r) for r in rows]

# Returns all visitors in current room
def current_visitors(room_id):
    """People whose most recent event in this room was an entry.

    DISTINCT ON keeps only the latest event per person; anyone whose latest
    event is a 'leave' has already gone and is filtered out.
    """
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT DISTINCT ON (u.id) u.username, g.action, g.occurred_at "
                 "FROM gallery_event g JOIN users u ON u.id = g.user_id "
                 "WHERE g.room_id = :i "
                 "ORDER BY u.id, g.occurred_at DESC, g.id DESC"),
            {"i": room_id},
        ).mappings().all()
    return [dict(r) for r in rows if r["action"] == "enter"]

# Keeps functions on same transaction to help prevent race conditions
def _current_event(c, user_id):
    return c.execute(
        text("SELECT action, room_id FROM gallery_event "
             "WHERE user_id = :u "
             "ORDER BY occurred_at DESC, id DESC "
         "LIMIT 1"),
        {"u": user_id}, 
    ).first()

# Returns the current room of the selected user
def current_room(user_id, connection=None):
    if connection is not None: 
        row = _current_event(connection, user_id)
    else:
        with _engine().connect() as c:
            row = _current_event(c, user_id)
    if row is None: return None
    if row[0] == "enter": return row[1]
    return None

# Returns the room name of the selected room
def room_name(room_id):
    if room_id is None:
        return None
    with _engine().begin() as c:
        return c.execute(
                text("SELECT name FROM room WHERE id = :i"),
                {"i": room_id},
        ).scalar_one_or_none()

# Returns true/false if the selected user is in the selected room
def is_inside(room_id, user_id):
    return current_room(user_id) == room_id

# Runs room checks and records valid events
def record_event(room_id, user_id, action, recorded_by):
    # Ensure action is enter/leave
    if action not in ("enter", "leave"):
        raise ValueError("action must be 'enter' or 'leave'")

    # Insert row
    with _engine().begin() as c:
        # Lock to prevent race condition
        c.execute(
            text("SELECT id FROM users WHERE id = :u FOR UPDATE"),
            {"u": user_id},
        )
        
        # Locate user
        current = current_room(user_id, c)
        
        # Checks
        if action == "enter":
            if current == room_id:
                raise InRoom("user is already in this room")
            elif current is not None:
                raise InDifferentRoom("user is in a different room")  
        elif action == "leave":
            if current != room_id:
                raise NotInThisRoom("user is not in this room")
            
        # Insertion
        c.execute(
            text("INSERT INTO gallery_event (user_id, room_id, action, recorded_by) "
                 "VALUES (:u, :r, :a, :by)"),
            {"u": user_id, "r": room_id, "a": action, "by": recorded_by},
        )

def update_role(username, role):
    with _engine().begin() as c:
        row = c.execute(
            text("UPDATE users SET role = :r WHERE username = :u RETURNING id"),
                {"u": username, "r": role},
            ).first()
        return row is not None

def add_user_rows(users):
    with _engine().connect() as conn:
        return[
            {
                "username": u["username"],
                "role": u["role"],
                "room": room_name(current_room(u["id"], connection=conn)),
            }
            for u in users
        ]