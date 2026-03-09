"""
Stage 1 Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List


class MaturityAssessmentInput(BaseModel):
    """성숙도 진단 입력 - 유연한 구조"""
    strategy: Dict[str, Any] = Field(default_factory=dict, description="전략 영역")
    organization: Dict[str, Any] = Field(default_factory=dict, description="조직 영역")
    data_technology: Dict[str, Any] = Field(default_factory=dict, description="데이터/기술 영역")
    process: Dict[str, Any] = Field(default_factory=dict, description="프로세스 영역")
    notes: str = Field(default="", description="비고")


class OpportunityInput(BaseModel):
    """기회 발굴 입력"""
    name: str = Field(default="", description="기회명")
    description: str = Field(default="", description="설명")
    business_area: str = Field(default="", description="비즈니스 영역")
    priority_quadrant: str = Field(default="strategic", description="우선순위 사분면")
    expected_impact: str = Field(default="", description="기대 효과")
    implementation_difficulty: str = Field(default="", description="구현 난이도")
    estimated_timeline: str = Field(default="", description="예상 소요 기간")
    required_resources: str = Field(default="", description="필요 자원")
    data_availability: int = Field(default=3, description="데이터 가용성 (1-5)")
    urgency: int = Field(default=3, description="긴급도 (1-5)")
    strategic_alignment: int = Field(default=3, description="전략 정합성 (1-5)")


class OpportunityListInput(BaseModel):
    """기회 발굴 목록 입력"""
    opportunities: List[OpportunityInput] = Field(default_factory=list, description="기회 목록")


class RoadmapInput(BaseModel):
    """로드맵 입력"""
    vision: str = Field(default="", description="AI 비전 선언문")
    goals: List[Any] = Field(default_factory=list, description="전략적 목표")
    kpis: List[Any] = Field(default_factory=list, description="핵심 성과 지표")
    phases: List[Any] = Field(default_factory=list, description="단계별 계획")
