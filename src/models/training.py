"""
100K-AX Expert Platform - AX Training & Certification Data Models
Phase 2: AX 전문가 양성 모듈 데이터 모델
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel, Field


# ============================================================
# 전문가 인증 등급
# ============================================================
class CertificationLevel(str, Enum):
    """AX 전문가 인증 5등급 체계"""
    BEGINNER = "AX Beginner"
    PRACTITIONER = "AX Practitioner"
    SPECIALIST = "AX Specialist"
    EXPERT = "AX Expert"
    MASTER = "AX Master"


class DXtoAXLevel(int, Enum):
    """DX-to-AX 전환 레벨"""
    MANUAL = 0          # 수기 작업, 엑셀, 경험 의존
    DIGITAL = 1         # 전산화, 시스템 도입, 표준화
    DATA_DRIVEN = 2     # 데이터 기반 의사결정
    AI_AUGMENTED = 3    # AI 보조 의사결정, 자동화
    AUTONOMOUS = 4      # AI 자율 운영, 지속 학습


class TaskStatus(str, Enum):
    """AX 과제 상태"""
    DISCOVERED = "discovered"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ROI_ACHIEVED = "roi_achieved"
    CANCELLED = "cancelled"


# ============================================================
# AX 과제 모델
# ============================================================
class AXTask(BaseModel):
    """개별 AX 과제"""
    task_id: str = Field(default="", description="과제 고유 ID")
    title: str = Field(..., description="과제명")
    department: str = Field(..., description="대상 부서")
    description: str = Field(default="", description="과제 설명")
    domain: str = Field(default="manufacturing", description="산업 도메인")
    dx_level_before: int = Field(default=0, description="전환 전 DX 레벨")
    dx_level_after: Optional[int] = Field(default=None, description="전환 후 DX 레벨")
    status: TaskStatus = Field(default=TaskStatus.DISCOVERED)
    roi_potential: float = Field(default=0.0, description="예상 ROI (%)")
    roi_achieved: Optional[float] = Field(default=None, description="달성 ROI (%)")
    investment_cost: float = Field(default=0.0, description="투자 비용 (만원)")
    annual_saving: float = Field(default=0.0, description="연간 절감 (만원)")
    complexity: str = Field(default="medium", description="구현 난이도 (low/medium/high)")
    started_at: Optional[str] = Field(default=None)
    completed_at: Optional[str] = Field(default=None)
    consulting_report_id: Optional[str] = Field(default=None)


class AXTaskCreate(BaseModel):
    """AX 과제 생성 요청"""
    title: str
    department: str
    description: str = ""
    domain: str = "manufacturing"
    complexity: str = "medium"
    roi_potential: float = 0.0
    investment_cost: float = 0.0


# ============================================================
# 역량 모델
# ============================================================
class SkillRadar(BaseModel):
    """역량 레이더 차트 데이터"""
    ax_discovery: float = Field(default=0.0, ge=0, le=100, description="AX 기회 발굴")
    roi_analysis: float = Field(default=0.0, ge=0, le=100, description="ROI 분석")
    risk_assessment: float = Field(default=0.0, ge=0, le=100, description="리스크 평가")
    implementation: float = Field(default=0.0, ge=0, le=100, description="구현 설계")
    change_management: float = Field(default=0.0, ge=0, le=100, description="변화 관리")
    report_generation: float = Field(default=0.0, ge=0, le=100, description="보고서 작성")


class GrowthPoint(BaseModel):
    """역량 성장 이력 포인트"""
    date: str
    level: str
    total_tasks: int
    roi_tasks: int
    skill_score: float
    event: str = ""


# ============================================================
# 학습 진도 모델
# ============================================================
class TrainingProgress(BaseModel):
    """실무자별 AX 학습 진도"""
    user_id: str = Field(..., description="실무자 ID")
    user_name: str = Field(default="", description="실무자명")
    company_id: str = Field(default="", description="기업 ID")
    company_name: str = Field(default="", description="기업명")
    department: str = Field(default="", description="소속 부서")
    domain: str = Field(default="manufacturing", description="산업 도메인")
    current_level: CertificationLevel = Field(default=CertificationLevel.BEGINNER)
    total_tasks_completed: int = Field(default=0, description="총 완료 AX 과제 수")
    roi_achieved_tasks: int = Field(default=0, description="ROI 달성 과제 수")
    dept_conversion_rate: float = Field(default=0.0, description="부서 AX 전환율")
    external_consulting: bool = Field(default=False, description="외부 컨설팅 경험")
    skill_radar: SkillRadar = Field(default_factory=SkillRadar)
    growth_history: list[GrowthPoint] = Field(default_factory=list)
    badges: list[str] = Field(default_factory=list)
    tasks: list[AXTask] = Field(default_factory=list)
    registered_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    last_activity: str = Field(default_factory=lambda: datetime.now().isoformat())


class TrainingProgressSummary(BaseModel):
    """학습 진도 요약"""
    user_id: str
    user_name: str
    current_level: str
    total_tasks: int
    roi_tasks: int
    conversion_rate: float
    skill_score: float
    next_level: str
    next_level_gap: dict


# ============================================================
# 부서 AX 현황
# ============================================================
class DepartmentAXStatus(BaseModel):
    """부서별 AX 전환 현황"""
    department: str
    company_id: str
    total_processes: int = Field(default=0, description="전체 업무 프로세스 수")
    ax_converted: int = Field(default=0, description="AX 전환 완료 수")
    conversion_rate: float = Field(default=0.0, description="AX 전환율")
    avg_dx_level: float = Field(default=0.0, description="평균 DX 레벨")
    total_tasks: int = Field(default=0)
    completed_tasks: int = Field(default=0)
    total_roi_saving: float = Field(default=0.0, description="총 ROI 절감액 (만원)")
    experts_count: dict = Field(default_factory=lambda: {
        "beginner": 0, "practitioner": 0, "specialist": 0, "expert": 0, "master": 0
    })


# ============================================================
# 기업 AX 성과 대시보드
# ============================================================
class EnterpriseAXDashboard(BaseModel):
    """기업 전체 AX 성과 대시보드"""
    company_id: str
    company_name: str
    total_employees_trained: int = Field(default=0)
    total_departments: int = Field(default=0)
    total_tasks_completed: int = Field(default=0)
    total_roi_achieved: float = Field(default=0.0, description="총 ROI 달성액 (만원)")
    avg_conversion_rate: float = Field(default=0.0)
    avg_dx_level: float = Field(default=0.0)
    certification_distribution: dict = Field(default_factory=lambda: {
        "beginner": 0, "practitioner": 0, "specialist": 0, "expert": 0, "master": 0
    })
    department_statuses: list[DepartmentAXStatus] = Field(default_factory=list)
    top_roi_tasks: list[AXTask] = Field(default_factory=list)
    growth_trend: list[dict] = Field(default_factory=list)
