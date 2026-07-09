from app.core.security import hash_password, new_session_token, verify_password


def test_hash_password_is_not_plaintext():
    assert hash_password("secret1") != "secret1"


def test_verify_password_accepts_correct_password():
    hashed = hash_password("secret1")
    assert verify_password("secret1", hashed) is True


def test_verify_password_rejects_wrong_password():
    hashed = hash_password("secret1")
    assert verify_password("wrong-password", hashed) is False


def test_verify_password_never_raises_on_garbage_hash():
    assert verify_password("secret1", "not-a-bcrypt-hash") is False


def test_new_session_token_is_unique_and_url_safe():
    tokens = {new_session_token() for _ in range(100)}
    assert len(tokens) == 100
    assert all(t.isascii() and " " not in t for t in tokens)
