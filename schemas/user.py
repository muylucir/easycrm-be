from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Optional, List

class UserBase(BaseModel):
    """사용자의 기본 스키마"""
    email: EmailStr = Field(..., description="사용자의 이메일 주소")
    #password: str = Field(..., description="사용자의 비밀번호")
    password: Optional[str] = None
    role: str = Field(..., description="사용자의 역할 (admin 또는 user)")

class UserCreate(UserBase):
    """사용자 생성 시 사용되는 스키마"""
    tenant_name: str = Field(..., description="사용자가 속한 테넌트의 ID")
    given_name: str  # 'name'을 'given_name'으로 변경
    family_name: str
    user_id: Optional[str] = None

class UserUpdate(BaseModel):
    """사용자 정보 업데이트 시 사용되는 스키마"""
    email: Optional[EmailStr] = Field(None, description="사용자의 이메일 주소")
    givenname: str = Field(..., description="사용자의 이름")
    familyname: str = Field(..., description="사용자의 성")
    role: Optional[str] = Field(None, description="사용자의 역할 (admin 또는 user)")
    is_active: Optional[bool] = Field(None, description="사용자의 활성 상태")

class UserInDB(UserBase):
    """데이터베이스에 저장된 사용자 정보를 표현하는 스키마"""
    user_id: str = Field(..., description="사용자의 고유 ID")
    tenant_name: str = Field(..., description="사용자가 속한 테넌트의 ID")
    created_at: datetime = Field(..., description="사용자 계정 생성 시간")
    updated_at: datetime = Field(..., description="사용자 정보 최종 수정 시간")
    is_active: bool = Field(..., description="사용자의 활성 상태")
    managed_account_ids: List[str] = Field(..., description="사용자가 관리하는 계정 ID 목록")

class UserOut(UserInDB):
    """API 응답으로 반환되는 사용자 정보 스키마"""
    pass

    class Config:
        orm_mode = True