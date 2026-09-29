import pytest

from app.schemas.auth import UserCreate
from app.services.auth_service import (
    AuthError,
    authenticate_user,
    get_user_by_email,
    register_user,
)


def test_register_user_creates_row_with_hashed_password(db_session):
    user = register_user(db_session, UserCreate(email="Test@Example.com", password="supersecret1"))

    assert user.id is not None
    # Email is normalized to lowercase for consistent lookups
    assert user.email == "test@example.com"
    assert user.hashed_password != "supersecret1"


def test_register_duplicate_email_raises(db_session):
    register_user(db_session, UserCreate(email="dup@example.com", password="supersecret1"))

    with pytest.raises(AuthError) as exc_info:
        register_user(db_session, UserCreate(email="dup@example.com", password="anotherpassword"))
    assert exc_info.value.status_code == 409


def test_authenticate_user_succeeds_with_correct_password(db_session):
    register_user(db_session, UserCreate(email="login@example.com", password="mypassword1"))

    user = authenticate_user(db_session, "login@example.com", "mypassword1")
    assert user.email == "login@example.com"


def test_authenticate_user_fails_with_wrong_password(db_session):
    register_user(db_session, UserCreate(email="login2@example.com", password="mypassword1"))

    with pytest.raises(AuthError) as exc_info:
        authenticate_user(db_session, "login2@example.com", "wrongpassword")
    assert exc_info.value.status_code == 401


def test_authenticate_nonexistent_user_fails(db_session):
    with pytest.raises(AuthError) as exc_info:
        authenticate_user(db_session, "nobody@example.com", "whatever")
    assert exc_info.value.status_code == 401


def test_get_user_by_email_is_case_insensitive(db_session):
    register_user(db_session, UserCreate(email="CaseTest@Example.com", password="supersecret1"))
    found = get_user_by_email(db_session, "casetest@example.com")
    assert found is not None
