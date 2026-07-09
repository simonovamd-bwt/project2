"""Integration tests for registration, login, sessions, and logout."""

from tests.conftest import register


def test_register_creates_user_and_session(client):
    res = register(client)
    assert res.status_code == 201
    assert res.json()["username"] == "alice"
    # The session cookie lets us reach an authenticated endpoint.
    me = client.get("/api/auth/me")
    assert me.status_code == 200
    assert me.json()["username"] == "alice"


def test_register_duplicate_username_conflicts(client):
    register(client)
    res = register(client)
    assert res.status_code == 409


def test_register_validates_short_password(client):
    res = client.post("/api/auth/register", json={"username": "bob", "password": "123"})
    assert res.status_code == 422


def test_register_rejects_overlong_password(client):
    # bcrypt only hashes 72 bytes; the schema must reject longer ones, not 500.
    res = client.post(
        "/api/auth/register", json={"username": "bob", "password": "a" * 73}
    )
    assert res.status_code == 422


def test_register_rejects_short_username(client):
    res = client.post(
        "/api/auth/register", json={"username": "ab", "password": "secret1"}
    )
    assert res.status_code == 422


def test_login_with_correct_and_wrong_password(client):
    register(client, "carol", "hunter2")
    client.post("/api/auth/logout")

    bad = client.post("/api/auth/login", json={"username": "carol", "password": "wrongpw"})
    assert bad.status_code == 401

    good = client.post("/api/auth/login", json={"username": "carol", "password": "hunter2"})
    assert good.status_code == 200
    assert client.get("/api/auth/me").status_code == 200


def test_login_unknown_username_returns_401_not_404(client):
    res = client.post(
        "/api/auth/login", json={"username": "ghost", "password": "secret1"}
    )
    # Same status for "no such user" and "wrong password" avoids leaking
    # which usernames exist.
    assert res.status_code == 401


def test_logout_clears_session(client):
    register(client)
    assert client.post("/api/auth/logout").status_code == 204
    assert client.get("/api/auth/me").status_code == 401


def test_logout_without_session_is_a_noop(client):
    assert client.post("/api/auth/logout").status_code == 204


def test_me_requires_authentication(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_rejects_a_forged_session_cookie(client):
    # A cookie whose token matches no session row must be rejected (deps.py
    # "Invalid session" branch), not silently treated as anonymous or accepted.
    client.cookies.set("prelegal_session", "not-a-real-token")
    assert client.get("/api/auth/me").status_code == 401


def test_register_strips_surrounding_whitespace_in_username(client):
    res = client.post(
        "/api/auth/register", json={"username": "  spacey  ", "password": "secret1"}
    )
    assert res.status_code == 201
    assert res.json()["username"] == "spacey"


def test_login_accepts_username_with_surrounding_whitespace(client):
    register(client, "trimmed", "secret1")
    client.post("/api/auth/logout")
    # Login trims the username too, so padding must still resolve the user.
    res = client.post(
        "/api/auth/login", json={"username": "  trimmed  ", "password": "secret1"}
    )
    assert res.status_code == 200
    assert res.json()["username"] == "trimmed"


def test_user_out_never_leaks_password_hash(client):
    body = register(client).json()
    assert "password_hash" not in body
    assert "password" not in body
    assert set(body.keys()) == {"id", "username"}


def test_register_accepts_boundary_password_lengths(client):
    # min_length=6 and max_length=72 (bcrypt's limit) must both be accepted.
    short_ok = client.post(
        "/api/auth/register", json={"username": "sixchar", "password": "abcdef"}
    )
    assert short_ok.status_code == 201

    long_ok = client.post(
        "/api/auth/register", json={"username": "maxchar", "password": "a" * 72}
    )
    assert long_ok.status_code == 201


def test_two_users_can_hold_sessions_and_me_returns_the_cookie_owner(client):
    # Register alice (cookie = alice's session), then log her out and register
    # bob; /me must reflect whoever the current cookie belongs to.
    register(client, "alice", "secret1")
    assert client.get("/api/auth/me").json()["username"] == "alice"
    client.post("/api/auth/logout")

    register(client, "bob", "secret1")
    assert client.get("/api/auth/me").json()["username"] == "bob"
