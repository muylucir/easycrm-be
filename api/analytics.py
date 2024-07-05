from fastapi import APIRouter, Depends
from app.services.analytics_service import AnalyticsService
from app.core.deps import get_current_active_user, get_tenant_id
from typing import Dict, List

router = APIRouter()

@router.get("/tenant-summary", response_model=Dict)
async def get_tenant_summary(
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    analytics_service: AnalyticsService = Depends()
):
    """
    테넌트의 요약 정보 조회
    """
    return await analytics_service.get_tenant_summary(tenant_id)

@router.get("/opportunity-stage-distribution", response_model=Dict[str, int])
async def get_opportunity_stage_distribution(
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    analytics_service: AnalyticsService = Depends()
):
    """
    테넌트의 영업 기회 단계별 분포 조회
    """
    return await analytics_service.get_opportunity_stage_distribution(tenant_id)

@router.get("/top-accounts-by-revenue", response_model=List[Dict])
async def get_top_accounts_by_revenue(
    limit: int = 5,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    analytics_service: AnalyticsService = Depends()
):
    """
    기대 매출 기준 상위 계정 조회
    """
    return await analytics_service.get_top_accounts_by_revenue(tenant_id, limit)

@router.get("/sales-pipeline", response_model=List[Dict])
async def get_sales_pipeline(
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    analytics_service: AnalyticsService = Depends()
):
    """
    테넌트의 영업 파이프라인 조회
    """
    return await analytics_service.get_sales_pipeline(tenant_id)