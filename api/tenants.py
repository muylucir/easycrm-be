from fastapi import APIRouter, Depends, HTTPException
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantInDB
from app.services.tenant_service import TenantService
from app.core.deps import get_current_active_admin
from typing import List

router = APIRouter()

@router.post("/", response_model=TenantInDB)
async def create_tenant(tenant: TenantCreate, current_admin: dict = Depends(get_current_active_admin), tenant_service: TenantService = Depends()):
    """
    새 테넌트 생성 (관리자 전용)
    """
    return await tenant_service.create_tenant(tenant)

@router.get("/{tenant_id}", response_model=TenantInDB)
async def get_tenant(tenant_id: str, current_admin: dict = Depends(get_current_active_admin), tenant_service: TenantService = Depends()):
    """
    테넌트 정보 조회 (관리자 전용)
    """
    tenant = await tenant_service.get_tenant(tenant_id)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.put("/{tenant_id}", response_model=TenantInDB)
async def update_tenant(tenant_id: str, tenant_update: TenantUpdate, current_admin: dict = Depends(get_current_active_admin), tenant_service: TenantService = Depends()):
    """
    테넌트 정보 업데이트 (관리자 전용)
    """
    tenant = await tenant_service.update_tenant(tenant_id, tenant_update)
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return tenant

@router.delete("/{tenant_id}")
async def delete_tenant(tenant_id: str, current_admin: dict = Depends(get_current_active_admin), tenant_service: TenantService = Depends()):
    """
    테넌트 삭제 (관리자 전용)
    """
    deleted = await tenant_service.delete_tenant(tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {"message": "Tenant successfully deleted"}

@router.get("/", response_model=List[TenantInDB])
async def list_tenants(current_admin: dict = Depends(get_current_active_admin), tenant_service: TenantService = Depends()):
    """
    모든 테넌트 목록 조회 (관리자 전용)
    """
    return await tenant_service.list_tenants()