"""
AI Consulting Assistant Platform - Data Models & Schemas
하위 호환성을 위한 통합 모듈 - 새로운 모듈 구조에서 re-export
"""
# 새로운 모듈 구조에서 이미 분리된 모델들을 import
from .enums import (
    IndustryType,
    CompanySize,
    MaturityLevel,
    PriorityLevel,
    RiskLevel,
    ConsultingStage,
    MLOpsImplementationStatus,
    ExpertiseLevel
)

from .company import (
    ITInfrastructure,
    DataAssets,
    HumanResources,
    FinancialResources,
    OrganizationalReadiness,
    CompanyProfile
)

from .consulting import (
    MaturityDimensionScore,
    MaturityAssessment,
    UseCase,
    ScenarioParameters,
    Scenario,
    StageProgress,
    HumanFeedback,
    ConsultingProject
)

# 아직 분리하지 않은 모델들은 아래에 그대로 유지
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


# ==================== Report Models ====================

class ReportSection(BaseModel):
    """보고서 섹션"""
    title: str
    content: str
    charts: List[Dict[str, Any]] = Field(default_factory=list)
    tables: List[Dict[str, Any]] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class ConsultingReport(BaseModel):
    """컨설팅 보고서"""
    id: Optional[str] = None
    project_id: str
    report_type: str  # strategy, design, implementation, final
    title: str

    executive_summary: str
    sections: List[ReportSection] = Field(default_factory=list)

    appendices: List[Dict[str, Any]] = Field(default_factory=list)

    # 메타데이터
    generated_at: datetime = Field(default_factory=datetime.now)
    generated_by: str = Field(default="AI Consulting Assistant")
    version: str = Field(default="1.0")
    status: str = Field(default="draft")  # draft, review, approved, final


# ==================== API Request/Response Models ====================

class CreateProjectRequest(BaseModel):
    """프로젝트 생성 요청"""
    project_name: str
    company_profile: CompanyProfile


class GenerateScenarioRequest(BaseModel):
    """시나리오 생성 요청"""
    project_id: str
    scenario_type: str  # conservative, balanced, aggressive
    parameters: ScenarioParameters


class SubmitFeedbackRequest(BaseModel):
    """피드백 제출 요청"""
    project_id: str
    feedback: HumanFeedback


class ApproveScenarioRequest(BaseModel):
    """시나리오 승인 요청"""
    project_id: str
    scenario_id: str
    approver_role: str
    approver_name: str
    comments: Optional[str] = None


class GenerateReportRequest(BaseModel):
    """보고서 생성 요청"""
    project_id: str
    report_type: str
    include_sections: List[str] = Field(default_factory=list)


# ==================== Chapter 5: MLOps Technical Implementation Standards ====================

class MLOpsImplementationStatus(str, Enum):
    """MLOps 구현 상태"""
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_IMPROVEMENT = "needs_improvement"


