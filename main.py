from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import auth, tenants, users, accounts, opportunities, onboarding
from app.core.config import settings

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Multi-tenant CRM SaaS application",
    version="1.0.0",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# CORS 미들웨어 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API 라우터 포함
app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(accounts.router, prefix="/api/v1/accounts", tags=["accounts"])
app.include_router(opportunities.router, prefix="/api/v1/opportunities", tags=["opportunities"])
app.include_router(tenants.router, prefix="/api/v1/tenants", tags=["tenants"])
app.include_router(onboarding.router, prefix="/api/v1/onboarding", tags=["onboarding"])

@app.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {"message": "Welcome to the Multi-tenant CRM SaaS API"}

@app.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)