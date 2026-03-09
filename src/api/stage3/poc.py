"""
Stage 3: PoC 수행 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import PoCInput


async def save_poc(project_id: str, poc: PoCInput):
    """PoC 계획 저장"""
    poc_data = {
        "poc_name": poc.poc_name,
        "objectives": poc.objectives,
        "scope": poc.scope,
        "success_metrics": poc.success_metrics,
        "timeline": poc.timeline,
        "resources": poc.resources,
        "risks": poc.risks,
        "status": "planned",
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage3_poc": poc_data})
    return {"status": "success", "message": "PoC 계획이 저장되었습니다.", "poc": poc_data}


async def get_poc(project_id: str):
    """PoC 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "poc": {}}
    return {"status": "success", "poc": project.get("stage3_poc", {})}

