import boto3
import traceback
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.security import verify_cognito_token
from app.schemas.user import UserCreate, UserInDB
from app.models.user import UserModel
from fastapi import HTTPException
from typing import Dict, Any

class AuthService:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AuthService, cls).__new__(cls)
            cls._instance.cognito_client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        return cls._instance

    async def register_user(self, user: UserCreate) -> UserInDB:
        """
        새 사용자를 등록하고 Cognito 및 DynamoDB에 저장합니다.
        """
        try:
            # Cognito에 사용자 등록
            cognito_response = self.cognito_client.sign_up(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                Username=user.email,
                Password=user.password,
                UserAttributes=[
                    {'Name': 'email', 'Value': user.email},
                    {'Name': 'given_name', 'Value': user.given_name},
                    {'Name': 'family_name', 'Value': user.family_name},
                    {'Name': 'custom:tenant_name', 'Value': user.tenant_name},
                    {'Name': 'custom:role', 'Value': user.role},
                ]
            )
            
            cognito_user_id = cognito_response['UserSub']
            
            db_user = UserModel(
                user_id=cognito_user_id,
                tenant_name=user.tenant_name,
                email=user.email,
                given_name=user.given_name,
                family_name=user.family_name,
                role=user.role
            )
            db_user.save()

           # Cognito 사용자 확인 (이메일 인증 건너뛰기)
            self.cognito_client.admin_confirm_sign_up(
                UserPoolId=settings.COGNITO_USER_POOL_ID,
                Username=user.email
            )

            return UserInDB(**db_user.attribute_values)
        except Exception as e:
            error_details = traceback.format_exc()
            raise HTTPException(status_code=400, detail=f"Error in register_user: {str(e)}\n{error_details}")

    async def authenticate_user(self, username: str, password: str) -> Dict[str, Any]:
        try:
            auth_response = self.cognito_client.initiate_auth(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            auth_result = auth_response['AuthenticationResult']
            
            # Cognito 토큰 검증
            claims = verify_cognito_token(auth_result['IdToken'])
            
            return {
                "access_token": auth_result['AccessToken'],
                "id_token": auth_result['IdToken'],
                "refresh_token": auth_result['RefreshToken'],
                "token_type": "bearer",
                "expires_in": auth_result['ExpiresIn'],
                "user_id": claims['sub'],
                "tenant_name": claims.get('custom:tenant_name')
            }
        except self.cognito_client.exceptions.NotAuthorizedException:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def change_password(self, access_token: str, old_password: str, new_password: str) -> bool:
        """
        사용자 비밀번호 변경
        """
        try:
            self.cognito_client.change_password(
                PreviousPassword=old_password,
                ProposedPassword=new_password,
                AccessToken=access_token
            )
            return True
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def forgot_password(self, email: str) -> bool:
        """
        비밀번호 재설정 코드 요청
        """
        try:
            self.cognito_client.forgot_password(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                Username=email
            )
            return True
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def confirm_forgot_password(self, email: str, confirmation_code: str, new_password: str) -> bool:
        """
        비밀번호 재설정 확인
        """
        try:
            self.cognito_client.confirm_forgot_password(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password
            )
            return True
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def logout_user(self, access_token: str):
        """
        사용자 로그아웃 처리
        :param access_token: 사용자의 액세스 토큰
        """
        try:
            # Cognito 글로벌 로그아웃 (모든 디바이스에서 로그아웃)
            self.cognito_client.global_sign_out(AccessToken=access_token)
            print(f"User logged out successfully")
        except Exception as e:
            print(f"Error during logout: {str(e)}")
            raise HTTPException(status_code=500, detail="Error during logout")

def get_auth_service():
    return AuthService()