class DataManagementStandard(BaseModel):
    """5.2 데이터 관리 및 준비 표준"""
    # 데이터 수집 및 통합
    data_collection_api_type: str = Field(default="", description="데이터 수집 API/커넥터 유형")
    data_lake_warehouse_type: str = Field(default="", description="데이터 레이크/웨어하우스 유형")
    data_pipeline_tool: str = Field(default="", description="데이터 파이프라인 도구 (예: Airflow, Spark)")

    # 데이터 검증
    data_validation_enabled: bool = Field(default=False, description="데이터 검증 자동화 여부")
    schema_validation: bool = Field(default=False, description="스키마 검증")
    statistical_validation: bool = Field(default=False, description="통계적 분포 검증")
    quality_threshold: float = Field(default=0.0, description="품질 임계값")
    alert_on_failure: bool = Field(default=False, description="기준 미달 시 알림 발생")

    # Feature Store
    feature_store_enabled: bool = Field(default=False, description="Feature Store 구축 여부")
    feature_store_tool: str = Field(default="", description="Feature Store 도구 (예: Feast, Tecton)")
    offline_online_consistency: bool = Field(default=False, description="오프라인/온라인 일관성 보장")

    # 데이터 버전 관리
    data_versioning_enabled: bool = Field(default=False, description="데이터 버전 관리 여부")
    dvc_tool: str = Field(default="", description="DVC 도구 (예: DVC, LakeFS)")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class ModelDevelopmentStandard(BaseModel):
    """5.3 모델 개발 및 훈련 표준"""
    # 모델 개발 환경
    containerized_environment: bool = Field(default=False, description="컨테이너화된 개발 환경")
    container_platform: str = Field(default="", description="컨테이너 플랫폼 (Docker, Kubernetes)")
    standard_image_registry: str = Field(default="", description="표준 이미지 레지스트리")

    # 실험 관리
    experiment_tracking_enabled: bool = Field(default=False, description="실험 관리 활성화")
    experiment_tracking_tool: str = Field(default="", description="실험 관리 도구 (MLflow, W&B, Neptune)")
    auto_logging_params: bool = Field(default=False, description="파라미터 자동 로깅")
    auto_logging_metrics: bool = Field(default=False, description="메트릭 자동 로깅")
    auto_logging_artifacts: bool = Field(default=False, description="아티팩트 자동 로깅")

    # 모델 버전 관리
    model_registry_enabled: bool = Field(default=False, description="모델 레지스트리 구축")
    model_registry_tool: str = Field(default="", description="모델 레지스트리 도구")
    model_metadata_tracking: bool = Field(default=False, description="모델 메타데이터 추적")

    # 하이퍼파라미터 최적화
    hpo_enabled: bool = Field(default=False, description="하이퍼파라미터 최적화 자동화")
    hpo_tool: str = Field(default="", description="HPO 도구 (Optuna, Ray Tune, Hyperopt)")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class ModelEvaluationStandard(BaseModel):
    """5.4 모델 평가 및 검증 표준"""
    # 성능 지표 자동 평가
    auto_evaluation_enabled: bool = Field(default=False, description="자동 평가 활성화")
    technical_metrics: List[str] = Field(default_factory=list, description="기술 지표 (F1, AUC 등)")
    business_metrics: List[str] = Field(default_factory=list, description="비즈니스 지표 (ROI, 전환율 등)")

    # XAI (설명가능성)
    xai_enabled: bool = Field(default=False, description="XAI 적용 여부")
    xai_methods: List[str] = Field(default_factory=list, description="XAI 기법 (LIME, SHAP 등)")
    feature_importance_tracking: bool = Field(default=False, description="특성 중요도 추적")

    # 오류 및 이상 탐지 검증
    robustness_testing_enabled: bool = Field(default=False, description="견고성 테스트 자동화")
    edge_case_testing: bool = Field(default=False, description="엣지 케이스 테스트")
    ethics_risk_testing: bool = Field(default=False, description="윤리/위험 테스트")

    # 배포 승인 게이트
    deployment_gate_enabled: bool = Field(default=False, description="배포 승인 게이트 활성화")
    min_performance_threshold: Dict[str, float] = Field(default_factory=dict, description="최소 성능 기준")
    ethics_review_required: bool = Field(default=False, description="윤리 검토 필수 여부")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class ModelDeploymentStandard(BaseModel):
    """5.5 모델 배포 및 서비스 표준"""
    # 지속적 배포
    cd_pipeline_enabled: bool = Field(default=False, description="CD 파이프라인 구축")
    cd_tool: str = Field(default="", description="CD 도구 (Jenkins, GitLab CI, Argo CD)")
    auto_deployment: bool = Field(default=False, description="자동 배포 활성화")

    # 서비스 구조 표준화
    api_type: str = Field(default="rest", description="API 유형 (REST, gRPC)")
    api_gateway: str = Field(default="", description="API Gateway")
    load_balancer: str = Field(default="", description="로드 밸런서")

    # 배포 전략
    deployment_strategy: str = Field(default="", description="배포 전략 (Canary, Blue/Green, Rolling)")
    canary_percentage: float = Field(default=0.0, description="Canary 배포 비율")
    rollback_enabled: bool = Field(default=False, description="자동 롤백 활성화")

    # A/B 테스트
    ab_testing_enabled: bool = Field(default=False, description="A/B 테스트 지원")
    traffic_splitting_tool: str = Field(default="", description="트래픽 분할 도구")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class ModelMonitoringStandard(BaseModel):
    """5.6 모델 모니터링 및 재학습 표준"""
    # 실시간 성능 모니터링
    realtime_monitoring_enabled: bool = Field(default=False, description="실시간 모니터링 활성화")
    latency_tracking: bool = Field(default=False, description="응답 지연 시간 추적")
    throughput_tracking: bool = Field(default=False, description="처리량 추적")
    error_rate_tracking: bool = Field(default=False, description="오류율 추적")
    accuracy_tracking: bool = Field(default=False, description="정확도 추적")
    monitoring_tool: str = Field(default="", description="모니터링 도구 (Prometheus, Grafana, DataDog)")

    # 드리프트 감지
    data_drift_detection: bool = Field(default=False, description="데이터 드리프트 감지")
    concept_drift_detection: bool = Field(default=False, description="개념 드리프트 감지")
    drift_detection_tool: str = Field(default="", description="드리프트 감지 도구 (Evidently, NannyML)")
    drift_threshold: float = Field(default=0.0, description="드리프트 임계값")

    # 자동 재학습
    auto_retraining_enabled: bool = Field(default=False, description="자동 재학습 활성화")
    retraining_trigger: str = Field(default="", description="재학습 트리거 조건")
    retraining_schedule: str = Field(default="", description="재학습 스케줄")

    # 피드백 루프
    feedback_loop_enabled: bool = Field(default=False, description="피드백 루프 구축")
    human_feedback_collection: bool = Field(default=False, description="현업 피드백 수집")
    prediction_logging: bool = Field(default=False, description="예측 결과 로깅")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class MLOpsSecurityGovernance(BaseModel):
    """5.7 보안 및 거버넌스 통합"""
    # 접근 통제
    rbac_enabled: bool = Field(default=False, description="RBAC 구현")
    least_privilege_principle: bool = Field(default=False, description="최소 권한 원칙 적용")
    access_control_tool: str = Field(default="", description="접근 통제 도구")

    # 파이프라인 감사 추적
    audit_trail_enabled: bool = Field(default=False, description="감사 추적 활성화")
    audit_logging_scope: List[str] = Field(default_factory=list, description="감사 로깅 범위")
    audit_retention_period: int = Field(default=0, description="감사 로그 보존 기간 (일)")

    # 보안 스캐닝
    code_security_scan: bool = Field(default=False, description="코드 보안 스캐닝")
    container_security_scan: bool = Field(default=False, description="컨테이너 이미지 스캐닝")
    security_scan_tool: str = Field(default="", description="보안 스캐닝 도구")
    cicd_integration: bool = Field(default=False, description="CI/CD 파이프라인 통합")

    implementation_status: MLOpsImplementationStatus = Field(default=MLOpsImplementationStatus.NOT_STARTED)
    notes: str = Field(default="", description="추가 메모")


