from app.models.user import UserModel
from app.schemas.user import UserCreate, UserUpdate, UserInDB
from fastapi import HTTPException
from typing import List
import uuid

class UserService:
    @staticmethod
    async def create_user(user: UserCreate) -> UserInDB:
        """
        새 사용자 생성
        :param user: 생성할 사용자 정보
        :return: 생성된 사용자 정보
        """
        db_user = UserModel(
            user_id=user.user_id,
            tenant_id=user.tenant_id,
            email=user.email,
            given_name=user.given_name,  # 'name'을 'given_name'으로 변경
            family_name=user.family_name,  # 'family_name' 추가
            role=user.role
        )
        try:
            db_user.save()
            return UserInDB(
                user_id=db_user.user_id,
                tenant_id=db_user.tenant_id,
                email=db_user.email,
                given_name=db_user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=db_user.family_name,  # 'family_name' 추가
                role=db_user.role,
                created_at=db_user.created_at,
                updated_at=db_user.updated_at,
                is_active=db_user.is_active,
                managed_account_ids=db_user.managed_account_ids
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create user: {str(e)}")

    @staticmethod
    async def get_user(user_id: str, tenant_id: str) -> UserInDB:
        """
        사용자 ID와 테넌트 ID로 사용자 조회
        :param user_id: 사용자 ID
        :param tenant_id: 테넌트 ID
        :return: 조회된 사용자 정보
        """
        try:
            user = UserModel.get(user_id, tenant_id)
            return UserInDB(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                given_name=user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=user.family_name,  # 'family_name' 추가
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                managed_account_ids=user.managed_account_ids
            )
        except UserModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def update_user(user_id: str, tenant_id: str, user_update: UserUpdate) -> UserInDB:
        """
        사용자 정보 업데이트
        :param user_id: 업데이트할 사용자 ID
        :param tenant_id: 테넌트 ID
        :param user_update: 업데이트할 사용자 정보
        :return: 업데이트된 사용자 정보
        """
        try:
            user = UserModel.get(user_id, tenant_id)
            update_data = user_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(user, key, value)
            user.save()
            return UserInDB(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                given_name=user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=user.family_name,  # 'family_name' 추가
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                managed_account_ids=user.managed_account_ids
            )
        except UserModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def delete_user(user_id: str, tenant_id: str) -> bool:
        """
        사용자 삭제 (소프트 삭제)
        :param user_id: 삭제할 사용자 ID
        :param tenant_id: 테넌트 ID
        :return: 삭제 성공 여부
        """
        try:
            user = UserModel.get(user_id, tenant_id)
            user.is_active = False
            user.save()
            return True
        except UserModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def list_users(tenant_id: str) -> List[UserInDB]:
        """
        테넌트의 모든 활성 사용자 목록 조회
        :param tenant_id: 테넌트 ID
        :return: 사용자 목록
        """
        users = UserModel.query(tenant_id, UserModel.is_active == True)
        return [
            UserInDB(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                given_name=user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=user.family_name,  # 'family_name' 추가
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                managed_account_ids=user.managed_account_ids
            )
            for user in users
        ]

    @staticmethod
    async def add_managed_account(user_id: str, tenant_id: str, account_id: str) -> UserInDB:
        """
        사용자에게 관리할 계정 추가
        :param user_id: 사용자 ID
        :param tenant_id: 테넌트 ID
        :param account_id: 추가할 계정 ID
        :return: 업데이트된 사용자 정보
        """
        try:
            user = UserModel.get(user_id, tenant_id)
            if account_id not in user.managed_account_ids:
                user.managed_account_ids.append(account_id)
                user.save()
            return UserInDB(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                given_name=user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=user.family_name,  # 'family_name' 추가
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                managed_account_ids=user.managed_account_ids
            )
        except UserModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")

    @staticmethod
    async def remove_managed_account(user_id: str, tenant_id: str, account_id: str) -> UserInDB:
        """
        사용자로부터 관리 계정 제거
        :param user_id: 사용자 ID
        :param tenant_id: 테넌트 ID
        :param account_id: 제거할 계정 ID
        :return: 업데이트된 사용자 정보
        """
        try:
            user = UserModel.get(user_id, tenant_id)
            if account_id in user.managed_account_ids:
                user.managed_account_ids.remove(account_id)
                user.save()
            return UserInDB(
                user_id=user.user_id,
                tenant_id=user.tenant_id,
                email=user.email,
                given_name=user.given_name,  # 'name'을 'given_name'으로 변경
                family_name=user.family_name,  # 'family_name' 추가
                role=user.role,
                created_at=user.created_at,
                updated_at=user.updated_at,
                is_active=user.is_active,
                managed_account_ids=user.managed_account_ids
            )
        except UserModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="User not found")