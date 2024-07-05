from app.models.opportunity import OpportunityModel
from app.schemas.opportunity import OpportunityCreate, OpportunityUpdate, OpportunityInDB
from fastapi import HTTPException
from typing import List
import uuid

class OpportunityService:
    @staticmethod
    async def create_opportunity(opportunity: OpportunityCreate) -> OpportunityInDB:
        """
        새 영업 기회 생성
        :param opportunity: 생성할 영업 기회 정보
        :return: 생성된 영업 기회 정보
        """
        opportunity_id = str(uuid.uuid4())
        db_opportunity = OpportunityModel(
            opportunity_id=opportunity_id,
            tenant_id=opportunity.tenant_id,
            account_id=opportunity.account_id,
            name=opportunity.name,
            stage=opportunity.stage,
            expected_revenue=opportunity.expected_revenue,
            manager_id=opportunity.manager_id
        )
        try:
            db_opportunity.save()
            return OpportunityInDB(
                opportunity_id=db_opportunity.opportunity_id,
                tenant_id=db_opportunity.tenant_id,
                account_id=db_opportunity.account_id,
                name=db_opportunity.name,
                stage=db_opportunity.stage,
                expected_revenue=db_opportunity.expected_revenue,
                manager_id=db_opportunity.manager_id,
                created_at=db_opportunity.created_at,
                updated_at=db_opportunity.updated_at,
                is_active=db_opportunity.is_active
            )
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Could not create opportunity: {str(e)}")

    @staticmethod
    async def get_opportunity(opportunity_id: str, tenant_id: str) -> OpportunityInDB:
        """
        영업 기회 ID와 테넌트 ID로 영업 기회 조회
        :param opportunity_id: 영업 기회 ID
        :param tenant_id: 테넌트 ID
        :return: 조회된 영업 기회 정보
        """
        try:
            opportunity = OpportunityModel.get(opportunity_id, tenant_id)
            return OpportunityInDB(
                opportunity_id=opportunity.opportunity_id,
                tenant_id=opportunity.tenant_id,
                account_id=opportunity.account_id,
                name=opportunity.name,
                stage=opportunity.stage,
                expected_revenue=opportunity.expected_revenue,
                manager_id=opportunity.manager_id,
                created_at=opportunity.created_at,
                updated_at=opportunity.updated_at,
                is_active=opportunity.is_active
            )
        except OpportunityModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    @staticmethod
    async def update_opportunity(opportunity_id: str, tenant_id: str, opportunity_update: OpportunityUpdate) -> OpportunityInDB:
        """
        영업 기회 정보 업데이트
        :param opportunity_id: 업데이트할 영업 기회 ID
        :param tenant_id: 테넌트 ID
        :param opportunity_update: 업데이트할 영업 기회 정보
        :return: 업데이트된 영업 기회 정보
        """
        try:
            opportunity = OpportunityModel.get(opportunity_id, tenant_id)
            update_data = opportunity_update.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(opportunity, key, value)
            opportunity.save()
            return OpportunityInDB(
                opportunity_id=opportunity.opportunity_id,
                tenant_id=opportunity.tenant_id,
                account_id=opportunity.account_id,
                name=opportunity.name,
                stage=opportunity.stage,
                expected_revenue=opportunity.expected_revenue,
                manager_id=opportunity.manager_id,
                created_at=opportunity.created_at,
                updated_at=opportunity.updated_at,
                is_active=opportunity.is_active
            )
        except OpportunityModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    @staticmethod
    async def delete_opportunity(opportunity_id: str, tenant_id: str) -> bool:
        """
        영업 기회 삭제 (소프트 삭제)
        :param opportunity_id: 삭제할 영업 기회 ID
        :param tenant_id: 테넌트 ID
        :return: 삭제 성공 여부
        """
        try:
            opportunity = OpportunityModel.get(opportunity_id, tenant_id)
            opportunity.is_active = False
            opportunity.save()
            return True
        except OpportunityModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    @staticmethod
    async def list_opportunities(tenant_id: str, account_id: str = None) -> List[OpportunityInDB]:
        """
        테넌트의 모든 활성 영업 기회 목록 조회
        :param tenant_id: 테넌트 ID
        :param account_id: 계정 ID (선택적)
        :return: 영업 기회 목록
        """
        if account_id:
            opportunities = OpportunityModel.query(tenant_id, OpportunityModel.account_id == account_id & OpportunityModel.is_active == True)
        else:
            opportunities = OpportunityModel.query(tenant_id, OpportunityModel.is_active == True)
        
        return [
            OpportunityInDB(
                opportunity_id=opportunity.opportunity_id,
                tenant_id=opportunity.tenant_id,
                account_id=opportunity.account_id,
                name=opportunity.name,
                stage=opportunity.stage,
                expected_revenue=opportunity.expected_revenue,
                manager_id=opportunity.manager_id,
                created_at=opportunity.created_at,
                updated_at=opportunity.updated_at,
                is_active=opportunity.is_active
            )
            for opportunity in opportunities
        ]

    @staticmethod
    async def change_opportunity_manager(opportunity_id: str, tenant_id: str, new_manager_id: str) -> OpportunityInDB:
        """
        영업 기회 담당자 변경
        :param opportunity_id: 영업 기회 ID
        :param tenant_id: 테넌트 ID
        :param new_manager_id: 새로운 담당자 ID
        :return: 업데이트된 영업 기회 정보
        """
        try:
            opportunity = OpportunityModel.get(opportunity_id, tenant_id)
            opportunity.manager_id = new_manager_id
            opportunity.save()
            return OpportunityInDB(
                opportunity_id=opportunity.opportunity_id,
                tenant_id=opportunity.tenant_id,
                account_id=opportunity.account_id,
                name=opportunity.name,
                stage=opportunity.stage,
                expected_revenue=opportunity.expected_revenue,
                manager_id=opportunity.manager_id,
                created_at=opportunity.created_at,
                updated_at=opportunity.updated_at,
                is_active=opportunity.is_active
            )
        except OpportunityModel.DoesNotExist:
            raise HTTPException(status_code=404, detail="Opportunity not found")

    @staticmethod
    async def calculate_total_expected_revenue(tenant_id: str) -> float:
        """
        테넌트의 총 기대 매출 계산
        :param tenant_id: 테넌트 ID
        :return: 총 기대 매출
        """
        opportunities = OpportunityModel.query(tenant_id, OpportunityModel.is_active == True)
        total_expected_revenue = sum(opportunity.expected_revenue for opportunity in opportunities)
        return total_expected_revenue