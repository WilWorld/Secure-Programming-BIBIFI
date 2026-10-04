"""Database access for rooms, artworks, and visits. Every query is parameterized.

Targets database/schema.sql:
  room(id PK, name UNIQUE)
  art(id PK, title, artist, price_cents, image_path, room_id FK)
  gallery_event(id PK, user_id FK, room_id FK, action, occurred_at, recorded_by FK)
"""
from sqlalchemy import text


def _engine():
    import auth_store
    return auth_store.engine()


def list_rooms():
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT r.id, r.name, "
                 "  (SELECT count(*) FROM art a WHERE a.room_id = r.id) AS artwork_count, "
                 "  (SELECT count(*) FROM gallery_event g "
                 "     WHERE g.room_id = r.id AND g.action = 'enter') AS visitor_count "
                 "FROM room r ORDER BY r.name"),
        ).mappings().all()
    return [dict(r) for r in rows]


def get_room(room_id):
    """Return one room, or None if it does not exist."""
    with _engine().connect() as c:
        row = c.execute(
            text("SELECT id, name FROM room WHERE id = :i"), {"i": room_id},
        ).mappings().first()
    return dict(row) if row else None


def list_art(room_id):
    with _engine().connect() as c:
        rows = c.execute(
            text("SELECT id, title, artist, price_cents, image_path "
                 "FROM art WHERE room_id = :i ORDER BY title"),
            {"i": room_id},
        ).mappings().all()
    return [dict(r) for r in rows]


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


def is_inside(room_id, user_id):
    """True when this user's most recent event in the room was an entry."""
    with _engine().connect() as c:
        row = c.execute(
            text("SELECT action FROM gallery_event "
                 "WHERE room_id = :r AND user_id = :u "
                 "ORDER BY occurred_at DESC, id DESC LIMIT 1"),
            {"r": room_id, "u": user_id},
        ).first()
    return row is not None and row[0] == "enter"


def record_event(room_id, user_id, action, recorded_by):
    """Append an enter/leave event. The guest records their own movement."""
    if action not in ("enter", "leave"):
        raise ValueError("action must be 'enter' or 'leave'")
    with _engine().begin() as c:
        c.execute(
            text("INSERT INTO gallery_event (user_id, room_id, action, recorded_by) "
                 "VALUES (:u, :r, :a, :by)"),
            {"u": user_id, "r": room_id, "a": action, "by": recorded_by},
        )