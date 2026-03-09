"""
Stage 4: 변화 관리 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import ChangeManagementInput


async def save_change_management(project_id: str, cm: ChangeManagementInput):
    """변화 관리 계획 저장"""
    cm_data = {
        "awareness": cm.awareness,
        "capability": cm.capability,
        "engagement": cm.engagement,
        "success_sharing": cm.success_sharing,
        "notes": cm.notes,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage4_change_management": cm_data})
    return {"status": "success", "message": "변화 관리 계획이 저장되었습니다.", "change_management": cm_data}


async def get_change_management(project_id: str):
    """변화 관리 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "change_management": {}}
    return {"status": "success", "change_management": project.get("stage4_change_management", {})}

