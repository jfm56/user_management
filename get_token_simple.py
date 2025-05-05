import asyncio
import json
import os
import time
import hmac
import hashlib
import base64
from urllib.parse import quote_plus
from datetime import datetime, timedelta

from app.database import Database
from app.models.user_model import User, UserRole
from sqlalchemy import text

# JWT settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your_jwt_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def encode_jwt(payload, secret, algorithm="HS256"):
    """Simple JWT encoder without dependencies"""
    # Create the header
    header = {"alg": algorithm, "typ": "JWT"}
    
    # Base64 encode the header and payload
    header_json = json.dumps(header, separators=(',', ':')).encode()
    header_b64 = base64.urlsafe_b64encode(header_json).decode().rstrip('=')
    
    payload_json = json.dumps(payload, separators=(',', ':')).encode()
    payload_b64 = base64.urlsafe_b64encode(payload_json).decode().rstrip('=')
    
    # Create the signature
    message = f"{header_b64}.{payload_b64}"
    signature = hmac.new(
        secret.encode(),
        message.encode(),
        hashlib.sha256
    ).digest()
    signature_b64 = base64.urlsafe_b64encode(signature).decode().rstrip('=')
    
    # Return the complete JWT
    return f"{header_b64}.{payload_b64}.{signature_b64}"

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
            "exp": int(expire.timestamp()),
            "role": UserRole.ADMIN.value
        }
        
        encoded_jwt = encode_jwt(to_encode, SECRET_KEY)
        print(f"Admin token: {encoded_jwt}")
        return encoded_jwt

if __name__ == "__main__":
    asyncio.run(get_admin_token())
