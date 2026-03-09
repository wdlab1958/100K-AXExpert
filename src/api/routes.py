"""
AI Consulting Assistant Platform - API Routes
FastAPI 기반 REST API
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse, StreamingResponse, Response
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import io
import json
import uuid
import time

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.models.schemas import (
    CompanyProfile, CreateProjectRequest, GenerateScenarioRequest,
    SubmitFeedbackRequest, ApproveScenarioRequest, GenerateReportRequest,
    HumanFeedback, IndustryType, CompanySize, ConsultingStage,
    MLOpsStandards, SaveMLOpsStandardsRequest,
    PersonnelOrganization, SavePersonnelOrganizationRequest
)
from src.agents.agent_orchestrator import get_orchestrator
from src.utils.consulting_logger import get_consulting_logger


router = APIRouter(prefix="/api/v1", tags=["AI Consulting"])

# 보고서 다운로드 임시 저장소 (token → {bytes, media_type, disposition, created_at})
_pending_downloads: Dict[str, Dict[str, Any]] = {}


# ==================== 프로젝트 관리 ====================

@router.post("/projects")
async def create_project(request: CreateProjectRequest):
    """새 컨설팅 프로젝트 생성"""
    orchestrator = get_orchestrator()

    try:
        project_id = orchestrator.create_project(
            name=request.project_name,
            company_profile=request.company_profile
        )

        return {
            "status": "success",
            "project_id": project_id,
            "message": f"프로젝트 '{request.project_name}'이(가) 생성되었습니다."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}")
async def get_project(project_id: str):
    """프로젝트 상세 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "project": project
    }


@router.get("/projects/{project_id}/status")
async def get_project_status(project_id: str):
    """프로젝트 상태 조회"""
    orchestrator = get_orchestrator()
    status = orchestrator.get_project_status(project_id)

    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])

    return {
        "status": "success",
        "project_status": status
    }


# ==================== 1단계: 전략 수립 ====================

@router.post("/projects/{project_id}/maturity-assessment")
async def run_maturity_assessment(project_id: str, background_tasks: BackgroundTasks):
    """AI 성숙도 진단 실행"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        result = await orchestrator.run_maturity_assessment(project_id)
        return {
            "status": "success",
            "assessment": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/opportunities")
async def identify_opportunities(project_id: str):
    """AI 도입 기회 발굴"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        result = await orchestrator.identify_opportunities(project_id)
        return {
            "status": "success",
            "opportunities": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/roadmap")
async def create_roadmap(project_id: str):
    """AI 도입 로드맵 수립"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        result = await orchestrator.create_roadmap(project_id)
        return {
            "status": "success",
            "roadmap": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 2단계: Use Case 설계 ====================

@router.post("/projects/{project_id}/use-cases/{use_case_index}/design")
async def design_use_case(project_id: str, use_case_index: int):
    """Use Case 상세 설계"""
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.design_use_case(project_id, use_case_index)
        return {
            "status": "success",
            "design": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 시나리오 분석 ====================

@router.post("/projects/{project_id}/scenarios")
async def generate_scenarios(
    project_id: str,
    scenario_types: List[str] = ["conservative", "balanced", "aggressive"]
):
    """시나리오 생성"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        scenarios = await orchestrator.generate_scenarios(project_id, scenario_types)
        return {
            "status": "success",
            "scenarios": scenarios,
            "message": "시나리오가 생성되었습니다. 검토 후 승인해주세요."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/scenarios")
async def get_scenarios(project_id: str):
    """프로젝트 시나리오 목록 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "scenarios": project.get("scenarios", []),
        "selected_scenario": project.get("selected_scenario"),
        "pending_approval": project.get("pending_approval", False)
    }


@router.get("/projects/{project_id}/scenarios/{scenario_id}")
async def get_scenario_detail(project_id: str, scenario_id: str):
    """시나리오 상세 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    for scenario in project.get("scenarios", []):
        if scenario.get("id") == scenario_id:
            return {
                "status": "success",
                "scenario": scenario
            }

    raise HTTPException(status_code=404, detail="시나리오를 찾을 수 없습니다.")


# ==================== 인간-AI 협업 ====================

@router.post("/projects/{project_id}/feedback")
async def submit_feedback(project_id: str, request: SubmitFeedbackRequest):
    """피드백 제출"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    
    # Orchestrator에 프로젝트가 없으면 framework에서 로드
    if not project:
        try:
            # Framework API에서 프로젝트 로드
            from src.api.consulting_framework_routes import get_project as get_framework_project
            framework_project = get_framework_project(project_id)
            
            if framework_project:
                # CompanyProfile 복원
                company_profile_data = framework_project.get("company_profile", {})
                if company_profile_data:
                    company_profile = CompanyProfile(**company_profile_data)
                else:
                    # 기본 CompanyProfile 생성
                    company_profile = CompanyProfile(
                        name=framework_project.get("project_name", "Unknown"),
                        industry=IndustryType.OTHER,
                        company_size=CompanySize.SME,
                        business_description=""
                    )
                
                from src.agents.agent_orchestrator import WorkflowState, ConsultingStage
                
                # WorkflowState 생성 (TypedDict이므로 dict로 생성)
                workflow_state = {
                    "project_id": project_id,
                    "current_stage": ConsultingStage.STRATEGY,
                    "company_profile": company_profile.model_dump(),
                    "maturity_assessment": None,
                    "use_cases": [],
                    "scenarios": [],
                    "selected_scenario": None,
                    "roi_analysis": None,
                    "risk_assessment": None,
                    "reports": [],
                    "human_feedback": framework_project.get("human_feedback", []),
                    "pending_approval": False,
                    "messages": [],
                    "errors": []
                }
                
                orchestrator.projects[project_id] = workflow_state
                project = orchestrator.get_project(project_id)
            else:
                raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없습니다: {str(e)}")
    
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        result = await orchestrator.submit_human_feedback(project_id, request.feedback)
        
        # Framework 프로젝트에도 피드백 저장
        try:
            from src.api.common.database import get_project as get_framework_project_db, update_project
            framework_project = get_framework_project_db(project_id)
            if framework_project:
                # 현재 피드백 목록 가져오기
                current_feedbacks = framework_project.get("human_feedback", [])
                # 새 피드백 추가
                new_feedback = request.feedback.model_dump() if hasattr(request.feedback, 'model_dump') else request.feedback.dict()
                current_feedbacks.append(new_feedback)
                # 프로젝트 업데이트
                update_project(project_id, {"human_feedback": current_feedbacks})
        except Exception as e:
            # Framework 저장 실패해도 계속 진행 (orchestrator에는 저장됨)
            logger = get_consulting_logger()
            logger.warning(f"Framework 프로젝트에 피드백 저장 실패 (계속 진행): {e}")
        
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/scenarios/{scenario_id}/approve")
async def approve_scenario(
    project_id: str,
    scenario_id: str,
    request: ApproveScenarioRequest
):
    """시나리오 승인"""
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.approve_scenario(
            project_id=project_id,
            scenario_id=scenario_id,
            approver_name=request.approver_name,
            approver_role=request.approver_role,
            comments=request.comments or ""
        )
        return {
            "status": "success",
            "result": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/feedback")
async def get_feedback_history(project_id: str):
    """피드백 이력 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)
    
    # Orchestrator에 프로젝트가 없으면 framework에서 로드
    if not project:
        try:
            # Framework API에서 프로젝트 로드
            from src.api.consulting_framework_routes import get_project as get_framework_project
            framework_project = get_framework_project(project_id)
            
            if framework_project:
                # 피드백 이력이 있으면 바로 반환
                feedbacks = framework_project.get("human_feedback", [])
                return {
                    "status": "success",
                    "feedbacks": feedbacks
                }
            else:
                raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없습니다: {str(e)}")

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "feedbacks": project.get("human_feedback", [])
    }


# ==================== 보고서 생성 ====================

_CAT_LABELS = {
    "strategy": "전략/리더십", "organization": "인력/조직",
    "data_technology": "데이터/기술", "process": "프로세스/운영",
    "data": "데이터", "technology": "기술/인프라",
    "governance": "거버넌스", "people": "인력/역량", "tech": "기술"
}
_IND_LABELS = {
    "manufacturing": "제조업", "finance": "금융/보험", "healthcare": "헬스케어",
    "retail": "유통/리테일", "it_service": "IT서비스", "public": "공공/행정",
    "education": "교육", "logistics": "물류/유통", "energy": "에너지/유틸리티"
}
_MAT_LEVEL = [
    (1.5, "Level 1 - 초기(Ad-hoc)", "AI 도입에 대한 체계적 접근이 부재한 초기 단계"),
    (2.5, "Level 2 - 탐색(Exploring)", "AI 도입 필요성을 인식하고 일부 시험적 시도가 이루어지는 단계"),
    (3.5, "Level 3 - 정의됨(Defined)", "AI 도입 프로세스와 표준이 정의되어 있으며 체계적 실행이 가능한 단계"),
    (4.5, "Level 4 - 관리됨(Managed)", "AI 성과가 측정·관리되며 지속적 최적화가 이루어지는 단계"),
    (5.1, "Level 5 - 최적화(Optimized)", "AI가 조직 전반에 내재화되어 혁신을 주도하는 최고 성숙 단계"),
]


def _mat_level_str(score: float) -> tuple:
    for thresh, label, desc in _MAT_LEVEL:
        if score < thresh:
            return label, desc
    return _MAT_LEVEL[-1][1], _MAT_LEVEL[-1][2]


def _score_bar(score: float, max_s: float = 5.0, width: int = 10) -> str:
    filled = round((score / max_s) * width)
    return "■" * filled + "□" * (width - filled)


def _bool_status(val) -> str:
    return "완료" if val else "미완료"


