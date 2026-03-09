"""
AI Consulting Framework Routes
5단계 AI 컨설팅 프레임워크 API 엔드포인트

NOTE: 이 파일은 점진적으로 Stage별 모듈로 분리되고 있습니다.
Stage 1은 src/api/stage1/routes.py로 분리되었습니다.
"""
from fastapi import APIRouter, HTTPException, Body
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import json
from pathlib import Path

router = APIRouter(prefix="/api/v1/framework", tags=["Consulting Framework"])

# Stage별 라우터 통합 (점진적 모듈화)
try:
    from .stage1.routes import router as stage1_router
    router.include_router(stage1_router)
except ImportError as e:
    import warnings
    warnings.warn(f"Stage 1 모듈을 로드할 수 없습니다: {e}. 기존 코드를 사용합니다.")

try:
    from .stage2.routes import router as stage2_router
    router.include_router(stage2_router)
except ImportError as e:
    import warnings
    warnings.warn(f"Stage 2 모듈을 로드할 수 없습니다: {e}. 기존 코드를 사용합니다.")

try:
    from .stage3.routes import router as stage3_router
    router.include_router(stage3_router)
except ImportError as e:
    import warnings
    warnings.warn(f"Stage 3 모듈을 로드할 수 없습니다: {e}. 기존 코드를 사용합니다.")

try:
    from .stage4.routes import router as stage4_router
    router.include_router(stage4_router)
except ImportError as e:
    import warnings
    warnings.warn(f"Stage 4 모듈을 로드할 수 없습니다: {e}. 기존 코드를 사용합니다.")

try:
    from .stage5.routes import router as stage5_router
    router.include_router(stage5_router)
except ImportError as e:
    import warnings
    warnings.warn(f"Stage 5 모듈을 로드할 수 없습니다: {e}. 기존 코드를 사용합니다.")

# 데이터 저장 경로 (현재 작업 디렉토리 기준)
BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_FILE = DATA_DIR / "consulting_projects.json"


# ==================== Pydantic Models ====================

class MaturityAssessmentInput(BaseModel):
    """성숙도 진단 입력 - 유연한 구조"""
    strategy: Dict[str, Any] = Field(default_factory=dict, description="전략 영역")
    organization: Dict[str, Any] = Field(default_factory=dict, description="조직 영역")
    data_technology: Dict[str, Any] = Field(default_factory=dict, description="데이터/기술 영역")
    process: Dict[str, Any] = Field(default_factory=dict, description="프로세스 영역")
    notes: str = Field(default="", description="비고")


class OpportunityInput(BaseModel):
    """기회 발굴 입력"""
    name: str = Field(default="", description="기회명")
    description: str = Field(default="", description="설명")
    business_area: str = Field(default="", description="비즈니스 영역")
    priority_quadrant: str = Field(default="strategic", description="우선순위 사분면")
    expected_impact: str = Field(default="", description="기대 효과")
    implementation_difficulty: str = Field(default="", description="구현 난이도")
    estimated_timeline: str = Field(default="", description="예상 소요 기간")
    required_resources: str = Field(default="", description="필요 자원")


class RoadmapInput(BaseModel):
    """로드맵 입력"""
    vision: str = Field(default="", description="AI 비전 선언문")
    goals: List[Any] = Field(default_factory=list, description="전략적 목표")
    kpis: List[Any] = Field(default_factory=list, description="핵심 성과 지표")
    phases: List[Any] = Field(default_factory=list, description="단계별 계획")











class PoCInput(BaseModel):
    """PoC 계획"""
    poc_name: str = Field(default="", description="PoC 명")
    objectives: str = Field(default="", description="목표")
    scope: str = Field(default="", description="범위")
    success_metrics: str = Field(default="", description="성공 지표")
    timeline: str = Field(default="", description="일정")
    resources: str = Field(default="", description="필요 리소스")
    risks: str = Field(default="", description="리스크")


class PlatformInput(BaseModel):
    """플랫폼 구축 계획"""
    components: Dict[str, Any] = Field(default_factory=dict, description="플랫폼 구성요소")
    infrastructure: str = Field(default="", description="인프라")
    security_config: str = Field(default="", description="보안 설정")
    scalability_plan: str = Field(default="", description="확장성 계획")


class IntegrationInput(BaseModel):
    """통합 설정"""
    target_systems: str = Field(default="", description="대상 시스템")
    api_specifications: str = Field(default="", description="API 명세")
    data_flow: str = Field(default="", description="데이터 흐름")
    testing_plan: str = Field(default="", description="테스트 계획")


class PilotInput(BaseModel):
    """파일럿 계획"""
    pilot_name: str = Field(default="", description="파일럿 명")
    target_department: str = Field(default="", description="대상 부서")
    pilot_scope: str = Field(default="", description="범위")
    duration: str = Field(default="", description="기간")
    success_criteria: str = Field(default="", description="성공 기준")
    support_plan: str = Field(default="", description="지원 계획")


class ChangeManagementInput(BaseModel):
    """변화 관리 계획"""
    awareness: Dict[str, Any] = Field(default_factory=dict, description="인식 제고")
    capability: Dict[str, Any] = Field(default_factory=dict, description="역량 강화")
    engagement: Dict[str, Any] = Field(default_factory=dict, description="참여 유도")
    success_sharing: Dict[str, Any] = Field(default_factory=dict, description="성과 공유")
    notes: str = Field(default="", description="비고")


