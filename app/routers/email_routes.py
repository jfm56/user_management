"""
Router for email notification testing endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Request, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any, Optional
from uuid import UUID

from app.dependencies import get_db, get_email_service, get_current_user, get_settings
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
    background_tasks: BackgroundTasks,
    payload: Dict[str, Any] = Body(...),
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
        user_id = payload.get("user_id")
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
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send verification email: {str(e)}")

@router.post("/test/account-locked", status_code=202)
async def test_account_locked_email(
    request: Request,
    payload: Dict[str, Any] = Body(...),
    session: AsyncSession = Depends(get_db),
    email_service: EmailService = Depends(get_email_service),
    settings=Depends(get_settings),
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
        user_id = payload.get("user_id")
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Direct send for account locked test endpoint
        support_url = f"{settings.server_base_url.rstrip('/')}/support"
        data = {
            "name": user.nickname or user.first_name or "User",
            "support_url": support_url,
            "email": user.email
        }
        await email_service.send_user_email_async(data, 'account_locked')
        return {"status": "success", "message": f"Account locked email sent to user {user.email} (test direct)"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send account locked email: {str(e)}")

@router.post("/test/role-upgrade", status_code=202)
async def test_role_upgrade_email(
    request: Request,
    payload: Dict[str, Any] = Body(...),
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
        user_id = payload.get("user_id")
        user = await UserService.get_by_id(session, user_id)
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        # Temporarily store the old role
        user_old_role = UserRole(payload.get("old_role"))
        
        # Publish the role upgrade event
        event_published = event_service.publish_role_change_event(user, user_old_role)
        
        return {"status": "success", "message": f"Role upgrade email event published for user {user.email}"}
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to send role upgrade email: {str(e)}")