class MLOpsStandards(BaseModel):
    """제5장 MLOps 기술적 구현 표준 종합"""
    project_id: Optional[str] = None

    data_management: DataManagementStandard = Field(default_factory=DataManagementStandard)
    model_development: ModelDevelopmentStandard = Field(default_factory=ModelDevelopmentStandard)
    model_evaluation: ModelEvaluationStandard = Field(default_factory=ModelEvaluationStandard)
    model_deployment: ModelDeploymentStandard = Field(default_factory=ModelDeploymentStandard)
    model_monitoring: ModelMonitoringStandard = Field(default_factory=ModelMonitoringStandard)
    security_governance: MLOpsSecurityGovernance = Field(default_factory=MLOpsSecurityGovernance)

    overall_maturity_score: float = Field(default=0.0, description="MLOps 전체 성숙도 점수 (0-100)")
    recommendations: List[str] = Field(default_factory=list, description="개선 권고사항")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


# ==================== Chapter 6: Personnel Organization & Structure ====================

class ExpertiseLevel(str, Enum):
    """역량 수준"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"


class PersonnelRole(BaseModel):
    """인력 역할 정의"""
    role_id: str
    role_name: str
    role_name_en: str
    category: str = Field(description="영역 (strategy_pmo, tech_dev, data_infra, governance)")

    key_responsibilities: List[str] = Field(default_factory=list, description="핵심 책임")
    required_competencies: List[str] = Field(default_factory=list, description="필수 역량")
    recommended_experience_years: int = Field(default=0, description="권장 경력 (년)")

    # 현황
    current_headcount: int = Field(default=0, description="현재 인원")
    target_headcount: int = Field(default=0, description="목표 인원")
    gap: int = Field(default=0, description="Gap (목표 - 현재)")

    # 충원 계획
    hiring_plan: str = Field(default="", description="충원 계획")
    training_plan: str = Field(default="", description="교육/역량 개발 계획")


class StrategyPMOTeam(BaseModel):
    """6.2 전략 및 프로젝트 관리 인력"""
    # Engagement Manager
    engagement_manager: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="em",
            role_name="Engagement Manager",
            role_name_en="Engagement Manager",
            category="strategy_pmo",
            key_responsibilities=[
                "프로젝트 총괄 책임자",
                "고객 관계 관리",
                "예산/일정 관리",
                "최종 산출물 검토 및 품질 보증"
            ],
            required_competencies=[
                "컨설팅 경험 (10년 이상)",
                "비즈니스 전략 이해",
                "리더십",
                "계약 관리"
            ],
            recommended_experience_years=10
        )
    )

    # AI Strategist
    ai_strategist: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="strategist",
            role_name="AI 전략가",
            role_name_en="AI Strategist",
            category="strategy_pmo",
            key_responsibilities=[
                "AI 비전 및 전략 수립",
                "비즈니스 가치(ROI) 분석",
                "AI 활용 사례 발굴 및 우선순위 결정"
            ],
            required_competencies=[
                "경영학/경제학 기반",
                "AI 기술 트렌드 이해",
                "산업 특화 지식"
            ],
            recommended_experience_years=7
        )
    )

    # Business Analyst
    business_analyst: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="ba",
            role_name="비즈니스 분석가",
            role_name_en="Business Analyst",
            category="strategy_pmo",
            key_responsibilities=[
                "고객사의 현행 업무 프로세스 분석",
                "상세 요구사항 정의 및 문서화"
            ],
            required_competencies=[
                "프로세스 분석 능력",
                "시스템 설계 지식",
                "커뮤니케이션 스킬"
            ],
            recommended_experience_years=5
        )
    )


class TechDevelopmentTeam(BaseModel):
    """6.3 기술 및 모델 개발 인력"""
    # Lead Data Scientist
    lead_data_scientist: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="lead_ds",
            role_name="리드 데이터 사이언티스트",
            role_name_en="Lead Data Scientist",
            category="tech_dev",
            key_responsibilities=[
                "AI 모델링 방법론 총괄",
                "모델 아키텍처 설계",
                "알고리즘 선택",
                "모델 성능 최적화 및 검증"
            ],
            required_competencies=[
                "고급 통계학 및 ML/DL 지식",
                "Python/R",
                "벤치마킹 경험"
            ],
            recommended_experience_years=7
        )
    )

    # ML Engineer
    ml_engineer: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="mle",
            role_name="ML 엔지니어",
            role_name_en="ML Engineer",
            category="tech_dev",
            key_responsibilities=[
                "AI 모델의 프로덕션 환경 적용",
                "MLOps 파이프라인 구축",
                "서비스 API 구현 및 시스템 통합"
            ],
            required_competencies=[
                "소프트웨어 엔지니어링",
                "MLOps 프레임워크",
                "클라우드 서비스 이해"
            ],
            recommended_experience_years=5
        )
    )

    # Software Engineer
    software_engineer: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="swe",
            role_name="소프트웨어 엔지니어",
            role_name_en="Software Engineer",
            category="tech_dev",
            key_responsibilities=[
                "AI 서비스의 백엔드/프론트엔드 시스템 구축",
                "레거시 시스템 통합 모듈 개발",
                "API 설계"
            ],
            required_competencies=[
                "마이크로 서비스 아키텍처",
                "시스템 통합(SI) 경험",
                "DevOps"
            ],
            recommended_experience_years=5
        )
    )


class DataInfraTeam(BaseModel):
    """6.4 데이터 및 인프라 인력"""
    # Data Engineer
    data_engineer: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="de",
            role_name="데이터 엔지니어",
            role_name_en="Data Engineer",
            category="data_infra",
            key_responsibilities=[
                "데이터 파이프라인 설계 및 구축 (ETL/ELT)",
                "Feature Store 구축",
                "데이터 레이크 관리"
            ],
            required_competencies=[
                "대규모 데이터 처리 (Spark, Hadoop)",
                "SQL/NoSQL",
                "클라우드 데이터 서비스"
            ],
            recommended_experience_years=5
        )
    )

    # Cloud/Infra Architect
    cloud_infra_architect: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="infra",
            role_name="클라우드/인프라 아키텍트",
            role_name_en="Cloud/Infra Architect",
            category="data_infra",
            key_responsibilities=[
                "AI 시스템을 위한 클라우드 인프라 설계",
                "리소스 확장성",
                "보안 및 비용 최적화"
            ],
            required_competencies=[
                "AWS, Azure, GCP 인증 및 경험",
                "Kubernetes"
            ],
            recommended_experience_years=7
        )
    )

    # Data Steward/Curator
    data_steward: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="steward",
            role_name="데이터 스튜어드/큐레이터",
            role_name_en="Data Steward/Curator",
            category="data_infra",
            key_responsibilities=[
                "데이터 거버넌스 정책 준수 확인",
                "메타데이터 관리",
                "데이터 적법성 및 보안 감사 지원"
            ],
            required_competencies=[
                "데이터 관리 지식 (DAMA)",
                "개인정보 보호법",
                "컴플라이언스 이해"
            ],
            recommended_experience_years=5
        )
    )


class GovernanceExpertiseTeam(BaseModel):
    """6.5 거버넌스 및 전문성 인력"""
    # AI Ethics Officer
    ai_ethics_officer: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="ethics",
            role_name="AI 윤리 담당자",
            role_name_en="AI Ethics Officer",
            category="governance",
            key_responsibilities=[
                "AI 윤리 정책 수립 및 검토",
                "편향성/공정성 감사",
                "규제 준수 모니터링"
            ],
            required_competencies=[
                "AI 윤리/법률 지식",
                "리스크 관리",
                "규제 분석"
            ],
            recommended_experience_years=5
        )
    )

    # Domain Expert
    domain_expert: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="domain",
            role_name="도메인 전문가",
            role_name_en="Domain Expert",
            category="governance",
            key_responsibilities=[
                "산업별 전문 지식 제공",
                "비즈니스 요구사항 검증",
                "AI 결과물 현업 적용성 평가"
            ],
            required_competencies=[
                "해당 산업 경력 (10년 이상)",
                "현업 프로세스 이해",
                "변화 관리 경험"
            ],
            recommended_experience_years=10
        )
    )

    # Quality Assurance
    qa_engineer: PersonnelRole = Field(
        default_factory=lambda: PersonnelRole(
            role_id="qa",
            role_name="QA 엔지니어",
            role_name_en="QA Engineer",
            category="governance",
            key_responsibilities=[
                "AI 모델 및 시스템 품질 검증",
                "테스트 자동화 구축",
                "성능/부하 테스트"
            ],
            required_competencies=[
                "테스트 자동화",
                "ML 테스트 방법론",
                "CI/CD 통합"
            ],
            recommended_experience_years=5
        )
    )


class PersonnelGapAnalysis(BaseModel):
    """인력 Gap 분석"""
    category: str
    current_total: int = Field(default=0, description="현재 총 인원")
    target_total: int = Field(default=0, description="목표 총 인원")
    gap: int = Field(default=0, description="Gap")
    gap_percentage: float = Field(default=0.0, description="Gap 비율 (%)")
    priority_roles: List[str] = Field(default_factory=list, description="우선 충원 필요 역할")
    recommendations: List[str] = Field(default_factory=list, description="권고사항")


class PersonnelOrganization(BaseModel):
    """제6장 필수 인력 구성 및 조직 체계 종합"""
    project_id: Optional[str] = None

    # 팀별 인력 구성
    strategy_pmo_team: StrategyPMOTeam = Field(default_factory=StrategyPMOTeam)
    tech_development_team: TechDevelopmentTeam = Field(default_factory=TechDevelopmentTeam)
    data_infra_team: DataInfraTeam = Field(default_factory=DataInfraTeam)
    governance_expertise_team: GovernanceExpertiseTeam = Field(default_factory=GovernanceExpertiseTeam)

    # Gap 분석
    gap_analysis: List[PersonnelGapAnalysis] = Field(default_factory=list)

    # 조직 구조
    organization_structure: str = Field(default="", description="조직 구조 설명")
    reporting_lines: Dict[str, str] = Field(default_factory=dict, description="보고 체계")

    # 외부 리소스 계획
    outsourcing_plan: str = Field(default="", description="외주/파트너 활용 계획")
    training_budget: float = Field(default=0.0, description="교육 예산 (억원)")

    # 채용 계획
    hiring_timeline: Dict[str, List[str]] = Field(default_factory=dict, description="채용 타임라인")

    total_current_headcount: int = Field(default=0, description="현재 총 인원")
    total_target_headcount: int = Field(default=0, description="목표 총 인원")

    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None


# ==================== API Request Models for Chapter 5 & 6 ====================

class SaveMLOpsStandardsRequest(BaseModel):
    """MLOps 표준 저장 요청"""
    project_id: str
    mlops_standards: MLOpsStandards


class SavePersonnelOrganizationRequest(BaseModel):
    """인력 구성 저장 요청"""
    project_id: str
    personnel_organization: PersonnelOrganization
