from datetime import timedelta

from app.utils.security import create_access_token, decode_access_token, hash_password, verify_password


def test_password_hash_and_verify_roundtrip():
    plain = "correct horse battery staple"
    hashed = hash_password(plain)

    assert hashed != plain
    assert verify_password(plain, hashed) is True
    assert verify_password("wrong password", hashed) is False


def test_access_token_roundtrip():
    token = create_access_token(subject="user-123")
    subject = decode_access_token(token)
    assert subject == "user-123"


def test_expired_token_is_rejected():
    token = create_access_token(subject="user-123", expires_minutes=-1)  # already expired
    assert decode_access_token(token) is None


def test_tampered_token_is_rejected():
    token = create_access_token(subject="user-123")
    tampered = token[:-1] + ("a" if token[-1] != "a" else "b")
    assert decode_access_token(tampered) is None
