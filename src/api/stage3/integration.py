"""
Stage 3: 솔루션 통합 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import IntegrationInput


async def save_integration(project_id: str, integration: IntegrationInput):
    """통합 설정 저장"""
    integration_data = {
        "target_systems": integration.target_systems,
        "api_specifications": integration.api_specifications,
        "data_flow": integration.data_flow,
        "testing_plan": integration.testing_plan,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage3_integration": integration_data})
    return {"status": "success", "message": "통합 설정이 저장되었습니다.", "integration": integration_data}


async def get_integration(project_id: str):
    """통합 설정 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "integration": {}}
    return {"status": "success", "integration": project.get("stage3_integration", {})}

