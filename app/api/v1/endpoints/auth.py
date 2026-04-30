from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_active_user
from app.core.security import (
    hash_password,
    verify_password,
    create_token_pair,
    verify_refresh_token,
)
from app.models.user import User
from app.models.marketing import ProductFeature
from app.schemas.auth import (
    AuthResponse,
    MessageResponse,
    RefreshTokenRequest,
    TokenResponse,
    UserLoginRequest,
    UserResponse,
    UserSignupRequest,
)

router = APIRouter()

ACCESS_TOKEN_EXPIRE_SECONDS = 15 * 60  # 15 minutes


def _build_user_response(user: User) -> UserResponse:
    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_verified=user.is_verified,
        is_super_admin=user.is_super_admin,
        avatar_url=user.avatar_url,
        created_at=user.created_at.isoformat(),
    )

# ---------------------------------------------------------------------------
# PUBLIC: GET /auth/product-guide
# ---------------------------------------------------------------------------
@router.get("/product-guide", response_model=List[Any])
def get_product_guide(db: Session = Depends(get_db)):
    """Retrieve high-fidelity platform onboarding nodes."""
    features = db.query(ProductFeature).order_by(ProductFeature.display_order).all()
    return [
        {
            "id": f.id,
            "title": f.title,
            "description": f.description,
            "icon_name": f.icon_name,
            "benefit_highlight": f.benefit_highlight,
            "category": f.category
        } for f in features
    ]

# ---------------------------------------------------------------------------
# POST /auth/signup
# ---------------------------------------------------------------------------
@router.post(
    "/signup",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user",
)
def signup(payload: UserSignupRequest, db: Session = Depends(get_db)):
    """Create a new user account."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    user = User(
        email=payload.email,
        full_name=payload.full_name.strip(),
        hashed_password=hash_password(payload.password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token, refresh_token = create_token_pair(user.id, user.email)

    return AuthResponse(
        user=_build_user_response(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        ),
    )


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------
@router.post(
    "/login",
    response_model=AuthResponse,
    summary="Log in with email and password",
)
def login(payload: UserLoginRequest, db: Session = Depends(get_db)):
    """Authenticate a user and return JWT access + refresh tokens."""
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated. Please contact support.",
        )

    access_token, refresh_token = create_token_pair(user.id, user.email)

    return AuthResponse(
        user=_build_user_response(user),
        tokens=TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
        ),
    )


# ---------------------------------------------------------------------------
# POST /auth/refresh
# ---------------------------------------------------------------------------
@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="Refresh access token using a refresh token",
)
def refresh_access_token(
    payload: RefreshTokenRequest,
    db: Session = Depends(get_db),
):
    """Exchange a valid refresh token for a new access + refresh token pair."""
    user_id = verify_refresh_token(payload.refresh_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or deactivated.",
        )

    access_token, refresh_token = create_token_pair(user.id, user.email)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=ACCESS_TOKEN_EXPIRE_SECONDS,
    )


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------
@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the currently authenticated user",
)
def get_me(current_user: User = Depends(get_current_active_user)):
    """Return the profile of the currently authenticated user."""
    return _build_user_response(current_user)


# ---------------------------------------------------------------------------
# POST /auth/logout
# ---------------------------------------------------------------------------
@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Log out (client-side token invalidation)",
)
def logout(_: User = Depends(get_current_active_user)):
    """Logout endpoint."""
    return MessageResponse(message="Logged out successfully. Please clear your tokens.")
