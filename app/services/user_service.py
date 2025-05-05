from builtins import Exception, bool, classmethod, int, str
from datetime import datetime, timezone
import secrets
import logging
from typing import Optional, Dict, List, Tuple, Any, Union
from uuid import UUID

from pydantic import ValidationError
from sqlalchemy import func, null, update, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_email_service, get_settings
from app.models.user_model import User, UserRole
from app.schemas.user_schemas import UserCreate, UserUpdate
from app.utils.nickname_gen import generate_nickname
from app.utils.security import generate_verification_token, hash_password, verify_password
from app.services.email_service import EmailService
from app.services.event_service import event_service

settings = get_settings()
logger = logging.getLogger(__name__)

class UserService:
    @classmethod
    async def _execute_query(cls, session: AsyncSession, query):
        try:
            result = await session.execute(query)
            await session.commit()
            return result
        except SQLAlchemyError as e:
            logger.error(f"Database error: {e}")
            await session.rollback()
            return None

    @classmethod
    async def _fetch_user(cls, session: AsyncSession, **filters) -> Optional[User]:
        query = select(User).filter_by(**filters)
        result = await cls._execute_query(session, query)
        return result.scalars().first() if result else None

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await cls._fetch_user(session, id=user_id)

    @classmethod
    async def get_by_nickname(cls, session: AsyncSession, nickname: str) -> Optional[User]:
        return await cls._fetch_user(session, nickname=nickname)

    @classmethod
    async def get_by_email(cls, session: AsyncSession, email: str) -> Optional[User]:
        return await cls._fetch_user(session, email=email)

    @classmethod
    async def create(cls, session: AsyncSession, user_data: Dict[str, str], email_service: EmailService) -> tuple[Optional[User], Optional[str]]:
        """Create a new user
        
        Returns:
            tuple: (User object or None, Error message or None)
        """
        try:
            # 1. Validate incoming user data
            validated_data = UserCreate(**user_data).model_dump()

            # 2. Check if user with same email exists
            existing_user = await cls.get_by_email(session, validated_data['email'])
            if existing_user:
                logger.error("User with given email already exists.")
                return None, "Email already exists"

            # 3. Hash password and prepare user
            validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
            new_user = User(**validated_data)
            new_user.email_verified = False

            # 4. Generate unique nickname
            new_nickname = generate_nickname()
            while await cls.get_by_nickname(session, new_nickname):
                new_nickname = generate_nickname()
            new_user.nickname = new_nickname

            # 5. Set user role
            user_count = await cls.count(session)
            new_user.role = UserRole.ADMIN if user_count == 0 else UserRole.ANONYMOUS

            # Generate verification token
            new_user.verification_token = generate_verification_token()

            # 7. Add and flush to populate user.id
            try:
                session.add(new_user)
                await session.flush()
                await session.refresh(new_user)  # Ensures token and ID are synced with DB
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Database error during user creation: {e}")
                return None, f"Database error: {str(e)}"

            # 8. Send verification email using event-driven approach
            # Try event-driven approach first
            event_published = event_service.publish_account_verification_event(new_user)
            
            # Fall back to direct email if event publishing fails
            if not event_published:
                try:
                    await email_service.send_verification_email(new_user)
                except Exception as email_error:
                    logger.error(f"Email verification error: {email_error}")
                    # Continue with registration even if email fails
                    # We'll just note the issue but still create the user

            # 9. Commit the transaction
            await session.commit()
            return new_user, None

        except ValidationError as e:
            logger.error(f"Validation error during user creation: {e}")
            return None, f"Validation error: {str(e)}"
        except Exception as e:
            logger.error(f"Unexpected error during user creation: {e}")
            await session.rollback()
            return None, f"Registration error: {str(e)}"

    @classmethod
    async def update(cls, session: AsyncSession, user_id: UUID, update_data: Dict[str, str]) -> Optional[User]:
        try:
            # First get the user to detect changes
            current_user = await cls.get_by_id(session, user_id)
            if not current_user:
                logger.error(f"User {user_id} not found for update.")
                return None
                
            # Save current role for comparison after update
            old_role = current_user.role
            old_is_professional = getattr(current_user, 'is_professional', False)
                
            # Validate update data
            validated_data = UserUpdate(**update_data).model_dump(exclude_unset=True)

            # Handle password updates
            if 'password' in validated_data:
                validated_data['hashed_password'] = hash_password(validated_data.pop('password'))
                
            # Perform the update
            query = update(User).where(User.id == user_id).values(**validated_data).execution_options(synchronize_session="fetch")
            await cls._execute_query(session, query)
            
            # Get updated user
            updated_user = await cls.get_by_id(session, user_id)
            if updated_user:
                await session.refresh(updated_user)  # Explicitly refresh the updated user object
                logger.info(f"User {user_id} updated successfully.")
                
                # Check for role changes and publish events if needed
                if 'role' in validated_data and old_role != updated_user.role:
                    logger.info(f"User {user_id} role changed from {old_role} to {updated_user.role}")
                    event_service.publish_role_change_event(updated_user, old_role)
                
                # Check for professional status changes
                new_is_professional = getattr(updated_user, 'is_professional', False)
                if 'is_professional' in validated_data and old_is_professional != new_is_professional and new_is_professional:
                    logger.info(f"User {user_id} upgraded to professional status")
                    event_service.publish_professional_status_event(updated_user)
                    
                return updated_user
            else:
                logger.error(f"User {user_id} not found after update attempt.")
                return None
        except Exception as e:  # Broad exception handling for debugging
            logger.error(f"Error during user update: {e}")
            return None

    @classmethod
    async def delete(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if not user:
            logger.info(f"User with ID {user_id} not found.")
            return False
        await session.delete(user)
        await session.commit()
        return True

    @classmethod
    async def list_users(cls, session: AsyncSession, skip: int = 0, limit: int = 10) -> List[User]:
        query = select(User).offset(skip).limit(limit)
        result = await cls._execute_query(session, query)
        return result.scalars().all() if result else []

    @classmethod
    async def register_user(cls, session: AsyncSession, user_data: Dict[str, str], get_email_service) -> tuple[Optional[User], Optional[str]]:
        """Register a new user
        
        Returns:
            tuple: (User object or None, Error message or None)
        """
        return await cls.create(session, user_data, get_email_service)
    

    @classmethod
    async def login_user(cls, session: AsyncSession, email: str, password: str) -> Optional[User]:
        user = await cls.get_by_email(session, email)
        if user:
            if user.email_verified is False:
                return None
            if user.is_locked:
                return None
            if verify_password(password, user.hashed_password):
                user.failed_login_attempts = 0
                user.last_login_at = datetime.now(timezone.utc)
                session.add(user)
                await session.commit()
                return user
            else:
                user.failed_login_attempts += 1
                was_just_locked = False
                
                if user.failed_login_attempts >= settings.max_login_attempts and not user.is_locked:
                    user.is_locked = True
                    was_just_locked = True
                    
                session.add(user)
                await session.commit()
                
                # Send account locked notification if the account was just locked
                if was_just_locked:
                    event_service.publish_account_locked_event(user)
                    
        return None

    @classmethod
    async def is_account_locked(cls, session: AsyncSession, email: str) -> bool:
        user = await cls.get_by_email(session, email)
        return user.is_locked if user else False


    @classmethod
    async def reset_password(cls, session: AsyncSession, user_id: UUID, new_password: str) -> bool:
        hashed_password = hash_password(new_password)
        user = await cls.get_by_id(session, user_id)
        if user:
            was_locked = user.is_locked
            
            user.hashed_password = hashed_password
            user.failed_login_attempts = 0  # Resetting failed login attempts
            user.is_locked = False  # Unlocking the user account, if locked
            
            session.add(user)
            await session.commit()
            
            # If the account was previously locked, send unlock notification
            if was_locked:
                event_service.publish_account_unlocked_event(user)
                
            return True
        return False

    @classmethod
    async def verify_email_with_token(cls, session: AsyncSession, user_id: UUID, token: str) -> bool:
        logger.info(f"Attempting email verification for user_id={user_id} with token={token}")

        try:
            user = await cls.get_by_id(session, user_id)
            if not user:
                logger.error(f"Verification failed: User {user_id} not found.")
                return False

            logger.info(
                f"User found: {user.email} (verified={user.email_verified}, "
                f"token_in_db={user.verification_token})"
            )

            if user.email_verified:
                logger.warning(f"Email already verified for user {user.email}")
                return True

            if not user.verification_token or user.verification_token != token:
                logger.error(
                    f"Verification failed: Token mismatch for user {user.email}. "
                    f"Expected={user.verification_token}, Provided={token}"
                )
                return False

            user.email_verified = True
            user.verification_token = None
            user.role = UserRole.AUTHENTICATED

            session.add(user)
            await session.commit()
            await session.refresh(user)

            logger.info(
                f"Email verified: user_id={user.id}, verified={user.email_verified}, role={user.role}"
            )
            return True

        except Exception as e:
            logger.error(f"Exception during email verification: {e}")
            await session.rollback()
            return False

    @classmethod
    async def count(cls, session: AsyncSession) -> int:
        """
        Count the number of users in the database.

        :param session: The AsyncSession instance for database access.
        :return: The count of users.
        """
        query = select(func.count()).select_from(User)
        result = await session.execute(query)
        count = result.scalar()
        return count
    
    @classmethod
    async def unlock_user_account(cls, session: AsyncSession, user_id: UUID) -> bool:
        user = await cls.get_by_id(session, user_id)
        if user and user.is_locked:
            user.is_locked = False
            user.failed_login_attempts = 0  # Optionally reset failed login attempts
            session.add(user)
            await session.commit()
            return True
        return False