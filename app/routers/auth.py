from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.dependencies.authentication import get_current_user
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LogoutRequest,
    RefreshRequest,
    RegisterRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


def issue_tokens(db: Session, user: User) -> TokenResponse:
    access_token, access_expires = create_access_token(user.id)
    raw_refresh, refresh_digest, refresh_expires = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_digest,
            expires_at=refresh_expires,
        )
    )
    db.commit()
    return TokenResponse(
        access_token=access_token,
        expires_in=access_expires,
        refresh_token=raw_refresh,
        refresh_expires_in=settings.refresh_token_expire_days * 86400,
    )


@router.post(
    "/register",
    response_model=UserProfile,
    status_code=status.HTTP_201_CREATED,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
) -> UserProfile:
    existing_user = db.scalar(select(User).where(User.email == str(payload.email)))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name,
        email=str(payload.email),
        password_hash=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        ) from None
    db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == str(payload.email)))
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )
    return issue_tokens(db, user)


@router.post("/refresh", response_model=TokenResponse)
def refresh(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
) -> TokenResponse:
    digest = hash_refresh_token(payload.refresh_token)
    stored_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == digest).with_for_update()
    )
    now = datetime.now(UTC)

    if stored_token is None or stored_token.revoked_at is not None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid or revoked.",
        )

    expires_at = stored_token.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=UTC)
    if expires_at <= now:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token has expired.",
        )

    user = db.get(User, stored_token.user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token is invalid.",
        )

    # Rotate: the old refresh token becomes unusable before a new one is issued.
    stored_token.revoked_at = now
    access_token, access_expires = create_access_token(user.id)
    raw_refresh, refresh_digest, refresh_expires = create_refresh_token()
    db.add(
        RefreshToken(
            user_id=user.id,
            token_hash=refresh_digest,
            expires_at=refresh_expires,
        )
    )
    db.commit()

    return TokenResponse(
        access_token=access_token,
        expires_in=access_expires,
        refresh_token=raw_refresh,
        refresh_expires_in=settings.refresh_token_expire_days * 86400,
    )


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    payload: LogoutRequest,
    db: Session = Depends(get_db),
) -> Response:
    digest = hash_refresh_token(payload.refresh_token)
    stored_token = db.scalar(
        select(RefreshToken).where(RefreshToken.token_hash == digest)
    )
    if stored_token is not None and stored_token.revoked_at is None:
        stored_token.revoked_at = datetime.now(UTC)
        db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get("/me", response_model=UserProfile)
def get_me(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    return current_user
