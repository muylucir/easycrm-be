from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import ValidationError
from app.core.config import settings
from app.schemas.user import UserInDB
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from typing import Optional

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> UserInDB:
    """
    현재 인증된 사용자를 가져오는 의존성 함수
    :param token: JWT 토큰
    :return: 인증된 사용자 정보
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        tenant_id: str = payload.get("tenant_id")
        if user_id is None or tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await UserService.get_user(user_id=user_id, tenant_id=tenant_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

async def get_current_active_user(current_user: UserInDB = Depends(get_current_user)) -> UserInDB:
    """
    현재 활성 상태인 사용자를 가져오는 의존성 함수
    :param current_user: 현재 인증된 사용자
    :return: 활성 상태인 사용자 정보
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_active_admin(current_user: UserInDB = Depends(get_current_active_user)) -> UserInDB:
    """
    현재 활성 상태인 관리자를 가져오는 의존성 함수
    :param current_user: 현재 인증된 활성 사용자
    :return: 활성 상태인 관리자 정보
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user

async def get_auth_service() -> AuthService:
    """
    AuthService 인스턴스를 가져오는 의존성 함수
    :return: AuthService 인스턴스
    """
    return AuthService()

async def get_user_service() -> UserService:
    """
    UserService 인스턴스를 가져오는 의존성 함수
    :return: UserService 인스턴스
    """
    return UserService()

async def get_tenant_id(token: str = Depends(oauth2_scheme)) -> str:
    """
    JWT 토큰에서 tenant_id를 추출하는 의존성 함수
    :param token: JWT 토큰
    :return: tenant_id
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        tenant_id: str = payload.get("tenant_id")
        if tenant_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return tenant_id
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
