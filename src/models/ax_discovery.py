"""
100K-AX Expert Platform - AX Discovery Data Models
Phase 1: AX 기회 발굴 모듈 데이터 모델
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from typing import Optional
from pydantic import BaseModel, Field


class BusinessProcess(BaseModel):
    """업무 프로세스 정의"""
    process_id: str = Field(default="", description="프로세스 ID")
    name: str = Field(..., description="프로세스명")
    department: str = Field(..., description="소속 부서")
    description: str = Field(default="", description="프로세스 설명")
    current_method: str = Field(default="manual", description="현재 수행 방법")
    pain_points: list[str] = Field(default_factory=list, description="페인포인트 목록")
    data_available: bool = Field(default=False, description="데이터 수집 가능 여부")
    data_volume: str = Field(default="low", description="데이터 양 (low/medium/high)")
    frequency: str = Field(default="daily", description="수행 빈도")
    staff_involved: int = Field(default=1, description="투입 인력 수")
    annual_cost: float = Field(default=0.0, description="연간 비용 (만원)")
    error_rate: float = Field(default=0.0, description="오류율 (%)")


class AXOpportunity(BaseModel):
    """AX 기회 (발굴 결과)"""
    opportunity_id: str = Field(default="", description="기회 ID")
    process: BusinessProcess = Field(..., description="원본 프로세스")
    title: str = Field(..., description="AX 기회명")
    description: str = Field(default="", description="AX 기회 설명")
    ax_approach: str = Field(default="", description="AX 접근 방법")
    target_dx_level: int = Field(default=2, description="목표 DX 레벨 (0~4)")

    # AX 적합도 점수 (100점 만점)
    roi_potential_score: float = Field(default=0.0, ge=0, le=100, description="ROI 잠재력 (30%)")
    implementation_ease_score: float = Field(default=0.0, ge=0, le=100, description="구현 용이성 (25%)")
    data_readiness_score: float = Field(default=0.0, ge=0, le=100, description="데이터 준비도 (25%)")
    org_readiness_score: float = Field(default=0.0, ge=0, le=100, description="조직 준비도 (20%)")
    overall_score: float = Field(default=0.0, ge=0, le=100, description="종합 적합도 점수")

    # 예상 효과
    estimated_roi: float = Field(default=0.0, description="예상 ROI (%)")
    estimated_saving: float = Field(default=0.0, description="예상 연간 절감 (만원)")
    estimated_investment: float = Field(default=0.0, description="예상 투자비 (만원)")
    payback_months: float = Field(default=0.0, description="회수 기간 (개월)")

    # 기술 요건
    required_tech: list[str] = Field(default_factory=list)
    required_data: list[str] = Field(default_factory=list)
    complexity: str = Field(default="medium")
    priority: str = Field(default="medium", description="우선순위 (high/medium/low)")


class AXDiscoveryRequest(BaseModel):
    """AX 기회 발굴 요청"""
    company_id: str = Field(default="", description="기업 ID")
    department: str = Field(..., description="대상 부서")
    domain: str = Field(default="manufacturing", description="산업 도메인")
    processes: list[BusinessProcess] = Field(default_factory=list)
    budget_limit: float = Field(default=0.0, description="예산 한도 (만원)")
    priority_focus: str = Field(default="roi", description="우선순위 기준 (roi/ease/balanced)")


class AXDiscoveryResult(BaseModel):
    """AX 기회 발굴 결과"""
    request_id: str = Field(default="")
    company_id: str = Field(default="")
    department: str = Field(default="")
    domain: str = Field(default="")
    total_processes_analyzed: int = Field(default=0)
    opportunities: list[AXOpportunity] = Field(default_factory=list)
    top_recommendations: list[str] = Field(default_factory=list)
    estimated_total_saving: float = Field(default=0.0)
    estimated_total_investment: float = Field(default=0.0)
    department_dx_level: float = Field(default=0.0)
    summary: str = Field(default="")


# ============================================================
# 부서별 AX 과제 템플릿
# ============================================================
DEPARTMENT_AX_TEMPLATES: dict[str, list[dict]] = {
    "제품/기술 개발 연구소": [
        {"title": "설계 자동화", "complexity": "high", "roi_range": "높음"},
        {"title": "시뮬레이션 최적화", "complexity": "high", "roi_range": "높음"},
        {"title": "특허 분석 자동화", "complexity": "medium", "roi_range": "중간"},
        {"title": "재료 물성 예측", "complexity": "high", "roi_range": "높음"},
        {"title": "설계 도면 자동 검증", "complexity": "medium", "roi_range": "중간"},
    ],
    "생산기술연구소": [
        {"title": "공정 파라미터 최적화", "complexity": "high", "roi_range": "매우 높음"},
        {"title": "설비 예지보전", "complexity": "medium", "roi_range": "높음"},
        {"title": "에너지 사용 최적화", "complexity": "medium", "roi_range": "중간"},
        {"title": "공정 이상 탐지", "complexity": "medium", "roi_range": "높음"},
    ],
    "생산부": [
        {"title": "생산 스케줄링 최적화", "complexity": "high", "roi_range": "매우 높음"},
        {"title": "불량 예측 시스템", "complexity": "medium", "roi_range": "높음"},
        {"title": "작업지시 자동화", "complexity": "low", "roi_range": "중간"},
        {"title": "실시간 생산 모니터링", "complexity": "medium", "roi_range": "높음"},
        {"title": "자동 품질 분류", "complexity": "medium", "roi_range": "높음"},
    ],
    "품질관리부": [
        {"title": "AI 비전 검사 시스템", "complexity": "medium", "roi_range": "매우 높음"},
        {"title": "SPC 실시간 자동화", "complexity": "medium", "roi_range": "높음"},
        {"title": "불량 원인 자동 분석", "complexity": "high", "roi_range": "높음"},
        {"title": "검사 데이터 기반 공정 피드백", "complexity": "high", "roi_range": "높음"},
    ],
    "자재부": [
        {"title": "수요 예측", "complexity": "medium", "roi_range": "높음"},
        {"title": "재고 최적화", "complexity": "medium", "roi_range": "높음"},
        {"title": "발주 자동화", "complexity": "low", "roi_range": "중간"},
        {"title": "공급망 리스크 예측", "complexity": "high", "roi_range": "높음"},
    ],
    "경영부": [
        {"title": "경영분석 자동화", "complexity": "medium", "roi_range": "중간"},
        {"title": "의사결정 지원 시스템", "complexity": "high", "roi_range": "높음"},
        {"title": "시장 트렌드 분석", "complexity": "medium", "roi_range": "중간"},
    ],
    "재무/인사관리부": [
        {"title": "재무 예측 자동화", "complexity": "medium", "roi_range": "높음"},
        {"title": "채용 적합도 분석", "complexity": "medium", "roi_range": "중간"},
        {"title": "급여/복리후생 최적화", "complexity": "low", "roi_range": "중간"},
        {"title": "이직률 예측", "complexity": "medium", "roi_range": "중간"},
    ],
    "영업/마케팅": [
        {"title": "고객 세분화", "complexity": "medium", "roi_range": "높음"},
        {"title": "매출 예측", "complexity": "medium", "roi_range": "높음"},
        {"title": "캠페인 ROI 최적화", "complexity": "medium", "roi_range": "높음"},
        {"title": "이탈 고객 예측", "complexity": "medium", "roi_range": "높음"},
    ],
    "수출부": [
        {"title": "환율 예측", "complexity": "high", "roi_range": "높음"},
        {"title": "물류 최적화", "complexity": "medium", "roi_range": "높음"},
        {"title": "통관 자동화", "complexity": "low", "roi_range": "중간"},
    ],
    "고객지원부": [
        {"title": "AI 챗봇 구축", "complexity": "medium", "roi_range": "높음"},
        {"title": "VOC 분석 자동화", "complexity": "medium", "roi_range": "중간"},
        {"title": "이슈 예측 시스템", "complexity": "high", "roi_range": "높음"},
    ],
}
