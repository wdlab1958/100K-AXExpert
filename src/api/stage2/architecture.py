"""
Stage 2: 아키텍처 설계 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import ArchitectureInput


async def save_architecture(project_id: str, architecture: ArchitectureInput):
    """아키텍처 설계 저장"""
    arch_data = {
        "data_architecture": architecture.data_architecture,
        "ml_architecture": architecture.ml_architecture,
        "tech_stack": architecture.tech_stack,
        "integration_points": architecture.integration_points,
        "updated_at": datetime.now().isoformat()
    }

    update_project(project_id, {"stage2_architecture": arch_data})

    return {
        "status": "success",
        "message": "아키텍처 설계가 저장되었습니다.",
        "architecture": arch_data
    }


async def get_architecture(project_id: str):
    """아키텍처 설계 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "architecture": {}}

    return {
        "status": "success",
        "architecture": project.get("stage2_architecture", {})
    }

