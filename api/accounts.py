from fastapi import APIRouter, Depends, HTTPException
from app.schemas.account import AccountCreate, AccountUpdate, AccountInDB
from app.services.account_service import AccountService
from app.core.deps import get_current_active_user, get_tenant_id
from typing import List

router = APIRouter()

@router.post("/", response_model=AccountInDB)
async def create_account(
    account: AccountCreate,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    새 계정 생성
    """
    account.tenant_id = tenant_id
    return await account_service.create_account(account)

@router.get("/{account_id}", response_model=AccountInDB)
async def get_account(
    account_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    특정 계정 정보 조회
    """
    account = await account_service.get_account(account_id, tenant_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.put("/{account_id}", response_model=AccountInDB)
async def update_account(
    account_id: str,
    account_update: AccountUpdate,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    계정 정보 업데이트
    """
    account = await account_service.update_account(account_id, tenant_id, account_update)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account

@router.delete("/{account_id}")
async def delete_account(
    account_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    계정 삭제
    """
    deleted = await account_service.delete_account(account_id, tenant_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Account not found")
    return {"message": "Account successfully deleted"}

@router.get("/", response_model=List[AccountInDB])
async def list_accounts(
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    테넌트의 모든 계정 목록 조회
    """
    return await account_service.list_accounts(tenant_id)

@router.put("/{account_id}/change-manager", response_model=AccountInDB)
async def change_account_manager(
    account_id: str,
    new_manager_id: str,
    current_user: dict = Depends(get_current_active_user),
    tenant_id: str = Depends(get_tenant_id),
    account_service: AccountService = Depends()
):
    """
    계정 담당자 변경
    """
    account = await account_service.change_account_manager(account_id, tenant_id, new_manager_id)
    if not account:
        raise HTTPException(status_code=404, detail="Account not found")
    return account