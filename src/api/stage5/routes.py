"""
Stage 5: Operate & Optimize 라우터
"""
from fastapi import APIRouter

from .models import MonitoringInput, ImprovementInput, GovernanceReviewInput
from .monitoring import save_monitoring, get_monitoring
from .improvement import save_improvement, get_improvement, save_governance_review, get_governance_review

router = APIRouter(prefix="/projects/{project_id}/stage5", tags=["Stage 5: Operate & Optimize"])


# ==================== 모니터링 ====================

@router.post("/monitoring")
async def save_monitoring_route(project_id: str, monitoring: MonitoringInput):
    """모니터링 설정 저장"""
    return await save_monitoring(project_id, monitoring)


@router.get("/monitoring")
async def get_monitoring_route(project_id: str):
    """모니터링 설정 조회"""
    return await get_monitoring(project_id)


# ==================== 개선 ====================

@router.post("/improvement")
async def save_improvement_route(project_id: str, improvement: ImprovementInput):
    """개선 계획 저장"""
    return await save_improvement(project_id, improvement)


@router.get("/improvement")
async def get_improvement_route(project_id: str):
    """개선 계획 조회"""
    return await get_improvement(project_id)


# ==================== 거버넌스 검토 ====================

@router.post("/governance-review")
async def save_governance_review_route(project_id: str, review: GovernanceReviewInput):
    """거버넌스 검토 설정 저장"""
    return await save_governance_review(project_id, review)


@router.get("/governance-review")
async def get_governance_review_route(project_id: str):
    """거버넌스 검토 설정 조회"""
    return await get_governance_review(project_id)

