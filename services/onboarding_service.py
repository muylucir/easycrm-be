# /crm_saas/app/services/onboarding_service.py
import uuid
from app.models.tenant import TenantModel
from app.models.user import UserModel
from app.schemas.tenant import TenantCreate
from app.schemas.user import UserCreate
from app.schemas.onboarding import OnboardingRequest
from app.services.auth_service import AuthService
from fastapi import HTTPException

class OnboardingService:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service
        self.cognito_client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)

    async def create_tenant_and_admin(self, onboarding_request: OnboardingRequest):
        tenant = onboarding_request.tenant
        admin = onboarding_request.admin

        # 테넌트 생성
        tenant_id = str(uuid.uuid4())
        try:
            new_tenant = TenantModel(
                tenant_id=tenant_id,
                tenant_name=tenant.tenant_name
            )
            new_tenant.save()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create tenant: {str(e)}")

        # Cognito 그룹 생성
        try:
            self.cognito_client.create_group(
                GroupName=tenant.tenant_name,
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Description=f"Group for tenant {tenant.tenant_name}"
            )
        except ClientError as e:
            # 테넌트 생성 롤백
            new_tenant.delete()
            raise HTTPException(status_code=400, detail=f"Could not create Cognito group: {str(e)}")

        # 테넌트 관리자 생성
        admin.tenant_name = tenant.tenant_name
        admin.role = "admin"
        try:
            admin_user = await self.auth_service.register_user(admin)
        except Exception as e:
            # 테넌트 및 Cognito 그룹 생성 롤백
            new_tenant.delete()
            self.cognito_client.delete_group(
                GroupName=tenant.tenant_name,
                UserPoolId=settings.COGNITO_USER_POOL_ID
            )
            raise HTTPException(status_code=400, detail=f"Could not create admin user: {str(e)}")

        # 관리자를 Cognito 그룹에 추가
        try:
            self.cognito_client.admin_add_user_to_group(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=admin_user.email,
                GroupName=tenant.tenant_name
            )
        except ClientError as e:
            # 에러 발생 시 롤백은 하지 않고 로그만 남김 (관리자는 이미 생성됨)
            print(f"Warning: Could not add admin to Cognito group: {str(e)}")

        return {"tenant": new_tenant, "admin": admin_user}


    @staticmethod
    async def create_user(user: UserCreate):
        # 테넌트 존재 확인
        try:
            TenantModel.get(tenant_name=user.tenant_name)
        except TenantModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Tenant not found")

        # 유저 생성
        new_user = await AuthService.register_user(user)

        # 사용자를 Cognito 그룹에 추가
        try:
            cognito_client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
            cognito_client.admin_add_user_to_group(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=new_user.email,
                GroupName=user.tenant_name
            )
        except ClientError as e:
            print(f"Warning: Could not add user to Cognito group: {str(e)}")

        return new_user