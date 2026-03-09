"""
Consulting Models - 컨설팅 프로젝트, 시나리오, 성숙도 진단 관련 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

from .enums import MaturityLevel, PriorityLevel, RiskLevel, ConsultingStage
from .company import CompanyProfile


class MaturityDimensionScore(BaseModel):
    """성숙도 영역별 점수"""
    dimension_id: str
    dimension_name: str
    current_level: MaturityLevel
    target_level: MaturityLevel
    gap: int = Field(default=0, description="Gap (목표 - 현재)")
    item_scores: Dict[str, int] = Field(default_factory=dict, description="세부 항목별 점수")
    recommendations: List[str] = Field(default_factory=list, description="개선 권고사항")


class MaturityAssessment(BaseModel):
    """AI 성숙도 진단 결과"""
    company_id: str
    assessment_date: datetime = Field(default_factory=datetime.now)

    # 영역별 점수
    strategy_score: MaturityDimensionScore
    organization_score: MaturityDimensionScore
    data_tech_score: MaturityDimensionScore
    process_score: MaturityDimensionScore

    # 종합
    overall_level: MaturityLevel
    overall_score: float = Field(description="종합 점수 (1-5)")
    key_strengths: List[str] = Field(default_factory=list)
    key_weaknesses: List[str] = Field(default_factory=list)
    priority_improvements: List[str] = Field(default_factory=list)


class UseCase(BaseModel):
    """AI 활용 사례"""
    id: Optional[str] = None
    name: str
    description: str
    business_area: str

    # 가치-실행 용이성 평가
    business_value_score: float = Field(ge=1, le=5, description="비즈니스 가치 (1-5)")
    feasibility_score: float = Field(ge=1, le=5, description="실행 용이성 (1-5)")
    priority: PriorityLevel = Field(default=PriorityLevel.RECONSIDER)

    # 세부 평가
    expected_roi: float = Field(default=0, description="예상 ROI (%)")
    implementation_cost: float = Field(default=0, description="구현 비용 (억원)")
    implementation_period: int = Field(default=6, description="구현 기간 (개월)")
    required_resources: Dict[str, Any] = Field(default_factory=dict)
    risks: List[str] = Field(default_factory=list)

    # 기술 요구사항
    required_data: List[str] = Field(default_factory=list)
    required_tech_stack: List[str] = Field(default_factory=list)
    integration_requirements: List[str] = Field(default_factory=list)


class ScenarioParameters(BaseModel):
    """시나리오 파라미터"""
    # 투자 관련
    investment_budget: float = Field(description="투자 예산 (억원)")
    timeline_months: int = Field(default=12, description="추진 기간 (개월)")

    # 리소스 할당
    internal_resource_ratio: float = Field(default=0.3, description="내부 자원 활용 비율")
    outsourcing_ratio: float = Field(default=0.7, description="외주 비율")

    # 전략 옵션
    risk_appetite: RiskLevel = Field(default=RiskLevel.MEDIUM)
    focus_areas: List[str] = Field(default_factory=list, description="집중 영역")

    # 우선순위 가중치
    roi_weight: float = Field(default=0.4, description="ROI 가중치")
    strategic_alignment_weight: float = Field(default=0.3, description="전략 정합성 가중치")
    feasibility_weight: float = Field(default=0.3, description="실현 가능성 가중치")


class Scenario(BaseModel):
    """컨설팅 시나리오"""
    id: Optional[str] = None
    name: str
    description: str
    scenario_type: str = Field(description="시나리오 유형 (conservative, balanced, aggressive)")

    parameters: ScenarioParameters
    selected_use_cases: List[UseCase] = Field(default_factory=list)

    # 예상 결과
    total_investment: float = Field(default=0, description="총 투자 비용")
    expected_total_roi: float = Field(default=0, description="예상 총 ROI")
    implementation_roadmap: Dict[str, List[str]] = Field(default_factory=dict)

    # 리스크 분석
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)
    mitigation_strategies: List[str] = Field(default_factory=list)

    # 평가
    overall_score: float = Field(default=0, description="종합 점수")
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)

    created_at: datetime = Field(default_factory=datetime.now)


class StageProgress(BaseModel):
    """단계별 진행 상황"""
    stage: ConsultingStage
    stage_name: str
    status: str = Field(default="not_started")  # not_started, in_progress, completed, on_hold
    progress_percent: float = Field(default=0, ge=0, le=100)
    activities_completed: List[str] = Field(default_factory=list)
    outputs_generated: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    next_actions: List[str] = Field(default_factory=list)


class HumanFeedback(BaseModel):
    """인간 전문가 피드백"""
    id: Optional[str] = None
    feedback_type: str  # approval, rejection, modification, question
    stage: ConsultingStage
    content: str
    reviewer_role: str  # manager, executive, specialist
    reviewer_name: str
    priority: str = Field(default="medium")

    # AI 응답
    ai_response: Optional[str] = None
    action_taken: Optional[str] = None

    created_at: datetime = Field(default_factory=datetime.now)
    resolved_at: Optional[datetime] = None


class ConsultingProject(BaseModel):
    """컨설팅 프로젝트"""
    id: Optional[str] = None
    name: str
    company: CompanyProfile

    # 진행 상황
    current_stage: ConsultingStage = Field(default=ConsultingStage.STRATEGY)
    stage_progress: List[StageProgress] = Field(default_factory=list)

    # 진단 결과
    maturity_assessment: Optional[MaturityAssessment] = None

    # 시나리오
    scenarios: List[Scenario] = Field(default_factory=list)
    selected_scenario: Optional[str] = None  # 선택된 시나리오 ID

    # 협업
    human_feedbacks: List[HumanFeedback] = Field(default_factory=list)
    pending_approvals: List[str] = Field(default_factory=list)

    # 산출물
    generated_reports: List[str] = Field(default_factory=list)

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None
    status: str = Field(default="active")  # active, completed, on_hold, cancelled

