"""
Stage 2: Use Case & Design 라우터
"""
from fastapi import APIRouter

from .models import RequirementsInput, ArchitectureInput, GovernanceInput
from .requirements import save_requirements, get_requirements
from .architecture import save_architecture, get_architecture
from .governance import save_governance, get_governance

router = APIRouter(prefix="/projects/{project_id}/stage2", tags=["Stage 2: Use Case & Design"])


# ==================== 상세 요건 정의 ====================

@router.post("/requirements")
async def save_requirements_route(project_id: str, requirements: RequirementsInput):
    """상세 요건 정의 저장"""
    return await save_requirements(project_id, requirements)


@router.get("/requirements")
async def get_requirements_route(project_id: str):
    """상세 요건 정의 조회"""
    return await get_requirements(project_id)


# ==================== 아키텍처 설계 ====================

@router.post("/architecture")
async def save_architecture_route(project_id: str, architecture: ArchitectureInput):
    """아키텍처 설계 저장"""
    return await save_architecture(project_id, architecture)


@router.get("/architecture")
async def get_architecture_route(project_id: str):
    """아키텍처 설계 조회"""
    return await get_architecture(project_id)


# ==================== 거버넌스 체계 ====================

@router.post("/governance")
async def save_governance_route(project_id: str, governance: GovernanceInput):
    """거버넌스 체계 저장"""
    return await save_governance(project_id, governance)


@router.get("/governance")
async def get_governance_route(project_id: str):
    """거버넌스 체계 조회"""
    return await get_governance(project_id)

