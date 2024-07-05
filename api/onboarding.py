# /crm_saas/app/api/onboarding.py
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate
from app.schemas.onboarding import OnboardingRequest
from app.services.onboarding_service import OnboardingService
from app.core.deps import get_current_active_admin

router = APIRouter()

@router.post("/onboard")
async def onboard_tenant_and_admin(
    onboarding_request: OnboardingRequest,
    onboarding_service: OnboardingService = Depends()
):
    return await onboarding_service.create_tenant_and_admin(onboarding_request)


@router.post("/user")
async def create_user(
    user: UserCreate,
    onboarding_service: OnboardingService = Depends(),
    current_admin: dict = Depends(get_current_active_admin)
):
    return await onboarding_service.create_user(user)