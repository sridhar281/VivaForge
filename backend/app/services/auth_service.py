import uuid

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import UserCreate
from app.utils.security import hash_password, verify_password


class AuthError(Exception):
    """Raised for any auth failure the API layer should turn into a 4xx response."""
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email.lower()).first()


def get_user_by_id(db: Session, user_id: str) -> User | None:
    try:
        parsed_id = uuid.UUID(user_id)
    except (ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == parsed_id).first()


def register_user(db: Session, payload: UserCreate) -> User:
    if get_user_by_email(db, payload.email):
        raise AuthError("An account with this email already exists.", status_code=409)

    user = User(
        email=payload.email.lower(),
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, email: str, password: str) -> User:
    user = get_user_by_email(db, email)
    # Deliberately identical error for "no such user" and "wrong password" —
    # don't leak which one failed.
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Incorrect email or password.", status_code=401)
    return user
