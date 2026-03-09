"""
100K-AX Expert Platform - AX Discovery API Routes
Phase 1: AX 기회 발굴 API 엔드포인트
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from fastapi import APIRouter
from src.services.ax_discovery import get_ax_discovery_service
from src.services.domain_kb import get_domain_kb_manager
from src.models.ax_discovery import AXDiscoveryRequest, DEPARTMENT_AX_TEMPLATES

router = APIRouter(prefix="/api/v1/ax-discovery", tags=["AX Discovery"])


# ============================================================
# AX 기회 발굴
# ============================================================
@router.post("/discover")
async def discover_opportunities(request: AXDiscoveryRequest):
    """AX 기회 발굴 실행 - 업무 프로세스 분석 → AX 기회 자동 식별"""
    service = get_ax_discovery_service()
    result = await service.discover_opportunities(request)
    return {"status": "success", "data": result.model_dump()}


@router.get("/templates")
async def get_department_templates():
    """부서별 AX 과제 템플릿 목록"""
    templates = {}
    for dept, items in DEPARTMENT_AX_TEMPLATES.items():
        templates[dept] = {
            "department": dept,
            "task_count": len(items),
            "tasks": items,
        }
    return {"status": "success", "data": templates}


@router.get("/templates/{department}")
async def get_department_template(department: str):
    """특정 부서의 AX 과제 템플릿"""
    items = DEPARTMENT_AX_TEMPLATES.get(department, [])
    return {
        "status": "success",
        "data": {
            "department": department,
            "task_count": len(items),
            "tasks": items,
        }
    }


# ============================================================
# 도메인 Knowledge Base
# ============================================================
@router.get("/domains")
async def list_domains():
    """산업 도메인 목록"""
    kb = get_domain_kb_manager()
    return {"status": "success", "data": kb.list_domains()}


@router.get("/domains/{domain}")
async def get_domain_info(domain: str):
    """도메인 상세 정보"""
    kb = get_domain_kb_manager()
    info = kb.get_domain_info(domain)
    if not info:
        return {"status": "error", "message": f"Unknown domain: {domain}"}
    return {"status": "success", "data": info}


@router.get("/domains/{domain}/best-practices")
async def get_domain_best_practices(domain: str):
    """도메인별 AX 베스트 프랙티스"""
    kb = get_domain_kb_manager()
    practices = kb.get_best_practices(domain)
    return {"status": "success", "data": practices}


@router.get("/domains/{domain}/regulations")
async def get_domain_regulations(domain: str):
    """도메인별 규제/표준 목록"""
    kb = get_domain_kb_manager()
    regulations = kb.get_regulations(domain)
    return {"status": "success", "data": regulations}


@router.get("/domains/{domain}/processes")
async def get_domain_processes(domain: str):
    """도메인별 핵심 프로세스"""
    kb = get_domain_kb_manager()
    processes = kb.get_key_processes(domain)
    return {"status": "success", "data": processes}


@router.get("/best-practices/search")
async def search_best_practices(query: str = ""):
    """전체 도메인 베스트 프랙티스 검색"""
    kb = get_domain_kb_manager()
    results = kb.search_best_practices(query)
    return {"status": "success", "count": len(results), "data": results}
