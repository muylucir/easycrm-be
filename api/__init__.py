from fastapi import APIRouter

from .auth import router as auth_router
from .tenants import router as tenants_router
from .users import router as users_router
from .accounts import router as accounts_router
from .opportunities import router as opportunities_router
from .analytics import router as analytics_router

# 메인 API 라우터 생성
api_router = APIRouter()

# 각 리소스의 라우터를 메인 라우터에 포함
api_router.include_router(auth_router, prefix="/auth", tags=["authentication"])
api_router.include_router(tenants_router, prefix="/tenants", tags=["tenants"])
api_router.include_router(users_router, prefix="/users", tags=["users"])
api_router.include_router(accounts_router, prefix="/accounts", tags=["accounts"])
api_router.include_router(opportunities_router, prefix="/opportunities", tags=["opportunities"])
api_router.include_router(analytics_router, prefix="/analytics", tags=["analytics"])