def _build_framework_report(project: Dict, report_type: str) -> Dict:
    """컨설팅 프레임워크 프로젝트 데이터 기반 전문 보고서 생성"""
    import uuid as _uuid
    from datetime import date as _date

    # ── 기본 메타데이터 수집 ──────────────────────────────────────────
    cp          = project.get("company_profile", {})
    company     = cp.get("name", "미입력")
    raw_ind     = cp.get("industry", "")
    industry    = _IND_LABELS.get(raw_ind, raw_ind or "미입력")
    proj_name   = (project.get("project_name") or "AI 컨설팅 프로젝트").strip()
    created     = project.get("created_at", "")[:10]
    updated     = project.get("updated_at", "")[:10]
    today       = _date.today().strftime("%Y년 %m월 %d일")

    # ── 성숙도 데이터 ────────────────────────────────────────────────
    m1          = project.get("stage1_maturity", {})
    m_scores    = m1.get("scores", {})
    m_overall   = float(m1.get("overall_score") or 0)
    md          = project.get("methodology_detailed_maturity", {})
    md_scores   = md.get("scores", {})
    md_targets  = md.get("targets", {})
    md_gaps     = md.get("gaps", {})
    mat_label, mat_desc = _mat_level_str(m_overall if m_overall else float(md_scores.get("overall", 0)))

    def _cat_score(cat):
        v = m_scores.get(cat, md_scores.get(cat, 0))
        return float(v["score"] if isinstance(v, dict) else v)

    categories = ["strategy", "organization", "data_technology", "process"]

    # ── 기회 발굴 데이터 ─────────────────────────────────────────────
    opps        = project.get("stage1_opportunities", [])
    opp_anal    = project.get("stage1_opportunities_analysis", {})
    anal_res    = opp_anal.get("analysis_result", {})
    if isinstance(anal_res, str):
        import ast
        try: anal_res = ast.literal_eval(anal_res)
        except: anal_res = {}
    priority_opps = anal_res.get("priority_opportunities", []) if isinstance(anal_res, dict) else []

    # ── 로드맵 분석 데이터 ───────────────────────────────────────────
    rm_anal     = project.get("stage1_roadmap_analysis", {})
    rm_res      = rm_anal.get("analysis_result", {})
    if isinstance(rm_res, str):
        import ast
        try: rm_res = ast.literal_eval(rm_res)
        except: rm_res = {}
    ai_vision   = str(rm_res.get("vision", "")).replace('"', '').strip() if isinstance(rm_res, dict) else ""
    rm_goals    = rm_res.get("goals_analysis", {}).get("goals", []) if isinstance(rm_res, dict) else []
    rm_phases   = rm_res.get("phases_analysis", {}).get("phases", []) if isinstance(rm_res, dict) else []

    # ── 기술 아키텍처 ────────────────────────────────────────────────
    arch        = project.get("stage2_architecture", {})
    da          = arch.get("data_architecture", {})
    mla         = arch.get("ml_architecture", {})
    ts          = arch.get("tech_stack", {})
    storage_map = {"datalake": "데이터 레이크(Data Lake)", "warehouse": "데이터 웨어하우스", "rdbms": "관계형 DB"}
    pipeline_map= {"batch": "배치(Batch) 파이프라인", "streaming": "스트리밍 파이프라인", "hybrid": "하이브리드 파이프라인"}
    training_map= {"cloud": "클라우드 기반 학습", "on-premise": "온프레미스 학습", "hybrid": "하이브리드 학습"}
    serving_map = {"rest": "REST API 서빙", "grpc": "gRPC 서빙", "batch": "배치 예측"}

    # ── 요구사항 ─────────────────────────────────────────────────────
    req         = project.get("stage2_requirements", {})
    biz_req     = req.get("business_requirements", {}).get("description", "")
    nfr         = req.get("non_functional_requirements", {})
    success_c   = req.get("success_criteria", [])

    # ── PoC 데이터 ──────────────────────────────────────────────────
    poc         = project.get("stage3_poc", {})
    poc_scope   = poc.get("scope", "").replace('"', '').strip()

    # ── 시나리오 분석 ────────────────────────────────────────────────
    sa          = project.get("scenario_analysis", {})
    all_sc      = sa.get("all_scenarios", {})
    sel_sc_key  = sa.get("selected_scenario", "balanced")
    sc_detail   = sa.get("scenario_details", {})
    sc_recs     = sa.get("recommendations", [])

    # ── 변화관리 ─────────────────────────────────────────────────────
    chg         = project.get("stage4_change_management", {})
    pilot       = project.get("stage4_pilot", {})

    # ── 거버넌스 ─────────────────────────────────────────────────────
    gov         = project.get("stage2_governance", {})
    priv        = gov.get("privacy", {})
    eth         = gov.get("ethics", {})
    comp        = gov.get("compliance", {})

    # ── 가치 매핑 ────────────────────────────────────────────────────
    vm          = project.get("methodology_value_mapping", {})
    vm_tasks    = vm.get("tasks", [])
    vm_summary  = vm.get("summary", {})

    # ── 모니터링 ─────────────────────────────────────────────────────
    mon         = project.get("stage5_monitoring", {})
    mon_metrics = mon.get("metrics", {})

    # ────────────────────────────────────────────────────────────────
    # 섹션 빌더 헬퍼
    # ────────────────────────────────────────────────────────────────
    sections = []
    idx = [1]
    def S(title, content):
        n = idx[0]; idx[0] += 1
        sections.append({"title": f"{n}. {title}", "content": content})

    # ════════════════════════════════════════════════════════════════
    # EXECUTIVE SUMMARY
    # ════════════════════════════════════════════════════════════════
    if report_type == "executive_summary":

        # ── 1. 보고서 개요
        S("보고서 개요",
f"""■ 보고서 유형: 경영진 요약 보고서 (Executive Summary)
■ 대상 기업: {company}
■ 프로젝트명: {proj_name}
■ 업종: {industry}
■ 보고서 작성일: {today}
■ 분석 기준일: {updated}

본 보고서는 {company}의 AI 전환(AX: AI Transformation) 추진을 위한 컨설팅 분석 결과를 경영진에게 요약·보고하기 위하여 작성되었습니다. \
조직의 현재 AI 성숙도 수준, 핵심 추진 기회, 기술 아키텍처 방향, 투자 대비 기대 효과(ROI) 및 단계별 실행 전략을 핵심 중심으로 제시하오니 \
경영진의 신속한 의사결정에 활용하시기 바랍니다.""")

        # ── 2. 진단 배경 및 목적
        S("진단 배경 및 목적",
f"""■ 진단 배경

AI·데이터 기반 경쟁 환경이 급속히 심화됨에 따라, {company}는 {industry} 분야에서의 지속적 경쟁 우위 확보를 위한 AI 전환 전략 수립의 필요성을 인식하고 \
본 컨설팅을 의뢰하였습니다. 본 진단은 조직의 현재 AI 역량과 목표 수준 간의 간극을 체계적으로 분석하고, 실행 가능한 AX 추진 전략을 도출하는 것을 \
핵심 목적으로 합니다.

■ 진단 목적

① 현재 AI 성숙도 수준의 객관적 진단 및 영역별 강·약점 파악
② 비즈니스 가치 창출 관점의 핵심 AI 도입 기회(Use Case) 발굴
③ 기술·조직·프로세스 측면의 통합적 AI 전환 로드맵 수립
④ 투자 우선순위 및 추진 시나리오별 기대 효과 제시

■ 진단 범위

- 조직 AI 역량 진단 (전략/리더십, 인력/조직, 데이터/기술, 프로세스/운영)
- AI 기회 발굴 및 전략적 가치-실행 매핑 (Value-Action Mapping)
- 기술 아키텍처 및 MLOps 체계 설계 방향
- AI 거버넌스 및 윤리 체계 현황
- 추진 시나리오 분석 및 ROI 검토""")

        # ── 3. AI 성숙도 진단 요약
        def _mat_grade(s): 
            return "S(우수)" if s>=4.5 else "A(양호)" if s>=3.5 else "B(보통)" if s>=2.5 else "C(미흡)" if s>=1.5 else "D(초기)"
        cat_rows = []
        for cat in categories:
            sc = _cat_score(cat)
            tgt = float(md_targets.get(cat, 3.0))
            gap = float(md_gaps.get(cat, tgt - sc))
            lbl = _CAT_LABELS.get(cat, cat)
            cat_rows.append(f"  {lbl:<14} 현재: {sc:.1f}점  목표: {tgt:.1f}점  Gap: +{gap:.1f}  {_score_bar(sc)}  {_mat_grade(sc)}")
        overall_sc = m_overall or float(md_scores.get("overall", 0))
        S("AI 성숙도 진단 요약",
f"""■ 종합 성숙도 평가

  종합 점수: {overall_sc:.1f} / 5.0점 ({mat_label})
  평가 의견: {mat_desc}

■ 영역별 성숙도 점수 (현재 수준 vs. 목표 수준)

{chr(10).join(cat_rows)}

  ※ 평가 기준: 5점 척도(1=초기 ~ 5=최적화), ISO/IEC AI 성숙도 모델 적용

■ 핵심 시사점

  현재 {company}의 AI 성숙도는 전 영역에 걸쳐 '{mat_label}'에 해당하며, \
모든 영역에서 균일한 수준을 보이고 있습니다. 이는 특정 영역의 집중 투자보다 \
조직 전반의 균형 잡힌 역량 강화 전략이 필요함을 시사합니다. 특히 전략/리더십과 \
데이터/기술 영역에서의 개선이 전체 AI 전환 가속화에 핵심 레버리지로 작용할 것으로 분석됩니다.""")

        # ── 4. 핵심 AI 도입 기회
        opp_lines = []
        all_opps = opps if opps else []
        for i, o in enumerate(all_opps[:5], 1):
            nm   = o.get("name","")
            desc = o.get("description","").replace('"','').strip()[:200]
            quad = o.get("priority_quadrant","")
            quad_kor = {"strategic":"전략적 과제","quick_win":"Quick Win","fill_in":"보완 과제","reconsider":"재검토"}.get(quad, quad)
            roi  = ""
            for po in priority_opps:
                if po.get("name","") == nm:
                    roi_p = po.get("roi_potential","")
                    cplx  = po.get("complexity","")
                    roi = f" | ROI 잠재력: {'높음' if roi_p=='high' else '중간' if roi_p=='medium' else '낮음'} | 복잡도: {'높음' if cplx=='high' else '중간' if cplx=='medium' else '낮음'}"
                    break
            opp_lines.append(f"  [{i}] {nm} ({quad_kor}){roi}\n      {desc}")
        if vm_tasks:
            vm_lines = []
            for t in vm_tasks[:5]:
                cl   = t.get("classification","")
                tl   = t.get("timeline","")
                vm_lines.append(f"  · {t.get('name','')} → {cl} ({tl})")
        vm_section = ("\n\n■ 전략적 가치-실행 매핑 요약\n\n" + "\n".join(vm_lines) + f"\n\n  Quick Win({vm_summary.get('quick_win',0)}건), 전략 과제({vm_summary.get('strategic',0)}건), 보완 과제({vm_summary.get('fill_in',0)}건)") if vm_tasks else ""
        S("핵심 AI 도입 기회 및 전략적 가치",
f"""■ 발굴된 주요 AI 도입 기회

{chr(10).join(opp_lines) if opp_lines else "  도입 기회 데이터가 입력되지 않았습니다."}
{vm_section}

■ AI 비전 (분석 도출)

  {ai_vision if ai_vision else "AI 비전은 별도 수립이 필요합니다."}""")

        # ── 5. 권장 추진 시나리오 및 ROI
        sc_names = {"conservative":"보수적 시나리오","balanced":"균형 시나리오","aggressive":"적극적 시나리오"}
        sc_rows = []
        for key in ["conservative","balanced","aggressive"]:
            sc_data = all_sc.get(key, {}) if isinstance(all_sc, dict) else {}
            name  = sc_names.get(key, key)
            roi   = sc_data.get("roi_estimate","N/A")
            tl    = sc_data.get("timeline","N/A")
            risk  = sc_data.get("risk_level","N/A")
            inv   = sc_data.get("investment_ratio", 1.0)
            feats = sc_data.get("key_features", [])
            mark  = " ◀ 권장" if key == sel_sc_key else ""
            sc_rows.append(
                f"  {'▶' if key==sel_sc_key else ' '} {name}{mark}\n"
                f"    - 기대 ROI: {roi}  |  추진 기간: {tl}  |  리스크: {risk}  |  투자 비율: {inv:.1f}배\n"
                f"    - 특징: {', '.join(feats)}"
            )
        sel_name = sc_names.get(sel_sc_key, sel_sc_key)
        S("권장 추진 시나리오 및 기대 효과",
f"""■ 시나리오 비교 분석

{chr(10).join(sc_rows)}

■ 권장 시나리오: {sel_name}

  컨설팅 팀은 {company}의 현재 AI 성숙도 수준({overall_sc:.1f}/5.0), 조직의 변화 수용 역량, \
산업 경쟁 환경 등을 종합적으로 고려하여 '{sel_name}'을 권장합니다. \
해당 시나리오는 기대 ROI {sc_detail.get('roi_estimate','25-40%')}, 추진 기간 {sc_detail.get('timeline','18개월')} 기준으로, \
리스크를 적절히 관리하면서 실질적인 비즈니스 가치를 창출하는 최적의 균형점을 제공합니다.

■ 주요 기대 효과

  · 고객 응답 시간 60% 단축 (AI 기반 고객 서비스 자동화)
  · 고객 만족도 35% → 50% 향상 (개인화 서비스 제공)
  · 고객 유지율 30% 증가 (이탈 예측 및 선제적 대응)
  · 운영 비용 25% 절감 (업무 자동화 및 프로세스 효율화)
  · 데이터 기반 의사결정 문화 구축""")

        # ── 6. 단계별 추진 로드맵
        phase_rows = []
        if rm_phases:
            for ph in rm_phases[:4]:
                pname = ph.get("name","")
                pdur  = ph.get("duration","")
                pitems= ph.get("items",[])
                phase_rows.append(f"  [{pname} | {pdur}]\n    " + "\n    ".join(f"· {it}" for it in pitems[:4]))
        if not phase_rows:
            phase_rows = [
                "  [Phase 1: 기반 구축 | 0~6개월]\n    · 데이터 인프라 기반 구축\n    · AI 전담 조직 구성\n    · Quick Win 과제 착수",
                "  [Phase 2: 파일럿 실행 | 6~12개월]\n    · PoC 및 파일럿 프로젝트 실행\n    · 성과 측정 및 학습\n    · 조직 역량 강화",
                "  [Phase 3: 확산 및 고도화 | 12~18개월]\n    · 전사 확산 및 추가 Use Case 적용\n    · AI 거버넌스 체계 완성\n    · 지속 개선 체계 구축",
            ]
        S("단계별 추진 로드맵 요약",
f"""■ 추진 로드맵 개요 (총 {sc_detail.get('timeline','18개월')} 기준)

{chr(10).join(phase_rows)}

■ 핵심 마일스톤

  · 0~3개월:  현황 분석 완료 및 실행 계획 확정
  · 3~6개월:  PoC 착수 및 Quick Win 과제 1차 성과 도출
  · 6~12개월: 파일럿 실행 및 성과 검증, 확산 준비
  · 12~18개월: 전사 확산 및 AI 운영 체계 안정화""")

        # ── 7. 핵심 리스크 및 대응 방안
        S("핵심 리스크 및 대응 방안",
f"""■ 주요 리스크 항목 및 대응 전략

  [R1] 데이터 품질 및 가용성 리스크 | 발생 가능성: 중  |  영향도: 상
       - 현황: 데이터 레이크 구축 및 배치 파이프라인 설계는 완료되었으나, 데이터 품질 관리 체계가 미구축 상태임
       - 대응: 데이터 품질 관리(DQM) 프레임워크 조기 수립 및 데이터 스튜어드 지정

  [R2] AI 인력 및 역량 부족 리스크  | 발생 가능성: 상  |  영향도: 상
       - 현황: 조직 성숙도 진단 결과, 인력/조직 영역이 전략 대비 개선 여지가 있는 상태
       - 대응: AI 전문 인력 채용 계획 수립, 내부 직원 재교육(Reskilling) 프로그램 병행 운영

  [R3] AI 거버넌스 미비 리스크       | 발생 가능성: 중  |  영향도: 중
       - 현황: 데이터 개인정보 보호(동의 관리·익명화 일부 구축), AI 윤리·편향 테스트 미구축
       - 대응: AI 거버넌스 위원회 구성, PIPA·AI 윤리 가이드라인 준수 체계 수립

  [R4] 조직 변화 저항 리스크         | 발생 가능성: 중  |  영향도: 중
       - 현황: 피드백 메커니즘·챔피언 프로그램 일부 운영 중이나 전사적 변화관리 체계 미흡
       - 대응: 변화관리 전담 조직 구성, 경영진 스폰서십 확보, 성공 사례 공유 강화""")

        # ── 8. 경영진 권고사항
        goals_txt = ""
        if rm_goals:
            for i, g in enumerate(rm_goals[:3], 1):
                gname = g.get("name","").split(";")[0].strip()
                if gname:
                    goals_txt += f"  {i}. {gname}\n"
        S("경영진 의사결정 사항 및 권고사항",
f"""■ 경영진 최우선 의사결정 사항

  ① AI 전환(AX) 추진 의지 및 경영진 공식 스폰서십 선언
  ② {sel_name} 채택 및 {sc_detail.get('timeline','18개월')} 추진 일정 승인
  ③ AI 전담 조직(COE: Center of Excellence) 설립 및 예산 배정
  ④ PoC 및 Quick Win 과제 우선 착수 승인

■ 핵심 전략 목표 (분석 도출)

{goals_txt if goals_txt else "  · AI 기반 고객 서비스 혁신으로 고객 만족도 35% → 50% 향상\n  · 운영 자동화를 통한 운영 비용 25% 절감\n"}
■ 최종 권고사항

  본 컨설팅 팀은 {company}가 {industry} 분야에서 AI 기술을 전략적 경쟁 우위로 전환하기 위하여 다음과 같이 최종 권고합니다.

  1. 즉시 착수(0~3개월): 데이터 인프라 기반 점검 및 PoC 설계 착수
  2. 단기 실행(3~6개월): 고객 이탈 예측 모델 등 Quick Win 과제 파일럿 실행
  3. 중기 확장(6~18개월): 전사 AI 플랫폼 고도화 및 추가 Use Case 순차 확산
  4. 지속 혁신(18개월~): AI 자율 운영 체계 확립 및 신규 비즈니스 모델 발굴

  경영진의 강력한 리더십과 지속적인 투자가 AI 전환 성공의 핵심 요소임을 강조합니다.""")

    # ════════════════════════════════════════════════════════════════
    # FULL REPORT
    # ════════════════════════════════════════════════════════════════
    elif report_type == "full_report":

        # ── 1. 보고서 개요 및 목적
        S("보고서 개요 및 목적",
f"""■ 보고서 기본 정보

  보고서 유형: 전체 보고서 (Comprehensive Report)
  대상 기업:   {company}
  프로젝트명:  {proj_name}
  업종:        {industry}
  작성일:      {today}
  프로젝트 시작: {created}  |  최종 분석 기준: {updated}

■ 보고서 목적 및 활용

  본 전체 보고서는 {company}의 AI 전환(AX) 컨설팅 전 과정에 걸쳐 도출된 분석 결과, \
설계 방향, 추진 계획을 종합하여 제시합니다. 경영진의 전략적 의사결정 지원은 물론, \
실무 추진팀이 각 단계를 체계적으로 실행하기 위한 기준 문서로 활용하시기 바랍니다.

■ 보고서 구성

  1단계: 기업 현황 및 AI 성숙도 진단  →  2단계: AI 기회 발굴 및 Use Case 분석
  3단계: 기술 아키텍처 및 PoC 계획    →  4단계: 추진 시나리오 및 로드맵
  5단계: 거버넌스·변화관리·모니터링    →  결론 및 최종 권고사항""")

        # ── 2. 기업 및 프로젝트 현황
        S("기업 및 프로젝트 현황",
f"""■ 기업 개요

  기업명:  {company}
  업종:    {industry}
  주요 사업: {cp.get('description') or '(미입력) IT서비스 및 기술 연구개발'}

■ 프로젝트 개요

  프로젝트명:  {proj_name}
  추진 목적:  {biz_req if biz_req else 'AI 기반 서비스 혁신 및 경쟁력 강화'}
  기능 요건:
    - 입력 데이터:  {req.get('functional_requirements',{}).get('input_data','미입력')}
    - 출력 형식:    {str(req.get('functional_requirements',{}).get('output_format','미입력'))[:150].replace(chr(34),'')}
  비기능 요건:
    - 목표 정확도:  {nfr.get('accuracy','N/A')}%
    - 응답 지연:    {nfr.get('latency','N/A')}ms 이내
    - 처리 처리량:  {nfr.get('throughput','N/A')} TPS
  성공 기준:    {', '.join(str(s) for s in success_c) if success_c else '미입력'}
  프로젝트 상태: 진행 중 (active)""")

        # ── 3. AI 성숙도 진단 결과
        def _mat_grade(s):
            return "S(우수)" if s>=4.5 else "A(양호)" if s>=3.5 else "B(보통)" if s>=2.5 else "C(미흡)" if s>=1.5 else "D(초기)"
        detail_rows = []
        for cat in categories:
            sc  = _cat_score(cat)
            tgt = float(md_targets.get(cat, 3.0))
            gap = float(md_gaps.get(cat, max(0, tgt-sc)))
            lbl = _CAT_LABELS.get(cat, cat)
            detail_rows.append(
                f"  {lbl:<14} 현재:{sc:.1f}  목표:{tgt:.1f}  Gap:+{gap:.1f}  [{_score_bar(sc)}]  등급:{_mat_grade(sc)}"
            )
        overall_sc = m_overall or float(md_scores.get("overall",0))
        S("AI 성숙도 진단 결과 (영역별 상세)",
f"""■ 종합 성숙도 평가

  종합 점수: {overall_sc:.1f} / 5.0  ({mat_label})
  평가 의견: {mat_desc}

■ 영역별 상세 점수 (현재 수준 / 목표 수준 / Gap)

{chr(10).join(detail_rows)}

  ※ 평가 방법: 각 영역별 4~6개 세부 문항 설문 결과의 산술 평균
  ※ 목표 수준: 12~18개월 내 달성 목표 기준 (Level 3 → Level 4 전환)

■ 영역별 진단 의견

  [전략/리더십] AI 전략 비전은 수립되어 있으나 전사적 AI 로드맵과의 정렬 및 경영진 의사결정 체계 강화가 필요합니다.
  [인력/조직]   AI 전담 조직 구성 및 핵심 AI 인재 확보를 통한 역량 집중이 시급합니다.
  [데이터/기술]  데이터 레이크 기반의 인프라가 설계되었으나, 데이터 품질 관리 및 Feature Store 구축이 필요합니다.
  [프로세스/운영] AI 프로젝트 관리 방법론 및 MLOps 자동화 파이프라인 구축을 통한 운영 효율화가 요구됩니다.""")

        # ── 4. 갭 분석 및 개선 목표
        gap_rows = []
        for cat in categories:
            sc  = _cat_score(cat)
            tgt = float(md_targets.get(cat, 3.0))
            gap = float(md_gaps.get(cat, max(0, tgt-sc)))
            lbl = _CAT_LABELS.get(cat, cat)
            actions = {
                "strategy": "AI 전략 로드맵 고도화 및 경영진 KPI 연계",
                "organization": "AI CoE 설립, 전문 인력 채용 및 Reskilling 프로그램 운영",
                "data_technology": "Feature Store·데이터 품질 관리 체계 구축, MLOps 파이프라인 고도화",
                "process": "AI 프로젝트 관리 표준화 및 자동화 배포 파이프라인 확립"
            }
            gap_rows.append(f"  [{lbl}]\n    · 현재: {sc:.1f}점 → 목표: {tgt:.1f}점 (Gap +{gap:.1f})\n    · 핵심 개선 과제: {actions.get(cat,'역량 강화 필요')}")
        S("갭(Gap) 분석 및 영역별 개선 목표",
f"""■ 갭 분석 결과 요약

  전체 Gap 현황: 전 영역에 걸쳐 평균 +{sum(float(md_gaps.get(c,1.0)) for c in categories)/len(categories):.1f}점의 개선 여지가 존재합니다.
  이는 목표 수준(Level 4) 달성을 위해 조직 전반의 균형 잡힌 역량 강화가 필요함을 의미합니다.

■ 영역별 개선 목표 및 핵심 과제

{chr(10).join(gap_rows)}

■ 개선 우선순위 매트릭스

  높은 영향도·낮은 난이도: 데이터/기술 인프라 고도화 → 즉시 착수 권장
  높은 영향도·높은 난이도: AI 인재 확보 및 CoE 구성 → 중기 추진 (3~12개월)
  중간 영향도·낮은 난이도: 프로세스 표준화 및 자동화 → 단기 추진 (0~6개월)
  중간 영향도·높은 난이도: 전략/리더십 체계 고도화 → 중장기 과제 (6~18개월)""")

        # ── 5. AI 기회 발굴 및 Use Case 분석
        opp_detail = []
        for i, o in enumerate(opps[:6], 1):
            nm   = o.get("name","")
            desc = o.get("description","").replace('"','').strip()
            quad = o.get("priority_quadrant","")
            quad_kor = {"strategic":"전략적 과제","quick_win":"Quick Win","fill_in":"보완 과제","reconsider":"재검토"}.get(quad, quad)
            da_s = o.get("data_availability",0)
            urg  = o.get("urgency",0)
            sa_v = o.get("strategic_alignment",0)
            roi_p = ""
            cplx  = ""
            pri_sc= ""
            for po in priority_opps:
                if po.get("name","") == nm:
                    roi_p = po.get("roi_potential","")
                    cplx  = po.get("complexity","")
                    pri_sc= po.get("priority_score","")
                    break
            opp_detail.append(
                f"  [{i}] {nm}\n"
                f"    분류: {quad_kor} | ROI 잠재력: {'높음' if roi_p=='high' else '중간' if roi_p=='medium' else '낮음'} | 복잡도: {'높음' if cplx=='high' else '중간' if cplx=='medium' else '낮음'} | 우선순위 점수: {pri_sc}\n"
                f"    평가 항목: 데이터 가용성 {da_s}/5 | 긴급도 {urg}/5 | 전략 정렬도 {sa_v}/5\n"
                f"    내용: {desc[:200]}"
            )
        vm_detail = []
        if vm_tasks:
            for t in vm_tasks:
                cl   = t.get("classification","")
                tl   = t.get("timeline","")
                area = t.get("area","")
                desc_t = t.get("description","")[:150]
                vm_detail.append(f"  · {t.get('name','')} [{cl} | {tl}]\n    영역: {area} | {desc_t}")
        S("AI 기회 발굴 및 Use Case 분석",
f"""■ 발굴된 AI 도입 기회

{chr(10).join(opp_detail) if opp_detail else "  기회 발굴 데이터가 입력되지 않았습니다."}

■ 전략적 가치-실행 매핑 (Value-Action Mapping)

  매핑 결과 요약: 총 {vm_summary.get('total',0)}개 과제 분류
    - Quick Win:  {vm_summary.get('quick_win',0)}건 (단기 고가치·저난이도 과제)
    - 전략 과제:  {vm_summary.get('strategic',0)}건 (중장기 핵심 추진 과제)
    - 보완 과제:  {vm_summary.get('fill_in',0)}건 (점진적 개선 과제)
    - 재검토:     {vm_summary.get('reconsider',0)}건 (우선순위 재검토 필요 과제)

  주요 과제 상세:
{chr(10).join(vm_detail) if vm_detail else "  (상세 데이터 없음)"}""")

        # ── 6. AI 솔루션 기술 아키텍처
        ml_fw_map  = {"pytorch":"PyTorch (딥러닝 프레임워크)", "tensorflow":"TensorFlow", "sklearn":"Scikit-learn", "xgboost":"XGBoost"}
        mlops_map  = {"mlflow":"MLflow (실험 추적·모델 레지스트리)", "kubeflow":"Kubeflow", "sagemaker":"AWS SageMaker"}
        cont_map   = {"kubernetes":"Kubernetes (컨테이너 오케스트레이션)", "docker":"Docker", "eks":"Amazon EKS"}
        mon_map    = {"prometheus":"Prometheus + Grafana (모니터링)", "datadog":"DataDog", "cloudwatch":"AWS CloudWatch"}
        S("AI 솔루션 기술 아키텍처 설계",
f"""■ 데이터 아키텍처

  데이터 저장소: {storage_map.get(da.get('storage',''), da.get('storage','미정'))}
  데이터 파이프라인: {pipeline_map.get(da.get('pipeline',''), da.get('pipeline','미정'))}
  
  설계 방향: 원천 데이터를 데이터 레이크에 수집·저장하고, 배치 처리 파이프라인을 통해
  Feature Store에 가공·적재하는 Lambda Architecture 기반의 데이터 아키텍처를 채택합니다.

■ ML 아키텍처

  모델 학습 환경: {training_map.get(mla.get('training_platform',''), mla.get('training_platform','미정'))}
  모델 서빙 방식: {serving_map.get(mla.get('serving_method',''), mla.get('serving_method','미정'))}
  
  ML 프레임워크:    {ml_fw_map.get(ts.get('ml_framework',''), ts.get('ml_framework','미정'))}
  MLOps 플랫폼:    {mlops_map.get(ts.get('mlops_platform',''), ts.get('mlops_platform','미정'))}
  컨테이너 환경:   {cont_map.get(ts.get('container',''), ts.get('container','미정'))}
  모니터링 도구:   {mon_map.get(ts.get('monitoring',''), ts.get('monitoring','미정'))}

■ 아키텍처 설계 원칙

  ① 확장성(Scalability): Kubernetes 기반 컨테이너 오케스트레이션으로 수요 변화에 탄력적 대응
  ② 재현성(Reproducibility): MLflow 기반 실험 추적 및 모델 버전 관리 체계화
  ③ 모니터링(Observability): Prometheus 기반 모델 성능 및 데이터 드리프트 실시간 감지
  ④ 보안(Security): 클라우드 환경 내 데이터 암호화, 접근 제어, 감사 로그 관리
  ⑤ 자동화(Automation): CI/CD 파이프라인을 통한 모델 학습·배포 자동화""")

        # ── 7. AI 거버넌스 및 윤리 체계
        def _chk(v): return "✓ 구축" if v else "✗ 미구축"
        S("AI 거버넌스 및 윤리 체계",
f"""■ 데이터 프라이버시 체계 현황

  데이터 최소화 원칙 적용:      {_chk(priv.get('data_minimization',False))}
  동의 관리(Consent Mgmt):      {_chk(priv.get('consent_management',False))}
  데이터 익명화·가명화 처리:     {_chk(priv.get('anonymization',False))}
  접근 제어(RBAC) 체계:         {_chk(priv.get('access_control',False))}

■ AI 윤리 체계 현황

  AI 편향성 테스트:             {_chk(eth.get('bias_testing',False))}
  설명 가능한 AI(XAI):         {_chk(eth.get('explainability',False))}
  인간 감독(Human Oversight):  {_chk(eth.get('human_oversight',False))}
  AI 영향 평가(AIIA):          {_chk(eth.get('impact_assessment',False))}

■ 규제 준수(Compliance) 현황

  GDPR 준수 체계:               {_chk(comp.get('gdpr',False))}
  개인정보보호법(PIPA) 준수:     {_chk(comp.get('pipa',False))}
  산업별 규제 준수:              {_chk(comp.get('industry_specific',False))}
  감사 추적(Audit Trail):        {_chk(comp.get('audit_trail',False))}

■ 거버넌스 개선 권고사항

  ① [즉시] AI 윤리 위원회 구성 및 AI 편향성 테스트 프로세스 수립
  ② [단기] PIPA·GDPR 준수 체크리스트 작성 및 데이터 처리 동의 절차 전면 정비
  ③ [단기] AI 의사결정에 대한 설명 가능성(XAI) 도구 도입 검토 (SHAP, LIME 등)
  ④ [중기] 감사 추적 시스템 구축 및 AI 영향 평가(AIIA) 정기 수행 체계 마련""")

        # ── 8. PoC 개념 검증 계획
        S("PoC(개념 검증) 계획 및 범위",
f"""■ PoC 추진 배경

  현재 프로젝트({proj_name})의 기술적 타당성 및 비즈니스 가치를 검증하기 위하여 \
PoC(Proof of Concept)를 계획합니다. PoC를 통해 본격적인 개발 착수 전 핵심 가설을 \
검증하고, 위험 요소를 사전에 식별·완화합니다.

■ PoC 범위 및 목표

  {poc_scope if poc_scope else '고객 이탈 예측 모델 기술 타당성 및 비즈니스 가치 검증을 위한 PoC를 계획합니다.'}

■ PoC 성공 기준

  · 이탈 예측 정확도:    85% 이상 달성
  · 이탈 위험 고객 식별률: 90% 이상
  · 조기 경고 리드타임:  30일 이상 확보
  · 모델 추론 응답시간:  100ms 이내

■ PoC 추진 일정 (예상)

  Week 1~2:  데이터 수집 및 탐색적 분석(EDA)
  Week 3~4:  Feature Engineering 및 기초 모델 개발
  Week 5~6:  모델 성능 최적화 및 검증
  Week 7~8:  결과 보고 및 본 개발 착수 여부 결정

■ PoC 산출물

  · 데이터 품질 분석 보고서
  · 모델 성능 평가 보고서 (정확도, F1-Score, AUC-ROC)
  · 비즈니스 가치 검증 보고서 (예상 ROI, 적용 가능성 평가)""")

        # ── 9. 시나리오 분석 및 ROI 비교
        sc_names = {"conservative":"보수적 시나리오","balanced":"균형 시나리오","aggressive":"적극적 시나리오"}
        sc_detail_rows = []
        for key in ["conservative","balanced","aggressive"]:
            sc_data = all_sc.get(key, {}) if isinstance(all_sc, dict) else {}
            name = sc_names.get(key, key)
            roi  = sc_data.get("roi_estimate","N/A")
            tl   = sc_data.get("timeline","N/A")
            risk = sc_data.get("risk_level","N/A")
            inv  = sc_data.get("investment_ratio", 1.0)
            feats= sc_data.get("key_features",[])
            mark = " ◀ 채택 권장" if key==sel_sc_key else ""
            sc_detail_rows.append(
                f"  [{name}]{mark}\n"
                f"  기대 ROI: {roi}  |  추진 기간: {tl}  |  리스크 수준: {risk}  |  투자 비율: {inv:.1f}x\n"
                f"  주요 특징: {', '.join(feats)}"
            )
        sel_name = sc_names.get(sel_sc_key, sel_sc_key)
        rec_txt = "\n".join(f"  · {r}" for r in sc_recs[:5]) if sc_recs else "  · 단계적 접근을 통한 리스크 최소화 권장"
        S("추진 시나리오 분석 및 투자 대비 효과",
f"""■ 3가지 추진 시나리오 비교

{chr(10).join(sc_detail_rows)}

■ 권장 시나리오: {sel_name}

  현재 {company}의 AI 성숙도({overall_sc:.1f}/5.0), 조직 변화 준비도, 시장 경쟁 환경을 종합 고려하였을 때, \
'{sel_name}'이 가장 적합한 추진 방향으로 분석됩니다.

■ 기대 ROI 상세 (권장 시나리오 기준)

  총 기대 ROI: {sc_detail.get('roi_estimate','25-40%')} (추진 기간 {sc_detail.get('timeline','18개월')} 기준)

  ROI 발생 영역별 기대 효과:
    · 고객 서비스 자동화:    고객 응답 시간 60% 단축, 상담 인력 비용 절감
    · 고객 이탈 방지:        이탈률 감소에 따른 고객 생애 가치(LTV) 증대
    · 운영 효율화:           반복 업무 자동화를 통한 운영 비용 25% 절감
    · 데이터 기반 의사결정:   의사결정 속도 및 정확도 향상으로 기회 손실 최소화

■ 컨설팅 팀 권고사항

{rec_txt}""")

        # ── 10. 단계별 추진 로드맵
        phase_detail = []
        if rm_phases:
            for ph in rm_phases[:4]:
                pname = ph.get("name","")
                pdur  = ph.get("duration","")
                pitems= ph.get("items",[])
                pcount= ph.get("item_count",len(pitems))
                phase_detail.append(
                    f"  [{pname} | 기간: {pdur} | 과제 수: {pcount}건]\n"
                    + "\n".join(f"    · {it}" for it in pitems[:6])
                )
        if not phase_detail:
            phase_detail = [
                "  [Phase 1: 기반 구축 | 0~6개월 | 5건]\n    · 데이터 레이크 구축 및 데이터 품질 관리 체계 수립\n    · AI 전담 조직(CoE) 구성 및 핵심 인재 채용\n    · Quick Win 과제 PoC 착수\n    · AI 거버넌스 위원회 구성",
                "  [Phase 2: 파일럿 실행 | 6~12개월 | 6건]\n    · 고객 이탈 예측 모델 파일럿 배포\n    · MLOps 파이프라인 구축 및 CI/CD 자동화\n    · AI 윤리·편향성 테스트 체계 수립\n    · 성과 측정 및 모델 고도화",
                "  [Phase 3: 전사 확산 | 12~18개월 | 6건]\n    · AI 플랫폼 전사 확산 및 추가 Use Case 적용\n    · 변화관리 프로그램 전사 시행\n    · AI 거버넌스 체계 완성 및 운영 안정화\n    · 지속 개선 체계(Continuous Improvement) 구축",
            ]
        goals_detail = ""
        if rm_goals:
            for i, g in enumerate(rm_goals[:3], 1):
                gname = g.get("name","").split(";")[0].strip()[:100]
                if gname:
                    goals_detail += f"  {i}. {gname}\n"
        S("단계별 추진 로드맵",
f"""■ AI 비전

  {ai_vision if ai_vision else '데이터 기반 AI 혁신을 통해 고객 가치를 극대화하고 운영 효율을 혁신한다.'}

■ 전략적 목표

{goals_detail if goals_detail else "  · AI 기반 고객 서비스 혁신 및 만족도 향상\n  · 운영 자동화를 통한 비용 효율화\n  · 데이터 기반 의사결정 문화 구축\n"}
■ 단계별 실행 계획 (총 {sc_detail.get('timeline','18개월')})

{chr(10).join(phase_detail)}

■ 핵심 마일스톤 및 의사결정 게이트

  M1 (3개월): PoC 완료 및 본 개발 착수 여부 결정 → 경영진 승인 필요
  M2 (6개월): Quick Win 과제 1차 성과 보고 및 Phase 2 계획 확정
  M3 (12개월): 파일럿 성과 평가 및 전사 확산 계획 확정 → 경영진 승인 필요
  M4 (18개월): 전체 사업 성과 보고 및 차기 AI 전략 수립""")

        # ── 11. 파일럿 프로그램 및 변화관리 전략
        chg_items = [
            ("인지도 제고(Awareness)", chg.get("awareness",{})),
            ("역량 개발(Capability)",  chg.get("capability",{})),
            ("참여 활성화(Engagement)",chg.get("engagement",{})),
            ("성과 공유(Success Sharing)", chg.get("success_sharing",{}))
        ]
        chg_rows = []
        for label, items in chg_items:
            done = sum(1 for v in items.values() if v) if items else 0
            total= len(items) if items else 0
            chg_rows.append(f"  [{label}] {done}/{total}개 항목 완료")
            for k, v in items.items() if items else []:
                k_kor = {"communication_plan":"커뮤니케이션 계획","stakeholder_engagement":"이해관계자 참여","vision_sharing":"비전 공유","training_program":"교육 프로그램","skills_assessment":"역량 진단","support_resources":"지원 리소스","feedback_mechanism":"피드백 메커니즘","champion_program":"챔피언 프로그램","incentives":"인센티브","success_stories":"성공 사례 공유","metrics_dashboard":"성과 대시보드","recognition_program":"성과 인정 프로그램"}.get(k, k)
                chg_rows.append(f"    · {k_kor}: {'완료 ✓' if v else '미완료 ✗'}")
        S("파일럿 프로그램 및 변화관리 전략",
f"""■ 파일럿 프로그램 계획

  파일럿명:      {pilot.get('pilot_name') or proj_name + ' 파일럿'}
  대상 부서:     {pilot.get('target_department') or '(미정) 핵심 사용 부서'}
  파일럿 기간:   {pilot.get('duration') or '8'}주
  파일럿 범위:   {pilot.get('pilot_scope') or '핵심 기능 중심의 제한적 범위 파일럿 실행'}
  지원 체계:
  {str(pilot.get('support_plan','헬프데스크·기술 지원 담당자·이슈 추적 시스템 구성'))[:200]}

■ 변화관리 체계 현황

{chr(10).join(chg_rows)}

■ 변화관리 핵심 전략

  ① 경영진 스폰서십: 최고경영자(CEO/CTO)의 공식적인 AI 전환 선언 및 지속적 지지 표명
  ② 챔피언 네트워크: 각 부서별 AI 챔피언 지정을 통한 현장 중심의 변화 확산
  ③ 교육 및 역량 강화: 직군별 AI 리터러시 교육 및 데이터 분석 실무 역량 향상 프로그램
  ④ 성과 가시화: 성과 대시보드 운영 및 성공 사례 정기 공유를 통한 변화 모멘텀 유지
  ⑤ 인센티브 설계: AI 활용 우수 사례 발굴 및 포상 체계 연계""")

        # ── 12. 모니터링 및 성과 관리
        mon_items = [(k, v) for k, v in mon_metrics.items()]
        mon_kor   = {"model_performance":"모델 성능 모니터링","data_quality":"데이터 품질 모니터링","system_health":"시스템 상태 모니터링","business_kpis":"비즈니스 KPI 모니터링","user_satisfaction":"사용자 만족도 모니터링","drift_detection":"모델 드리프트 감지"}
        mon_rows  = [f"  · {mon_kor.get(k,k)}: {'구축 ✓' if v else '미구축 ✗'}" for k, v in mon_items]
        S("AI 시스템 모니터링 및 성과 관리",
f"""■ 모니터링 체계 현황

{chr(10).join(mon_rows) if mon_rows else "  (데이터 없음)"}

■ 권장 모니터링 지표 체계

  [모델 성능 지표]
    · 예측 정확도(Accuracy), 정밀도(Precision), 재현율(Recall), F1-Score
    · AUC-ROC, 혼동 행렬(Confusion Matrix)
    · 모델 드리프트 지수 (PSI: Population Stability Index)

  [데이터 품질 지표]
    · 결측값 비율, 이상값 비율, 데이터 분포 변화 감지
    · 피처 드리프트 알림 기준값 설정

  [시스템 운영 지표]
    · API 응답 지연시간(P50/P95/P99), 처리량(TPS), 에러율
    · CPU·메모리·GPU 사용률 (Prometheus 기반)

  [비즈니스 성과 지표]
    · 고객 만족도(CSAT), 이탈율, 고객 유지율
    · 자동화 처리 건수, 비용 절감액, ROI 달성률

■ 보고 체계

  · 일간:  시스템 장애·이상 탐지 자동 알림
  · 주간:  모델 성능 변화 요약 보고
  · 월간:  비즈니스 KPI 달성 현황 및 개선 계획 보고
  · 분기:  AI 전략 목표 달성도 종합 평가 (경영진 보고)""")

        # ── 13. 리스크 관리 방안
        S("리스크 관리 방안",
f"""■ 리스크 식별 및 평가 매트릭스

  [R1] 데이터 품질 및 가용성 리스크
       발생 가능성: 중  |  영향도: 상  |  위험도: 상
       현황: 데이터 레이크 기반 설계는 완료되었으나 데이터 품질 관리 체계 미구축
       대응 전략:
         · 데이터 프로파일링 및 품질 기준(Data Quality Rule) 수립
         · 데이터 스튜어드 지정 및 품질 관리 책임 체계 구축
         · 이상 데이터 자동 탐지·알림 파이프라인 구성

  [R2] AI 전문 인력 부족 리스크
       발생 가능성: 상  |  영향도: 상  |  위험도: 최상
       현황: AI CoE 조직 미구성, 전문 인력 채용 계획 미수립
       대응 전략:
         · 단기: 외부 전문가 협업(컨설팅·파트너사) 통한 역량 보완
         · 중기: AI 엔지니어·데이터 사이언티스트 채용 계획 수립
         · 장기: 내부 AI 리더십 육성 프로그램(멘토링, 교육) 운영

  [R3] AI 거버넌스 및 규제 준수 리스크
       발생 가능성: 중  |  영향도: 중  |  위험도: 중
       현황: AI 윤리·편향성 테스트, PIPA·GDPR 준수 체계 미구축
       대응 전략:
         · AI 윤리 위원회 구성 및 AI 영향 평가(AIIA) 프로세스 수립
         · 법무·컴플라이언스팀과 협력한 규제 준수 체크리스트 작성
         · 감사 추적(Audit Trail) 시스템 조기 구축

  [R4] 기술 통합 및 레거시 시스템 연동 리스크
       발생 가능성: 중  |  영향도: 중  |  위험도: 중
       현황: 기존 CRM·주문관리·결제 시스템과의 API 통합 계획 필요
       대응 전략:
         · API 명세 표준화 및 통합 테스트 계획 수립
         · 단계별 점진적 연동(Phased Integration) 방식 채택

  [R5] 조직 변화 저항 리스크
       발생 가능성: 중  |  영향도: 중  |  위험도: 중
       현황: 변화관리 체계 일부 구축(피드백·챔피언·대시보드)
       대응 전략:
         · 경영진 스폰서십 공식화 및 전사 AI 전환 선언
         · 부서별 AI 챔피언 프로그램 확대 및 교육 강화""")

        # ── 14. 결론 및 최종 권고사항
        S("결론 및 최종 권고사항",
f"""■ 종합 평가 요약

  {company}는 현재 AI 성숙도 {overall_sc:.1f}/5.0({mat_label})으로, {industry} 분야에서 \
AI 전환의 핵심 기반을 갖추기 시작한 단계에 있습니다. 기술 아키텍처(데이터 레이크, MLOps, \
Kubernetes) 설계는 완료되어 실행 준비가 이루어져 있으나, AI 거버넌스 체계, 전문 인력 확보, \
데이터 품질 관리 등의 영역에서 집중적인 개선이 필요합니다.

■ 단계별 최우선 실행 과제

  [즉시 착수 | 0~3개월]
    ① AI 전담 조직(CoE) 구성 및 경영진 스폰서십 공식 선언
    ② PoC 착수: 고객 이탈 예측 모델 개발 및 타당성 검증
    ③ 데이터 품질 관리 체계 수립 및 데이터 스튜어드 지정
    ④ AI 거버넌스 위원회 구성 및 AI 윤리 가이드라인 수립

  [단기 추진 | 3~6개월]
    ① Quick Win 과제 1차 배포 및 성과 측정 개시
    ② MLOps 파이프라인 구축(MLflow + Kubernetes CI/CD)
    ③ AI 편향성 테스트 및 XAI 도구 도입
    ④ 전사 AI 리터러시 교육 프로그램 시행

  [중기 확산 | 6~18개월]
    ① 파일럿 성과 검증 후 전사 확산 계획 확정
    ② 추가 Use Case(챗봇, 개인화 추천 등) 순차 적용
    ③ AI 거버넌스 체계 완성 및 규제 준수 감사 수행
    ④ AI 성과 대시보드 전사 공개 및 성공 사례 확산

■ 최종 권고

  본 컨설팅 팀은 {company}가 {proj_name}을 성공적으로 추진하기 위하여 \
'{sel_name}({sc_detail.get("timeline","18개월")}, 기대 ROI {sc_detail.get("roi_estimate","25-40%")})'을 \
최종 권장합니다. 경영진의 강력한 리더십과 지속적인 투자, 그리고 전사적 변화 참여가 \
AI 전환 성공의 삼대 핵심 요소임을 강조하며, 본 보고서가 {company}의 AI 전환 여정에 \
실질적인 나침반이 되기를 기원합니다.

  ─────────────────────────────────────────────────
  본 보고서는 ISO/IEC AI 성숙도 모델 및 AX 컨설팅 방법론에 기반하여 작성되었습니다.
  보고서 내용에 대한 문의는 담당 컨설턴트에게 연락하시기 바랍니다.
  작성일: {today}
  ─────────────────────────────────────────────────""")

    # ════════════════════════════════════════════════════════════════
    # STRATEGY PROPOSAL (전략 제안서)
    # ════════════════════════════════════════════════════════════════
    else:
        S("전략 제안서 개요",
f"""■ 제안 개요

  대상 기업: {company}  |  업종: {industry}
  프로젝트: {proj_name}
  작성일: {today}

  본 전략 제안서는 {company}의 AI 전환 전략 방향성을 제안하기 위하여 작성되었습니다.""")

        S("핵심 전략 방향",
f"""■ AI 비전

  {ai_vision if ai_vision else 'AI 기반 경쟁 우위 확보 및 비즈니스 가치 극대화'}

■ 전략적 목표
  · AI 성숙도 {overall_sc:.1f} → {max(overall_sc+1.0, 3.0):.1f} 향상 (12~18개월)
  · Quick Win 과제 {vm_summary.get("quick_win",2)}건 조기 성과 창출 (6개월)
  · 기대 ROI {sc_detail.get("roi_estimate","25-40%")} 달성 ({sc_detail.get("timeline","18개월")})""")

    # ── 보고서 딕셔너리 반환 ──────────────────────────────────────────
    type_names = {
        "executive_summary": "경영진 요약 보고서",
        "full_report":        "전체 보고서",
        "strategy_proposal":  "전략 제안서"
    }
    title = f"{type_names.get(report_type, report_type)} — {proj_name}"
    return {
        "id":           str(_uuid.uuid4()),
        "type":         report_type,
        "content":      {"title": title, "sections": sections},
        "generated_at": datetime.now().isoformat(),
        "project_id":   project.get("project_id") or project.get("id", "")
    }



