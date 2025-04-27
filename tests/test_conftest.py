import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.dependencies import get_db
from app.models.user_model import User, UserRole
from app.utils.security import get_password_hash

# --- Async test client fixture ---
@pytest.fixture
async def async_client():
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        yield client

# --- Database session fixture ---
@pytest.fixture
async def db_session():
    async for session in get_db():
        yield session

# --- User fixture (basic user) ---
@pytest.fixture
async def user(db_session: AsyncSession):
    new_user = User(
        nickname="testuser",
        email="testuser@example.com",
        hashed_password=get_password_hash("MySuperPassword$1234"),
        email_verified=False,
        is_locked=False,
        role=UserRole.AUTHENTICATED
    )
    db_session.add(new_user)
    await db_session.commit()
    await db_session.refresh(new_user)
    return new_user

# --- Verified user fixture ---
@pytest.fixture
async def verified_user(db_session: AsyncSession):
    user = User(
        nickname="verifieduser",
        email="verified@example.com",
        hashed_password=get_password_hash("MySuperPassword$1234"),
        email_verified=True,
        is_locked=False,
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# --- Locked user fixture ---
@pytest.fixture
async def locked_user(db_session: AsyncSession):
    user = User(
        nickname="lockeduser",
        email="locked@example.com",
        hashed_password=get_password_hash("MySuperPassword$1234"),
        email_verified=True,
        is_locked=True,
        role=UserRole.AUTHENTICATED
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# --- Admin user fixture ---
@pytest.fixture
async def admin_user(db_session: AsyncSession):
    user = User(
        nickname="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("MySuperPassword$1234"),
        email_verified=True,
        is_locked=False,
        role=UserRole.ADMIN
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user

# --- Bulk create 50 users fixture ---
@pytest.fixture
async def users_with_same_role_50_users(db_session: AsyncSession):
    users = [
        User(
            nickname=f"user_{i}",
            email=f"user_{i}@example.com",
            hashed_password=get_password_hash("MySuperPassword$1234"),
            email_verified=True,
            is_locked=False,
            role=UserRole.AUTHENTICATED
        )
        for i in range(50)
    ]
    db_session.add_all(users)
    await db_session.commit()
    return users