class ScaleInput(BaseModel):
    """확산 계획"""
    rollout_phases: List[Any] = Field(default_factory=list, description="단계별 롤아웃")
    target_coverage: str = Field(default="", description="목표 커버리지")
    timeline: str = Field(default="", description="일정")
    resource_plan: str = Field(default="", description="자원 계획")
    risk_mitigation: str = Field(default="", description="리스크 완화")


class MonitoringInput(BaseModel):
    """모니터링 설정"""
    metrics: Dict[str, Any] = Field(default_factory=dict, description="모니터링 지표")
    alert_thresholds: str = Field(default="", description="알림 임계값")
    dashboard_config: str = Field(default="", description="대시보드 설정")
    reporting_frequency: str = Field(default="", description="보고 주기")


class ImprovementInput(BaseModel):
    """개선 계획"""
    improvement_cycle: str = Field(default="", description="개선 사이클")
    feedback_sources: str = Field(default="", description="피드백 소스")
    prioritization_criteria: str = Field(default="", description="우선순위 기준")
    experiment_framework: str = Field(default="", description="실험 프레임워크")
    success_metrics: str = Field(default="", description="성공 지표")


class GovernanceReviewInput(BaseModel):
    """거버넌스 검토"""
    review_frequency: str = Field(default="", description="검토 주기")
    review_scope: str = Field(default="", description="검토 범위")
    audit_checklist: str = Field(default="", description="감사 체크리스트")
    compliance_updates: str = Field(default="", description="규제 업데이트")
    policy_revisions: str = Field(default="", description="정책 개정")


# ==================== Helper Functions ====================

def load_projects() -> Dict:
    """프로젝트 데이터 로드"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"projects": {}}


def save_projects(data: Dict):
    """프로젝트 데이터 저장"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def get_project(project_id: str) -> Optional[Dict]:
    """프로젝트 조회"""
    data = load_projects()
    return data["projects"].get(project_id)


def update_project(project_id: str, updates: Dict):
    """프로젝트 업데이트"""
    data = load_projects()
    if project_id not in data["projects"]:
        data["projects"][project_id] = {"id": project_id, "created_at": datetime.now().isoformat()}
    data["projects"][project_id].update(updates)
    data["projects"][project_id]["updated_at"] = datetime.now().isoformat()
    save_projects(data)
    return data["projects"][project_id]


# ==================== Stage 1: AI Vision & Strategy (Moved to src.api.stage1) ====================
# Routes are imported via router.include_router(stage1_router)

# ==================== Stage 2: Use Case Design (Moved to src.api.stage2) ====================
# Routes are imported via router.include_router(stage2_router)


# Routes for Stage 1 are imported from src.api.stage1

# ==================== Stage 2: Use Case & Design ====================

# Routes for Stage 2 are imported from src.api.stage2

# ==================== Stage 3: Platform & Solution Build ====================

# Routes for Stage 3 are imported from src.api.stage3

# ==================== Stage 4: Pilot & Scale ====================

# Routes for Stage 4 are imported from src.api.stage4

# ==================== Stage 5: Operate & Optimize ====================

# Routes for Stage 5 are imported from src.api.stage5

# ==================== Project Summary ====================

