"""
Stage 4: Pilot & Scale 라우터
"""
from fastapi import APIRouter

from .models import PilotInput, ChangeManagementInput, ScaleInput
from .pilot import save_pilot, get_pilot
from .change_management import save_change_management, get_change_management
from .scale import save_scale, get_scale

router = APIRouter(prefix="/projects/{project_id}/stage4", tags=["Stage 4: Pilot & Scale"])


# ==================== 파일럿 ====================

@router.post("/pilot")
async def save_pilot_route(project_id: str, pilot: PilotInput):
    """파일럿 계획 저장"""
    return await save_pilot(project_id, pilot)


@router.get("/pilot")
async def get_pilot_route(project_id: str):
    """파일럿 계획 조회"""
    return await get_pilot(project_id)


# ==================== 변화 관리 ====================

@router.post("/change-management")
async def save_change_management_route(project_id: str, cm: ChangeManagementInput):
    """변화 관리 계획 저장"""
    return await save_change_management(project_id, cm)


@router.get("/change-management")
async def get_change_management_route(project_id: str):
    """변화 관리 계획 조회"""
    return await get_change_management(project_id)


# ==================== 확산 ====================

@router.post("/scale")
async def save_scale_route(project_id: str, scale: ScaleInput):
    """확산 계획 저장"""
    return await save_scale(project_id, scale)


@router.get("/scale")
async def get_scale_route(project_id: str):
    """확산 계획 조회"""
    return await get_scale(project_id)

