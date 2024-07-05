# /crm_saas/app/schemas/onboarding.py
from pydantic import BaseModel
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate

class OnboardingRequest(BaseModel):
    tenant: TenantCreate
    admin: UserCreate