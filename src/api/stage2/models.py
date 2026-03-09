"""
Stage 2 Pydantic Models
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List


class RequirementsInput(BaseModel):
    """상세 요건 정의 입력"""
    use_case_name: str = Field(default="", description="Use Case명")
    business_requirements: Dict[str, Any] = Field(default_factory=dict, description="비즈니스 요구사항")
    functional_requirements: Dict[str, Any] = Field(default_factory=dict, description="기능 요구사항")
    non_functional_requirements: Dict[str, Any] = Field(default_factory=dict, description="비기능 요구사항")
    data_requirements: Dict[str, Any] = Field(default_factory=dict, description="데이터 요구사항")
    constraints: List[str] = Field(default_factory=list, description="제약사항")
    success_criteria: List[str] = Field(default_factory=list, description="성공 기준")


class ArchitectureInput(BaseModel):
    """아키텍처 설계 입력"""
    data_architecture: Dict[str, Any] = Field(default_factory=dict, description="데이터 아키텍처")
    ml_architecture: Dict[str, Any] = Field(default_factory=dict, description="ML 아키텍처")
    tech_stack: Dict[str, Any] = Field(default_factory=dict, description="기술 스택")
    integration_points: List[str] = Field(default_factory=list, description="통합 지점")


class GovernanceInput(BaseModel):
    """거버넌스 체계 입력"""
    privacy: Dict[str, Any] = Field(default_factory=dict, description="프라이버시")
    ethics: Dict[str, Any] = Field(default_factory=dict, description="윤리")
    compliance: Dict[str, Any] = Field(default_factory=dict, description="컴플라이언스")
    notes: str = Field(default="", description="비고")

