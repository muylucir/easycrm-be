from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class OpportunityStage(str, Enum):
    """영업 기회의 단계를 나타내는 열거형"""
    PROSPECTING = "Prospecting"
    QUALIFICATION = "Qualification"
    COMMITTED = "Committed"
    CLOSED_LOST = "Closed Lost"
    CLOSED_WON = "Closed Won"

class OpportunityBase(BaseModel):
    """영업 기회의 기본 스키마"""
    name: str = Field(..., description="영업 기회의 이름")
    account_id: str = Field(..., description="영업 기회가 연관된 고객 계정의 ID")
    stage: OpportunityStage = Field(..., description="영업 기회의 현재 단계")
    expected_revenue: float = Field(..., description="예상 매출")
    manager_id: str = Field(..., description="영업 기회 담당자의 사용자 ID")

class OpportunityCreate(OpportunityBase):
    """영업 기회 생성 시 사용되는 스키마"""
    tenant_id: str = Field(..., description="영업 기회가 속한 테넌트의 ID")

class OpportunityUpdate(BaseModel):
    """영업 기회 정보 업데이트 시 사용되는 스키마"""
    name: Optional[str] = Field(None, description="영업 기회의 이름")
    stage: Optional[OpportunityStage] = Field(None, description="영업 기회의 현재 단계")
    expected_revenue: Optional[float] = Field(None, description="예상 매출")
    manager_id: Optional[str] = Field(None, description="영업 기회 담당자의 사용자 ID")
    is_active: Optional[bool] = Field(None, description="영업 기회의 활성 상태")

class OpportunityInDB(OpportunityBase):
    """데이터베이스에 저장된 영업 기회 정보를 표현하는 스키마"""
    opportunity_id: str = Field(..., description="영업 기회의 고유 ID")
    tenant_id: str = Field(..., description="영업 기회가 속한 테넌트의 ID")
    created_at: datetime = Field(..., description="영업 기회 생성 시간")
    updated_at: datetime = Field(..., description="영업 기회 정보 최종 수정 시간")
    is_active: bool = Field(..., description="영업 기회의 활성 상태")

class OpportunityOut(OpportunityInDB):
    """API 응답으로 반환되는 영업 기회 정보 스키마"""
    pass

    class Config:
        orm_mode = True