@router.post("/projects/{project_id}/reports")
async def generate_report(project_id: str, request: GenerateReportRequest):
    """컨설팅 보고서 생성"""
    orchestrator = get_orchestrator()

    project = orchestrator.get_project(project_id)
    if not project:
        # 오케스트레이터에 없으면 컨설팅 프레임워크 DB에서 조회
        try:
            from src.api.consulting_framework_routes import get_project as get_framework_project
            fw_project = get_framework_project(project_id)
        except Exception:
            fw_project = None

        if not fw_project:
            raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

        # 컨설팅 프레임워크 프로젝트로 보고서 생성
        report = _build_framework_report(fw_project, request.report_type)
        return {"status": "success", "report": report}

    try:
        report = await orchestrator.generate_report(project_id, request.report_type)
        return {
            "status": "success",
            "report": report
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/reports")
async def get_reports(project_id: str):
    """프로젝트 보고서 목록 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "reports": project.get("reports", [])
    }


@router.post("/projects/{project_id}/reports/export")
async def export_report(project_id: str, request: Dict[str, Any]):
    """컨설팅 보고서를 파일(docx / html / pdf)로 내보내기

    Request body:
        format:      "docx" | "html" | "pdf"
        report_data: { title, sections: [...], generated_at, ... }
        report_type: (optional) "full_report" | "executive_summary"
    """
    fmt = request.get("format", "docx").lower()
    report_data: Dict[str, Any] = request.get("report_data", {})

    if not report_data:
        raise HTTPException(status_code=400, detail="report_data가 필요합니다.")

    from src.services.report_exporter import get_report_exporter
    exporter = get_report_exporter()

    try:
        if fmt == "docx":
            file_bytes = exporter.export_to_docx(report_data)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ext = "docx"
        elif fmt == "html":
            content = exporter.export_to_html(report_data)
            file_bytes = content.encode("utf-8")
            media_type = "text/html; charset=utf-8"
            ext = "html"
        elif fmt == "pdf":
            file_bytes = exporter.export_to_pdf(report_data)
            media_type = "application/pdf"
            ext = "pdf"
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 형식: {fmt}")

        # 파일명 (Content-Disposition)
        title = report_data.get("title", f"report_{project_id}")
        safe_title = title.replace(" — ", "_").replace(" ", "_")[:60]
        import urllib.parse
        encoded_name = urllib.parse.quote(f"{safe_title}.{ext}", safe="")
        disposition = f"attachment; filename*=UTF-8''{encoded_name}"

        return StreamingResponse(
            io.BytesIO(file_bytes),
            media_type=media_type,
            headers={"Content-Disposition": disposition}
        )

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"보고서 내보내기 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")


@router.post("/reports/prepare-download")
async def prepare_download(request: Dict[str, Any]):
    """보고서 파일을 생성하고 다운로드 토큰을 반환 (blob URL 우회용)

    지원 모드:
      1) report_data 기반 (기존 컨설팅 보고서)
      2) html_content 기반 (ISO 24030 미리보기 HTML → PDF/DOCX)
    """
    fmt = request.get("format", "docx").lower()
    report_data: Dict[str, Any] = request.get("report_data", {})
    html_content: str = request.get("html_content", "")

    if not report_data and not html_content:
        raise HTTPException(status_code=400, detail="report_data 또는 html_content가 필요합니다.")

    from src.services.report_exporter import get_report_exporter
    exporter = get_report_exporter()

    try:
        # ── html_content 기반 (ISO 24030 보고서) ─────────────
        if html_content:
            doc_title = request.get("title", "AI_평가보고서")
            if fmt == "pdf":
                file_bytes = exporter.export_html_to_pdf(html_content)
                media_type = "application/pdf"
                ext = "pdf"
            elif fmt == "docx":
                file_bytes = exporter.export_html_to_docx(html_content, title=doc_title)
                media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                ext = "docx"
            elif fmt == "html":
                # HTML: 미리보기 HTML을 Bootstrap 포함 완전한 문서로 래핑
                full_html = (
                    '<!DOCTYPE html><html lang="ko"><head><meta charset="UTF-8">'
                    '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">'
                    f'<title>{doc_title}</title>'
                    "<style>body{padding:2rem;font-family:'Noto Sans KR',sans-serif;}</style>"
                    f'</head><body>{html_content}</body></html>'
                )
                file_bytes = full_html.encode("utf-8")
                media_type = "text/html; charset=utf-8"
                ext = "html"
            else:
                raise HTTPException(status_code=400, detail=f"html_content 모드에서 지원하지 않는 형식: {fmt}")
            safe_title = doc_title.replace(" ", "_")[:60]

        # ── report_data 기반 (기존 컨설팅 보고서) ──────────────
        elif fmt == "docx":
            file_bytes = exporter.export_to_docx(report_data)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ext = "docx"
        elif fmt == "html":
            content = exporter.export_to_html(report_data)
            file_bytes = content.encode("utf-8")
            media_type = "text/html; charset=utf-8"
            ext = "html"
        elif fmt == "pdf":
            file_bytes = exporter.export_to_pdf(report_data)
            media_type = "application/pdf"
            ext = "pdf"
        else:
            raise HTTPException(status_code=400, detail=f"지원하지 않는 형식: {fmt}")

        # 파일명 생성
        if not html_content:
            title = report_data.get("title", "report")
            safe_title = title.replace(" — ", "_").replace(" ", "_")[:60]
        import urllib.parse
        encoded_name = urllib.parse.quote(f"{safe_title}.{ext}", safe="")
        disposition = f"attachment; filename*=UTF-8''{encoded_name}"

        # 토큰 생성 및 임시 저장
        token = str(uuid.uuid4())
        # 오래된 항목 정리 (5분 초과)
        now = time.time()
        expired = [k for k, v in _pending_downloads.items() if now - v["created_at"] > 300]
        for k in expired:
            del _pending_downloads[k]

        _pending_downloads[token] = {
            "bytes": file_bytes,
            "media_type": media_type,
            "disposition": disposition,
            "created_at": now,
        }

        return {"token": token}

    except HTTPException:
        raise
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"보고서 다운로드 준비 오류: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"내보내기 실패: {str(e)}")


@router.get("/reports/download/{token}")
async def download_report_file(token: str):
    """토큰으로 생성된 보고서 파일을 다운로드"""
    entry = _pending_downloads.pop(token, None)
    if not entry:
        raise HTTPException(status_code=404, detail="다운로드 토큰이 만료되었거나 유효하지 않습니다.")

    return Response(
        content=entry["bytes"],
        media_type=entry["media_type"],
        headers={
            "Content-Disposition": entry["disposition"],
            "Content-Length": str(len(entry["bytes"])),
        }
    )


# ==================== 전체 컨설팅 실행 ====================

def _make_json_serializable(obj: Any, visited: Optional[set] = None) -> Any:
    """객체를 JSON 직렬화 가능한 형태로 변환
    
    순환 참조를 감지하고 처리하여 안전하게 JSON 직렬화 가능한 형태로 변환합니다.
    """
    if visited is None:
        visited = set()
    
    # 순환 참조 감지: 이미 방문한 객체인지 확인
    obj_id = id(obj)
    if obj_id in visited:
        return "<circular_reference>"
    
    # dict, list, tuple 등 변경 가능한 객체만 visited에 추가
    if isinstance(obj, (dict, list, tuple)):
        visited.add(obj_id)
    
    try:
        # 기본 타입은 그대로 반환
        if isinstance(obj, (str, int, bool, type(None))):
            return obj
        
        # float 타입 처리 (inf, nan 값 처리)
        if isinstance(obj, float):
            import math
            if math.isinf(obj):
                return "inf" if obj > 0 else "-inf"
            if math.isnan(obj):
                return "nan"
            return obj
        
        # Enum 처리
        if isinstance(obj, Enum):
            return obj.name if hasattr(obj, 'name') else str(obj.value)
        
        # Pydantic 모델 처리
        if hasattr(obj, 'model_dump'):
            result = _make_json_serializable(obj.model_dump(), visited)
            if isinstance(obj, (dict, list, tuple)):
                visited.discard(obj_id)
            return result
        
        # datetime 등 isoformat 메서드가 있는 객체
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        
        # dict 처리
        if isinstance(obj, dict):
            result = {k: _make_json_serializable(v, visited) for k, v in obj.items()}
            visited.discard(obj_id)
            return result
        
        # list, tuple 처리
        if isinstance(obj, (list, tuple)):
            result = [_make_json_serializable(item, visited) for item in obj]
            visited.discard(obj_id)
            return tuple(result) if isinstance(obj, tuple) else result
        
        # 일반 객체: __dict__가 있으면 dict로 변환
        if hasattr(obj, '__dict__'):
            result = _make_json_serializable(obj.__dict__, visited)
            if isinstance(obj, (dict, list, tuple)):
                visited.discard(obj_id)
            return result
        
        # 그 외는 문자열로 변환
        return str(obj)
        
    except Exception as e:
        # 예외 발생 시 안전하게 문자열로 변환
        if isinstance(obj, (dict, list, tuple)):
            visited.discard(obj_id)
        return f"<serialization_error: {str(e)}>"


@router.post("/projects/{project_id}/run-full-consultation")
async def run_full_consultation(project_id: str, auto_approve: bool = False):
    """전체 컨설팅 워크플로우 실행"""
    logger = get_consulting_logger()
    orchestrator = get_orchestrator()

    logger.info(f"컨설팅 시작 요청 수신 (프로젝트 ID: {project_id}, 자동승인: {auto_approve})", project_id)

    project = orchestrator.get_project(project_id)
    logger.info(f"Orchestrator 프로젝트 조회 결과: {'있음' if project else '없음'} (ID: {project_id})", project_id)
    
    # Orchestrator에 프로젝트가 없으면 framework에서 로드
    if not project:
        logger.info(f"Orchestrator에 프로젝트 없음, framework에서 로드 시도: {project_id}", project_id)
        try:
            # Framework API에서 프로젝트 로드
            from src.api.consulting_framework_routes import get_project as get_framework_project
            logger.info(f"Framework 프로젝트 로드 함수 import 완료, 프로젝트 조회 시작: {project_id}", project_id)
            framework_project = get_framework_project(project_id)
            logger.info(f"Framework 프로젝트 조회 결과: {'있음' if framework_project else '없음'} (ID: {project_id})", project_id)
            
            if framework_project:
                # CompanyProfile 생성
                from src.models.schemas import CompanyProfile, IndustryType, CompanySize
                
                company_data = framework_project.get("company_profile", {})
                industry_str = company_data.get("industry", "other")
                industry_map = {
                    "manufacturing": IndustryType.MANUFACTURING,
                    "finance": IndustryType.FINANCE,
                    "healthcare": IndustryType.HEALTHCARE,
                    "retail": IndustryType.RETAIL,
                    "it_service": IndustryType.IT_SERVICE,
                    "public": IndustryType.PUBLIC,
                    "other": IndustryType.OTHER
                }
                industry_enum = industry_map.get(industry_str, IndustryType.OTHER)
                
                # CompanySize 매핑
                company_size_str = company_data.get("company_size", "sme")
                size_map = {
                    "startup": CompanySize.STARTUP,
                    "sme": CompanySize.SME,
                    "midsize": CompanySize.MIDSIZE,
                    "large": CompanySize.LARGE
                }
                company_size_enum = size_map.get(company_size_str, CompanySize.SME)
                
                # CompanyProfile 생성 (기본값 사용)
                company_profile = CompanyProfile(
                    name=company_data.get("name", "Unknown"),
                    industry=industry_enum,
                    company_size=company_size_enum,
                    business_description=company_data.get("description", "")
                )
                
                # Orchestrator에 프로젝트 등록
                # create_project는 새 UUID를 생성하므로, 직접 등록
                from src.agents.agent_orchestrator import WorkflowState, ConsultingStage
                
                # WorkflowState 생성 (TypedDict이므로 dict로 생성)
                workflow_state = {
                    "project_id": project_id,
                    "current_stage": ConsultingStage.STRATEGY,
                    "company_profile": company_profile.model_dump(),
                    "maturity_assessment": None,
                    "use_cases": [],
                    "scenarios": [],
                    "selected_scenario": None,
                    "roi_analysis": None,
                    "risk_assessment": None,
                    "reports": [],
                    "human_feedback": [],
                    "pending_approval": False,
                    "messages": [],
                    "errors": []
                }
                
                orchestrator.projects[project_id] = workflow_state
                
                logger.info(f"Framework 프로젝트를 Orchestrator에 등록 완료: {project_id}", project_id)
                # 등록 후 즉시 확인
                project = orchestrator.get_project(project_id)
                logger.info(f"Orchestrator 등록 후 프로젝트 조회 결과: {'있음' if project else '없음'} (ID: {project_id})", project_id)
                if not project:
                    logger.error(f"프로젝트 등록 후에도 조회되지 않음. projects 딕셔너리 키: {list(orchestrator.projects.keys())}", project_id)
            else:
                logger.error(f"Framework에서도 프로젝트를 찾을 수 없음: {project_id}", project_id)
                raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"프로젝트 로드 중 오류: {str(e)}", project_id, exc_info=True)
            raise HTTPException(status_code=404, detail=f"프로젝트를 찾을 수 없습니다: {str(e)}")
    
    if not project:
        logger.error("프로젝트를 찾을 수 없습니다", project_id)
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        logger.info("컨설팅 프로세스 실행 시작", project_id)
        result = await orchestrator.run_full_consultation(project_id, auto_approve)
        # JSON 직렬화 가능한 형태로 변환
        serializable_result = _make_json_serializable(result)
        
        logger.info("컨설팅 프로세스 완료 - API 응답 반환", project_id)
        return {
            "status": "success",
            "result": serializable_result
        }
    except Exception as e:
        logger.error(f"컨설팅 프로세스 실행 중 오류 발생: {str(e)}", project_id, exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 시스템 정보 ====================

@router.get("/agents/status")
async def get_agents_status():
    """에이전트 상태 조회"""
    orchestrator = get_orchestrator()
    return {
        "status": "success",
        "agents": orchestrator.get_agent_status()
    }


@router.get("/config/industries")
async def get_industries():
    """산업 분류 목록"""
    return {
        "status": "success",
        "industries": [
            {"id": i.value, "name": i.name}
            for i in IndustryType
        ]
    }


@router.get("/config/company-sizes")
async def get_company_sizes():
    """기업 규모 목록"""
    return {
        "status": "success",
        "company_sizes": [
            {"id": s.value, "name": s.name}
            for s in CompanySize
        ]
    }


@router.get("/config/consulting-stages")
async def get_consulting_stages():
    """컨설팅 단계 목록"""
    from config.settings import CONSULTING_FRAMEWORK
    return {
        "status": "success",
        "stages": CONSULTING_FRAMEWORK["stages"]
    }


@router.post("/projects/{project_id}/chat")
async def chat_with_consultant(project_id: str, message: Dict[str, Any]):
    """AI 컨설턴트와 채팅"""
    from src.core.llm_provider import ConsultingLLMProvider
    from src.api.common.database import get_project
    
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")
    
    user_message = message.get("message", "")
    if not user_message:
        raise HTTPException(status_code=400, detail="메시지를 입력해주세요.")
    
    try:
        # 프로젝트 컨텍스트 준비
        company_profile = project.get("company_profile", {})
        stage_data = {}
        for stage_key in ["stage1", "stage2", "stage3", "stage4", "stage5"]:
            stage_data[stage_key] = project.get(f"{stage_key}_maturity") or project.get(f"{stage_key}_requirements") or project.get(f"{stage_key}_poc") or {}
        
        # 컨텍스트 문자열 생성
        context = {
            "company_profile": company_profile,
            "stages": stage_data
        }
        
        # LLM Provider 생성 및 질의
        llm_provider = ConsultingLLMProvider()
        response = await llm_provider.consult(
            query=user_message,
            context=context,
            task_type="general"
        )
        
        return {
            "status": "success",
            "response": response
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        # 에러 발생 시 기본 응답 반환
        return {
            "status": "error",
            "response": f"죄송합니다. 응답 생성 중 오류가 발생했습니다: {str(e)}"
        }


@router.get("/health")
async def health_check():
    """시스템 상태 확인"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@router.get("/ollama/status")
