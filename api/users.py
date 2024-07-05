from fastapi import APIRouter, Depends, HTTPException
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from app.services.user_service import UserService
from app.core.deps import get_current_active_user, get_current_active_admin
from typing import List

router = APIRouter()

@router.post("/", response_model=UserInDB)
async def create_user(user: UserCreate, current_admin: dict = Depends(get_current_active_admin), user_service: UserService = Depends()):
    """
    새 사용자 생성 (관리자 전용)
    """
    return await user_service.create_user(user)

@router.get("/me", response_model=UserInDB)
async def get_current_user(current_user: UserInDB = Depends(get_current_active_user)):
    """
    현재 로그인한 사용자 정보 조회
    """
    return current_user

@router.put("/me", response_model=UserInDB)
async def update_current_user(user_update: UserUpdate, current_user: UserInDB = Depends(get_current_active_user), user_service: UserService = Depends()):
    """
    현재 로그인한 사용자 정보 업데이트
    """
    return await user_service.update_user(current_user.user_id, current_user.tenant_id, user_update)

@router.get("/{user_id}", response_model=UserInDB)
async def get_user(user_id: str, current_admin: dict = Depends(get_current_active_admin), user_service: UserService = Depends()):
    """
    특정 사용자 정보 조회 (관리자 전용)
    """
    user = await user_service.get_user(user_id, current_admin.tenant_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.put("/{user_id}", response_model=UserInDB)
async def update_user(user_id: str, user_update: UserUpdate, current_admin: dict = Depends(get_current_active_admin), user_service: UserService = Depends()):
    """
    특정 사용자 정보 업데이트 (관리자 전용)
    """
    user = await user_service.update_user(user_id, current_admin.tenant_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.delete("/{user_id}")
async def delete_user(user_id: str, current_admin: dict = Depends(get_current_active_admin), user_service: UserService = Depends()):
    """
    사용자 삭제 (관리자 전용)
    """
    deleted = await user_service.delete_user(user_id, current_admin.tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User successfully deleted"}

@router.get("/", response_model=List[UserInDB])
async def list_users(current_admin: dict = Depends(get_current_active_admin), user_service: UserService = Depends()):
    """
    테넌트의 모든 사용자 목록 조회 (관리자 전용)
    """
    return await user_service.list_users(current_admin.tenant_id)