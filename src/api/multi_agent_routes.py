"""
멀티 에이젠틱 프레임워크 API 라우트
LangGraph, CrewAI, AutoGen 프레임워크 통합 엔드포인트
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
import traceback

router = APIRouter(prefix="/api/v1/multi-agent", tags=["Multi-Agent Frameworks"])


# ==================== Pydantic Models ====================

class ConsultationRequest(BaseModel):
    """컨설팅 실행 요청"""
    project_id: str = Field(default="", description="프로젝트 ID (빈 문자열이면 자동 생성)")
    company_profile: Dict[str, Any] = Field(default_factory=dict, description="기업 프로필")
    options: Dict[str, Any] = Field(default_factory=dict, description="프레임워크별 옵션")


class FrameworkComparisonRequest(BaseModel):
    """프레임워크 비교 실행 요청"""
    project_id: str = Field(default="", description="프로젝트 ID")
    company_profile: Dict[str, Any] = Field(default_factory=dict, description="기업 프로필")
    frameworks: List[str] = Field(
        default=["langgraph", "crewai", "autogen"],
        description="비교할 프레임워크 목록"
    )


# ==================== 공통 유틸리티 ====================

def _get_sample_company_profile() -> Dict[str, Any]:
    """테스트용 샘플 기업 프로필 반환"""
    import json as _json
    from src.utils.sample_data_generator import generate_sample_company_profile
    profile = generate_sample_company_profile()
    return _json.loads(profile.model_dump_json())


def _ensure_company_profile(data: ConsultationRequest) -> Dict[str, Any]:
    """기업 프로필이 없으면 샘플 데이터 사용"""
    if data.company_profile:
        return data.company_profile
    return _get_sample_company_profile()


def _ensure_project_id(data_id: str) -> str:
    """프로젝트 ID가 없으면 자동 생성"""
    if data_id:
        return data_id
    import uuid
    return f"multi-agent-{uuid.uuid4().hex[:8]}"


# ==================== 프레임워크 정보 엔드포인트 ====================

@router.get("/frameworks")
async def list_frameworks():
    """사용 가능한 멀티 에이젠틱 프레임워크 목록"""
    return {
        "status": "success",
        "frameworks": [
            {
                "id": "langgraph",
                "name": "LangGraph",
                "version": "0.2.76",
                "description": "StateGraph 기반 조건부 분기 워크플로우 오케스트레이션",
                "features": ["조건부 분기", "상태 관리", "품질 기반 반복 실행", "그래프 시각화"],
                "status": "active",
            },
            {
                "id": "crewai",
                "name": "CrewAI",
                "version": "1.9.3",
                "description": "역할(Role) 기반 에이전트 팀 협업 프로세스",
                "features": ["역할 기반 에이전트", "순차/계층적 프로세스", "태스크 간 컨텍스트 전달", "위임 지원"],
                "status": "active",
            },
            {
                "id": "autogen",
                "name": "AutoGen (AG2)",
                "version": "0.7.5",
                "description": "GroupChat 기반 대화형 멀티 에이전트 협업",
                "features": ["RoundRobin/Selector GroupChat", "대화 기반 합의", "Ollama 네이티브", "종료 조건 제어"],
                "status": "active",
            },
            {
                "id": "native",
                "name": "100K-AX Expert Native",
                "version": "1.0.0",
                "description": "기존 커스텀 순차 실행 오케스트레이터",
                "features": ["규칙 기반 스코어링", "순차 비동기 실행", "이벤트 핸들링"],
                "status": "active",
            },
        ],
    }


# ==================== LangGraph 엔드포인트 ====================

@router.get("/langgraph/info")
async def langgraph_info():
    """LangGraph 오케스트레이터 정보"""
    try:
        from src.agents.langgraph_orchestrator import get_langgraph_orchestrator
        orchestrator = get_langgraph_orchestrator()
        return {
            "status": "success",
            "framework": "langgraph",
            "graph": orchestrator.get_graph_visualization(),
            "agents": list(orchestrator.agents.keys()),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangGraph 초기화 오류: {str(e)}")


@router.post("/langgraph/run")
async def langgraph_run(data: ConsultationRequest):
    """LangGraph 워크플로우 실행"""
    try:
        from src.agents.langgraph_orchestrator import get_langgraph_orchestrator
        orchestrator = get_langgraph_orchestrator()

        project_id = _ensure_project_id(data.project_id)
        company_profile = _ensure_company_profile(data)
        max_iterations = data.options.get("max_iterations", 2)

        result = await orchestrator.run_consultation(
            project_id=project_id,
            company_profile=company_profile,
            max_iterations=max_iterations,
        )

        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangGraph 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


@router.get("/langgraph/graph")
async def langgraph_graph():
    """LangGraph 그래프 시각화 데이터"""
    try:
        from src.agents.langgraph_orchestrator import get_langgraph_orchestrator
        orchestrator = get_langgraph_orchestrator()
        return {
            "status": "success",
            "graph": orchestrator.get_graph_visualization(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== CrewAI 엔드포인트 ====================

@router.get("/crewai/info")
async def crewai_info():
    """CrewAI 에이전트 구성 정보"""
    try:
        from src.agents.crewai_orchestrator import get_crewai_orchestrator
        orchestrator = get_crewai_orchestrator()
        return {
            "status": "success",
            **orchestrator.get_crew_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CrewAI 초기화 오류: {str(e)}")


@router.post("/crewai/run")
async def crewai_run(data: ConsultationRequest):
    """CrewAI Crew 실행"""
    try:
        from src.agents.crewai_orchestrator import get_crewai_orchestrator
        orchestrator = get_crewai_orchestrator()

        project_id = _ensure_project_id(data.project_id)
        company_profile = _ensure_company_profile(data)
        process_type = data.options.get("process_type", "sequential")

        result = await orchestrator.run_consultation(
            project_id=project_id,
            company_profile=company_profile,
            process_type=process_type,
        )

        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"CrewAI 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


# ==================== AutoGen 엔드포인트 ====================

@router.get("/autogen/info")
async def autogen_info():
    """AutoGen 에이전트 구성 정보"""
    try:
        from src.agents.autogen_orchestrator import get_autogen_orchestrator
        orchestrator = get_autogen_orchestrator()
        return {
            "status": "success",
            **orchestrator.get_agent_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AutoGen 초기화 오류: {str(e)}")


@router.post("/autogen/run")
async def autogen_run(data: ConsultationRequest):
    """AutoGen GroupChat 실행"""
    try:
        from src.agents.autogen_orchestrator import get_autogen_orchestrator
        orchestrator = get_autogen_orchestrator()

        project_id = _ensure_project_id(data.project_id)
        company_profile = _ensure_company_profile(data)
        chat_mode = data.options.get("chat_mode", "round_robin")
        max_messages = data.options.get("max_messages", 12)

        result = await orchestrator.run_consultation(
            project_id=project_id,
            company_profile=company_profile,
            chat_mode=chat_mode,
            max_messages=max_messages,
        )

        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"AutoGen 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


# ==================== 프레임워크 비교 엔드포인트 ====================

@router.post("/compare")
async def compare_frameworks(data: FrameworkComparisonRequest):
    """여러 프레임워크의 컨설팅 결과 비교"""
    project_id = _ensure_project_id(data.project_id)

    if data.company_profile:
        company_profile = data.company_profile
    else:
        company_profile = _get_sample_company_profile()

    results = {}
    errors = {}

    for framework in data.frameworks:
        try:
            if framework == "langgraph":
                from src.agents.langgraph_orchestrator import get_langgraph_orchestrator
                orch = get_langgraph_orchestrator()
                results["langgraph"] = await orch.run_consultation(
                    project_id=f"{project_id}-lg",
                    company_profile=company_profile,
                )
            elif framework == "crewai":
                from src.agents.crewai_orchestrator import get_crewai_orchestrator
                orch = get_crewai_orchestrator()
                results["crewai"] = await orch.run_consultation(
                    project_id=f"{project_id}-crew",
                    company_profile=company_profile,
                )
            elif framework == "autogen":
                from src.agents.autogen_orchestrator import get_autogen_orchestrator
                orch = get_autogen_orchestrator()
                results["autogen"] = await orch.run_consultation(
                    project_id=f"{project_id}-ag",
                    company_profile=company_profile,
                )
            elif framework == "native":
                from src.agents.agent_orchestrator import get_orchestrator
                from src.models.schemas import CompanyProfile
                orch = get_orchestrator()
                company = CompanyProfile(**company_profile)
                pid = orch.create_project(f"비교 테스트 - {project_id}", company)
                native_result = await orch.run_full_consultation(pid, auto_approve=True)
                results["native"] = {
                    "framework": "native",
                    "project_id": pid,
                    "status": native_result.get("status", "unknown"),
                    "results": native_result.get("stages", {}),
                }
        except Exception as e:
            errors[framework] = str(e)

    return {
        "status": "success",
        "project_id": project_id,
        "comparison": results,
        "errors": errors,
        "frameworks_tested": list(results.keys()),
        "frameworks_failed": list(errors.keys()),
        "timestamp": datetime.now().isoformat(),
    }


# ==================== 헬스체크 ====================

@router.get("/health")
async def multi_agent_health():
    """멀티 에이젠틱 프레임워크 헬스체크"""
    health = {}

    # LangGraph
    try:
        from src.agents.langgraph_orchestrator import get_langgraph_orchestrator
        orch = get_langgraph_orchestrator()
        health["langgraph"] = {
            "status": "healthy",
            "agents": len(orch.agents),
            "graph_nodes": len(orch.get_graph_visualization()["nodes"]),
        }
    except Exception as e:
        health["langgraph"] = {"status": "error", "error": str(e)}

    # CrewAI
    try:
        from src.agents.crewai_orchestrator import get_crewai_orchestrator
        orch = get_crewai_orchestrator()
        health["crewai"] = {
            "status": "healthy",
            "agents": len(orch.crew_agents),
        }
    except Exception as e:
        health["crewai"] = {"status": "error", "error": str(e)}

    # AutoGen
    try:
        from src.agents.autogen_orchestrator import get_autogen_orchestrator
        orch = get_autogen_orchestrator()
        health["autogen"] = {
            "status": "healthy",
            "agents": len(orch.autogen_agents),
        }
    except Exception as e:
        health["autogen"] = {"status": "error", "error": str(e)}

    all_healthy = all(v["status"] == "healthy" for v in health.values())

    return {
        "status": "success" if all_healthy else "degraded",
        "frameworks": health,
        "timestamp": datetime.now().isoformat(),
    }
