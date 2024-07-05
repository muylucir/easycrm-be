from pynamodb.models import Model
from pynamodb.attributes import UnicodeAttribute, NumberAttribute, UTCDateTimeAttribute
from datetime import datetime
from app.core.config import settings
import os

class OpportunityModel(Model):
    """
    영업 기회 정보를 저장하는 DynamoDB 모델
    """
    class Meta:
        table_name = settings.DYNAMODB_OPPORTUNITY_TABLE
        region = settings.AWS_REGION

    opportunity_id = UnicodeAttribute(hash_key=True)
    tenant_id = UnicodeAttribute(range_key=True)
    account_id = UnicodeAttribute()
    name = UnicodeAttribute()
    stage = UnicodeAttribute()  # Prospecting, Qualification, Committed, Closed Lost, Closed Won
    expected_revenue = NumberAttribute()
    manager_id = UnicodeAttribute()  # 담당자 ID (User의 user_id)
    created_at = UTCDateTimeAttribute(default=datetime.utcnow)
    updated_at = UTCDateTimeAttribute(default=datetime.utcnow)
    is_active = NumberAttribute(default=1)  # 1: 활성, 0: 비활성

    def save(self, **kwargs):
        self.updated_at = datetime.utcnow()
        super().save(**kwargs)