from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.user import UserInDB
from app.services.user_service import UserService
from app.core.security import verify_cognito_token
from typing import Generator


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    try:
        claims = verify_cognito_token(token)
        user_id = claims['sub']
        tenant_id = claims.get('custom:tenant_id')
        is_active = claims.get('custom:is_active', 'true').lower() == 'true'
        role = claims.get('custom:role', 'user')
        
        if user_id is None or tenant_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        user = await UserService.get_user(user_id=user_id, tenant_id=tenant_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        # JWT 클레임의 정보로 사용자 정보 업데이트
        user.is_active = is_active
        user.role = role
        
        return user
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    현재 활성 상태인 사용자 정보 가져오기
    :param current_user: 현재 인증된 사용자
    :return: 활성 상태인 사용자 정보
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    현재 활성 상태인 관리자 정보 가져오기
    :param current_user: 현재 인증된 활성 사용자
    :return: 활성 상태인 관리자 정보
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

def get_tenant_id(current_user: UserInDB = Depends(get_current_active_user)) -> str:
    """
    현재 사용자의 테넌트 ID 가져오기
    :param current_user: 현재 인증된 활성 사용자
    :return: 테넌트 ID
    """
    return current_user.tenant_id