from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute, ListAttribute
from datetime import datetime
from app.core.config import settings
import os

class UserModel(Model):
    """
    사용자 정보를 저장하는 DynamoDB 모델
    """
    class Meta:
        table_name = settings.DYNAMODB_USER_TABLE
        region = settings.AWS_REGION

    user_id = UnicodeAttribute(hash_key=True)  # Cognito의 사용자 ID와 연동
    tenant_id = UnicodeAttribute(range_key=True)  # 테넌트 ID (Cognito 그룹 이름)
    email = UnicodeAttribute()
    given_name = UnicodeAttribute()
    family_name = UnicodeAttribute()
    role = UnicodeAttribute()  # 'admin' 또는 'user'
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    is_active = BooleanAttribute(default=True)  # 1: 활성, 0: 비활성
    managed_account_ids = ListAttribute(default=list)  # 사용자가 관리하는 계정 ID 목록

    def save(self, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(**kwargs)