@router.get("/projects/{project_id}/summary")
async def get_project_summary(project_id: str):
    """프로젝트 전체 요약 조회"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # 각 단계별 완료 상태 확인
    stage_completion = {
        "stage1": {
            "maturity": bool(project.get("stage1_maturity")),
            "opportunities": bool(project.get("stage1_opportunities")),
            "roadmap": bool(project.get("stage1_roadmap"))
        },
        "stage2": {
            "requirements": bool(project.get("stage2_requirements")),
            "architecture": bool(project.get("stage2_architecture")),
            "governance": bool(project.get("stage2_governance"))
        },
        "stage3": {
            "poc": bool(project.get("stage3_poc")),
            "platform": bool(project.get("stage3_platform"))
        },
        "stage4": {
            "pilot": bool(project.get("stage4_pilot")),
            "change_management": bool(project.get("stage4_change_management")),
            "scale": bool(project.get("stage4_scale"))
        },
        "stage5": {
            "monitoring": bool(project.get("stage5_monitoring")),
            "improvement": bool(project.get("stage5_improvement")),
            "governance_review": bool(project.get("stage5_governance_review"))
        }
    }

    # 단계별 진행률 계산
    stage_progress = {}
    for stage, items in stage_completion.items():
        completed = sum(1 for v in items.values() if v)
        total = len(items)
        stage_progress[stage] = round((completed / total) * 100) if total > 0 else 0

    return {
        "status": "success",
        "project_id": project_id,
        "stage_completion": stage_completion,
        "stage_progress": stage_progress,
        "overall_progress": round(sum(stage_progress.values()) / 5),
        "project_data": project
    }


@router.get("/projects")
async def list_projects():
    """프로젝트 목록 조회"""
    data = load_projects()
    return {
        "status": "success",
        "projects": list(data["projects"].values())
    }


@router.post("/projects/create-sample")
async def create_sample_project():
    """샘플 프로젝트 생성 (테스트용)"""
    import uuid
    from src.utils.sample_data_generator import (
        generate_sample_company_profile,
        generate_sample_project_data
    )
    
    # 프로젝트 ID 생성
    project_id = f"sample-{uuid.uuid4().hex[:8]}"
    
    # 샘플 데이터 생성
    company_profile = generate_sample_company_profile()
    project_data = generate_sample_project_data(project_id)
    
    # 기업 프로필 추가
    project_data["company_profile"] = company_profile.model_dump()
    project_data["project_name"] = f"샘플 프로젝트 - {company_profile.name}"
    
    # 프로젝트 저장
    data = load_projects()
    data["projects"][project_id] = project_data
    save_projects(data)
    
    return {
        "status": "success",
        "message": "샘플 프로젝트가 생성되었습니다.",
        "project_id": project_id,
        "project_name": project_data["project_name"],
        "project": project_data
    }


# ==================== Methodology Endpoints ====================

class DetailedMaturityInput(BaseModel):
    """상세 성숙도 평가 입력"""
    strategy: Dict[str, Any] = Field(default_factory=dict)
    organization: Dict[str, Any] = Field(default_factory=dict)
    data_technology: Dict[str, Any] = Field(default_factory=dict)
    process: Dict[str, Any] = Field(default_factory=dict)
    targets: Dict[str, Any] = Field(default_factory=dict)
    notes: str = Field(default="")


class ValueMappingInput(BaseModel):
    """가치-실행 매핑 입력"""
    tasks: List[Dict[str, Any]] = Field(default_factory=list)


@router.post("/projects/{project_id}/methodology/detailed-maturity")
async def save_detailed_maturity(project_id: str, data: DetailedMaturityInput):
    """상세 성숙도 평가 저장 (16개 항목)"""
    # Calculate scores
    def calc_area_score(items: Dict[str, Any]) -> float:
        values = [v for v in items.values() if isinstance(v, (int, float))]
        return sum(values) / len(values) if values else 0

    strategy_score = calc_area_score(data.strategy)
    org_score = calc_area_score(data.organization)
    data_tech_score = calc_area_score(data.data_technology)
    process_score = calc_area_score(data.process)
    overall_score = (strategy_score + org_score + data_tech_score + process_score) / 4

    # Calculate gaps
    gaps = {
        "strategy": data.targets.get("strategy", 3) - strategy_score,
        "organization": data.targets.get("organization", 3) - org_score,
        "data_technology": data.targets.get("data_technology", 3) - data_tech_score,
        "process": data.targets.get("process", 3) - process_score
    }

    maturity_data = {
        "assessment_date": datetime.now().isoformat(),
        "items": {
            "strategy": data.strategy,
            "organization": data.organization,
            "data_technology": data.data_technology,
            "process": data.process
        },
        "scores": {
            "strategy": round(strategy_score, 2),
            "organization": round(org_score, 2),
            "data_technology": round(data_tech_score, 2),
            "process": round(process_score, 2),
            "overall": round(overall_score, 2)
        },
        "targets": data.targets,
        "gaps": {k: round(v, 2) for k, v in gaps.items()},
        "notes": data.notes
    }

    update_project(project_id, {"methodology_detailed_maturity": maturity_data})

    return {
        "status": "success",
        "message": "상세 성숙도 평가가 저장되었습니다.",
        "maturity": maturity_data
    }


@router.get("/projects/{project_id}/methodology/detailed-maturity")
async def get_detailed_maturity(project_id: str):
    """상세 성숙도 평가 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "maturity": {}}

    return {
        "status": "success",
        "maturity": project.get("methodology_detailed_maturity", {})
    }


@router.post("/projects/{project_id}/methodology/value-mapping")
async def save_value_mapping(project_id: str, data: ValueMappingInput):
    """가치-실행 매핑 저장"""
    # Categorize tasks
    categories = {
        "quick_win": [],
        "strategic": [],
        "fill_in": [],
        "reconsider": []
    }

    for task in data.tasks:
        classification = task.get("classification", "").lower().replace(" ", "_").replace("-", "_")
        if classification == "quick_win":
            categories["quick_win"].append(task)
        elif classification == "strategic":
            categories["strategic"].append(task)
        elif classification == "fill_in":
            categories["fill_in"].append(task)
        else:
            categories["reconsider"].append(task)

    mapping_data = {
        "created_at": datetime.now().isoformat(),
        "tasks": data.tasks,
        "categories": categories,
        "summary": {
            "total": len(data.tasks),
            "quick_win": len(categories["quick_win"]),
            "strategic": len(categories["strategic"]),
            "fill_in": len(categories["fill_in"]),
            "reconsider": len(categories["reconsider"])
        }
    }

    update_project(project_id, {"methodology_value_mapping": mapping_data})

    return {
        "status": "success",
        "message": "가치-실행 매핑이 저장되었습니다.",
        "mapping": mapping_data
    }


