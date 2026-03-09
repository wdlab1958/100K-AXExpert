"""
Stage 5: 지속적 개선 로직
"""
from datetime import datetime
from typing import Dict, Any

from ..common.database import get_project, update_project
from .models import ImprovementInput, GovernanceReviewInput


async def save_improvement(project_id: str, improvement: ImprovementInput):
    """개선 계획 저장"""
    improvement_data = {
        "improvement_cycle": improvement.improvement_cycle,
        "feedback_sources": improvement.feedback_sources,
        "prioritization_criteria": improvement.prioritization_criteria,
        "experiment_framework": improvement.experiment_framework,
        "success_metrics": improvement.success_metrics,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage5_improvement": improvement_data})
    return {"status": "success", "message": "개선 계획이 저장되었습니다.", "improvement": improvement_data}


async def get_improvement(project_id: str):
    """개선 계획 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "improvement": {}}
    return {"status": "success", "improvement": project.get("stage5_improvement", {})}


async def save_governance_review(project_id: str, review: GovernanceReviewInput):
    """거버넌스 검토 설정 저장"""
    review_data = {
        "review_frequency": review.review_frequency,
        "review_scope": review.review_scope,
        "audit_checklist": review.audit_checklist,
        "compliance_updates": review.compliance_updates,
        "policy_revisions": review.policy_revisions,
        "updated_at": datetime.now().isoformat()
    }
    update_project(project_id, {"stage5_governance_review": review_data})
    return {"status": "success", "message": "거버넌스 검토 설정이 저장되었습니다.", "governance_review": review_data}


async def get_governance_review(project_id: str):
    """거버넌스 검토 설정 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "governance_review": {}}
    return {"status": "success", "governance_review": project.get("stage5_governance_review", {})}

