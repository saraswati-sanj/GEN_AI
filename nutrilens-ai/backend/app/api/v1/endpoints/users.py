"""
NutriLens AI — User Profile & Auth API Endpoints
"""
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, decode_access_token, get_password_hash, verify_password
from app.models.user import User
from app.models.schemas import UserCreate, UserLogin, UserResponse, UserUpdate, Token

router = APIRouter(prefix="/users", tags=["Users & Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users/login-form", auto_error=False)


async def get_current_user_optional(
    token: Optional[str] = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Optional[User]:
    """Extract user from JWT token if provided; returns None for guest access."""
    if not token:
        return None
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        return None
    user_id_str = payload["sub"]
    try:
        user_id = uuid.UUID(user_id_str)
    except ValueError:
        return None

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    return user


async def get_current_user(
    user: Optional[User] = Depends(get_current_user_optional),
) -> User:
    """FastAPI dependency requiring an authenticated user."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new NutriLens AI user account."""
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    db_user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        full_name=user_in.full_name,
        age=user_in.age,
        health_conditions=user_in.health_conditions.model_dump(),
        allergies=user_in.allergies,
        preferred_language=user_in.preferred_language,
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)

    token_str = create_access_token(data={"sub": str(db_user.id)})
    return Token(access_token=token_str, user=UserResponse.model_validate(db_user))


@router.post("/login", response_model=Token)
async def login(
    login_in: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user with JSON credentials."""
    result = await db.execute(select(User).where(User.email == login_in.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(login_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    token_str = create_access_token(data={"sub": str(user.id)})
    return Token(access_token=token_str, user=UserResponse.model_validate(user))


@router.post("/login-form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 compatible form login."""
    return await login(UserLogin(email=form_data.username, password=form_data.password), db)


@router.get("/me", response_model=UserResponse)
async def read_current_user_profile(
    current_user: User = Depends(get_current_user),
):
    """Fetch profile of current logged-in user."""
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile preferences, health conditions, allergies, or preferred language."""
    if user_update.full_name is not None:
        current_user.full_name = user_update.full_name
    if user_update.age is not None:
        current_user.age = user_update.age
    if user_update.health_conditions is not None:
        current_user.health_conditions = user_update.health_conditions.model_dump()
    if user_update.allergies is not None:
        current_user.allergies = user_update.allergies
    if user_update.preferred_language is not None:
        current_user.preferred_language = user_update.preferred_language

    await db.commit()
    await db.refresh(current_user)
    return current_user