@router.get("/projects/{project_id}/methodology/value-mapping")
async def get_value_mapping(project_id: str):
    """가치-실행 매핑 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "mapping": {}}

    return {
        "status": "success",
        "mapping": project.get("methodology_value_mapping", {})
    }


# ============================================================
# AI 거버넌스 프레임워크 API
# ============================================================

class GovernanceCoreAreasInput(BaseModel):
    """3대 핵심 영역 평가 입력"""
    strategy: Dict[str, Any] = Field(default_factory=dict)
    process: Dict[str, Any] = Field(default_factory=dict)
    technology: Dict[str, Any] = Field(default_factory=dict)
    notes: Dict[str, str] = Field(default_factory=dict)


class GovernanceComponentsInput(BaseModel):
    """7대 필수 구성요소 평가 입력"""
    organization: Dict[str, Any] = Field(default_factory=dict)  # 1. 조직 및 책임
    ethics: Dict[str, Any] = Field(default_factory=dict)        # 2. 윤리 및 투명성
    data_management: Dict[str, Any] = Field(default_factory=dict)  # 3. 데이터 관리
    risk_management: Dict[str, Any] = Field(default_factory=dict)  # 4. 위험 관리
    development: Dict[str, Any] = Field(default_factory=dict)   # 5. 개발 및 배포 표준
    monitoring: Dict[str, Any] = Field(default_factory=dict)    # 6. 모니터링 및 운영
    training: Dict[str, Any] = Field(default_factory=dict)      # 7. 교육 및 변화 관리


class GovernanceAssessmentInput(BaseModel):
    """거버넌스 종합 평가 입력"""
    overall_score: float = Field(default=0)
    overall_grade: str = Field(default="")
    area_scores: Dict[str, float] = Field(default_factory=dict)
    component_scores: Dict[str, float] = Field(default_factory=dict)
    recommendations: List[str] = Field(default_factory=list)


def calculate_governance_component_score(component_data: Dict[str, Any]) -> float:
    """구성요소 점수 계산"""
    score_map = {
        # 레벨 1 (낮음)
        "no": 0, "none": 0, "never": 0,
        # 레벨 2 (기본)
        "planned": 25, "partial": 25, "informal": 25, "basic": 25,
        "simple": 25, "adhoc": 25, "manual": 25, "once": 25,
        "draft": 25, "optional": 25, "passive": 25, "spot": 25,
        # 레벨 3 (중간)
        "established": 50, "designated": 50, "formal": 50,
        "approved": 50, "uniform": 50, "periodic": 50,
        "email": 50, "annual": 50, "git": 50,
        # 레벨 4 (양호)
        "active": 75, "full": 75, "all": 75, "detailed": 75,
        "tiered": 75, "critical": 75, "trigger": 75,
        "quarterly": 75, "proactive": 75, "standard": 75,
        "implemented": 75, "mandatory": 75,
        # 레벨 5 (우수)
        "optimized": 100, "auto": 100, "automated": 100,
        "mature": 100, "realtime": 100, "integrated": 100,
        "system": 100, "weekly": 100, "regular": 100
    }

    if not component_data:
        return 0

    total_score = 0
    count = 0

    for key, value in component_data.items():
        if isinstance(value, str) and value:
            score = score_map.get(value.lower(), 0)
            total_score += score
            count += 1

    return round(total_score / count, 1) if count > 0 else 0


@router.post("/projects/{project_id}/governance/core-areas")
async def save_governance_core_areas(project_id: str, data: GovernanceCoreAreasInput):
    """3대 핵심 영역 평가 저장"""
    # Calculate scores for each area
    strategy_score = calculate_governance_component_score(data.strategy)
    process_score = calculate_governance_component_score(data.process)
    technology_score = calculate_governance_component_score(data.technology)
    overall_score = round((strategy_score + process_score + technology_score) / 3, 1)

    core_areas_data = {
        "assessment_date": datetime.now().isoformat(),
        "areas": {
            "strategy": data.strategy,
            "process": data.process,
            "technology": data.technology
        },
        "scores": {
            "strategy": strategy_score,
            "process": process_score,
            "technology": technology_score,
            "overall": overall_score
        },
        "notes": data.notes
    }

    update_project(project_id, {"governance_core_areas": core_areas_data})

    return {
        "status": "success",
        "message": "3대 핵심 영역 평가가 저장되었습니다.",
        "core_areas": core_areas_data
    }


@router.get("/projects/{project_id}/governance/core-areas")
async def get_governance_core_areas(project_id: str):
    """3대 핵심 영역 평가 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "core_areas": {}}

    return {
        "status": "success",
        "core_areas": project.get("governance_core_areas", {})
    }


@router.post("/projects/{project_id}/governance/components")
async def save_governance_components(project_id: str, data: GovernanceComponentsInput):
    """7대 필수 구성요소 평가 저장"""
    # Calculate scores for each component
    scores = {
        "organization": calculate_governance_component_score(data.organization),
        "ethics": calculate_governance_component_score(data.ethics),
        "data_management": calculate_governance_component_score(data.data_management),
        "risk_management": calculate_governance_component_score(data.risk_management),
        "development": calculate_governance_component_score(data.development),
        "monitoring": calculate_governance_component_score(data.monitoring),
        "training": calculate_governance_component_score(data.training)
    }

    overall_score = round(sum(scores.values()) / len(scores), 1)

    # Determine grade
    if overall_score >= 90:
        grade = "우수 (Advanced)"
    elif overall_score >= 70:
        grade = "양호 (Established)"
    elif overall_score >= 50:
        grade = "보통 (Developing)"
    else:
        grade = "미흡 (Initial)"

    # Generate recommendations based on low scores
    recommendations = []
    component_names = {
        "organization": "조직 및 책임",
        "ethics": "윤리 및 투명성",
        "data_management": "데이터 관리",
        "risk_management": "위험 관리",
        "development": "개발 및 배포 표준",
        "monitoring": "모니터링 및 운영",
        "training": "교육 및 변화 관리"
    }

    for key, score in scores.items():
        if score < 50:
            recommendations.append(f"[우선] {component_names[key]} 영역 강화 필요 (현재 {score}점)")
        elif score < 70:
            recommendations.append(f"[개선] {component_names[key]} 영역 개선 권장 (현재 {score}점)")

    components_data = {
        "assessment_date": datetime.now().isoformat(),
        "components": {
            "organization": data.organization,
            "ethics": data.ethics,
            "data_management": data.data_management,
            "risk_management": data.risk_management,
            "development": data.development,
            "monitoring": data.monitoring,
            "training": data.training
        },
        "scores": scores,
        "overall_score": overall_score,
        "grade": grade,
        "recommendations": recommendations
    }

    update_project(project_id, {"governance_components": components_data})

    return {
        "status": "success",
        "message": "7대 필수 구성요소 평가가 저장되었습니다.",
        "components": components_data
    }


