"""
ROI Analyst Agent
ROI 분석가 에이전트 - 투자 대비 효과 분석, 비용-편익 분석, 재무적 타당성 검토
"""
from typing import Optional, List, Dict, Any

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from .base_agent import BaseConsultingAgent
from src.utils.consulting_logger import get_consulting_logger


class ROIAnalystAgent(BaseConsultingAgent):
    """ROI 분석가 에이전트
    투자 대비 효과 분석, 비용-편익 분석, 재무적 타당성 검토
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="roi_analyst",
            name="ROI 분석가",
            role="ROI Analyst",
            description="AI 투자의 ROI를 분석하고, 비용-편익 분석 및 재무적 타당성을 검토합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 투자 ROI 분석 전문가입니다.

[전문 영역]
1. 정량적 ROI 분석 (비용 절감, 매출 증대, 생산성 향상)
2. 정성적 효과 분석 (고객 만족도, 브랜드 가치, 경쟁력)
3. TCO(Total Cost of Ownership) 분석
4. 재무적 타당성 검토 (NPV, IRR, Payback Period)

[분석 원칙]
- 보수적 가정 기반의 현실적 추정
- 정량적/정성적 효과의 균형있는 평가
- 리스크 요인을 반영한 시나리오 분석
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """ROI 분석 태스크 실행"""
        task_type = task.get("type", "analysis")

        if task_type == "roi_calculation":
            return await self._calculate_roi(task)
        elif task_type == "tco_analysis":
            return await self._analyze_tco(task)
        elif task_type == "scenario_comparison":
            return await self._compare_scenarios(task.get("scenarios", []))
        else:
            return await self._general_analysis(task)

    async def _calculate_roi(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """ROI 계산"""
        investment = task.get("investment", 0)
        benefits = task.get("expected_benefits", {})
        period_months = task.get("period_months", 36)

        self.logger.debug(f"ROI 계산 시작 - 투자액: {investment:,.0f}, 기간: {period_months}개월")

        # 투자액이 0이면 기본값 설정
        if investment <= 0:
            investment = 1000000  # 기본값: 100만원
            self.logger.warning(f"투자액이 0이거나 음수입니다. 기본값 {investment:,.0f}원을 사용합니다.")

        # 비용 구성
        costs = {
            "initial_investment": investment,
            "annual_operation": investment * 0.15,  # 연간 운영비 15%
            "annual_maintenance": investment * 0.10,  # 연간 유지보수 10%
            "total_3year": investment + (investment * 0.25 * 3)
        }

        # 효과 추정
        annual_benefits = sum(benefits.values()) if benefits else investment * 0.5

        # ROI 지표 계산 (0으로 나누기 방지)
        total_3year = costs["total_3year"]
        if total_3year <= 0:
            total_3year = investment  # 최소값으로 초기 투자액 사용
            costs["total_3year"] = total_3year
            self.logger.warning(f"3년 총 비용이 0이거나 음수입니다. 초기 투자액 {total_3year:,.0f}원을 사용합니다.")

        # 회수기간 계산 (0으로 나누기 방지)
        payback_months = float('inf')
        if annual_benefits > 0:
            monthly_benefit = annual_benefits / 12
            if monthly_benefit > 0:
                payback_months = costs["initial_investment"] / monthly_benefit
                # 무한대 값 방지 (너무 큰 값은 999로 제한)
                if payback_months > 999:
                    payback_months = 999
        
        roi_metrics = {
            "roi_percent": ((annual_benefits * 3 - total_3year) / total_3year) * 100 if total_3year > 0 else 0,
            "payback_months": round(payback_months, 1) if payback_months != float('inf') else 999,
            "npv_3year": self._calculate_npv(costs["initial_investment"], annual_benefits, 3, 0.1),
            "irr": self._estimate_irr(costs["initial_investment"], annual_benefits, 3)
        }

        self.logger.debug(f"ROI 계산 완료 - ROI: {roi_metrics['roi_percent']:.2f}%, 회수기간: {roi_metrics['payback_months']:.1f}개월")

        return {
            "costs": costs,
            "benefits": {
                "annual": annual_benefits,
                "3year_total": annual_benefits * 3
            },
            "metrics": roi_metrics,
            "recommendation": self._get_roi_recommendation(roi_metrics)
        }

    def _calculate_npv(self, investment: float, annual_benefit: float, years: int, discount_rate: float) -> float:
        """NPV 계산"""
        npv = -investment
        for year in range(1, years + 1):
            npv += annual_benefit / ((1 + discount_rate) ** year)
        return round(npv, 2)

    def _estimate_irr(self, investment: float, annual_benefit: float, years: int) -> float:
        """IRR 추정 (단순화)"""
        if annual_benefit <= 0 or investment <= 0:
            return 0
        simple_return = (annual_benefit * years - investment) / investment
        irr = (simple_return / years) * 100
        return round(max(irr, 0), 2)

    def _get_roi_recommendation(self, metrics: Dict) -> str:
        """ROI 기반 권고"""
        if metrics["roi_percent"] > 50 and metrics["payback_months"] < 24:
            return "강력 추천: 높은 ROI와 빠른 투자 회수 기간"
        elif metrics["roi_percent"] > 20:
            return "추천: 양호한 투자 수익률"
        elif metrics["roi_percent"] > 0:
            return "조건부 추천: 추가 최적화 검토 필요"
        else:
            return "재검토 필요: 투자 효과 미흡"

    async def _analyze_tco(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """TCO 분석"""
        investment = task.get("investment", 0)

        tco = {
            "year_1": {
                "infrastructure": investment * 0.4,
                "software": investment * 0.2,
                "personnel": investment * 0.3,
                "training": investment * 0.05,
                "other": investment * 0.05
            },
            "year_2": {
                "infrastructure": investment * 0.1,
                "software": investment * 0.1,
                "personnel": investment * 0.35,
                "maintenance": investment * 0.1,
                "other": investment * 0.03
            },
            "year_3": {
                "infrastructure": investment * 0.05,
                "software": investment * 0.1,
                "personnel": investment * 0.35,
                "maintenance": investment * 0.1,
                "other": investment * 0.03
            }
        }

        tco["total"] = sum(sum(year.values()) for year in tco.values() if isinstance(year, dict))

        return tco

    async def _compare_scenarios(self, scenarios: List[Dict]) -> Dict[str, Any]:
        """시나리오 비교 분석"""
        comparison = []

        for scenario in scenarios:
            roi_result = await self._calculate_roi({
                "investment": scenario.get("investment", 0),
                "expected_benefits": scenario.get("benefits", {}),
                "period_months": 36
            })

            comparison.append({
                "scenario_name": scenario.get("name", "Unknown"),
                "investment": scenario.get("investment", 0),
                "roi": roi_result["metrics"]["roi_percent"],
                "payback_months": roi_result["metrics"]["payback_months"],
                "npv": roi_result["metrics"]["npv_3year"],
                "recommendation": roi_result["recommendation"]
            })

        # ROI 기준 정렬
        comparison.sort(key=lambda x: x["roi"], reverse=True)

        return {
            "comparison": comparison,
            "best_scenario": comparison[0] if comparison else None,
            "analysis_summary": self._generate_comparison_summary(comparison)
        }

    def _generate_comparison_summary(self, comparison: List[Dict]) -> str:
        """비교 분석 요약"""
        if not comparison:
            return "비교할 시나리오가 없습니다."

        best = comparison[0]
        return f"최적 시나리오: {best['scenario_name']} (ROI: {best['roi']:.1f}%, 회수기간: {best['payback_months']:.0f}개월)"

    async def _general_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """일반 분석"""
        if self.llm_provider:
            prompt = task.get("query", "")
            response = await self.llm_provider.consult(prompt, {}, "roi_analysis")
            return {"analysis": response}
        return {"error": "LLM provider not configured"}

