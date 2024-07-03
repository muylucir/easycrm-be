from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TenantBase(BaseModel):
    """테넌트의 기본 스키마"""
    name: str = Field(..., description="테넌트의 이름")

class TenantCreate(TenantBase):
    """테넌트 생성 시 사용되는 스키마"""
    pass

class TenantUpdate(BaseModel):
    """테넌트 업데이트 시 사용되는 스키마"""
    name: Optional[str] = Field(None, description="테넌트의 이름")
    is_active: Optional[bool] = Field(None, description="테넌트의 활성 상태")

class TenantInDB(TenantBase):
    """데이터베이스에 저장된 테넌트 정보를 표현하는 스키마"""
    tenant_id: str = Field(..., description="테넌트의 고유 ID")
    created_at: datetime = Field(..., description="테넌트 생성 시간")
    updated_at: datetime = Field(..., description="테넌트 정보 최종 수정 시간")
    is_active: bool = Field(..., description="테넌트의 활성 상태")

class TenantOut(TenantInDB):
    """API 응답으로 반환되는 테넌트 정보 스키마"""
    pass

    class Config:
        orm_mode = True