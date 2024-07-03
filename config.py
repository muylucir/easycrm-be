import os
from pydantic import BaseSettings, AnyHttpUrl
from typing import List, Union, Any
import boto3
from botocore.exceptions import ClientError

class ParameterStoreSettings(BaseSettings):
    AWS_REGION: str = "us-east-1"
    AWS_ACCESS_KEY_ID: str = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: str = os.getenv("AWS_SECRET_ACCESS_KEY")

    def get_ssm_parameter(self, param_name: str, with_decryption: bool = True) -> str:
        ssm_client = boto3.client('ssm', 
                                  region_name=self.AWS_REGION, 
                                  aws_access_key_id=self.AWS_ACCESS_KEY_ID,
                                  aws_secret_access_key=self.AWS_SECRET_ACCESS_KEY)
        try:
            response = ssm_client.get_parameter(Name=param_name, WithDecryption=with_decryption)
            return response['Parameter']['Value']
        except ClientError as e:
            print(f"Error getting parameter {param_name}: {e}")
            return None

class Settings(ParameterStoreSettings):
    # 기본 설정
    PROJECT_NAME: str = "CRM SaaS"
    API_V1_STR: str = "/api/v1"
    
    # CORS 설정
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    # AWS 설정
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str

    # Cognito 설정
    COGNITO_USER_POOL_ID: str
    COGNITO_APP_CLIENT_ID: str

    # DynamoDB 테이블 이름
    DYNAMODB_TENANT_TABLE: str
    DYNAMODB_USER_TABLE: str
    DYNAMODB_ACCOUNT_TABLE: str
    DYNAMODB_OPPORTUNITY_TABLE: str

    # JWT 설정
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

    def __init__(self, **values: Any):
        super().__init__(**values)
        
        # Parameter Store에서 값을 가져와 설정
        self.AWS_REGION = self.get_ssm_parameter("/crm-saas/aws/region") or self.AWS_REGION
        self.AWS_ACCESS_KEY_ID = self.get_ssm_parameter("/crm-saas/aws/access_key_id") or self.AWS_ACCESS_KEY_ID
        self.AWS_SECRET_ACCESS_KEY = self.get_ssm_parameter("/crm-saas/aws/secret_access_key", True) or self.AWS_SECRET_ACCESS_KEY
        
        self.COGNITO_USER_POOL_ID = self.get_ssm_parameter("/crm-saas/cognito/user_pool_id")
        self.COGNITO_APP_CLIENT_ID = self.get_ssm_parameter("/crm-saas/cognito/app_client_id")
        
        self.DYNAMODB_TENANT_TABLE = self.get_ssm_parameter("/crm-saas/dynamodb/tenant_table")
        self.DYNAMODB_USER_TABLE = self.get_ssm_parameter("/crm-saas/dynamodb/user_table")
        self.DYNAMODB_ACCOUNT_TABLE = self.get_ssm_parameter("/crm-saas/dynamodb/account_table")
        self.DYNAMODB_OPPORTUNITY_TABLE = self.get_ssm_parameter("/crm-saas/dynamodb/opportunity_table")
        
        self.JWT_SECRET_KEY = self.get_ssm_parameter("/crm-saas/jwt/secret_key", True)

settings = Settings()