@router.get("/projects/{project_id}/governance/components")
async def get_governance_components(project_id: str):
    """7대 필수 구성요소 평가 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "components": {}}

    return {
        "status": "success",
        "components": project.get("governance_components", {})
    }


@router.post("/projects/{project_id}/governance/assessment")
async def save_governance_assessment(project_id: str, data: GovernanceAssessmentInput):
    """거버넌스 종합 평가 저장"""
    assessment_data = {
        "assessment_date": datetime.now().isoformat(),
        "overall_score": data.overall_score,
        "overall_grade": data.overall_grade,
        "area_scores": data.area_scores,
        "component_scores": data.component_scores,
        "recommendations": data.recommendations
    }

    update_project(project_id, {"governance_assessment": assessment_data})

    return {
        "status": "success",
        "message": "거버넌스 종합 평가가 저장되었습니다.",
        "assessment": assessment_data
    }


@router.get("/projects/{project_id}/governance/assessment")
async def get_governance_assessment(project_id: str):
    """거버넌스 종합 평가 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "assessment": {}}

    return {
        "status": "success",
        "assessment": project.get("governance_assessment", {})
    }


@router.get("/projects/{project_id}/governance/summary")
async def get_governance_summary(project_id: str):
    """거버넌스 전체 요약 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "summary": {}}

    return {
        "status": "success",
        "summary": {
            "core_areas": project.get("governance_core_areas", {}),
            "components": project.get("governance_components", {}),
            "assessment": project.get("governance_assessment", {})
        }
    }


# ============================================================
# MLOps Standards API
# ============================================================

class MLOpsStandardsInput(BaseModel):
    """MLOps 표준 입력"""
    data_management: Dict[str, Any] = Field(default_factory=dict)
    model_development: Dict[str, Any] = Field(default_factory=dict)
    model_evaluation: Dict[str, Any] = Field(default_factory=dict)
    model_deployment: Dict[str, Any] = Field(default_factory=dict)
    model_monitoring: Dict[str, Any] = Field(default_factory=dict)
    security_governance: Dict[str, Any] = Field(default_factory=dict)
    overall_maturity_score: float = Field(default=0.0)
    recommendations: List[str] = Field(default_factory=list)


@router.get("/projects/{project_id}/mlops-standards")
async def get_mlops_standards(project_id: str):
    """프로젝트의 MLOps 표준 설정 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "mlops_standards": {}}

    return {
        "status": "success",
        "mlops_standards": project.get("mlops_standards", {})
    }


@router.post("/projects/{project_id}/mlops-standards")
async def save_mlops_standards(project_id: str, data: MLOpsStandardsInput):
    """프로젝트의 MLOps 표준 설정 저장"""
    mlops_data = {
        "project_id": project_id,
        "data_management": data.data_management,
        "model_development": data.model_development,
        "model_evaluation": data.model_evaluation,
        "model_deployment": data.model_deployment,
        "model_monitoring": data.model_monitoring,
        "security_governance": data.security_governance,
        "overall_maturity_score": data.overall_maturity_score,
        "recommendations": data.recommendations,
        "updated_at": datetime.now().isoformat()
    }

    update_project(project_id, {"mlops_standards": mlops_data})

    return {
        "status": "success",
        "message": "MLOps 표준 설정이 저장되었습니다.",
        "mlops_standards": mlops_data
    }


