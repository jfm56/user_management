import asyncio
import os
from datetime import datetime, timedelta
from jose import jwt

from app.database import Database
from app.models.user_model import User, UserRole
from sqlalchemy import text

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_jwt_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

async def get_admin_token():
    # Initialize the database
    database_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://user:password@postgres/myappdb')
    Database.initialize(database_url)
    
    # Get session
    async_session = Database.get_session_factory()
    
    async with async_session() as session:
        # Get the admin user
        result = await session.execute(text("SELECT id FROM users WHERE email = 'admin@example.com'"))
        admin_id = result.scalar_one_or_none()
        
        if not admin_id:
            print("Admin user not found")
            return
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        expire = datetime.utcnow() + access_token_expires
        
        to_encode = {
            "sub": str(admin_id),
            "exp": expire,
            "role": UserRole.ADMIN.value
        }
        
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        print(f"Admin token: {encoded_jwt}")
        return encoded_jwt

if __name__ == "__main__":
    asyncio.run(get_admin_token())
