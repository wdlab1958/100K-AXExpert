"""
Models Package - 모든 모델을 통합하여 export
하위 호환성을 위해 기존 schemas.py에서도 import 가능하도록 유지
"""
# Enums
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

# Company Models
from .company import (
    ITInfrastructure,
    DataAssets,
    HumanResources,
    FinancialResources,
    OrganizationalReadiness,
    CompanyProfile
)

# Consulting Models
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

# 하위 호환성: 기존 schemas.py에서 import하는 경우를 위해
# schemas.py의 나머지 모델들은 그대로 유지하고, 여기서 re-export
try:
    from .schemas import (
        ReportSection,
        ConsultingReport,
        CreateProjectRequest,
        GenerateScenarioRequest,
        SubmitFeedbackRequest,
        ApproveScenarioRequest,
        GenerateReportRequest,
        # MLOps models
        DataManagementStandard,
        ModelDevelopmentStandard,
        ModelEvaluationStandard,
        ModelDeploymentStandard,
        ModelMonitoringStandard,
        MLOpsSecurityGovernance,
        MLOpsStandards,
        # Personnel models
        PersonnelRole,
        StrategyPMOTeam,
        TechDevelopmentTeam,
        DataInfraTeam,
        GovernanceExpertiseTeam,
        PersonnelGapAnalysis,
        PersonnelOrganization,
        SaveMLOpsStandardsRequest,
        SavePersonnelOrganizationRequest
    )
except ImportError:
    # schemas.py가 아직 완전히 분리되지 않은 경우
    pass

# __all__ 정의
__all__ = [
    # Enums
    "IndustryType",
    "CompanySize",
    "MaturityLevel",
    "PriorityLevel",
    "RiskLevel",
    "ConsultingStage",
    "MLOpsImplementationStatus",
    "ExpertiseLevel",
    # Company
    "ITInfrastructure",
    "DataAssets",
    "HumanResources",
    "FinancialResources",
    "OrganizationalReadiness",
    "CompanyProfile",
    # Consulting
    "MaturityDimensionScore",
    "MaturityAssessment",
    "UseCase",
    "ScenarioParameters",
    "Scenario",
    "StageProgress",
    "HumanFeedback",
    "ConsultingProject",
]