@router.post("/projects/{project_id}/mlops-standards/analyze")
async def analyze_mlops_maturity(project_id: str):
    """MLOps 성숙도 분석 (AI 기반)"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    mlops_standards = project.get("mlops_standards", {})
    
    # 기본 분석 결과 반환 (향후 AI 분석 기능 추가 가능)
    analysis_result = {
        "maturity_score": mlops_standards.get("overall_maturity_score", 0.0),
        "recommendations": mlops_standards.get("recommendations", []),
        "analysis_date": datetime.now().isoformat(),
        "note": "AI 분석 기능은 향후 추가될 예정입니다."
    }

    return {
        "status": "success",
        "analysis": analysis_result
    }


# ============================================================
# Personnel Organization API (제6장: 필수 인력 구성 및 조직 체계)
# ============================================================

class PersonnelOrganizationInput(BaseModel):
    """인력 구성 입력"""
    personnel_organization: Dict[str, Any] = Field(default_factory=dict)


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
    project = get_project(project_id)
    if not project:
        return {"status": "success", "personnel_organization": {}}

    return {
        "status": "success",
        "personnel_organization": project.get("personnel_organization", {})
    }


@router.post("/projects/{project_id}/personnel-organization")
async def save_project_personnel_organization(project_id: str, data: PersonnelOrganizationInput):
    """프로젝트의 인력 구성 현황 저장"""
    try:
        # 인력 구성 저장
        personnel_data = data.personnel_organization.copy()
        personnel_data["project_id"] = project_id
        personnel_data["updated_at"] = datetime.now().isoformat()

        # Gap 계산
        total_current = 0
        total_target = 0

        for team_key in ["strategy_pmo_team", "tech_development_team", "data_infra_team", "governance_expertise_team"]:
            team = personnel_data.get(team_key, {})
            if isinstance(team, dict):
                for role_key, role_data in team.items():
                    if isinstance(role_data, dict):
                        current = role_data.get("current_headcount", 0)
                        target = role_data.get("target_headcount", 0)
                        role_data["gap"] = target - current
                        total_current += current
                        total_target += target

        personnel_data["total_current_headcount"] = total_current
        personnel_data["total_target_headcount"] = total_target

        update_project(project_id, {"personnel_organization": personnel_data})

        return {
            "status": "success",
            "message": "인력 구성 현황이 저장되었습니다.",
            "personnel_organization": personnel_data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/projects/{project_id}/personnel-organization/gap-analysis")
async def analyze_personnel_gap(project_id: str, data: Optional[PersonnelOrganizationInput] = Body(None)):
    """인력 Gap 분석 (AI 기반)"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # 요청 본문에서 personnel_organization 데이터를 가져오거나, 프로젝트에서 가져옴
    if data and data.personnel_organization:
        personnel_org = data.personnel_organization
    else:
        personnel_org = project.get("personnel_organization", {})
    
    # Gap 분석 데이터 추출
    gap_analysis = personnel_org.get("gap_analysis", {})
    
    # 기본 분석 결과 구성
    analysis_result = {
        "total_current": gap_analysis.get("total_current", personnel_org.get("total_current_headcount", 0)),
        "total_target": gap_analysis.get("total_target", personnel_org.get("total_target_headcount", 0)),
        "total_gap": gap_analysis.get("total_gap", 0),
        "gap_percent": gap_analysis.get("gap_percent", 0.0),
        "team_gaps": gap_analysis.get("team_gaps", []),
        "priority_hiring": gap_analysis.get("priority_hiring", []),
        "training_needs": gap_analysis.get("training_needs", []),
        "timeline_months": gap_analysis.get("timeline_months", 12),
        "recommendations": gap_analysis.get("recommendations", []),
        "analysis_date": datetime.now().isoformat(),
        "note": "AI 분석 기능은 향후 추가될 예정입니다."
    }

    # Gap 계산이 없으면 계산
    if analysis_result["total_gap"] == 0 and analysis_result["total_current"] > 0:
        analysis_result["total_gap"] = analysis_result["total_target"] - analysis_result["total_current"]
        if analysis_result["total_target"] > 0:
            analysis_result["gap_percent"] = (analysis_result["total_gap"] / analysis_result["total_target"]) * 100

    return {
        "status": "success",
        "gap_analysis": analysis_result
    }


# ==================== Project Management Endpoints ====================

class NewProjectInput(BaseModel):
    """새 프로젝트 생성 입력"""
    project_name: str = Field(..., min_length=1)
    company_name: str = Field(default="")
    industry: str = Field(default="")
    description: str = Field(default="")


@router.post("/projects")
async def create_project(data: NewProjectInput):
    """새 프로젝트 생성"""
    import uuid
    from src.models.schemas import CompanyProfile, IndustryType, CompanySize

    project_id = f"project-{uuid.uuid4().hex[:8]}"

    project_data = {
        "project_id": project_id,
        "project_name": data.project_name,
        "company_profile": {
            "name": data.company_name,
            "industry": data.industry,
            "description": data.description
        },
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "status": "active",
        "stages": {
            "stage1": {},
            "stage2": {},
            "stage3": {},
            "stage4": {},
            "stage5": {}
        }
    }

    projects_data = load_projects()
    projects_data["projects"][project_id] = project_data
    save_projects(projects_data)

    # Orchestrator에도 프로젝트 등록 (run-full-consultation을 위해)
    try:
        from src.agents.agent_orchestrator import get_orchestrator, WorkflowState, ConsultingStage
        
        # IndustryType 매핑
        industry_map = {
            "manufacturing": IndustryType.MANUFACTURING,
            "finance": IndustryType.FINANCE,
            "healthcare": IndustryType.HEALTHCARE,
            "retail": IndustryType.RETAIL,
            "it_service": IndustryType.IT_SERVICE,
            "public": IndustryType.PUBLIC,
            "other": IndustryType.OTHER
        }
        industry_enum = industry_map.get(data.industry, IndustryType.OTHER)
        
        # CompanyProfile 생성
        company_profile = CompanyProfile(
            name=data.company_name or "Unknown",
            industry=industry_enum,
            company_size=CompanySize.SME,  # 기본값
            business_description=data.description or ""
        )
        
        # Orchestrator에 프로젝트 직접 등록 (프로젝트 ID 지정)
        # WorkflowState는 TypedDict이므로 dict로 생성
        orchestrator = get_orchestrator()
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
    except Exception as e:
        # Orchestrator 등록 실패해도 계속 진행 (파일 저장은 성공, run-full-consultation에서 자동 로드됨)
        import logging
        logging.warning(f"Orchestrator에 프로젝트 등록 실패 (계속 진행, run-full-consultation에서 자동 로드됨): {e}")

    return {
        "status": "success",
        "message": "프로젝트가 생성되었습니다.",
        "project_id": project_id,
        "project": project_data
    }