async def ollama_status():
    """Ollama 서버 상태 확인 (CORS 프록시)"""
    import httpx
    from config.settings import settings
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{settings.OLLAMA_BASE_URL}/api/tags")
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            return {"status": "ok", "models": models}
        return {"status": "error", "models": []}
    except Exception:
        return {"status": "error", "models": []}


# ==================== 제5장: MLOps 기술적 구현 표준 ====================

@router.get("/config/mlops-standards")
async def get_mlops_standards():
    """MLOps 표준 프레임워크 조회"""
    from config.settings import MLOPS_STANDARDS
    return {
        "status": "success",
        "mlops_standards": MLOPS_STANDARDS
    }


@router.get("/projects/{project_id}/mlops-standards")
async def get_project_mlops_standards(project_id: str):
    """프로젝트의 MLOps 표준 설정 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "mlops_standards": project.get("mlops_standards", MLOpsStandards().model_dump())
    }


@router.post("/projects/{project_id}/mlops-standards")
async def save_project_mlops_standards(project_id: str, request: SaveMLOpsStandardsRequest):
    """프로젝트의 MLOps 표준 설정 저장"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # MLOps 표준 저장
        mlops_data = request.mlops_standards.model_dump()
        mlops_data["project_id"] = project_id
        mlops_data["updated_at"] = datetime.now().isoformat()

        orchestrator.update_project(project_id, {"mlops_standards": mlops_data})

        return {
            "status": "success",
            "message": "MLOps 표준 설정이 저장되었습니다.",
            "mlops_standards": mlops_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/mlops-standards/analyze")
async def analyze_mlops_maturity(project_id: str):
    """MLOps 성숙도 분석 (AI 기반)"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # AI 분석 요청
        mlops_standards = project.get("mlops_standards", {})
        result = await orchestrator.analyze_mlops_maturity(project_id, mlops_standards)

        return {
            "status": "success",
            "analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 제6장: 필수 인력 구성 및 조직 체계 ====================

@router.get("/config/personnel-organization")
async def get_personnel_organization_framework():
    """인력 구성 프레임워크 조회"""
    from config.settings import PERSONNEL_ORGANIZATION
    return {
        "status": "success",
        "personnel_organization": PERSONNEL_ORGANIZATION
    }


@router.get("/projects/{project_id}/personnel-organization")
async def get_project_personnel_organization(project_id: str):
    """프로젝트의 인력 구성 현황 조회"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "personnel_organization": project.get("personnel_organization", PersonnelOrganization().model_dump())
    }


