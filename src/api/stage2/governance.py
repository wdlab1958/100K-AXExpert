"""
Stage 2: 거버넌스 체계 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import GovernanceInput


async def save_governance(project_id: str, governance: GovernanceInput):
    """거버넌스 체계 저장"""
    governance_data = {
        "privacy": governance.privacy,
        "ethics": governance.ethics,
        "compliance": governance.compliance,
        "notes": governance.notes,
        "updated_at": datetime.now().isoformat()
    }

    update_project(project_id, {"stage2_governance": governance_data})

    return {
        "status": "success",
        "message": "거버넌스 체계가 저장되었습니다.",
        "governance": governance_data
    }


async def get_governance(project_id: str):
    """거버넌스 체계 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "governance": {}}

    return {
        "status": "success",
        "governance": project.get("stage2_governance", {})
    }