@router.get("/projects/{project_id}")
async def get_project_detail(project_id: str):
    """프로젝트 단일 조회"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "project": project
    }


@router.delete("/projects/{project_id}")
async def delete_project(project_id: str):
    """프로젝트 삭제"""
    projects_data = load_projects()

    if project_id not in projects_data["projects"]:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    del projects_data["projects"][project_id]
    save_projects(projects_data)

    return {
        "status": "success",
        "message": "프로젝트가 삭제되었습니다."
    }


@router.post("/projects/{project_id}/duplicate")
async def duplicate_project(project_id: str):
    """프로젝트 복제"""
    import uuid
    import copy

    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    new_project_id = f"project-{uuid.uuid4().hex[:8]}"
    new_project = copy.deepcopy(project)
    new_project["project_id"] = new_project_id
    new_project["project_name"] = f"{project.get('project_name', '프로젝트')} (복사본)"
    new_project["created_at"] = datetime.now().isoformat()
    new_project["updated_at"] = datetime.now().isoformat()

    projects_data = load_projects()
    projects_data["projects"][new_project_id] = new_project
    save_projects(projects_data)

    return {
        "status": "success",
        "message": "프로젝트가 복제되었습니다.",
        "project_id": new_project_id,
        "project": new_project
    }


# ==================== Final Report Generation Endpoints ====================

class ScenarioAnalysisInput(BaseModel):
    """시나리오 분석 입력"""
    scenarios: List[Dict[str, Any]] = Field(default_factory=list)
    selected_scenario: Optional[str] = Field(default="balanced")
    analysis_parameters: Dict[str, Any] = Field(default_factory=dict)


@router.post("/projects/{project_id}/scenarios/analyze")
async def analyze_scenarios(project_id: str, data: ScenarioAnalysisInput):
    """시나리오 분석 실행"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # 프로젝트 전체 데이터에서 분석 수행
    stages = project.get("stages", {})

    # 각 Stage의 완료도 계산
    stage_completion = {}
    for stage_key in ["stage1", "stage2", "stage3", "stage4", "stage5"]:
        stage_data = stages.get(stage_key, {})
        if stage_data:
            filled_fields = sum(1 for v in stage_data.values() if v)
            total_fields = max(len(stage_data), 1)
            stage_completion[stage_key] = round((filled_fields / total_fields) * 100)
        else:
            stage_completion[stage_key] = 0

    # 시나리오 기반 분석 결과 생성
    scenarios_result = {
        "conservative": {
            "name": "보수적 시나리오",
            "roi_estimate": "15-25%",
            "timeline": "24개월",
            "risk_level": "낮음",
            "investment_ratio": 0.7,
            "key_features": ["안정적 도입", "단계적 확장", "리스크 최소화"]
        },
        "balanced": {
            "name": "균형 시나리오",
            "roi_estimate": "25-40%",
            "timeline": "18개월",
            "risk_level": "중간",
            "investment_ratio": 1.0,
            "key_features": ["최적화된 접근", "균형잡힌 투자", "적정 리스크"]
        },
        "aggressive": {
            "name": "적극적 시나리오",
            "roi_estimate": "40-60%",
            "timeline": "12개월",
            "risk_level": "높음",
            "investment_ratio": 1.5,
            "key_features": ["빠른 도입", "대규모 투자", "고위험 고수익"]
        }
    }

    # selected_scenario가 None이거나 유효하지 않은 경우 기본값 사용
    selected_scenario = data.selected_scenario or "balanced"
    if selected_scenario not in scenarios_result:
        selected_scenario = "balanced"
    
    selected = scenarios_result.get(selected_scenario, scenarios_result["balanced"])

    analysis_result = {
        "analysis_date": datetime.now().isoformat(),
        "stage_completion": stage_completion,
        "overall_completion": round(sum(stage_completion.values()) / 5),
        "selected_scenario": selected_scenario,
        "scenario_details": selected,
        "all_scenarios": scenarios_result,
        "recommendations": [
            "현재 프로젝트 진행률을 고려하여 단계적 접근을 권장합니다.",
            "핵심 인력 확보를 우선 진행하시기 바랍니다.",
            "파일럿 프로젝트를 통한 검증 후 확대 적용을 권장합니다."
        ]
    }

    # 분석 결과 저장
    update_project(project_id, {"scenario_analysis": analysis_result})

    return {
        "status": "success",
        "analysis": analysis_result
    }


