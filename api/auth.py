from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.schemas.user import UserCreate, UserInDB
from app.services.auth_service import AuthService
from app.core.deps import get_current_active_user

router = APIRouter()

@router.post("/register", response_model=UserInDB)
async def register_user(user: UserCreate, auth_service: AuthService = Depends()):
    """
    새 사용자 등록
    """
    return await auth_service.register_user(user)

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), auth_service: AuthService = Depends()):
    """
    사용자 로그인 및 토큰 발급
    """
    user = await auth_service.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    return {"access_token": user["access_token"], "token_type": "bearer"}

@router.post("/logout")
async def logout(current_user: UserInDB = Depends(get_current_active_user), auth_service: AuthService = Depends()):
    # 여기서 로그아웃 로직을 구현합니다
    await auth_service.logout_user(current_user.user_id)
    return {"message": "Successfully logged out"}

@router.post("/change-password")
async def change_password(old_password: str, new_password: str, current_user: UserInDB = Depends(get_current_active_user), auth_service: AuthService = Depends()):
    """
    사용자 비밀번호 변경
    """
    return await auth_service.change_password(current_user.user_id, old_password, new_password)

@router.post("/forgot-password")
async def forgot_password(email: str, auth_service: AuthService = Depends()):
    """
    비밀번호 재설정 요청
    """
    return await auth_service.forgot_password(email)

@router.post("/reset-password")
async def reset_password(email: str, reset_code: str, new_password: str, auth_service: AuthService = Depends()):
    """
    비밀번호 재설정
    """
    return await auth_service.confirm_forgot_password(email, reset_code, new_password)