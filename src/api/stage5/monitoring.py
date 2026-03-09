"""
Stage 5: 모니터링 설정 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import MonitoringInput


async def save_monitoring(project_id: str, monitoring: MonitoringInput):
    """모니터링 설정 저장"""
    monitoring_data = {
        "metrics": monitoring.metrics,
        "alert_thresholds": monitoring.alert_thresholds,
        "dashboard_config": monitoring.dashboard_config,
        "reporting_frequency": monitoring.reporting_frequency,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage5_monitoring": monitoring_data})
    return {"status": "success", "message": "모니터링 설정이 저장되었습니다.", "monitoring": monitoring_data}


async def get_monitoring(project_id: str):
    """모니터링 설정 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "monitoring": {}}
    return {"status": "success", "monitoring": project.get("stage5_monitoring", {})}

