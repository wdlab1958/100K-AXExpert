"""
Strategy Analyst Agent
AI 전략 분석가 에이전트 - AI 성숙도 진단, 기회 발굴, 전략 및 로드맵 수립
"""
from typing import Optional, List, Dict, Any
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from .base_agent import BaseConsultingAgent
from src.models.schemas import CompanyProfile
from config.settings import INDUSTRY_TEMPLATES
from src.utils.consulting_logger import get_consulting_logger


class StrategyAnalystAgent(BaseConsultingAgent):
    """1단계: AI 전략 분석가 에이전트
    AI 성숙도 진단, 기회 발굴, 전략 및 로드맵 수립
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="strategy_analyst",
            name="AI 전략 분석가",
            role="Strategy Analyst",
            description="고객사의 AI 성숙도를 진단하고, AI 도입 기회를 발굴하며, 전략 및 로드맵을 수립합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 전략 분석 전문가입니다.

[전문 영역]
1. AI 성숙도 진단 (4대 영역: 전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스)
2. 비즈니스 가치 사슬 분석을 통한 AI 기회 발굴
3. AI 전략 및 로드맵 수립

[진단 기준]
- Level 1 (초기): AI 활동이 산발적, 개인 역량 의존
- Level 2 (반복 가능): 최소한의 프로젝트 관리 체계
- Level 3 (정의됨): 표준 프로세스 및 방법론 문서화
- Level 4 (관리됨): 정량적 KPI 기반 관리
- Level 5 (최적화됨): AI가 비즈니스 핵심 동력

[분석 원칙]
- 객관적이고 데이터 기반의 평가
- 현실적이고 실현 가능한 목표 설정
- 단기/중기/장기 균형잡힌 로드맵
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전략 분석 태스크 실행"""
        task_type = task.get("type", "analysis")

        if task_type == "maturity_assessment":
            return await self._assess_maturity(task.get("company_profile"))
        elif task_type == "opportunity_identification":
            return await self._identify_opportunities(task.get("company_profile"))
        elif task_type == "roadmap_planning":
            return await self._plan_roadmap(task.get("company_profile"), task.get("use_cases", []))
        else:
            return await self._general_analysis(task)

    async def _assess_maturity(self, company: CompanyProfile) -> Dict[str, Any]:
        """AI 성숙도 진단"""
        self.logger.debug(f"성숙도 진단 시작: {company.name} ({company.industry.value})")
        
        # 컨텍스트 구성
        context = {
            "company_name": company.name,
            "industry": company.industry.value,
            "company_size": company.company_size.value,
            "it_infrastructure": company.it_infrastructure.model_dump(),
            "data_assets": company.data_assets.model_dump(),
            "human_resources": company.human_resources.model_dump(),
            "organizational_readiness": company.organizational_readiness.model_dump()
        }

        prompt = f"""다음 기업의 AI 성숙도를 진단해주세요.

[기업 정보]
{json.dumps(context, ensure_ascii=False, indent=2)}

[진단 요청]
4대 핵심 영역(전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스)에 대해:
1. 각 영역별 현재 성숙도 레벨 (1-5) 평가
2. 세부 항목별 점수 및 근거
3. 주요 강점 및 약점
4. 우선 개선 과제

JSON 형식으로 결과를 반환해주세요."""

        if self.llm_provider:
            self.logger.debug("LLM을 통한 성숙도 진단 수행 중...")
            response = await self.llm_provider.generate(prompt, self.get_system_prompt())
            # 실제 구현에서는 LLM 응답을 파싱하여 구조화

        # 규칙 기반 평가 (LLM 보완)
        self.logger.debug("규칙 기반 성숙도 점수 계산 중...")
        scores = self._calculate_maturity_scores(company)
        overall_level = self._determine_overall_level(scores)
        
        self.logger.debug(f"성숙도 진단 완료 - 전체 레벨: {overall_level}")

        return {
            "assessment_type": "maturity",
            "company_id": company.id or company.name,
            "scores": scores,
            "overall_level": overall_level,
            "recommendations": self._generate_recommendations(scores, company)
        }

    def _calculate_maturity_scores(self, company: CompanyProfile) -> Dict[str, Any]:
        """성숙도 점수 계산 (규칙 기반)"""
        scores = {}

        # 전략 및 비전 점수
        strategy_score = 2.0
        if company.organizational_readiness.executive_support >= 4:
            strategy_score += 1.0
        if company.financial_resources.ai_investment_budget > 0:
            strategy_score += 0.5

        scores["strategy"] = {
            "level": min(int(strategy_score), 5),
            "score": strategy_score,
            "items": {
                "AI 비전 명확성": company.organizational_readiness.executive_support,
                "AI 투자 계획": 4 if company.financial_resources.ai_investment_budget > 0 else 2,
                "전략적 정합성": company.organizational_readiness.innovation_culture
            }
        }

        # 조직 및 역량 점수
        hr = company.human_resources
        org_score = 1.0
        if hr.data_scientist_count > 0:
            org_score += 1.0
        if hr.ml_engineer_count > 0:
            org_score += 1.0
        if hr.ai_experience_projects > 0:
            org_score += 0.5
        if hr.training_budget_ratio > 0:
            org_score += 0.5

        scores["organization"] = {
            "level": min(int(org_score), 5),
            "score": org_score,
            "items": {
                "AI 전담 인력": min(hr.data_scientist_count + hr.ml_engineer_count, 5),
                "AI 프로젝트 경험": min(hr.ai_experience_projects, 5),
                "교육 투자": 4 if hr.training_budget_ratio > 2 else 2,
                "변화 관리 역량": company.organizational_readiness.change_management_capability
            }
        }

        # 데이터 및 기술 점수
        data = company.data_assets
        infra = company.it_infrastructure
        tech_score = 1.0
        if data.data_volume_tb > 1:
            tech_score += 0.5
        if data.data_quality_score >= 3:
            tech_score += 0.5
        if data.has_data_governance:
            tech_score += 1.0
        if infra.has_cloud:
            tech_score += 0.5
        if infra.gpu_available:
            tech_score += 0.5
        if infra.has_data_warehouse or infra.has_data_lake:
            tech_score += 1.0

        scores["data_tech"] = {
            "level": min(int(tech_score), 5),
            "score": tech_score,
            "items": {
                "데이터 인프라": 4 if (infra.has_data_warehouse or infra.has_data_lake) else 2,
                "데이터 품질": int(data.data_quality_score),
                "클라우드 활용": 4 if infra.has_cloud else 2,
                "AI 인프라(GPU)": 4 if infra.gpu_available else 2
            }
        }

        # 프로세스 및 거버넌스 점수
        process_score = 1.5
        if data.has_data_governance:
            process_score += 1.0
        if infra.security_level != "basic":
            process_score += 0.5
        if hr.ai_experience_projects > 2:
            process_score += 1.0

        scores["process"] = {
            "level": min(int(process_score), 5),
            "score": process_score,
            "items": {
                "AI 개발 방법론": 3 if hr.ai_experience_projects > 0 else 1,
                "데이터 거버넌스": 4 if data.has_data_governance else 2,
                "보안 체계": 4 if infra.security_level != "basic" else 2,
                "모니터링 체계": 2
            }
        }

        return scores

    def _determine_overall_level(self, scores: Dict[str, Any]) -> int:
        """종합 성숙도 레벨 결정"""
        total_score = sum(s["score"] for s in scores.values()) / len(scores)
        return min(max(int(total_score), 1), 5)

    def _generate_recommendations(self, scores: Dict[str, Any], company: CompanyProfile) -> List[str]:
        """개선 권고사항 생성"""
        recommendations = []

        for dimension, data in scores.items():
            if data["level"] <= 2:
                if dimension == "strategy":
                    recommendations.append("AI 비전 및 전략 수립 워크숍 진행 권장")
                elif dimension == "organization":
                    recommendations.append("AI 전문 인력 채용 또는 외부 파트너십 구축 필요")
                elif dimension == "data_tech":
                    recommendations.append("데이터 인프라 현대화 및 클라우드 도입 검토")
                elif dimension == "process":
                    recommendations.append("AI 거버넌스 체계 수립 및 표준 프로세스 정의 필요")

        return recommendations

    async def _identify_opportunities(self, company: CompanyProfile) -> Dict[str, Any]:
        """AI 도입 기회 발굴"""
        industry = company.industry.value
        template = INDUSTRY_TEMPLATES.get(industry, INDUSTRY_TEMPLATES["manufacturing"])

        opportunities = []
        for use_case in template["use_cases"]:
            opportunities.append({
                "name": use_case["name"],
                "roi_potential": use_case["roi_range"],
                "complexity": use_case["complexity"],
                "fit_score": self._calculate_fit_score(use_case, company)
            })

        # 적합도 순으로 정렬
        opportunities.sort(key=lambda x: x["fit_score"], reverse=True)

        return {
            "industry": template["name"],
            "opportunities": opportunities,
            "top_recommendations": opportunities[:3]
        }

    def _calculate_fit_score(self, use_case: Dict, company: CompanyProfile) -> float:
        """Use Case 적합도 점수 계산"""
        score = 50.0  # 기본 점수

        # 데이터 가용성
        if company.data_assets.data_volume_tb > 1:
            score += 10
        if company.data_assets.data_quality_score >= 3:
            score += 10

        # 인프라 준비도
        if company.it_infrastructure.has_cloud:
            score += 10
        if company.it_infrastructure.gpu_available:
            score += 5

        # 인력 역량
        if company.human_resources.data_scientist_count > 0:
            score += 10
        if company.human_resources.ai_experience_projects > 0:
            score += 5

        return min(score, 100)

    async def _plan_roadmap(self, company: CompanyProfile, use_cases: List[Dict]) -> Dict[str, Any]:
        """AI 도입 로드맵 수립"""
        roadmap = {
            "short_term": {
                "period": "0-6개월",
                "focus": "Quick Win",
                "activities": []
            },
            "mid_term": {
                "period": "6-18개월",
                "focus": "핵심 역량 구축",
                "activities": []
            },
            "long_term": {
                "period": "18-36개월",
                "focus": "비즈니스 혁신",
                "activities": []
            }
        }

        # Quick Win 과제 배치
        for uc in use_cases:
            if uc.get("priority") == "quick_win":
                roadmap["short_term"]["activities"].append(uc["name"])
            elif uc.get("priority") == "strategic":
                roadmap["mid_term"]["activities"].append(uc["name"])
            else:
                roadmap["long_term"]["activities"].append(uc["name"])

        return roadmap

    async def _general_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """일반 분석 태스크"""
        if self.llm_provider:
            prompt = task.get("query", "")
            context = task.get("context", {})
            response = await self.llm_provider.consult(prompt, context, "general")
            return {"analysis": response}
        return {"error": "LLM provider not configured"}

