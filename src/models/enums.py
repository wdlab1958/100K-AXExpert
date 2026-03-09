"""
Enums - 모든 Enum 타입 정의
"""
from enum import Enum


class IndustryType(str, Enum):
    """산업 분류"""
    MANUFACTURING = "manufacturing"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    RETAIL = "retail"
    LOGISTICS = "logistics"
    IT_SERVICE = "it_service"
    PUBLIC = "public"
    OTHER = "other"


class CompanySize(str, Enum):
    """기업 규모"""
    STARTUP = "startup"  # 스타트업 (50인 미만)
    SME = "sme"  # 중소기업 (50-300인)
    MIDSIZE = "midsize"  # 중견기업 (300-1000인)
    LARGE = "large"  # 대기업 (1000인 이상)


class MaturityLevel(int, Enum):
    """AI 성숙도 레벨"""
    INITIAL = 1
    REPEATABLE = 2
    DEFINED = 3
    MANAGED = 4
    OPTIMIZED = 5


class PriorityLevel(str, Enum):
    """우선순위"""
    QUICK_WIN = "quick_win"  # 높은 가치 + 높은 용이성
    STRATEGIC = "strategic"  # 높은 가치 + 낮은 용이성
    FILL_IN = "fill_in"  # 낮은 가치 + 높은 용이성
    RECONSIDER = "reconsider"  # 낮은 가치 + 낮은 용이성


class RiskLevel(str, Enum):
    """리스크 등급"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ConsultingStage(int, Enum):
    """컨설팅 단계"""
    STRATEGY = 1  # AI 비전 및 전략 수립
    DESIGN = 2  # Use Case 및 설계 정의
    BUILD = 3  # 플랫폼 및 솔루션 구축
    SCALE = 4  # 파일럿 및 확산
    OPERATE = 5  # 운영, 모니터링 및 개선


class MLOpsImplementationStatus(str, Enum):
    """MLOps 구현 상태"""
    NOT_STARTED = "not_started"
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    NEEDS_IMPROVEMENT = "needs_improvement"


class ExpertiseLevel(str, Enum):
    """역량 수준"""
    JUNIOR = "junior"
    INTERMEDIATE = "intermediate"
    SENIOR = "senior"
    EXPERT = "expert"

