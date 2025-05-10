"""
Router for email notification testing endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from uuid import UUID
from enum import Enum
from pydantic import BaseModel, Field

from app.dependencies import get_db, get_email_service, get_current_user, get_settings
from app.services.email_service import EmailService
from app.models.user_model import User, UserRole
from app.services.user_service import UserService

router = APIRouter(
    prefix="/emails",
    tags=["Email Notifications"]
)

class RoleEnum(str, Enum):
    ANONYMOUS = "ANONYMOUS"
    AUTHENTICATED = "AUTHENTICATED"
    MANAGER = "MANAGER"
    ADMIN = "ADMIN"


def admin_required(current_user_data: dict = Depends(get_current_user)):
    if current_user_data.get('role') != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can use this testing endpoint")
    return current_user_data

@router.post("/test/verification/{user_id}", status_code=202)
async def test_verification_email(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    settings = Depends(get_settings),
    _: dict = Depends(admin_required)
):
    """
    Test endpoint to send a verification email to a user.
    This is for testing purposes only.
    """
    # Get the user to send the verification email to
    try:
        # Validate UUID format
        try:
            user_id = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid user_id format")
            
        # Check if user exists
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Send verification email directly
        verification_url = f"{settings.server_base_url.rstrip('/')}/verify-email/{user.id}/{user.verification_token}"
        dashboard_url = f"{settings.server_base_url.rstrip('/')}/dashboard"
        data = {
            "name": user.nickname or user.first_name or "User",
            "verification_url": verification_url,
            "email": user.email,
            "dashboard_url": dashboard_url
        }
        await email_service.send_user_email_async(data, 'email_verification')
        return {"status": "success", "message": f"Verification email sent to user {user.email} (test direct)"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@router.post("/test/account-locked/{user_id}", status_code=202)
async def test_account_locked_email(
    user_id: str,
    session: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    settings=Depends(get_settings),
    _: dict = Depends(admin_required)
):
    """
    Test endpoint to send an account locked email to a user.
    This is for testing purposes only.
    """
    # Get the user to send the account locked email to
    try:
        # Validate UUID format
        try:
            user_id = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid user_id format")
            
        # Check if user exists
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Direct send for account locked test endpoint
        support_url = f"{settings.server_base_url.rstrip('/')}/support"
        dashboard_url = f"{settings.server_base_url.rstrip('/')}/dashboard"
        data = {
            "name": user.nickname or user.first_name or "User",
            "support_url": support_url,
            "email": user.email,
            "dashboard_url": dashboard_url
        }
        await email_service.send_user_email_async(data, 'account_locked')
        return {"status": "success", "message": f"Account locked email sent to user {user.email} (test direct)"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send account locked email: {str(e)}")

@router.post("/test/role-upgrade/{user_id}/{old_role}/{new_role}", status_code=202)
async def test_role_upgrade_email(
    user_id: str,
    old_role: RoleEnum,
    new_role: RoleEnum,
    session: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    settings = Depends(get_settings),
    _: dict = Depends(admin_required)
):
    """
    Test endpoint to send a role upgrade email to a user.
    This is for testing purposes only.
    """
    # Get the user to send the role upgrade email to
    try:
        # First, validate the UUID format
        try:
            user_id = UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=422, detail="Invalid user_id format")
        
        # Check if user exists first - return 404 if not
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Convert role enums to UserRole
        try:
            user_old_role = UserRole[old_role.value]
            user_new_role = UserRole[new_role.value]
        except (ValueError, KeyError):
            raise HTTPException(status_code=422, detail="Invalid role value")
        
        # Send role upgrade email directly
        dashboard_url = f"{settings.server_base_url.rstrip('/')}/dashboard"
        data = {
            "name": user.nickname or user.first_name or "User",
            "old_role": user_old_role.value,
            "new_role": user_new_role.value,
            "email": user.email,
            "dashboard_url": dashboard_url
        }
        await email_service.send_user_email_async(data, 'role_upgrade')
        return {"status": "success", "message": f"Role upgrade email sent to user {user.email} (test direct)"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send role upgrade email: {str(e)}")
