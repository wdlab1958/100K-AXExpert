"""
Stage 3 Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List


class PoCInput(BaseModel):
    """PoC 계획 입력"""
    poc_name: str = Field(default="", description="PoC 명")
    objectives: str = Field(default="", description="목표")
    scope: str = Field(default="", description="범위")
    success_metrics: str = Field(default="", description="성공 지표")
    timeline: str = Field(default="", description="일정")
    resources: str = Field(default="", description="필요 리소스")
    risks: str = Field(default="", description="리스크")


class PlatformInput(BaseModel):
    """플랫폼 구축 계획 입력"""
    components: Dict[str, Any] = Field(default_factory=dict, description="플랫폼 구성요소")
    infrastructure: str = Field(default="", description="인프라")
    security_config: str = Field(default="", description="보안 설정")
    scalability_plan: str = Field(default="", description="확장성 계획")


class IntegrationInput(BaseModel):
    """통합 설정 입력"""
    target_systems: str = Field(default="", description="대상 시스템")
    api_specifications: str = Field(default="", description="API 명세")
    data_flow: str = Field(default="", description="데이터 흐름")
    testing_plan: str = Field(default="", description="테스트 계획")

