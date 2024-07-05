from app.models.tenant import TenantModel
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantInDB
from fastapi import HTTPException
from typing import List
import uuid

class TenantService:
    @staticmethod
    async def create_tenant(tenant: TenantCreate) -> TenantInDB:
        """
        새 테넌트 생성
        """
        tenant_id = str(uuid.uuid4())
        db_tenant = TenantModel(
            tenant_id=tenant_id,
            name=tenant.name
        )
        try:
            db_tenant.save()
            return TenantInDB(
                tenant_id=db_tenant.tenant_id,
                name=db_tenant.name,
                created_at=db_tenant.created_at,
                updated_at=db_tenant.updated_at,
                is_active=db_tenant.is_active
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create tenant: {str(e)}")

    @staticmethod
    async def get_tenant(tenant_id: str) -> TenantInDB:
        """
        테넌트 ID로 테넌트 조회
        """
        try:
            tenant = TenantModel.get(tenant_id)
            return TenantInDB(
                tenant_id=tenant.tenant_id,
                name=tenant.name,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                is_active=tenant.is_active
            )
        except TenantModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Tenant not found")

    @staticmethod
    async def update_tenant(tenant_id: str, tenant_update: TenantUpdate) -> TenantInDB:
        """
        테넌트 정보 업데이트
        """
        try:
            tenant = TenantModel.get(tenant_id)
            update_data = tenant_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(tenant, key, value)
            tenant.save()
            return TenantInDB(
                tenant_id=tenant.tenant_id,
                name=tenant.name,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                is_active=tenant.is_active
            )
        except TenantModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Tenant not found")

    @staticmethod
    async def delete_tenant(tenant_id: str) -> bool:
        """
        테넌트 삭제 (소프트 삭제)
        """
        try:
            tenant = TenantModel.get(tenant_id)
            tenant.is_active = False
            tenant.save()
            return True
        except TenantModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Tenant not found")

    @staticmethod
    async def list_tenants() -> List[TenantInDB]:
        """
        모든 활성 테넌트 목록 조회
        """
        tenants = TenantModel.scan(TenantModel.is_active == True)
        return [
            TenantInDB(
                tenant_id=tenant.tenant_id,
                name=tenant.name,
                created_at=tenant.created_at,
                updated_at=tenant.updated_at,
                is_active=tenant.is_active
            )
            for tenant in tenants
        ]