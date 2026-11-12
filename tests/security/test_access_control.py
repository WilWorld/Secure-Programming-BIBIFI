"""IDOR and broken access control tests.

Checks that access is decided on the server (not the UI), that IDs in the
request cannot be used to act as another user, and that role-restricted data
is not exposed to lower-privileged accounts.
"""
import pytest


# ------------------------------------------------------------ authentication
@pytest.mark.parametrize("path", ["/", "/room/1", "/admin"])
def test_anonymous_users_are_redirected_to_login(client, path):
    response = client.get(path)

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]


@pytest.mark.parametrize("path", ["/api/rooms", "/api/whoami"])
def test_anonymous_api_calls_get_401(client, path):
    response = client.get(path)

    assert response.status_code == 401
    assert response.is_json


def test_anonymous_users_cannot_record_visits(client, fake):
    response = client.post("/rooms/1/visit", data={"action": "enter"})

    assert response.status_code == 302
    assert "/login" in response.headers["Location"]
    assert fake.events == []


# --------------------------------------------------------------- role checks
def test_guest_is_forbidden_from_admin_page(guest_client):
    assert guest_client.get("/admin").status_code == 403


@pytest.mark.parametrize("client_fixture", ["employee_client", "admin_client"])
def test_staff_can_view_admin_page(request, client_fixture):
    staff_client = request.getfixturevalue(client_fixture)
    assert staff_client.get("/admin").status_code == 200


def test_guest_cannot_submit_admin_actions(guest_client, fake):
    response = guest_client.post(
        "/admin",
        data={"action": "users", "username": "alice", "selected_role": "administrator"},
    )

    assert response.status_code == 403
    assert fake.users[1]["role"] == "guest"


@pytest.mark.xfail(
    reason=(
        "FINDING: POST /admin action=users is protected with "
        "require_role('administrator', 'employee'), so an employee can change "
        "roles in the database even though the UI hides the control. Restrict "
        "role changes to administrators."
    ),
    strict=False,
)
def test_employee_cannot_change_roles(employee_client, fake):
    response = employee_client.post(
        "/admin",
        data={"action": "users", "username": "alice", "selected_role": "administrator"},
    )

    assert response.status_code == 403
    assert fake.users[1]["role"] == "guest"


def test_admin_cannot_assign_unknown_role(admin_client, fake):
    response = admin_client.post(
        "/admin",
        data={"action": "users", "username": "alice", "selected_role": "superadmin"},
    )

    assert response.status_code == 400
    assert fake.users[1]["role"] == "guest"


def test_signup_ignores_injected_role_field(client, fake):
    response = client.post(
        "/signup",
        data={
            "username": "newuser",
            "password": "Password1",
            "passwordMatch": "Password1",
            "role": "administrator",
        },
    )

    assert response.status_code == 302
    assert fake.users[fake.usernames["newuser"]]["role"] == "guest"


# --------------------------------------------------- data exposure (IDOR)
def test_guest_cannot_see_room_visitor_list(guest_client, fake):
    fake.add_event(1, 4, "enter", 4)  # employee1 is inside room 1

    body = guest_client.get("/room/1").get_data(as_text=True)

    assert "employee1" not in body


def test_staff_can_see_room_visitor_list(employee_client, fake):
    fake.add_event(1, 6, "enter", 6)  # guest2 is inside room 1

    body = employee_client.get("/room/1").get_data(as_text=True)

    assert "guest2" in body


def test_whoami_ignores_subject_parameter(guest_client):
    response = guest_client.get("/api/whoami?user_id=5")

    assert response.status_code == 200
    assert response.get_json() == {"username": "guest1", "role": "guest"}


# ----------------------------------------------- acting as another subject
def test_guest_cannot_record_a_visit_for_another_user(guest_client, fake):
    response = guest_client.post(
        "/rooms/1/visit", data={"action": "enter", "user_id": "4"}
    )

    assert response.status_code == 403
    assert fake.events == []
    assert any(record[3] == "denied" for record in fake.audit)


def test_employee_can_record_a_visit_for_another_user(employee_client, fake):
    response = employee_client.post(
        "/rooms/1/visit", data={"action": "enter", "user_id": "6"}
    )

    assert response.status_code == 302
    assert any(
        event["user_id"] == 6
        and event["room_id"] == 1
        and event["action"] == "enter"
        and event["recorded_by"] == 4
        for event in fake.events
    )


def test_visit_for_unknown_user_is_rejected(employee_client, fake):
    response = employee_client.post(
        "/rooms/1/visit", data={"action": "enter", "user_id": "9999"}
    )

    assert response.status_code == 404
    assert fake.events == []


def test_visit_to_unknown_room_is_rejected(employee_client, fake):
    response = employee_client.post(
        "/rooms/999/visit", data={"action": "enter"}
    )

    assert response.status_code == 404
    assert fake.events == []


def test_unknown_room_is_not_found(guest_client):
    assert guest_client.get("/room/999").status_code == 404