@router.get("/projects/{project_id}/scenarios")
async def get_scenarios(project_id: str):
    """저장된 시나리오 분석 결과 조회"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "scenario_analysis": project.get("scenario_analysis", {})
    }


class ReportGenerationInput(BaseModel):
    """보고서 생성 입력"""
    report_type: str = Field(default="full")  # full, summary, executive
    include_sections: List[str] = Field(default_factory=lambda: [
        "executive_summary", "current_state", "gap_analysis",
        "recommendations", "roadmap", "investment", "risks"
    ])
    format: str = Field(default="html")  # html, pdf, docx


@router.post("/projects/{project_id}/report/generate")
async def generate_report(project_id: str, data: ReportGenerationInput):
    """최종 컨설팅 보고서 생성"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # 프로젝트 전체 데이터 수집
    company_profile = project.get("company_profile", {})
    stages = project.get("stages", {})
    scenario_analysis = project.get("scenario_analysis", {})

    # Stage 1 데이터
    stage1 = stages.get("stage1", {})
    maturity_assessment = stage1.get("maturity_assessment", {})
    opportunities = stage1.get("opportunities", {})
    roadmap = stage1.get("roadmap", {})

    # Stage 2-5 데이터
    stage2 = stages.get("stage2", {})
    stage3 = stages.get("stage3", {})
    stage4 = stages.get("stage4", {})
    stage5 = stages.get("stage5", {})

    # 보고서 구조 생성
    report = {
        "report_id": f"report-{project_id}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "generated_at": datetime.now().isoformat(),
        "project_info": {
            "project_id": project_id,
            "project_name": project.get("project_name", ""),
            "company": company_profile
        },
        "report_type": data.report_type,
        "sections": {}
    }

    # 요청된 섹션별 내용 생성
    if "executive_summary" in data.include_sections:
        report["sections"]["executive_summary"] = {
            "title": "경영진 요약",
            "content": {
                "overview": f"{company_profile.get('name', '기업')}의 AI 전환 전략 컨설팅 보고서입니다.",
                "key_findings": [
                    "현재 AI 성숙도 수준 분석 완료",
                    "핵심 AI 도입 기회 영역 도출",
                    "단계별 실행 로드맵 수립"
                ],
                "recommendations_summary": scenario_analysis.get("recommendations", [])
            }
        }

    if "current_state" in data.include_sections:
        report["sections"]["current_state"] = {
            "title": "현황 분석",
            "content": {
                "maturity_level": maturity_assessment.get("overall_score", 0),
                "maturity_details": maturity_assessment.get("scores", {}),
                "company_profile": company_profile
            }
        }

    if "gap_analysis" in data.include_sections:
        report["sections"]["gap_analysis"] = {
            "title": "Gap 분석",
            "content": {
                "current_vs_target": maturity_assessment.get("gaps", {}),
                "priority_areas": opportunities.get("priority_areas", [])
            }
        }

    if "recommendations" in data.include_sections:
        report["sections"]["recommendations"] = {
            "title": "전략적 권고사항",
            "content": {
                "strategic_recommendations": [
                    "AI 거버넌스 체계 수립",
                    "데이터 인프라 현대화",
                    "AI 전문 인력 확보 및 육성",
                    "파일럿 프로젝트 추진"
                ],
                "quick_wins": opportunities.get("quick_wins", []),
                "long_term_initiatives": opportunities.get("long_term", [])
            }
        }

    if "roadmap" in data.include_sections:
        report["sections"]["roadmap"] = {
            "title": "실행 로드맵",
            "content": {
                "phases": roadmap.get("phases", []),
                "milestones": roadmap.get("milestones", []),
                "timeline": roadmap.get("timeline", "18-24개월")
            }
        }

    if "investment" in data.include_sections:
        report["sections"]["investment"] = {
            "title": "투자 계획",
            "content": {
                "total_investment": roadmap.get("total_investment", "미산정"),
                "roi_projection": scenario_analysis.get("scenario_details", {}).get("roi_estimate", "25-40%"),
                "budget_allocation": roadmap.get("budget_allocation", {})
            }
        }

    if "risks" in data.include_sections:
        report["sections"]["risks"] = {
            "title": "리스크 분석",
            "content": {
                "key_risks": [
                    {"risk": "기술 인력 부족", "impact": "높음", "mitigation": "외부 전문가 활용 및 내부 교육"},
                    {"risk": "데이터 품질 이슈", "impact": "높음", "mitigation": "데이터 거버넌스 체계 수립"},
                    {"risk": "조직 저항", "impact": "중간", "mitigation": "변화관리 프로그램 운영"}
                ],
                "risk_level": scenario_analysis.get("scenario_details", {}).get("risk_level", "중간")
            }
        }

    # 보고서 저장
    update_project(project_id, {"latest_report": report})

    return {
        "status": "success",
        "message": "보고서가 생성되었습니다.",
        "report": report
    }


@router.get("/projects/{project_id}/report")
async def get_report(project_id: str):
    """최신 보고서 조회"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    return {
        "status": "success",
        "report": project.get("latest_report", {})
    }


@router.get("/projects/{project_id}/report/download")
async def download_report(project_id: str, format: str = "html"):
    """보고서 다운로드 (HTML 형식)"""
    from fastapi.responses import HTMLResponse

    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    report = project.get("latest_report", {})
    if not report:
        raise HTTPException(status_code=404, detail="생성된 보고서가 없습니다.")

    # HTML 보고서 생성
    html_content = f"""
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI 컨설팅 보고서 - {report.get('project_info', {}).get('project_name', '')}</title>
        <style>
            body {{ font-family: 'Malgun Gothic', sans-serif; line-height: 1.6; max-width: 900px; margin: 0 auto; padding: 40px; }}
            h1 {{ color: #1a365d; border-bottom: 3px solid #3182ce; padding-bottom: 10px; }}
            h2 {{ color: #2c5282; margin-top: 30px; }}
            .section {{ background: #f7fafc; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .meta {{ color: #718096; font-size: 0.9em; }}
            table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
            th, td {{ border: 1px solid #e2e8f0; padding: 12px; text-align: left; }}
            th {{ background: #edf2f7; }}
            .risk-high {{ color: #e53e3e; font-weight: bold; }}
            .risk-medium {{ color: #dd6b20; }}
            .risk-low {{ color: #38a169; }}
        </style>
    </head>
    <body>
        <h1>AI 전환 전략 컨설팅 보고서</h1>
        <p class="meta">프로젝트: {report.get('project_info', {}).get('project_name', '')}<br>
        생성일: {report.get('generated_at', '')[:10]}</p>
    """

    for section_key, section_data in report.get("sections", {}).items():
        html_content += f"""
        <div class="section">
            <h2>{section_data.get('title', section_key)}</h2>
            <pre>{str(section_data.get('content', {}))}</pre>
        </div>
        """

    html_content += """
    </body>
    </html>
    """

    return HTMLResponse(content=html_content, media_type="text/html")
