"""
고급 멀티 에이젠틱 프레임워크 API 라우트
DSPy, LangChain (확장), LlamaIndex RAG 엔드포인트
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import traceback

router = APIRouter(prefix="/api/v1/advanced-frameworks", tags=["Advanced Frameworks"])


# ==================== Pydantic Models ====================

class DSPyRequest(BaseModel):
    """DSPy 실행 요청"""
    company_profile: Dict[str, Any] = Field(default_factory=dict, description="기업 프로필")
    task_type: str = Field(default="full", description="작업 유형: maturity, use_case, roi, risk, report, full")


class LangChainRequest(BaseModel):
    """LangChain 실행 요청"""
    project_id: str = Field(default="", description="프로젝트 ID")
    company_profile: Dict[str, Any] = Field(default_factory=dict, description="기업 프로필")
    task_type: str = Field(default="full", description="작업 유형: maturity, use_case, roi, risk, report, full")


class RAGQueryRequest(BaseModel):
    """LlamaIndex RAG 질의 요청"""
    query: str = Field(default="", description="질의 텍스트")
    query_type: str = Field(default="general", description="질의 유형: maturity, use_case, roi, risk, governance, mlops")
    company_profile: Dict[str, Any] = Field(default_factory=dict, description="기업 프로필 (전체 실행 시)")


# ==================== 공통 유틸리티 ====================

def _get_sample_company_profile() -> Dict[str, Any]:
    """테스트용 샘플 기업 프로필 반환"""
    import json
    from src.utils.sample_data_generator import generate_sample_company_profile
    profile = generate_sample_company_profile()
    # datetime 직렬화 문제 방지: JSON 왕복 변환
    return json.loads(profile.model_dump_json())


def _ensure_company_profile(profile: Dict[str, Any]) -> Dict[str, Any]:
    """기업 프로필이 없으면 샘플 데이터 사용"""
    if profile:
        return profile
    return _get_sample_company_profile()


def _ensure_project_id(project_id: str) -> str:
    """프로젝트 ID가 없으면 자동 생성"""
    if project_id:
        return project_id
    import uuid
    return f"adv-{uuid.uuid4().hex[:8]}"


# ==================== DSPy 엔드포인트 ====================

@router.get("/dspy/info")
async def dspy_info():
    """DSPy 모듈 구성 정보"""
    try:
        from src.core.dspy_provider import get_dspy_provider
        provider = get_dspy_provider()
        return {
            "status": "success",
            **provider.get_module_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DSPy 초기화 오류: {str(e)}")


@router.post("/dspy/run")
async def dspy_run(data: DSPyRequest):
    """DSPy 파이프라인 실행"""
    try:
        from src.core.dspy_provider import get_dspy_provider
        provider = get_dspy_provider()

        company_profile = _ensure_company_profile(data.company_profile)

        if data.task_type == "maturity":
            result = await provider.assess_maturity(company_profile)
        elif data.task_type == "use_case":
            result = await provider.discover_use_cases(company_profile, 3)
        elif data.task_type == "roi":
            budget = company_profile.get("financial_resources", {}).get("ai_investment_budget", 1000000000)
            result = await provider.analyze_roi(budget, ["품질 검사 자동화", "예지 정비"])
        elif data.task_type == "risk":
            result = await provider.assess_risk(company_profile, ["품질 검사 자동화", "예지 정비"])
        elif data.task_type == "report":
            result = await provider.generate_report({}, {}, {}, {})
        else:  # full
            result = await provider.run_full_consultation(company_profile)

        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"DSPy 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


# ==================== LangChain (확장) 엔드포인트 ====================

@router.get("/langchain/info")
async def langchain_info():
    """LangChain 체인 구성 정보"""
    try:
        from src.core.langchain_chains import get_langchain_provider
        provider = get_langchain_provider()
        return {
            "status": "success",
            **provider.get_chain_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LangChain 초기화 오류: {str(e)}")


@router.post("/langchain/run")
async def langchain_run(data: LangChainRequest):
    """LangChain 파이프라인 실행"""
    try:
        from src.core.langchain_chains import get_langchain_provider
        provider = get_langchain_provider()

        project_id = _ensure_project_id(data.project_id)
        company_profile = _ensure_company_profile(data.company_profile)

        if data.task_type == "maturity":
            result = await provider.analyze_maturity(company_profile)
        elif data.task_type == "use_case":
            result = await provider.discover_use_cases(company_profile, "Level 3 성숙도")
        elif data.task_type == "roi":
            result = await provider.analyze_roi(company_profile, "품질 검사 자동화, 예지 정비")
        elif data.task_type == "risk":
            result = await provider.assess_risk(company_profile, "품질 검사 자동화, 예지 정비")
        elif data.task_type == "report":
            result = await provider.generate_report("N/A", "N/A", "N/A", "N/A")
        else:  # full
            result = await provider.run_full_consultation(project_id, company_profile)

        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LangChain 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


# ==================== LlamaIndex RAG 엔드포인트 ====================

@router.get("/llamaindex/info")
async def llamaindex_info():
    """LlamaIndex RAG 인덱스 정보"""
    try:
        from src.core.llamaindex_rag import get_rag_provider
        provider = get_rag_provider()
        return {
            "status": "success",
            **provider.get_index_info(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LlamaIndex 초기화 오류: {str(e)}")


@router.post("/llamaindex/query")
async def llamaindex_query(data: RAGQueryRequest):
    """LlamaIndex RAG 질의"""
    try:
        from src.core.llamaindex_rag import get_rag_provider
        provider = get_rag_provider()

        query = data.query or "AI 도입 시 참조해야 할 ISO 표준은?"

        result = await provider.query(query, data.query_type)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LlamaIndex 질의 오류: {str(e)}\n{traceback.format_exc()}"
        )


@router.post("/llamaindex/run")
async def llamaindex_run(data: RAGQueryRequest):
    """LlamaIndex 전체 RAG 컨설팅 실행"""
    try:
        from src.core.llamaindex_rag import get_rag_provider
        provider = get_rag_provider()

        company_profile = _ensure_company_profile(data.company_profile)

        result = await provider.run_full_rag_consultation(company_profile)
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"LlamaIndex RAG 실행 오류: {str(e)}\n{traceback.format_exc()}"
        )


@router.post("/llamaindex/rebuild-index")
async def llamaindex_rebuild():
    """LlamaIndex 인덱스 재구축"""
    try:
        from src.core.llamaindex_rag import get_rag_provider
        provider = get_rag_provider()
        result = provider.rebuild_index()
        return {"status": "success", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"인덱스 재구축 오류: {str(e)}")


# ==================== 프레임워크 통합 엔드포인트 ====================

@router.get("/overview")
async def frameworks_overview():
    """고급 프레임워크 전체 현황"""
    status = {}

    # DSPy
    try:
        from src.core.dspy_provider import get_dspy_provider
        provider = get_dspy_provider()
        info = provider.get_module_info()
        status["dspy"] = {
            "status": "healthy",
            "modules": len(info.get("modules", [])),
            "lm_model": info.get("lm_model", "unknown"),
        }
    except Exception as e:
        status["dspy"] = {"status": "error", "error": str(e)}

    # LangChain
    try:
        from src.core.langchain_chains import get_langchain_provider
        provider = get_langchain_provider()
        info = provider.get_chain_info()
        status["langchain"] = {
            "status": "healthy",
            "chains": len(info.get("chains", [])),
            "features": len(info.get("features", [])),
        }
    except Exception as e:
        status["langchain"] = {"status": "error", "error": str(e)}

    # LlamaIndex
    try:
        from src.core.llamaindex_rag import get_rag_provider
        provider = get_rag_provider()
        info = provider.get_index_info()
        status["llamaindex"] = {
            "status": "healthy",
            "indexed_documents": info.get("indexed_documents", 0),
            "standard_files": len(info.get("standard_files", [])),
        }
    except Exception as e:
        status["llamaindex"] = {"status": "error", "error": str(e)}

    all_healthy = all(v.get("status") == "healthy" for v in status.values())

    return {
        "status": "success" if all_healthy else "degraded",
        "frameworks": status,
        "timestamp": datetime.now().isoformat(),
    }


# ==================== 헬스체크 ====================

@router.get("/health")
async def advanced_frameworks_health():
    """고급 프레임워크 헬스체크"""
    return await frameworks_overview()
