"""
Stage 4: 파일럿 운영 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import PilotInput


async def save_pilot(project_id: str, pilot: PilotInput):
    """파일럿 계획 저장"""
    pilot_data = {
        "pilot_name": pilot.pilot_name,
        "target_department": pilot.target_department,
        "pilot_scope": pilot.pilot_scope,
        "duration": pilot.duration,
        "success_criteria": pilot.success_criteria,
        "support_plan": pilot.support_plan,
        "status": "planned",
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage4_pilot": pilot_data})
    return {"status": "success", "message": "파일럿 계획이 저장되었습니다.", "pilot": pilot_data}


async def get_pilot(project_id: str):
    """파일럿 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "pilot": {}}
    return {"status": "success", "pilot": project.get("stage4_pilot", {})}

