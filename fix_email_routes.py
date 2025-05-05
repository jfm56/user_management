#!/usr/bin/env python3
"""
This script fixes the email_routes.py file to use the correct role comparison.
"""
import os

# The corrected content for email_routes.py
EMAIL_ROUTES_CONTENT = '''"""
Router for email notification testing endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from uuid import UUID

from app.dependencies import get_db, get_email_service, get_current_user
from app.services.email_service import EmailService
from app.models.user_model import User, UserRole
from app.services.user_service import UserService
from app.services.event_service import event_service

router = APIRouter(
    prefix="/emails",
    tags=["Email Notifications"]
)

@router.post("/test/verification", status_code=202)
async def test_verification_email(
    request: Request,
    user_id: str, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    current_user_data: dict = Depends(get_current_user)
):
    """
    Test endpoint to send a verification email to a user.
    This is for testing purposes only.
    """
    # Check if the current user has admin privileges
    if current_user_data.get('role') != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can use this testing endpoint")
    
    # Get the user to send the verification email to
    try:
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Publish the verification event
        event_published = event_service.publish_account_verification_event(user)
        
        if event_published:
            return {"status": "success", "message": f"Verification email event published for user {user.email}"}
        else:
            # Fall back to direct email sending if event publishing fails
            background_tasks.add_task(email_service.send_verification_email, user)
            return {"status": "success", "message": f"Verification email scheduled for user {user.email} (direct send)"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@router.post("/test/account-locked", status_code=202)
async def test_account_locked_email(
    request: Request,
    user_id: str, 
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """
    Test endpoint to send an account locked email to a user.
    This is for testing purposes only.
    """
    # Check if the current user has admin privileges
    if current_user_data.get('role') != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can use this testing endpoint")
    
    # Get the user to send the account locked email to
    try:
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Publish the account locked event
        event_published = event_service.publish_account_locked_event(user)
        
        return {"status": "success", "message": f"Account locked email event published for user {user.email}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send account locked email: {str(e)}")

@router.post("/test/role-upgrade", status_code=202)
async def test_role_upgrade_email(
    request: Request,
    user_id: str,
    old_role: str,
    session: AsyncSession = Depends(get_db),
    current_user_data: dict = Depends(get_current_user)
):
    """
    Test endpoint to send a role upgrade email to a user.
    This is for testing purposes only.
    """
    # Check if the current user has admin privileges
    if current_user_data.get('role') != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Only administrators can use this testing endpoint")
    
    # Get the user to send the role upgrade email to
    try:
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Temporarily store the old role
        user_old_role = UserRole(old_role)
        
        # Publish the role upgrade event
        event_published = event_service.publish_role_change_event(user, user_old_role)
        
        return {"status": "success", "message": f"Role upgrade email event published for user {user.email}"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send role upgrade email: {str(e)}")
'''

# Write the corrected file to the user_management app
email_routes_path = '/Users/jimmullen/user_management/app/routers/email_routes.py'
with open(email_routes_path, 'w') as f:
    f.write(EMAIL_ROUTES_CONTENT)

print(f"Fixed email_routes.py with correct role check: current_user_data.get('role') != UserRole.ADMIN.value")
