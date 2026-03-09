"""
Stage 3: 플랫폼 구축 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import PlatformInput


async def save_platform(project_id: str, platform: PlatformInput):
    """플랫폼 구축 계획 저장"""
    platform_data = {
        "components": platform.components,
        "infrastructure": platform.infrastructure,
        "security_config": platform.security_config,
        "scalability_plan": platform.scalability_plan,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage3_platform": platform_data})
    return {"status": "success", "message": "플랫폼 구축 계획이 저장되었습니다.", "platform": platform_data}


async def get_platform(project_id: str):
    """플랫폼 구축 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "platform": {}}
    return {"status": "success", "platform": project.get("stage3_platform", {})}

