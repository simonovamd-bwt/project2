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
