from pydantic import BaseModel
from pydantic import BaseModel
from app.models.user_model import UserRole

class VerificationEmailRequest(BaseModel):
    user_id: str

class AccountLockedEmailRequest(BaseModel):
    user_id: str

class RoleUpgradeEmailRequest(BaseModel):
    user_id: str
    old_role: UserRole
