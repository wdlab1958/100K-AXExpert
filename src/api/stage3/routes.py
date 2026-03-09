"""
Stage 3: Platform & Solution Build 라우터
"""
from fastapi import APIRouter

from .models import PoCInput, PlatformInput, IntegrationInput
from .poc import save_poc, get_poc
from .platform import save_platform, get_platform
from .integration import save_integration, get_integration

router = APIRouter(prefix="/projects/{project_id}/stage3", tags=["Stage 3: Platform & Solution Build"])


# ==================== PoC ====================

@router.post("/poc")
async def save_poc_route(project_id: str, poc: PoCInput):
    """PoC 계획 저장"""
    return await save_poc(project_id, poc)


@router.get("/poc")
async def get_poc_route(project_id: str):
    """PoC 계획 조회"""
    return await get_poc(project_id)


# ==================== 플랫폼 구축 ====================

@router.post("/platform")
async def save_platform_route(project_id: str, platform: PlatformInput):
    """플랫폼 구축 계획 저장"""
    return await save_platform(project_id, platform)


@router.get("/platform")
async def get_platform_route(project_id: str):
    """플랫폼 구축 계획 조회"""
    return await get_platform(project_id)


# ==================== 통합 ====================

@router.post("/integration")
async def save_integration_route(project_id: str, integration: IntegrationInput):
    """통합 설정 저장"""
    return await save_integration(project_id, integration)


@router.get("/integration")
async def get_integration_route(project_id: str):
    """통합 설정 조회"""
    return await get_integration(project_id)

