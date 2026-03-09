"""
Stage 4 Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List


class PilotInput(BaseModel):
    """파일럿 계획 입력"""
    pilot_name: str = Field(default="", description="파일럿 명")
    target_department: str = Field(default="", description="대상 부서")
    pilot_scope: str = Field(default="", description="범위")
    duration: str = Field(default="", description="기간")
    success_criteria: str = Field(default="", description="성공 기준")
    support_plan: str = Field(default="", description="지원 계획")


class ChangeManagementInput(BaseModel):
    """변화 관리 계획 입력"""
    awareness: Dict[str, Any] = Field(default_factory=dict, description="인식 제고")
    capability: Dict[str, Any] = Field(default_factory=dict, description="역량 강화")
    engagement: Dict[str, Any] = Field(default_factory=dict, description="참여 유도")
    success_sharing: Dict[str, Any] = Field(default_factory=dict, description="성과 공유")
    notes: str = Field(default="", description="비고")


class ScaleInput(BaseModel):
    """확산 계획 입력"""
    rollout_phases: List[Any] = Field(default_factory=list, description="단계별 롤아웃")
    target_coverage: str = Field(default="", description="목표 커버리지")
    timeline: str = Field(default="", description="일정")
    resource_plan: str = Field(default="", description="자원 계획")
    risk_mitigation: str = Field(default="", description="리스크 완화")

