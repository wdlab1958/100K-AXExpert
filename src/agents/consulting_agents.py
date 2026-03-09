"""
AI Consulting Assistant Platform - Consulting Agents
5단계 컨설팅 프레임워크를 위한 전문 에이전트들
"""
from typing import Optional, List, Dict, Any
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.agents.base_agent import BaseConsultingAgent, AgentMessage
from src.models.schemas import (
    CompanyProfile, MaturityAssessment, MaturityDimensionScore,
    MaturityLevel, UseCase, PriorityLevel, Scenario, ScenarioParameters,
    RiskLevel, ConsultingStage
)
from config.settings import MATURITY_MODEL, INDUSTRY_TEMPLATES
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


class UseCaseDesignerAgent(BaseConsultingAgent):
    """2단계: Use Case 설계자 에이전트
    상세 요건 정의, 기술 아키텍처 설계, 거버넌스 체계 수립
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="use_case_designer",
            name="Use Case 설계자",
            role="Use Case Designer",
            description="AI Use Case의 상세 요건을 정의하고, 기술 아키텍처를 설계하며, 거버넌스 체계를 수립합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 솔루션 설계 전문가입니다.

[전문 영역]
1. AI Use Case 상세 요건 정의 (비즈니스 목표, 성공 기준, 데이터 요구사항)
2. 기술 아키텍처 설계 (데이터 파이프라인, MLOps, 모델 서빙)
3. AI 거버넌스 및 윤리 체계 수립

[설계 원칙]
- 비즈니스 요구사항과 기술 구현의 정합성 확보
- 확장성과 유지보수성을 고려한 아키텍처
- 보안, 프라이버시, 윤리적 고려사항 반영
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 설계 태스크 실행"""
        task_type = task.get("type", "design")

        if task_type == "requirements_definition":
            return await self._define_requirements(task.get("use_case"))
        elif task_type == "architecture_design":
            return await self._design_architecture(task.get("use_case"), task.get("requirements"))
        elif task_type == "governance_setup":
            return await self._setup_governance(task.get("use_case"))
        else:
            return await self._general_design(task)

    async def _define_requirements(self, use_case: Dict[str, Any]) -> Dict[str, Any]:
        """상세 요건 정의"""
        requirements = {
            "business_requirements": {
                "objectives": [],
                "success_criteria": [],
                "kpis": []
            },
            "functional_requirements": {
                "input_data": [],
                "output_format": [],
                "processing_logic": []
            },
            "non_functional_requirements": {
                "performance": {
                    "response_time_ms": 1000,
                    "throughput": "100 req/sec",
                    "availability": "99.9%"
                },
                "scalability": "horizontal",
                "security": []
            },
            "data_requirements": {
                "required_data_sources": [],
                "data_volume": "",
                "data_quality_criteria": []
            },
            "integration_requirements": []
        }

        if self.llm_provider:
            prompt = f"""다음 AI Use Case에 대한 상세 요건을 정의해주세요:
Use Case: {json.dumps(use_case, ensure_ascii=False)}

요건 정의 항목:
1. 비즈니스 목표 및 성공 기준
2. 기능 요구사항 (입력, 출력, 처리 로직)
3. 비기능 요구사항 (성능, 확장성, 보안)
4. 데이터 요구사항
5. 통합 요구사항"""

            response = await self.llm_provider.generate(prompt, self.get_system_prompt())
            requirements["llm_analysis"] = response

        return requirements

    async def _design_architecture(self, use_case: Dict, requirements: Dict) -> Dict[str, Any]:
        """기술 아키텍처 설계"""
        architecture = {
            "layers": {
                "data_layer": {
                    "components": ["Data Lake/Warehouse", "Feature Store", "Data Pipeline"],
                    "technologies": ["Apache Spark", "Delta Lake", "Airflow"]
                },
                "ml_layer": {
                    "components": ["Model Training", "Experiment Tracking", "Model Registry"],
                    "technologies": ["PyTorch/TensorFlow", "MLflow", "Kubeflow"]
                },
                "serving_layer": {
                    "components": ["Model Serving", "API Gateway", "Load Balancer"],
                    "technologies": ["TorchServe/Triton", "Kong", "Kubernetes"]
                },
                "monitoring_layer": {
                    "components": ["Performance Monitoring", "Drift Detection", "Alerting"],
                    "technologies": ["Prometheus", "Grafana", "Evidently AI"]
                }
            },
            "data_flow": [],
            "deployment_topology": "",
            "security_architecture": []
        }

        return architecture

    async def _setup_governance(self, use_case: Dict) -> Dict[str, Any]:
        """거버넌스 체계 수립"""
        governance = {
            "organization": {
                "governance_committee": True,
                "roles": ["AI Model Owner", "Data Steward", "Ethics Officer"]
            },
            "policies": {
                "data_privacy": [],
                "model_validation": [],
                "deployment_approval": []
            },
            "processes": {
                "bias_review": "모델 개발 전 데이터 편향성 평가 필수",
                "explainability": "XAI 기법 적용 의무화",
                "audit_trail": "모든 의사결정 기록 및 추적"
            },
            "risk_management": {
                "risk_classification": ["저", "중", "고"],
                "mitigation_strategies": [],
                "fallback_plan": "Human-in-the-Loop 체계 구축"
            }
        }

        return governance

    async def _general_design(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """일반 설계 태스크"""
        if self.llm_provider:
            prompt = task.get("query", "")
            context = task.get("context", {})
            response = await self.llm_provider.consult(prompt, context, "architecture_design")
            return {"design": response}
        return {"error": "LLM provider not configured"}


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

        # 비용 구성
        costs = {
            "initial_investment": investment,
            "annual_operation": investment * 0.15,  # 연간 운영비 15%
            "annual_maintenance": investment * 0.10,  # 연간 유지보수 10%
            "total_3year": investment + (investment * 0.25 * 3)
        }

        # 효과 추정
        annual_benefits = sum(benefits.values()) if benefits else investment * 0.5

        # ROI 지표 계산
        roi_metrics = {
            "roi_percent": ((annual_benefits * 3 - costs["total_3year"]) / costs["total_3year"]) * 100,
            "payback_months": costs["initial_investment"] / (annual_benefits / 12) if annual_benefits > 0 else float('inf'),
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


class ReportGeneratorAgent(BaseConsultingAgent):
    """보고서 생성 에이전트
    컨설팅 결과 보고서 작성
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="report_generator",
            name="보고서 생성 전문가",
            role="Report Generator",
            description="컨설팅 결과를 종합하여 전문적인 보고서를 생성합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 컨설팅 보고서 작성 전문가입니다.

[전문 영역]
1. 경영진용 Executive Summary 작성
2. 기술 보고서 작성
3. 전략 제안서 작성
4. 실행 로드맵 문서화

[작성 원칙]
- 명확하고 간결한 문장
- 데이터 기반의 객관적 서술
- 핵심 메시지의 명확한 전달
- 전문적이면서도 이해하기 쉬운 표현
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """보고서 생성 태스크 실행"""
        report_type = task.get("report_type", "summary")

        if report_type == "executive_summary":
            return await self._generate_executive_summary(task)
        elif report_type == "full_report":
            return await self._generate_full_report(task)
        elif report_type == "strategy_proposal":
            return await self._generate_strategy_proposal(task)
        else:
            return await self._generate_custom_report(task)

    async def _generate_executive_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executive Summary 생성"""
        data = task.get("data", {})

        summary = {
            "title": "AI 컨설팅 Executive Summary",
            "sections": [
                {
                    "title": "프로젝트 개요",
                    "content": data.get("overview", "")
                },
                {
                    "title": "현황 진단 결과",
                    "content": self._summarize_assessment(data.get("assessment", {}))
                },
                {
                    "title": "핵심 제안",
                    "content": data.get("recommendations", [])
                },
                {
                    "title": "예상 효과",
                    "content": data.get("expected_benefits", {})
                },
                {
                    "title": "실행 로드맵",
                    "content": data.get("roadmap", {})
                }
            ]
        }

        return summary

    def _summarize_assessment(self, assessment: Dict) -> str:
        """진단 결과 요약"""
        if not assessment:
            return "진단 데이터가 없습니다."

        level = assessment.get("overall_level", "N/A")
        return f"AI 성숙도 Level {level}. 주요 개선 영역 식별 완료."

    async def _generate_full_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전체 보고서 생성"""
        data = task.get("data", {})

        report = {
            "title": "AI 인프라 도입 컨설팅 종합 보고서",
            "version": "1.0",
            "chapters": [
                {
                    "number": 1,
                    "title": "개요",
                    "sections": ["배경 및 목적", "프로젝트 범위", "추진 경과"]
                },
                {
                    "number": 2,
                    "title": "현황 분석",
                    "sections": ["AI 성숙도 진단", "IT 인프라 분석", "조직 역량 분석", "데이터 자산 분석"]
                },
                {
                    "number": 3,
                    "title": "AI 전략 수립",
                    "sections": ["AI 비전", "핵심 Use Case", "우선순위 결정"]
                },
                {
                    "number": 4,
                    "title": "실행 계획",
                    "sections": ["로드맵", "투자 계획", "조직 및 인력 계획"]
                },
                {
                    "number": 5,
                    "title": "기대 효과",
                    "sections": ["정량적 효과", "정성적 효과", "ROI 분석"]
                },
                {
                    "number": 6,
                    "title": "리스크 관리",
                    "sections": ["리스크 식별", "완화 전략"]
                }
            ],
            "appendices": ["용어 정의", "산출물 템플릿", "참고 자료"]
        }

        return report

    async def _generate_strategy_proposal(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전략 제안서 생성"""
        data = task.get("data", {})

        proposal = {
            "title": "AI 전환 전략 제안서",
            "sections": [
                {"title": "전략적 배경", "content": ""},
                {"title": "현황 분석 요약", "content": ""},
                {"title": "제안 전략", "content": ""},
                {"title": "실행 방안", "content": ""},
                {"title": "소요 자원", "content": ""},
                {"title": "기대 효과", "content": ""},
                {"title": "Next Steps", "content": ""}
            ]
        }

        return proposal

    async def _generate_custom_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """커스텀 보고서 생성"""
        if self.llm_provider:
            prompt = f"""다음 데이터를 기반으로 보고서를 작성해주세요:
{json.dumps(task.get('data', {}), ensure_ascii=False, indent=2)}

보고서 형식: {task.get('format', 'general')}
"""
            response = await self.llm_provider.generate(prompt, self.get_system_prompt())
            return {"report_content": response}

        return {"error": "LLM provider not configured"}
