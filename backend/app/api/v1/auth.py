"""
Authentication endpoints: registration, login, Google OAuth, current user.
"""

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from app.api.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


# ---------------------------------------------------------------------------
# Request / response schemas
# ---------------------------------------------------------------------------

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    name: str = Field(..., min_length=1, max_length=200)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Payload sent by the frontend after Google sign-in."""
    id_token: str = Field(..., description="Google ID token from OAuth callback")


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = Field(description="Token lifetime in seconds")


class UserResponse(BaseModel):
    id: str
    email: str
    name: str
    avatar_url: Optional[str] = None
    is_active: bool = True
    created_at: datetime

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    payload: RegisterRequest,
    # db=Depends(get_db),
):
    """
    Register a new user with email and password.
    Returns a JWT access token on success.
    """
    # TODO: check if email already taken
    # existing = await crud.user.get_by_email(db, payload.email)
    # if existing:
    #     raise HTTPException(
    #         status_code=status.HTTP_409_CONFLICT,
    #         detail="Email already registered",
    #     )
    # hashed = hash_password(payload.password)
    # user = await crud.user.create(db, email=payload.email, name=payload.name, hashed_password=hashed)
    # token = create_access_token(subject=str(user.id))
    # return AuthResponse(access_token=token, expires_in=3600)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Registration not implemented yet",
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    payload: LoginRequest,
    # db=Depends(get_db),
):
    """
    Authenticate with email and password. Returns a JWT access token.
    """
    # user = await crud.user.authenticate(db, email=payload.email, password=payload.password)
    # if not user:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid email or password",
    #     )
    # token = create_access_token(subject=str(user.id))
    # return AuthResponse(access_token=token, expires_in=3600)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Login not implemented yet",
    )


@router.post("/google", response_model=AuthResponse)
async def google_auth(
    payload: GoogleAuthRequest,
    # db=Depends(get_db),
):
    """
    Verify a Google ID token, create or link the user account,
    and return a JWT access token.
    """
    # TODO: verify Google ID token with google-auth library
    # from google.oauth2 import id_token as google_id_token
    # from google.auth.transport import requests as google_requests
    # info = google_id_token.verify_oauth2_token(
    #     payload.id_token, google_requests.Request(), GOOGLE_CLIENT_ID
    # )
    # email = info["email"]
    # user = await crud.user.get_by_email(db, email)
    # if not user:
    #     user = await crud.user.create(
    #         db, email=email, name=info.get("name", ""),
    #         avatar_url=info.get("picture"), auth_provider="google",
    #     )
    # token = create_access_token(subject=str(user.id))
    # return AuthResponse(access_token=token, expires_in=3600)
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Google auth not implemented yet",
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user=Depends(get_current_user),
):
    """
    Return the currently authenticated user's profile.
    """
    return current_user
