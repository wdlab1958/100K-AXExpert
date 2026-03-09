"""
100K-AX Expert Platform - AX Discovery Service
Phase 1: 업무 프로세스 분석 → AX 기회 자동 식별
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

import uuid
import logging
from datetime import datetime
from src.models.ax_discovery import (
    BusinessProcess, AXOpportunity, AXDiscoveryRequest, AXDiscoveryResult,
    DEPARTMENT_AX_TEMPLATES
)

logger = logging.getLogger("ax_discovery")


class AXDiscoveryService:
    """AX 기회 발굴 서비스 - 업무 프로세스를 분석하여 AX 기회를 자동 식별"""

    # ROI 잠재력 계산 가중치
    WEIGHTS = {
        "roi_potential": 0.30,
        "implementation_ease": 0.25,
        "data_readiness": 0.25,
        "org_readiness": 0.20,
    }

    # 복잡도별 기본 투자비 (만원)
    COMPLEXITY_COST = {
        "low": 3000,
        "medium": 8000,
        "high": 20000,
    }

    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider

    async def discover_opportunities(self, request: AXDiscoveryRequest) -> AXDiscoveryResult:
        """전체 AX 기회 발굴 파이프라인 실행"""
        result = AXDiscoveryResult(
            request_id=str(uuid.uuid4())[:8],
            company_id=request.company_id,
            department=request.department,
            domain=request.domain,
            total_processes_analyzed=len(request.processes),
        )

        # 1. 입력된 프로세스 분석
        opportunities = []
        for process in request.processes:
            opps = await self._analyze_process(process, request.domain)
            opportunities.extend(opps)

        # 2. 부서 템플릿 기반 추가 기회 발굴
        template_opps = self._discover_from_templates(request.department, request.domain)
        opportunities.extend(template_opps)

        # 3. 종합 점수 계산 및 정렬
        for opp in opportunities:
            opp.overall_score = self._calculate_overall_score(opp)
        opportunities.sort(key=lambda x: x.overall_score, reverse=True)

        # 4. 예산 한도 적용
        if request.budget_limit > 0:
            filtered = []
            total_inv = 0
            for opp in opportunities:
                if total_inv + opp.estimated_investment <= request.budget_limit:
                    filtered.append(opp)
                    total_inv += opp.estimated_investment
            opportunities = filtered

        result.opportunities = opportunities
        result.estimated_total_saving = sum(o.estimated_saving for o in opportunities)
        result.estimated_total_investment = sum(o.estimated_investment for o in opportunities)
        result.top_recommendations = [o.title for o in opportunities[:5]]
        result.department_dx_level = self._assess_dept_dx_level(request.processes)
        result.summary = self._generate_summary(result)

        logger.info(f"AX Discovery 완료: {len(opportunities)}건 기회 발굴 ({request.department})")
        return result

    async def _analyze_process(self, process: BusinessProcess, domain: str) -> list[AXOpportunity]:
        """개별 프로세스 AX 기회 분석"""
        opportunities = []

        # 현재 수행 방법 기반 AX 가능성 평가
        if process.current_method in ("manual", "수기", "엑셀"):
            opp = self._create_opportunity_from_process(process, domain, "자동화")
            opp.roi_potential_score = min(90, process.annual_cost / 500 * 10 + 40)
            opp.target_dx_level = 2
            opportunities.append(opp)

        if process.error_rate > 3.0:
            opp = self._create_opportunity_from_process(process, domain, "AI 품질 개선")
            opp.roi_potential_score = min(95, process.error_rate * 10 + 30)
            opp.target_dx_level = 3
            opportunities.append(opp)

        if process.staff_involved >= 3 and process.data_available:
            opp = self._create_opportunity_from_process(process, domain, "AI 의사결정 지원")
            opp.roi_potential_score = min(85, process.staff_involved * 15 + 20)
            opp.target_dx_level = 3
            opportunities.append(opp)

        if process.data_available and process.data_volume in ("medium", "high"):
            opp = self._create_opportunity_from_process(process, domain, "예측 분석")
            opp.roi_potential_score = 70 if process.data_volume == "high" else 55
            opp.target_dx_level = 3
            opportunities.append(opp)

        # 각 기회에 세부 점수 산출
        for opp in opportunities:
            opp.implementation_ease_score = self._score_implementation_ease(process, opp)
            opp.data_readiness_score = self._score_data_readiness(process)
            opp.org_readiness_score = self._score_org_readiness(process)
            opp.estimated_investment = self._estimate_investment(opp)
            opp.estimated_saving = self._estimate_saving(process, opp)
            opp.estimated_roi = (
                (opp.estimated_saving / opp.estimated_investment * 100)
                if opp.estimated_investment > 0 else 0
            )
            opp.payback_months = (
                (opp.estimated_investment / opp.estimated_saving * 12)
                if opp.estimated_saving > 0 else 999
            )

        return opportunities

    def _create_opportunity_from_process(
        self, process: BusinessProcess, domain: str, ax_type: str
    ) -> AXOpportunity:
        """프로세스 기반 AX 기회 생성"""
        return AXOpportunity(
            opportunity_id=str(uuid.uuid4())[:8],
            process=process,
            title=f"{process.name} {ax_type}",
            description=f"{process.name} 업무의 {ax_type}를 통한 효율성 향상",
            ax_approach=ax_type,
            complexity="medium",
            required_tech=self._suggest_tech(ax_type, domain),
            required_data=[f"{process.name} 관련 데이터"],
        )

    def _discover_from_templates(self, department: str, domain: str) -> list[AXOpportunity]:
        """부서 템플릿 기반 AX 기회 자동 발굴"""
        templates = DEPARTMENT_AX_TEMPLATES.get(department, [])
        opportunities = []

        for tmpl in templates:
            roi_map = {"낮음": 40, "중간": 60, "높음": 80, "매우 높음": 95}
            dummy_process = BusinessProcess(
                name=tmpl["title"], department=department,
                description=f"{department} - {tmpl['title']}",
                data_available=True, data_volume="medium",
            )
            opp = AXOpportunity(
                opportunity_id=str(uuid.uuid4())[:8],
                process=dummy_process,
                title=tmpl["title"],
                description=f"{department}의 {tmpl['title']} AX 전환",
                ax_approach="AI/ML 기반 자동화 및 최적화",
                complexity=tmpl["complexity"],
                roi_potential_score=roi_map.get(tmpl.get("roi_range", "중간"), 60),
                implementation_ease_score=85 if tmpl["complexity"] == "low" else (65 if tmpl["complexity"] == "medium" else 45),
                data_readiness_score=65,
                org_readiness_score=60,
                estimated_investment=self.COMPLEXITY_COST.get(tmpl["complexity"], 8000),
                required_tech=self._suggest_tech(tmpl["title"], domain),
                priority="high" if roi_map.get(tmpl.get("roi_range"), 0) >= 80 else "medium",
            )
            opp.estimated_saving = opp.estimated_investment * (opp.roi_potential_score / 100) * 1.2
            opp.estimated_roi = opp.estimated_saving / opp.estimated_investment * 100 if opp.estimated_investment > 0 else 0
            opp.payback_months = opp.estimated_investment / opp.estimated_saving * 12 if opp.estimated_saving > 0 else 999
            opp.overall_score = self._calculate_overall_score(opp)
            opportunities.append(opp)

        return opportunities

    def _calculate_overall_score(self, opp: AXOpportunity) -> float:
        """종합 AX 적합도 점수 계산"""
        return round(
            opp.roi_potential_score * self.WEIGHTS["roi_potential"]
            + opp.implementation_ease_score * self.WEIGHTS["implementation_ease"]
            + opp.data_readiness_score * self.WEIGHTS["data_readiness"]
            + opp.org_readiness_score * self.WEIGHTS["org_readiness"],
            1
        )

    def _score_implementation_ease(self, process: BusinessProcess, opp: AXOpportunity) -> float:
        """구현 용이성 점수"""
        base = {"low": 85, "medium": 60, "high": 35}.get(opp.complexity, 60)
        if process.data_available:
            base += 10
        return min(100, base)

    def _score_data_readiness(self, process: BusinessProcess) -> float:
        """데이터 준비도 점수"""
        score = 30
        if process.data_available:
            score += 30
        volume_bonus = {"low": 10, "medium": 25, "high": 40}.get(process.data_volume, 10)
        score += volume_bonus
        return min(100, score)

    def _score_org_readiness(self, process: BusinessProcess) -> float:
        """조직 준비도 점수"""
        score = 50
        if process.staff_involved >= 3:
            score += 15
        if process.frequency in ("daily", "hourly"):
            score += 10
        return min(100, score)

    def _estimate_investment(self, opp: AXOpportunity) -> float:
        """투자비 추정"""
        return self.COMPLEXITY_COST.get(opp.complexity, 8000)

    def _estimate_saving(self, process: BusinessProcess, opp: AXOpportunity) -> float:
        """연간 절감 추정"""
        base_saving = process.annual_cost * 0.3
        if opp.ax_approach == "자동화":
            base_saving = process.annual_cost * 0.5
        elif "품질" in opp.ax_approach:
            base_saving = process.annual_cost * 0.25 + process.error_rate * 500
        elif "예측" in opp.ax_approach:
            base_saving = process.annual_cost * 0.2
        return round(max(base_saving, 500), 0)

    def _suggest_tech(self, task_title: str, domain: str) -> list[str]:
        """기술 스택 제안"""
        tech_map = {
            "비전": ["Computer Vision", "YOLO", "OpenCV"],
            "예측": ["XGBoost", "LSTM", "Prophet"],
            "최적화": ["Optimization", "Reinforcement Learning"],
            "분석": ["NLP", "Transformer", "RAG"],
            "자동화": ["RPA", "Workflow Automation", "API Integration"],
            "챗봇": ["LLM", "RAG", "Langchain"],
            "검사": ["Computer Vision", "Anomaly Detection"],
        }
        techs = ["Python", "FastAPI"]
        for keyword, stack in tech_map.items():
            if keyword in task_title:
                techs.extend(stack)
                break
        return techs[:5]

    def _assess_dept_dx_level(self, processes: list[BusinessProcess]) -> float:
        """부서 평균 DX 레벨 평가"""
        if not processes:
            return 0.0
        level_map = {"manual": 0, "수기": 0, "엑셀": 0.5, "시스템": 1, "반자동": 1.5, "자동화": 2}
        levels = [level_map.get(p.current_method, 0.5) for p in processes]
        return round(sum(levels) / len(levels), 1)

    def _generate_summary(self, result: AXDiscoveryResult) -> str:
        """결과 요약 생성"""
        return (
            f"{result.department} 부서에서 총 {len(result.opportunities)}건의 AX 기회를 발굴하였습니다. "
            f"예상 총 연간 절감액은 {result.estimated_total_saving:,.0f}만원이며, "
            f"예상 총 투자비는 {result.estimated_total_investment:,.0f}만원입니다. "
            f"현재 부서 DX 수준은 Level {result.department_dx_level}입니다. "
            f"상위 추천 과제: {', '.join(result.top_recommendations[:3])}"
        )


# 싱글톤 인스턴스
_discovery_service: AXDiscoveryService | None = None


def get_ax_discovery_service(llm_provider=None) -> AXDiscoveryService:
    global _discovery_service
    if _discovery_service is None:
        _discovery_service = AXDiscoveryService(llm_provider)
    return _discovery_service
