from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from datetime import datetime
import os

class TenantModel(Model):
    """
    테넌트 정보를 저장하는 DynamoDB 모델
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_TENANT_TABLE', 'Tenants')
        region = os.environ.get('AWS_REGION', 'us-east-1')

    tenant_id = UnicodeAttribute(hash_key=True)  # Cognito 그룹 이름과 연동
    name = UnicodeAttribute()
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    is_active = NumberAttribute(default=1)  # 1: 활성, 0: 비활성

    def save(self, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(**kwargs)