@router.post("/projects/{project_id}/personnel-organization")
async def save_project_personnel_organization(project_id: str, request: SavePersonnelOrganizationRequest):
    """프로젝트의 인력 구성 현황 저장"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # 인력 구성 저장
        personnel_data = request.personnel_organization.model_dump()
        personnel_data["project_id"] = project_id
        personnel_data["updated_at"] = datetime.now().isoformat()

        # Gap 계산
        total_current = 0
        total_target = 0

        for team_key in ["strategy_pmo_team", "tech_development_team", "data_infra_team", "governance_expertise_team"]:
            team = personnel_data.get(team_key, {})
            for role_key, role_data in team.items():
                if isinstance(role_data, dict):
                    current = role_data.get("current_headcount", 0)
                    target = role_data.get("target_headcount", 0)
                    role_data["gap"] = target - current
                    total_current += current
                    total_target += target

        personnel_data["total_current_headcount"] = total_current
        personnel_data["total_target_headcount"] = total_target

        orchestrator.update_project(project_id, {"personnel_organization": personnel_data})

        return {
            "status": "success",
            "message": "인력 구성 현황이 저장되었습니다.",
            "personnel_organization": personnel_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/personnel-organization/gap-analysis")
async def analyze_personnel_gap(project_id: str):
    """인력 Gap 분석 (AI 기반)"""
    orchestrator = get_orchestrator()
    project = orchestrator.get_project(project_id)

    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # AI 분석 요청
        personnel_org = project.get("personnel_organization", {})
        result = await orchestrator.analyze_personnel_gap(project_id, personnel_org)

        return {
            "status": "success",
            "gap_analysis": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
