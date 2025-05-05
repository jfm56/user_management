import asyncio
from app.models.user_model import UserRole

def check_role():
    print(f"UserRole.ADMIN = {UserRole.ADMIN}")
    print(f"UserRole.ADMIN.value = {UserRole.ADMIN.value}")
    print(f"str(UserRole.ADMIN) = {str(UserRole.ADMIN)}")
    
    # Check what the JWT token would contain
    print(f"This should match the JWT token's 'role' claim: {UserRole.ADMIN.value}")

if __name__ == "__main__":
    check_role()
