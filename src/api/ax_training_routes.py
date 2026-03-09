"""
100K-AX Expert Platform - AX Training & Certification API Routes
Phase 2: AX 전문가 양성 API 엔드포인트
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from src.services.training_tracker import get_training_tracker
from src.services.certification_engine import get_certification_engine
from src.models.training import AXTaskCreate

router = APIRouter(prefix="/api/v1/training", tags=["AX Training"])


# ============================================================
# Request Models
# ============================================================
class UserRegistrationRequest(BaseModel):
    user_id: str
    user_name: str
    company_id: str
    company_name: str = ""
    department: str
    domain: str = "manufacturing"


class TaskCompleteRequest(BaseModel):
    roi_achieved: float = 0.0
    dx_level_after: int = 0


# ============================================================
# 플랫폼 통계
# ============================================================
@router.get("/stats")
async def get_platform_stats():
    """플랫폼 전체 통계 (100K 목표 대비 현황)"""
    tracker = get_training_tracker()
    return {"status": "success", "data": tracker.get_platform_stats()}


# ============================================================
# 사용자 관리
# ============================================================
@router.post("/users")
async def register_user(req: UserRegistrationRequest):
    """실무자 등록"""
    tracker = get_training_tracker()
    progress = tracker.register_user(
        user_id=req.user_id, user_name=req.user_name,
        company_id=req.company_id, company_name=req.company_name,
        department=req.department, domain=req.domain,
    )
    return {"status": "success", "data": progress.model_dump()}


@router.get("/users")
async def list_users(company_id: str = "", department: str = ""):
    """실무자 목록 조회"""
    tracker = get_training_tracker()
    users = tracker.list_users(company_id=company_id, department=department)
    return {
        "status": "success",
        "count": len(users),
        "data": [u.model_dump() for u in users],
    }


@router.get("/users/{user_id}")
async def get_user(user_id: str):
    """실무자 상세 조회"""
    tracker = get_training_tracker()
    user = tracker.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "data": user.model_dump()}


@router.get("/users/{user_id}/summary")
async def get_user_summary(user_id: str):
    """실무자 학습 진도 요약"""
    tracker = get_training_tracker()
    user = tracker.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    engine = get_certification_engine()
    summary = engine.generate_summary(user)
    return {"status": "success", "data": summary.model_dump()}


@router.get("/users/{user_id}/certification")
async def get_user_certification(user_id: str):
    """실무자 인증 등급 및 갭 분석"""
    tracker = get_training_tracker()
    user = tracker.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    engine = get_certification_engine()
    level = engine.evaluate(user)
    gap = engine.get_next_level_gap(user)
    return {
        "status": "success",
        "data": {
            "current_level": level.value,
            "level_description": engine.LEVELS[level]["label"],
            "next_level_gap": gap,
            "badges": user.badges,
            "growth_history": [g.model_dump() for g in user.growth_history],
        }
    }


# ============================================================
# AX 과제 관리
# ============================================================
@router.post("/users/{user_id}/tasks")
async def add_task(user_id: str, task: AXTaskCreate):
    """AX 과제 추가"""
    tracker = get_training_tracker()
    result = tracker.add_task(user_id, task)
    if not result:
        raise HTTPException(status_code=404, detail="User not found")
    return {"status": "success", "data": result.model_dump()}


@router.post("/users/{user_id}/tasks/{task_id}/start")
async def start_task(user_id: str, task_id: str):
    """AX 과제 시작"""
    tracker = get_training_tracker()
    result = tracker.start_task(user_id, task_id)
    if not result:
        raise HTTPException(status_code=404, detail="User or task not found")
    return {"status": "success", "data": result.model_dump()}


@router.post("/users/{user_id}/tasks/{task_id}/complete")
async def complete_task(user_id: str, task_id: str, req: TaskCompleteRequest):
    """AX 과제 완료"""
    tracker = get_training_tracker()
    result = tracker.complete_task(
        user_id, task_id,
        roi_achieved=req.roi_achieved,
        dx_level_after=req.dx_level_after,
    )
    if not result:
        raise HTTPException(status_code=404, detail="User or task not found")
    return {"status": "success", "data": result}


@router.get("/users/{user_id}/tasks")
async def list_user_tasks(user_id: str):
    """실무자 과제 목록"""
    tracker = get_training_tracker()
    user = tracker.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return {
        "status": "success",
        "count": len(user.tasks),
        "data": [t.model_dump() for t in user.tasks],
    }


# ============================================================
# 부서 / 기업 대시보드
# ============================================================
@router.get("/departments/{company_id}/{department}")
async def get_department_status(company_id: str, department: str):
    """부서별 AX 현황"""
    tracker = get_training_tracker()
    status = tracker.get_department_status(company_id, department)
    return {"status": "success", "data": status.model_dump()}


@router.get("/enterprise/{company_id}")
async def get_enterprise_dashboard(company_id: str, company_name: str = ""):
    """기업 전체 AX 성과 대시보드"""
    tracker = get_training_tracker()
    dashboard = tracker.get_enterprise_dashboard(company_id, company_name)
    return {"status": "success", "data": dashboard.model_dump()}


# ============================================================
# 인증 등급 정보
# ============================================================
@router.get("/certification/levels")
async def get_certification_levels():
    """전문가 인증 등급 체계 조회"""
    engine = get_certification_engine()
    levels = []
    for level in engine.LEVEL_ORDER:
        req = engine.LEVELS[level]
        levels.append({
            "level": level.value,
            "label": req["label"],
            "min_tasks": req["min_tasks"],
            "min_roi_tasks": req["min_roi_tasks"],
            "min_conversion": req["min_conversion"],
            "external_consulting": req["external_consulting"],
        })
    return {"status": "success", "data": levels}
