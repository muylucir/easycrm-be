from fastapi import APIRouter, Depends, HTTPException
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityInDB
from app.services.opportunity_service import OpportunityService
from app.core.deps import get_current_active_user, get_tenant_id
from typing import List

router = APIRouter()

@router.post("/", response_model=OpportunityInDB)
async def create_opportunity(
    opportunity: OpportunityCreate,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    새 영업 기회 생성
    """
    opportunity.tenant_id = tenant_id
    return await opportunity_service.create_opportunity(opportunity)

@router.get("/{opportunity_id}", response_model=OpportunityInDB)
async def get_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    특정 영업 기회 정보 조회
    """
    opportunity = await opportunity_service.get_opportunity(opportunity_id, tenant_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.put("/{opportunity_id}", response_model=OpportunityInDB)
async def update_opportunity(
    opportunity_id: str,
    opportunity_update: OpportunityUpdate,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    영업 기회 정보 업데이트
    """
    opportunity = await opportunity_service.update_opportunity(opportunity_id, tenant_id, opportunity_update)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.delete("/{opportunity_id}")
async def delete_opportunity(
    opportunity_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    영업 기회 삭제
    """
    deleted = await opportunity_service.delete_opportunity(opportunity_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return {"message": "Opportunity successfully deleted"}

@router.get("/", response_model=List[OpportunityInDB])
async def list_opportunities(
    account_id: str = None,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    테넌트의 모든 영업 기회 목록 조회 (선택적으로 특정 계정의 영업 기회만 조회)
    """
    return await opportunity_service.list_opportunities(tenant_id, account_id)

@router.put("/{opportunity_id}/change-manager", response_model=OpportunityInDB)
async def change_opportunity_manager(
    opportunity_id: str,
    new_manager_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    영업 기회 담당자 변경
    """
    opportunity = await opportunity_service.change_opportunity_manager(opportunity_id, tenant_id, new_manager_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    return opportunity

@router.get("/total-expected-revenue", response_model=float)
async def get_total_expected_revenue(
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    opportunity_service: OpportunityService = Depends()
):
    """
    테넌트의 총 기대 매출 조회
    """
    return await opportunity_service.calculate_total_expected_revenue(tenant_id)