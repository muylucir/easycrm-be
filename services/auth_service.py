import boto3
from botocore.exceptions import ClientError
from app.core.config import settings
from app.core.security import verify_cognito_token
from app.schemas.user import UserCreate, UserInDB
from app.services.user_service import UserService
from fastapi import HTTPException
from jose import jwt
from datetime import datetime, timedelta
from typing import Optional

class AuthService:
    def __init__(self):
        self.cognito_client = boto3.client('cognito-idp', region_name=settings.AWS_REGION)
        self.user_service = UserService()

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
                    {'Name': 'custom:tenant_id', 'Value': user.tenant_id},
                    {'Name': 'custom:role', 'Value': user.role},
                ]
            )
            
            cognito_user_id = cognito_response['UserSub']
            
            # UserCreate 객체에 Cognito 사용자 ID 추가
            user_data = user.dict()
            user_data['user_id'] = cognito_user_id
            
            db_user = await self.user_service.create_user(UserCreate(**user_data))
            
            return db_user
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def authenticate_user(self, username: str, password: str):
        try:
            auth_response = self.cognito_client.initiate_auth(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                }
            )
            
            id_token = auth_response['AuthenticationResult']['IdToken']
            
            # Cognito 토큰 검증
            claims = verify_cognito_token(id_token)
            
            user_id = claims['sub']
            tenant_id = claims.get('custom:tenant_id')  # Cognito에서 설정한 사용자 지정 속성
            
            return {
                "access_token": id_token,
                "token_type": "bearer",
                "user_id": user_id,
                "tenant_id": tenant_id
            }
        except self.cognito_client.exceptions.NotAuthorizedException:
            raise HTTPException(status_code=401, detail="Incorrect username or password")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        """
        사용자 비밀번호 변경
        """
        try:
            user = await self.user_service.get_user(user_id)
            if not user:
                raise HTTPException(status_code=404, detail="User not found")

            response = self.cognito_client.change_password(
                PreviousPassword=old_password,
                ProposedPassword=new_password,
                AccessToken=user.cognito_access_token  # 이 필드가 UserInDB 모델에 추가되어야 함
            )
            return True
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def forgot_password(self, email: str) -> bool:
        """
        비밀번호 재설정 코드 요청
        """
        try:
            response = self.cognito_client.forgot_password(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                Username=email
            )
            return True
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def confirm_forgot_password(self, email: str, confirmation_code: str, new_password: str) -> bool:
        """
        비밀번호 재설정 확인
        """
        try:
            response = self.cognito_client.confirm_forgot_password(
                ClientId=settings.COGNITO_APP_CLIENT_ID,
                Username=email,
                ConfirmationCode=confirmation_code,
                Password=new_password
            )
            return True
        except ClientError as e:
            raise HTTPException(status_code=400, detail=str(e))
    
    async def logout_user(self, user_id: str):
        """
        사용자 로그아웃 처리
        :param user_id: 로그아웃할 사용자의 ID
        """
        try:
            # 여기서 필요한 로그아웃 로직을 구현합니다
            # 예: 토큰 블랙리스트에 추가, Cognito 세션 무효화 등
            
            # Cognito 글로벌 로그아웃 (모든 디바이스에서 로그아웃)
            self.cognito_client.global_sign_out(
                AccessToken=user_id  # 실제로는 액세스 토큰을 사용해야 합니다
            )
            
            print(f"User {user_id} logged out successfully")
        except Exception as e:
            print(f"Error during logout for user {user_id}: {str(e)}")
            raise HTTPException(status_code=500, detail="Error during logout")