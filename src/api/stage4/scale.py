"""
Stage 4: 전사 확산 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import ScaleInput


async def save_scale(project_id: str, scale: ScaleInput):
    """확산 계획 저장"""
    scale_data = {
        "rollout_phases": scale.rollout_phases,
        "target_coverage": scale.target_coverage,
        "timeline": scale.timeline,
        "resource_plan": scale.resource_plan,
        "risk_mitigation": scale.risk_mitigation,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage4_scale": scale_data})
    return {"status": "success", "message": "확산 계획이 저장되었습니다.", "scale": scale_data}


async def get_scale(project_id: str):
    """확산 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "scale": {}}
    return {"status": "success", "scale": project.get("stage4_scale", {})}

