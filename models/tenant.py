from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, BooleanAttribute, UTCDateTimeAttribute
from datetime import datetime
from app.core.config import settings
import os

class TenantModel(Model):
    """
    테넌트 정보를 저장하는 DynamoDB 모델
    """
    class Meta:
        table_name = settings.DYNAMODB_TENANT_TABLE
        region = settings.AWS_REGION

    tenant_id = UnicodeAttribute(hash_key=True)  # Cognito 그룹 이름과 연동
    tenant_name = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    is_active = BooleanAttribute(default=True)  # 1: 활성, 0: 비활성

    def save(self, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(**kwargs)