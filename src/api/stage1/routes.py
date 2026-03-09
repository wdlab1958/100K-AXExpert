"""
Stage 1: AI 비전 및 전략 수립 라우터
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, Dict, Any, Union

from .models import MaturityAssessmentInput, OpportunityInput, RoadmapInput, OpportunityListInput
from .maturity import (
    save_maturity_assessment,
    get_maturity_assessment,
    analyze_maturity_with_ai
)
from .opportunities import (
    save_opportunities,
    get_opportunities,
    analyze_opportunities_with_ai
)
from .roadmap import (
    save_roadmap,
    get_roadmap,
    analyze_roadmap_with_ai
)

router = APIRouter(prefix="/projects/{project_id}/stage1", tags=["Stage 1: AI 비전 및 전략 수립"])


# ==================== 성숙도 진단 ====================

@router.post("/maturity-assessment")
async def save_maturity(project_id: str, assessment: MaturityAssessmentInput):
    """AI 성숙도 진단 저장"""
    return await save_maturity_assessment(project_id, assessment)


@router.get("/maturity-assessment")
async def get_maturity(project_id: str):
    """AI 성숙도 진단 조회"""
    return await get_maturity_assessment(project_id)


@router.post("/maturity-assessment/analyze")
async def analyze_maturity(project_id: str, assessment: MaturityAssessmentInput):
    """AI 기반 성숙도 진단 분석"""
    return await analyze_maturity_with_ai(project_id, assessment)


# ==================== 기회 발굴 ====================

@router.post("/opportunities")
async def save_opportunities_route(
    project_id: str, 
    opportunity: Union[OpportunityInput, OpportunityListInput] = Body(...)
):
    """AI 기회 발굴 저장 (단일 기회 또는 전체 목록)"""
    return await save_opportunities(project_id, opportunity)


@router.get("/opportunities")
async def get_opportunities_route(project_id: str):
    """AI 기회 발굴 조회"""
    return await get_opportunities(project_id)


@router.post("/opportunities/analyze")
async def analyze_opportunities_route(project_id: str, opportunities_data: Optional[Dict[str, Any]] = Body(None)):
    """AI 기반 기회 발굴 분석"""
    return await analyze_opportunities_with_ai(project_id, opportunities_data)


# ==================== 전략 로드맵 ====================

@router.post("/roadmap")
async def save_roadmap_route(project_id: str, roadmap: RoadmapInput):
    """로드맵 저장"""
    return await save_roadmap(project_id, roadmap)


@router.get("/roadmap")
async def get_roadmap_route(project_id: str):
    """로드맵 조회"""
    return await get_roadmap(project_id)


@router.post("/roadmap/analyze")
async def analyze_roadmap_route(project_id: str, roadmap_data: Optional[Dict[str, Any]] = Body(None)):
    """AI 기반 로드맵 분석"""
    return await analyze_roadmap_with_ai(project_id, roadmap_data)

