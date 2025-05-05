import asyncio
import os
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from app.models.user_model import User, UserRole
from app.utils.security import get_password_hash
from app.database import Database
from settings.config import settings

async def create_admin():
    # Initialize the database with the URL from settings
    database_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://user:password@postgres/myappdb')
    Database.initialize(database_url)
    
    # Get the session factory and create a session
    async_session = Database.get_session_factory()
    
    async with async_session() as session:
        # Check if admin already exists
        result = await session.execute(text("SELECT id FROM users WHERE email = 'admin@example.com'"))
        if result.first():
            print("Admin user already exists")
            return

        # Create a new admin user
        admin = User(
            id=uuid4(),
            email='admin@example.com',
            nickname='admin',
            hashed_password=get_password_hash('password123'),
            role=UserRole.ADMIN,
            email_verified=True
        )
        
        session.add(admin)
        await session.commit()
        print(f"Admin created with ID: {admin.id}")
        return admin

if __name__ == "__main__":
    asyncio.run(create_admin())
