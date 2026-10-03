Enum user_role {
  guest
  employee
  administrator
}

Enum event_action {
  enter
  leave
}

Table users {
  id int [pk, increment]
  username varchar(255) [unique, not null]
  password_hash varchar(255) [not null]
  role user_role [not null, default: 'guest']
  created_at timestamp [not null, default: `now()`]
}

Table room {
  id int [pk, increment]
  name varchar(255) [unique, not null]
}

Table art {
  id int [pk, increment]
  title varchar(255) [not null]
  artist varchar(255)
  price_cents int
  image_path varchar(500)
  room_id int [ref: > room.id]
}

// One row per enter/leave. room_id NULL = the gallery itself.
Table gallery_event {
  id int [pk, increment]
  user_id int [not null, ref: > users.id]
  room_id int [ref: > room.id]
  action event_action [not null]
  occurred_at timestamp [not null, default: `now()`]
  recorded_by int [ref: > users.id]
}

Table audit_log {
  id int [pk, increment]
  actor_id int [ref: > users.id]
  action varchar(100) [not null]   // e.g. 'login_failed', 'role_changed'
  target varchar(255)
  success boolean [not null]
  created_at timestamp [not null, default: `now()`]
}

Ref: "art"."image_path" ?<>? "art"."room_id"