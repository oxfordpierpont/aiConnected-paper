"""User service."""

from typing import Optional
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User, Agency
from app.services.auth_service import AuthService


class UserService:
    """Service for user operations."""

    @staticmethod
    async def get_by_id(db: AsyncSession, user_id: str) -> Optional[User]:
        """Get a user by ID."""
        result = await db.execute(select(User).where(User.id == user_id))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get a user by email."""
        result = await db.execute(select(User).where(User.email == email.lower()))
        return result.scalar_one_or_none()

    @staticmethod
    async def create(
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        role: str = "agency_admin",
        agency_id: Optional[str] = None,
        is_verified: bool = False,
    ) -> User:
        """Create a new user."""
        user = User(
            id=str(uuid4()),
            email=email.lower(),
            hashed_password=AuthService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            agency_id=agency_id,
            is_active=True,
            is_verified=is_verified,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user

    @staticmethod
    async def create_with_agency(
        db: AsyncSession,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        agency_name: str,
    ) -> tuple[User, Agency]:
        """Create a new user with a new agency."""
        from python_slugify import slugify

        # Create agency first
        agency_slug = slugify(agency_name)
        agency = Agency(
            id=str(uuid4()),
            name=agency_name,
            slug=agency_slug,
            subdomain=agency_slug[:50],
            is_active=True,
        )
        db.add(agency)
        await db.flush()

        # Create user with agency
        user = User(
            id=str(uuid4()),
            email=email.lower(),
            hashed_password=AuthService.hash_password(password),
            first_name=first_name,
            last_name=last_name,
            role="agency_admin",
            agency_id=agency.id,
            is_active=True,
            is_verified=True,  # Auto-verify for now
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        await db.refresh(agency)

        return user, agency

    @staticmethod
    async def update(db: AsyncSession, user: User, **kwargs) -> User:
        """Update a user."""
        for key, value in kwargs.items():
            if hasattr(user, key) and value is not None:
                if key == "password":
                    user.hashed_password = AuthService.hash_password(value)
                else:
                    setattr(user, key, value)
        await db.commit()
        await db.refresh(user)
        return user
