import boto3
from botocore.exceptions import ClientError
from pydantic import BaseSettings, AnyHttpUrl
from typing import Any, Dict, Optional, List

class Settings(BaseSettings):
    PROJECT_NAME: str = "CRM SaaS"
    API_V1_STR: str = "/api/v1"
    AWS_REGION: Optional[str] = None
    COGNITO_USER_POOL_ID: Optional[str] = None
    COGNITO_APP_CLIENT_ID: Optional[str] = None
    DYNAMODB_TENANT_TABLE: Optional[str] = None
    DYNAMODB_USER_TABLE: Optional[str] = None
    DYNAMODB_ACCOUNT_TABLE: Optional[str] = None
    DYNAMODB_OPPORTUNITY_TABLE: Optional[str] = None
    JWT_SECRET_KEY: Optional[str] = None
    ALLOWED_ORIGINS: List[AnyHttpUrl] = []  # 이 줄을 추가했습니다
    ACCESS_TOKEN_EXPIRE_MINUTES: Optional[int] = None
    JWT_ALGORITHM: Optional[str] = None

    @staticmethod
    def get_ssm_parameter(param_name: str, region: str, with_decryption: bool = True) -> Optional[str]:
        ssm_client = boto3.client('ssm', region_name=region)
        try:
            response = ssm_client.get_parameter(Name=param_name, WithDecryption=with_decryption)
            return response['Parameter']['Value']
        except ClientError as e:
            print(f"Error getting parameter {param_name}: {e}")
            return None

    def _load_from_parameter_store(self):
        params = {
            "AWS_REGION": "/crm-saas/aws/region",
            "COGNITO_USER_POOL_ID": "/crm-saas/cognito/user_pool_id",
            "COGNITO_APP_CLIENT_ID": "/crm-saas/cognito/app_client_id",
            "DYNAMODB_TENANT_TABLE": "/crm-saas/dynamodb/tenants_table",
            "DYNAMODB_USER_TABLE": "/crm-saas/dynamodb/users_table",
            "DYNAMODB_ACCOUNT_TABLE": "/crm-saas/dynamodb/accounts_table",
            "DYNAMODB_OPPORTUNITY_TABLE": "/crm-saas/dynamodb/opportunities_table",
            "JWT_SECRET_KEY": "/crm-saas/jwt/secret_key",
            "PROJECT_NAME": "/crm-saas/app/project_name",
            "ALLOWED_ORIGINS": "/crm-saas/app/allowed_origins",  # 이 줄을 추가했습니다
            "ACCESS_TOKEN_EXPIRE_MINUTES": "/crm-saas/cognito/access_token_expire_minutes",
            "JWT_ALGORITHM": "/crm-saas/cognito/jwt_algorithm"
        }

        # AWS_REGION이 None인 경우 기본값 사용
        region = self.AWS_REGION or "ap-northeast-2"

        for attr, param_name in params.items():
            value = self.get_ssm_parameter(param_name, region)
            if value is not None:
                if attr == "ALLOWED_ORIGINS":
                    # ALLOWED_ORIGINS를 쉼표로 구분된 문자열로 저장했다고 가정
                    setattr(self, attr, [origin.strip() for origin in value.split(',')])
                else:
                    setattr(self, attr, value)
            else:
                print(f"Warning: Failed to load {attr} from Parameter Store. Using default value if available.")

    def __init__(self, **values: Any):
        super().__init__(**values)
        self._load_from_parameter_store()

    def get_settings_dict(self) -> Dict[str, Any]:
        return {
            key: value for key, value in self.__dict__.items()
            if not key.startswith('_') and isinstance(value, (str, int, float, bool, list))
        }

settings = Settings()

# 설정 값 로드 확인
print("Loaded settings:")
for key, value in settings.get_settings_dict().items():
    #if key in ["JWT_SECRET_KEY"]:
    #    print(f"{key}: {'*' * 10}")  # 민감한 정보는 별표로 마스킹
    #else:
    #    print(f"{key}: {value}")
    print(f"{key}: {value}")