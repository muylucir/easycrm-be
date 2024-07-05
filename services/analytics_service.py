from app.services.account_service import AccountService
from app.services.opportunity_service import OpportunityService
from typing import Dict, List

class AnalyticsService:
    @staticmethod
    async def get_tenant_summary(tenant_id: str) -> Dict:
        """
        테넌트의 요약 정보 조회
        :param tenant_id: 테넌트 ID
        :return: 테넌트 요약 정보
        """
        accounts = await AccountService.list_accounts(tenant_id)
        opportunities = await OpportunityService.list_opportunities(tenant_id)
        total_expected_revenue = await OpportunityService.calculate_total_expected_revenue(tenant_id)

        return {
            "total_accounts": len(accounts),
            "total_opportunities": len(opportunities),
            "total_expected_revenue": total_expected_revenue
        }

    @staticmethod
    async def get_opportunity_stage_distribution(tenant_id: str) -> Dict[str, int]:
        """
        테넌트의 영업 기회 단계별 분포 조회
        :param tenant_id: 테넌트 ID
        :return: 단계별 영업 기회 수
        """
        opportunities = await OpportunityService.list_opportunities(tenant_id)
        stage_distribution = {}
        for opportunity in opportunities:
            stage = opportunity.stage
            if stage in stage_distribution:
                stage_distribution[stage] += 1
            else:
                stage_distribution[stage] = 1
        return stage_distribution

    @staticmethod
    async def get_top_accounts_by_revenue(tenant_id: str, limit: int = 5) -> List[Dict]:
        """
        기대 매출 기준 상위 계정 조회
        :param tenant_id: 테넌트 ID
        :param limit: 조회할 계정 수
        :return: 상위 계정 목록
        """
        accounts = await AccountService.list_accounts(tenant_id)
        account_revenue = {}
        for account in accounts:
            opportunities = await OpportunityService.list_opportunities(tenant_id, account.account_id)
            total_revenue = sum(opp.expected_revenue for opp in opportunities)
            account_revenue[account.account_id] = {
                "account_id": account.account_id,
                "account_name": account.name,
                "total_revenue": total_revenue
            }
        
        sorted_accounts = sorted(account_revenue.values(), key=lambda x: x["total_revenue"], reverse=True)
        return sorted_accounts[:limit]

    @staticmethod
    async def get_sales_pipeline(tenant_id: str) -> List[Dict]:
        """
        테넌트의 영업 파이프라인 조회
        :param tenant_id: 테넌트 ID
        :return: 단계별 영업 기회 및 기대 매출
        """
        opportunities = await OpportunityService.list_opportunities(tenant_id)
        pipeline = {}
        for opportunity in opportunities:
            stage = opportunity.stage
            if stage not in pipeline:
                pipeline[stage] = {
                    "stage": stage,
                    "count": 0,
                    "total_expected_revenue": 0
                }
            pipeline[stage]["count"] += 1
            pipeline[stage]["total_expected_revenue"] += opportunity.expected_revenue
        
        return list(pipeline.values())