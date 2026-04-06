from datetime import datetime, timedelta
from typing import Any

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.db.session import get_db
from app.models import RefreshSession, User
from app.schemas.auth import LoginRequest, LoginResponse, TokenResponse
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["auth"])


def set_refresh_cookie(response: Response, refresh_token: str) -> None:
    """Set the HTTP-only refresh token cookie on the response."""
    response.set_cookie(
        key=settings.REFRESH_TOKEN_COOKIE_NAME,
        value=refresh_token,
        httponly=True,
        secure=settings.REFRESH_TOKEN_COOKIE_SECURE,
        samesite=settings.REFRESH_TOKEN_COOKIE_SAMESITE,
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()),
        path="/",
    )


def revoke_refresh_session(db: Session, token: str) -> None:
    """Revoke an active refresh session by hashed token, if it exists."""
    token_hash = hash_refresh_token(token)
    session = db.execute(
        select(RefreshSession).where(
            RefreshSession.token_hash == token_hash,
            RefreshSession.revoked_at.is_(None),
        )
    ).scalar_one_or_none()
    if session is None:
        return
    typed_session: Any = session
    setattr(typed_session, "revoked_at", datetime.now())
    db.add(typed_session)
    db.commit()


def authenticate_user(db: Session, email: str, password: str) -> Any:
    """Validate user credentials and return the user model instance."""
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    typed_user: Any = user
    user_password_hash = str(getattr(typed_user, "password_hash"))
    is_valid_password, updated_hash = verify_password(password, user_password_hash)

    if not is_valid_password:
        raise HTTPException(status_code=401, detail="Invalid email or password")

    if updated_hash:
        setattr(typed_user, "password_hash", updated_hash)
        db.add(typed_user)
        db.commit()

    return typed_user


def issue_tokens_for_user(
    db: Session, response: Response, typed_user: Any
) -> TokenResponse:
    """Create access/refresh tokens, persist refresh session, and set cookie."""
    user_id = int(getattr(typed_user, "id"))

    access_token = create_access_token(subject=user_id)
    refresh_token = create_refresh_token()

    refresh_session = RefreshSession(
        user_id=user_id,
        token_hash=hash_refresh_token(refresh_token),
        expires_at=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_session)
    db.commit()

    set_refresh_cookie(response, refresh_token)
    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    """Authenticate user and start a session.

    Validation:
    - Requires JSON body with `email` and `password`.
    - Email/password must match a user record.

    Auth input:
    - No bearer token required.
    - No token in request body; credentials only.
    - Sets refresh token as HTTP-only cookie in response.
    """
    typed_user = authenticate_user(db, payload.email, payload.password)
    token_response = issue_tokens_for_user(db, response, typed_user)
    return LoginResponse(access_token=token_response.access_token, user=typed_user)


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """OAuth2 password-flow login endpoint used by Swagger Authorize.

    Validation:
    - Requires form fields `username` (email) and `password`.
    - Credentials must match a user record.

    Auth input:
    - No bearer token required.
    - No token in request body.
    - Sets refresh token as HTTP-only cookie in response.
    """
    typed_user = authenticate_user(db, form_data.username, form_data.password)
    return issue_tokens_for_user(db, response, typed_user)


@router.post("/refresh", response_model=TokenResponse)
def refresh_access_token(
    request: Request, response: Response, db: Session = Depends(get_db)
):
    """Rotate refresh token cookie and issue a new access token.

    Validation:
    - Requires a non-expired, non-revoked refresh session.

    Auth input:
    - Uses refresh token from HTTP-only cookie.
    - Does not use bearer token.
    - Does not require token in request body.
    """
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if not refresh_token:
        raise HTTPException(status_code=401, detail="Refresh token is missing")

    refresh_token_hash = hash_refresh_token(refresh_token)
    refresh_session = db.execute(
        select(RefreshSession).where(
            RefreshSession.token_hash == refresh_token_hash,
            RefreshSession.revoked_at.is_(None),
            RefreshSession.expires_at > datetime.now(),
        )
    ).scalar_one_or_none()

    if refresh_session is None:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    typed_refresh_session: Any = refresh_session
    refresh_user_id = int(getattr(typed_refresh_session, "user_id"))

    setattr(typed_refresh_session, "revoked_at", datetime.now())
    db.add(typed_refresh_session)

    rotated_refresh_token = create_refresh_token()
    rotated_refresh_session = RefreshSession(
        user_id=refresh_user_id,
        token_hash=hash_refresh_token(rotated_refresh_token),
        expires_at=datetime.now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(rotated_refresh_session)
    db.commit()

    set_refresh_cookie(response, rotated_refresh_token)
    access_token = create_access_token(subject=refresh_user_id)
    return TokenResponse(access_token=access_token)


@router.post("/logout")
def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    """End the current refresh session and clear cookie.

    Validation:
    - Refresh cookie must be present.

    Auth input:
    - Uses refresh token from HTTP-only cookie.
    - Does not use bearer token.
    - Does not require token in request body.
    """
    refresh_token = request.cookies.get(settings.REFRESH_TOKEN_COOKIE_NAME)
    if refresh_token is None:
        raise HTTPException(status_code=400, detail="Refresh token cookie is missing")
    if refresh_token:
        revoke_refresh_session(db, refresh_token)

    response.delete_cookie(key=settings.REFRESH_TOKEN_COOKIE_NAME, path="/")
    return {"message": "Logged out successfully"}
