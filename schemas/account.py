from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class AccountBase(BaseModel):
    """고객 계정의 기본 스키마"""
    name: str = Field(..., description="고객 계정의 이름")
    manager_id: str = Field(..., description="고객 계정 담당자의 사용자 ID")

class AccountCreate(AccountBase):
    """고객 계정 생성 시 사용되는 스키마"""
    tenant_id: str = Field(..., description="고객 계정이 속한 테넌트의 ID")

class AccountUpdate(BaseModel):
    """고객 계정 정보 업데이트 시 사용되는 스키마"""
    name: Optional[str] = Field(None, description="고객 계정의 이름")
    manager_id: Optional[str] = Field(None, description="고객 계정 담당자의 사용자 ID")
    is_active: Optional[bool] = Field(None, description="고객 계정의 활성 상태")

class AccountInDB(AccountBase):
    """데이터베이스에 저장된 고객 계정 정보를 표현하는 스키마"""
    account_id: str = Field(..., description="고객 계정의 고유 ID")
    tenant_id: str = Field(..., description="고객 계정이 속한 테넌트의 ID")
    created_at: datetime = Field(..., description="고객 계정 생성 시간")
    updated_at: datetime = Field(..., description="고객 계정 정보 최종 수정 시간")
    is_active: bool = Field(..., description="고객 계정의 활성 상태")

class AccountOut(AccountInDB):
    """API 응답으로 반환되는 고객 계정 정보 스키마"""
    pass

    class Config:
        orm_mode = True