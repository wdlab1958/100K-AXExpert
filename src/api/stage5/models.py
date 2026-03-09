"""
Stage 5 Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any


class MonitoringInput(BaseModel):
    """모니터링 설정 입력"""
    metrics: Dict[str, Any] = Field(default_factory=dict, description="모니터링 지표")
    alert_thresholds: str = Field(default="", description="알림 임계값")
    dashboard_config: str = Field(default="", description="대시보드 설정")
    reporting_frequency: str = Field(default="", description="보고 주기")


class ImprovementInput(BaseModel):
    """개선 계획 입력"""
    improvement_cycle: str = Field(default="", description="개선 사이클")
    feedback_sources: str = Field(default="", description="피드백 소스")
    prioritization_criteria: str = Field(default="", description="우선순위 기준")
    experiment_framework: str = Field(default="", description="실험 프레임워크")
    success_metrics: str = Field(default="", description="성공 지표")


class GovernanceReviewInput(BaseModel):
    """거버넌스 검토 입력"""
    review_frequency: str = Field(default="", description="검토 주기")
    review_scope: str = Field(default="", description="검토 범위")
    audit_checklist: str = Field(default="", description="감사 체크리스트")
    compliance_updates: str = Field(default="", description="규제 업데이트")
    policy_revisions: str = Field(default="", description="정책 개정")

