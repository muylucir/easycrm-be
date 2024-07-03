from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from datetime import datetime
import os

class AccountModel(Model):
    """
    고객 계정 정보를 저장하는 DynamoDB 모델
    """
    class Meta:
        table_name = os.environ.get('DYNAMODB_ACCOUNT_TABLE', 'Accounts')
        region = os.environ.get('AWS_REGION', 'us-east-1')

    account_id = UnicodeAttribute(hash_key=True)
    tenant_id = UnicodeAttribute(range_key=True)
    name = UnicodeAttribute()
    manager_id = UnicodeAttribute()  # 담당자 ID (User의 user_id)
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    is_active = NumberAttribute(default=1)  # 1: 활성, 0: 비활성

    def save(self, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(**kwargs)