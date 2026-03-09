"""
Stage 2: 상세 요건 정의 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import RequirementsInput


async def save_requirements(project_id: str, requirements: RequirementsInput):
    """상세 요건 정의 저장"""
    req_data = {
        "use_case_name": requirements.use_case_name,
        "business_requirements": requirements.business_requirements,
        "functional_requirements": requirements.functional_requirements,
        "non_functional_requirements": requirements.non_functional_requirements,
        "data_requirements": requirements.data_requirements,
        "constraints": requirements.constraints,
        "success_criteria": requirements.success_criteria,
        "updated_at": datetime.now().isoformat()
    }

    update_project(project_id, {"stage2_requirements": req_data})

    return {
        "status": "success",
        "message": "요건 정의가 저장되었습니다.",
        "requirements": req_data
    }


async def get_requirements(project_id: str):
    """상세 요건 정의 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "requirements": {}}

    return {
        "status": "success",
        "requirements": project.get("stage2_requirements", {})
    }

