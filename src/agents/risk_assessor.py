"""
Risk Assessor Agent
리스크 평가 에이전트 - 기술적, 조직적, 비즈니스, 운영적 리스크 평가
"""
from typing import Optional, List, Dict, Any

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from .base_agent import BaseConsultingAgent
from src.models.schemas import CompanyProfile
from src.utils.consulting_logger import get_consulting_logger


class RiskAssessorAgent(BaseConsultingAgent):
    """리스크 평가 에이전트
    기술적, 조직적, 비즈니스, 운영적 리스크 평가
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="risk_assessor",
            name="리스크 평가 전문가",
            role="Risk Assessor",
            description="AI 프로젝트의 다양한 리스크를 평가하고 완화 전략을 수립합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 프로젝트 리스크 평가 전문가입니다.

[전문 영역]
1. 기술적 리스크 (데이터 품질, 모델 성능, 시스템 통합)
2. 조직적 리스크 (인력 확보, 변화 저항, 역량 부족)
3. 비즈니스 리스크 (ROI 미달성, 시장 변화, 규제)
4. 운영적 리스크 (시스템 장애, 보안, 모델 드리프트)

[평가 원칙]
- 발생 확률과 영향도를 고려한 리스크 등급화
- 실질적이고 실행 가능한 완화 전략 제시
- 예방, 대응, 복구 관점의 종합적 접근
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """리스크 평가 태스크 실행"""
        task_type = task.get("type", "assessment")

        if task_type == "full_assessment":
            return await self._full_assessment(task)
        elif task_type == "mitigation_planning":
            return await self._plan_mitigation(task.get("risks", []))
        else:
            return await self._general_assessment(task)

    async def _full_assessment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """종합 리스크 평가"""
        company = task.get("company_profile")
        use_cases = task.get("use_cases", [])

        self.logger.debug(f"리스크 평가 시작 - Use Case 수: {len(use_cases)}")

        risks = {
            "technical": self._assess_technical_risks(company, use_cases),
            "organizational": self._assess_organizational_risks(company),
            "business": self._assess_business_risks(company, use_cases),
            "operational": self._assess_operational_risks(company)
        }

        # 종합 리스크 점수
        all_risks = []
        for category, risk_list in risks.items():
            all_risks.extend(risk_list)

        total_risk_score = sum(r["risk_score"] for r in all_risks) / len(all_risks) if all_risks else 0
        risk_level = self._determine_risk_level(total_risk_score)

        self.logger.debug(f"리스크 평가 완료 - 총 리스크 수: {len(all_risks)}, 종합 점수: {total_risk_score:.2f}, 레벨: {risk_level}")

        return {
            "risks_by_category": risks,
            "total_risk_score": round(total_risk_score, 2),
            "risk_level": risk_level,
            "top_risks": sorted(all_risks, key=lambda x: x["risk_score"], reverse=True)[:5],
            "mitigation_priorities": self._prioritize_mitigations(all_risks)
        }

    def _assess_technical_risks(self, company, use_cases) -> List[Dict]:
        """기술적 리스크 평가"""
        risks = []

        # 데이터 품질 리스크
        data_quality = company.data_assets.data_quality_score if company else 3
        if data_quality < 3:
            risks.append({
                "name": "데이터 품질 부족",
                "category": "technical",
                "probability": 4,
                "impact": 4,
                "risk_score": 16,
                "mitigation": "데이터 품질 개선 프로그램 선행 필요"
            })

        # 인프라 리스크
        if company and not company.it_infrastructure.has_cloud:
            risks.append({
                "name": "AI 인프라 부족",
                "category": "technical",
                "probability": 3,
                "impact": 4,
                "risk_score": 12,
                "mitigation": "클라우드 인프라 도입 검토"
            })

        # 통합 복잡성
        if company and company.it_infrastructure.legacy_system_count > 3:
            risks.append({
                "name": "레거시 시스템 통합 복잡성",
                "category": "technical",
                "probability": 4,
                "impact": 3,
                "risk_score": 12,
                "mitigation": "단계적 통합 전략 및 API 게이트웨이 도입"
            })

        return risks

    def _assess_organizational_risks(self, company) -> List[Dict]:
        """조직적 리스크 평가"""
        risks = []

        # 인력 부족
        if company:
            ai_staff = company.human_resources.data_scientist_count + company.human_resources.ml_engineer_count
            if ai_staff < 2:
                risks.append({
                    "name": "AI 전문 인력 부족",
                    "category": "organizational",
                    "probability": 4,
                    "impact": 4,
                    "risk_score": 16,
                    "mitigation": "외부 전문가 영입 또는 파트너십 구축"
                })

        # 변화 저항
        if company and company.organizational_readiness.change_management_capability < 3:
            risks.append({
                "name": "조직 변화 저항",
                "category": "organizational",
                "probability": 3,
                "impact": 3,
                "risk_score": 9,
                "mitigation": "체계적인 변화 관리 프로그램 운영"
            })

        return risks

    def _assess_business_risks(self, company, use_cases) -> List[Dict]:
        """비즈니스 리스크 평가"""
        risks = []

        # ROI 미달성
        risks.append({
            "name": "기대 ROI 미달성",
            "category": "business",
            "probability": 3,
            "impact": 4,
            "risk_score": 12,
            "mitigation": "보수적 ROI 목표 설정 및 단계별 검증"
        })

        # 요구사항 변경
        risks.append({
            "name": "프로젝트 범위 변경",
            "category": "business",
            "probability": 4,
            "impact": 3,
            "risk_score": 12,
            "mitigation": "명확한 범위 정의 및 변경 관리 프로세스"
        })

        return risks

    def _assess_operational_risks(self, company) -> List[Dict]:
        """운영적 리스크 평가"""
        risks = []

        # 모델 성능 저하
        risks.append({
            "name": "모델 성능 저하 (Drift)",
            "category": "operational",
            "probability": 4,
            "impact": 3,
            "risk_score": 12,
            "mitigation": "지속적 모니터링 및 재학습 체계 구축"
        })

        # 보안 리스크
        if company and company.it_infrastructure.security_level == "basic":
            risks.append({
                "name": "보안 취약점",
                "category": "operational",
                "probability": 3,
                "impact": 5,
                "risk_score": 15,
                "mitigation": "보안 강화 및 정기 감사 체계 구축"
            })

        return risks

    def _determine_risk_level(self, score: float) -> str:
        """리스크 레벨 결정"""
        if score >= 15:
            return "높음 (High)"
        elif score >= 10:
            return "중간 (Medium)"
        else:
            return "낮음 (Low)"

    def _prioritize_mitigations(self, risks: List[Dict]) -> List[str]:
        """완화 전략 우선순위화"""
        sorted_risks = sorted(risks, key=lambda x: x["risk_score"], reverse=True)
        return [r["mitigation"] for r in sorted_risks[:5]]

    async def _plan_mitigation(self, risks: List[Dict]) -> Dict[str, Any]:
        """완화 전략 계획"""
        strategies = []
        for risk in risks:
            strategies.append({
                "risk": risk.get("name"),
                "strategy_type": "mitigation",
                "actions": [risk.get("mitigation", "")],
                "timeline": "즉시" if risk.get("risk_score", 0) >= 15 else "3개월 내",
                "owner": "프로젝트 매니저"
            })

        return {"mitigation_strategies": strategies}

    async def _general_assessment(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """일반 평가"""
        if self.llm_provider:
            prompt = task.get("query", "")
            response = await self.llm_provider.consult(prompt, {}, "risk_assessment")
            return {"assessment": response}
        return {"error": "LLM provider not configured"}

