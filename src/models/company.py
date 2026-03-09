"""
Company Models - 기업 프로필 관련 모델
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from .enums import IndustryType, CompanySize


class ITInfrastructure(BaseModel):
    """IT 인프라 현황"""
    has_cloud: bool = Field(default=False, description="클라우드 환경 보유 여부")
    cloud_provider: Optional[str] = Field(default=None, description="클라우드 제공자 (AWS, GCP, Azure 등)")
    has_data_warehouse: bool = Field(default=False, description="데이터 웨어하우스 보유 여부")
    has_data_lake: bool = Field(default=False, description="데이터 레이크 보유 여부")
    server_count: int = Field(default=0, description="서버 수")
    gpu_available: bool = Field(default=False, description="GPU 서버 보유 여부")
    legacy_system_count: int = Field(default=0, description="레거시 시스템 수")
    api_capability: bool = Field(default=False, description="API 연동 가능 여부")
    security_level: str = Field(default="basic", description="보안 수준")


class DataAssets(BaseModel):
    """데이터 자산 현황"""
    data_volume_tb: float = Field(default=0, description="데이터 총량 (TB)")
    structured_ratio: float = Field(default=0.5, description="정형 데이터 비율")
    data_quality_score: float = Field(default=3.0, description="데이터 품질 점수 (1-5)")
    has_data_governance: bool = Field(default=False, description="데이터 거버넌스 체계 보유")
    data_sources: List[str] = Field(default_factory=list, description="데이터 소스 목록")
    historical_data_years: int = Field(default=0, description="축적된 히스토리 데이터 기간 (년)")


class HumanResources(BaseModel):
    """인적 자원 현황"""
    total_employees: int = Field(default=0, description="총 직원 수")
    it_staff_count: int = Field(default=0, description="IT 인력 수")
    data_scientist_count: int = Field(default=0, description="데이터 사이언티스트 수")
    ml_engineer_count: int = Field(default=0, description="ML 엔지니어 수")
    data_engineer_count: int = Field(default=0, description="데이터 엔지니어 수")
    ai_experience_projects: int = Field(default=0, description="AI 프로젝트 경험 수")
    training_budget_ratio: float = Field(default=0, description="교육 예산 비율 (%)")


class FinancialResources(BaseModel):
    """재무 자원"""
    annual_revenue_billion: float = Field(default=0, description="연 매출 (억원)")
    it_budget_ratio: float = Field(default=0, description="IT 예산 비율 (%)")
    ai_investment_budget: float = Field(default=0, description="AI 투자 가능 예산 (억원)")
    roi_expectation_period: int = Field(default=24, description="ROI 기대 기간 (개월)")


class OrganizationalReadiness(BaseModel):
    """조직 준비도"""
    executive_support: int = Field(default=3, ge=1, le=5, description="경영진 지원도 (1-5)")
    change_management_capability: int = Field(default=3, ge=1, le=5, description="변화 관리 역량 (1-5)")
    innovation_culture: int = Field(default=3, ge=1, le=5, description="혁신 문화 수준 (1-5)")
    cross_functional_collaboration: int = Field(default=3, ge=1, le=5, description="부서간 협업 수준 (1-5)")
    risk_tolerance: int = Field(default=3, ge=1, le=5, description="리스크 허용도 (1-5)")


class CompanyProfile(BaseModel):
    """기업 프로필 (종합)"""
    id: Optional[str] = None
    name: str = Field(..., description="기업명")
    industry: IndustryType = Field(..., description="산업 분류")
    company_size: CompanySize = Field(..., description="기업 규모")
    business_description: str = Field(default="", description="사업 개요")

    # 세부 리소스
    it_infrastructure: ITInfrastructure = Field(default_factory=ITInfrastructure)
    data_assets: DataAssets = Field(default_factory=DataAssets)
    human_resources: HumanResources = Field(default_factory=HumanResources)
    financial_resources: FinancialResources = Field(default_factory=FinancialResources)
    organizational_readiness: OrganizationalReadiness = Field(default_factory=OrganizationalReadiness)

    # 메타데이터
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

