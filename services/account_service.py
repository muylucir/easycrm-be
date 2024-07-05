from app.models.account import AccountModel
from app.schemas.account import AccountCreate, AccountUpdate, AccountInDB
from fastapi import HTTPException
from typing import List
import uuid

class AccountService:
    @staticmethod
    async def create_account(account: AccountCreate) -> AccountInDB:
        """
        새 계정 생성
        :param account: 생성할 계정 정보
        :return: 생성된 계정 정보
        """
        account_id = str(uuid.uuid4())
        db_account = AccountModel(
            account_id=account_id,
            tenant_id=account.tenant_id,
            name=account.name,
            manager_id=account.manager_id
        )
        try:
            db_account.save()
            return AccountInDB(
                account_id=db_account.account_id,
                tenant_id=db_account.tenant_id,
                name=db_account.name,
                manager_id=db_account.manager_id,
                created_at=db_account.created_at,
                updated_at=db_account.updated_at,
                is_active=db_account.is_active
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create account: {str(e)}")

    @staticmethod
    async def get_account(account_id: str, tenant_id: str) -> AccountInDB:
        """
        계정 ID와 테넌트 ID로 계정 조회
        :param account_id: 계정 ID
        :param tenant_id: 테넌트 ID
        :return: 조회된 계정 정보
        """
        try:
            account = AccountModel.get(account_id, tenant_id)
            return AccountInDB(
                account_id=account.account_id,
                tenant_id=account.tenant_id,
                name=account.name,
                manager_id=account.manager_id,
                created_at=account.created_at,
                updated_at=account.updated_at,
                is_active=account.is_active
            )
        except AccountModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Account not found")

    @staticmethod
    async def update_account(account_id: str, tenant_id: str, account_update: AccountUpdate) -> AccountInDB:
        """
        계정 정보 업데이트
        :param account_id: 업데이트할 계정 ID
        :param tenant_id: 테넌트 ID
        :param account_update: 업데이트할 계정 정보
        :return: 업데이트된 계정 정보
        """
        try:
            account = AccountModel.get(account_id, tenant_id)
            update_data = account_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(account, key, value)
            account.save()
            return AccountInDB(
                account_id=account.account_id,
                tenant_id=account.tenant_id,
                name=account.name,
                manager_id=account.manager_id,
                created_at=account.created_at,
                updated_at=account.updated_at,
                is_active=account.is_active
            )
        except AccountModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Account not found")

    @staticmethod
    async def delete_account(account_id: str, tenant_id: str) -> bool:
        """
        계정 삭제 (소프트 삭제)
        :param account_id: 삭제할 계정 ID
        :param tenant_id: 테넌트 ID
        :return: 삭제 성공 여부
        """
        try:
            account = AccountModel.get(account_id, tenant_id)
            account.is_active = False
            account.save()
            return True
        except AccountModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Account not found")

    @staticmethod
    async def list_accounts(tenant_id: str) -> List[AccountInDB]:
        """
        테넌트의 모든 활성 계정 목록 조회
        :param tenant_id: 테넌트 ID
        :return: 계정 목록
        """
        accounts = AccountModel.query(tenant_id, AccountModel.is_active == True)
        return [
            AccountInDB(
                account_id=account.account_id,
                tenant_id=account.tenant_id,
                name=account.name,
                manager_id=account.manager_id,
                created_at=account.created_at,
                updated_at=account.updated_at,
                is_active=account.is_active
            )
            for account in accounts
        ]

    @staticmethod
    async def change_account_manager(account_id: str, tenant_id: str, new_manager_id: str) -> AccountInDB:
        """
        계정 담당자 변경
        :param account_id: 계정 ID
        :param tenant_id: 테넌트 ID
        :param new_manager_id: 새로운 담당자 ID
        :return: 업데이트된 계정 정보
        """
        try:
            account = AccountModel.get(account_id, tenant_id)
            account.manager_id = new_manager_id
            account.save()
            return AccountInDB(
                account_id=account.account_id,
                tenant_id=account.tenant_id,
                name=account.name,
                manager_id=account.manager_id,
                created_at=account.created_at,
                updated_at=account.updated_at,
                is_active=account.is_active
            )
        except AccountModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Account not found")