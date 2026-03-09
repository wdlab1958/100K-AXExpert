"""
100K-AX Expert Platform - Configuration Settings
AI/AX 10만 전문인력 양성 플랫폼 설정
"""
from pydantic_settings import BaseSettings
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application Settings"""

    # Application
    APP_NAME: str = "100K-AX Expert Platform"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = True

    # AX Training Configuration
    AX_TRAINING_TARGET: int = 100000  # 10만명 양성 목표
    AX_ENTERPRISE_TARGET: int = 10000  # 10,000기업 목표
    AX_CERTIFICATION_LEVELS: int = 5  # 5등급 인증 체계
    AX_DOMAINS: list = ["manufacturing", "finance", "public", "logistics", "healthcare", "education", "defense"]

    # Ollama Configuration
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "llama3.2:latest"  # 사용 가능한 로컬 모델
    OLLAMA_EMBEDDING_MODEL: str = "nomic-embed-text"

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/consulting.db"

    # Paths
    BASE_DIR: Path = Path(__file__).resolve().parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    REPORTS_DIR: Path = BASE_DIR / "reports"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # Agent Configuration
    MAX_AGENT_ITERATIONS: int = 10
    AGENT_TIMEOUT: int = 300  # seconds

    # Report Generation
    DEFAULT_LANGUAGE: str = "ko"
    REPORT_FORMAT: str = "docx"  # docx, pdf, html

    class Config:
        env_file = ".env"
        case_sensitive = True


# 컨설팅 5단계 프레임워크 정의
CONSULTING_FRAMEWORK = {
    "stages": [
        {
            "id": 1,
            "name": "AI 비전 및 전략 수립",
            "name_en": "Strategy",
            "description": "고객사의 AI 도입 목표와 전사적 방향 정의",
            "activities": [
                "AI 성숙도 진단",
                "기회 발굴",
                "전략 및 로드맵 수립"
            ],
            "outputs": [
                "AI 비전 선언문",
                "AI 성숙도 진단 보고서",
                "AI 활용 사례 후보 목록",
                "AI 전략 로드맵"
            ]
        },
        {
            "id": 2,
            "name": "Use Case 및 설계 정의",
            "name_en": "Define & Design",
            "description": "우선순위 높은 과제에 대한 구체적인 AI 시스템/솔루션 설계",
            "activities": [
                "상세 요건 정의",
                "기술 및 아키텍처 설계",
                "거버넌스 및 윤리 체계 수립"
            ],
            "outputs": [
                "AI 솔루션 요구사항 정의서",
                "AI 시스템 아키텍처 설계서",
                "데이터 파이프라인 설계서",
                "AI 거버넌스 체계 수립 계획"
            ]
        },
        {
            "id": 3,
            "name": "플랫폼 및 솔루션 구축",
            "name_en": "Build & Implement",
            "description": "AI 플랫폼 구축 및 개별 AI 솔루션 검증(PoC) 및 개발/통합",
            "activities": [
                "PoC 수행",
                "AI 플랫폼 구축",
                "솔루션 개발 및 통합"
            ],
            "outputs": [
                "PoC 결과 보고서",
                "AI 모델 개발 문서",
                "MLOps 플랫폼 구축 가이드",
                "시스템 통합 테스트 결과서"
            ]
        },
        {
            "id": 4,
            "name": "파일럿 및 확산",
            "name_en": "Scale & Deploy",
            "description": "개발된 솔루션의 현업 적용 및 전사적 확산",
            "activities": [
                "파일럿 운영",
                "변화 관리",
                "전사 확산"
            ],
            "outputs": [
                "파일럿 운영 결과 보고서",
                "사용자 교육 자료",
                "운영 매뉴얼",
                "지속적 개선 계획"
            ]
        },
        {
            "id": 5,
            "name": "운영, 모니터링 및 개선",
            "name_en": "Operate & Optimize",
            "description": "구축된 AI 시스템의 지속적 가치 창출을 위한 관리 및 개선",
            "activities": [
                "운영 및 모니터링",
                "피드백 루프 및 지속적 개선",
                "거버넌스 관리"
            ],
            "outputs": [
                "운영 현황 대시보드",
                "성능 모니터링 보고서",
                "개선 과제 목록",
                "거버넌스 감사 보고서"
            ]
        }
    ]
}

# AI 성숙도 진단 모델
MATURITY_MODEL = {
    "levels": [
        {"level": 1, "name": "초기 (Initial)", "description": "AI 활동이 산발적이며 특정 개인의 역량에 의존"},
        {"level": 2, "name": "반복 가능 (Repeatable)", "description": "최소한의 프로젝트 관리 체계 수립"},
        {"level": 3, "name": "정의됨 (Defined)", "description": "표준 프로세스 및 방법론이 전사적으로 문서화"},
        {"level": 4, "name": "관리됨 (Managed)", "description": "정량적 측정 지표(KPI) 기반 프로세스 관리"},
        {"level": 5, "name": "최적화됨 (Optimized)", "description": "AI가 비즈니스 전략의 핵심 동력"}
    ],
    "dimensions": [
        {
            "id": "strategy",
            "name": "전략 및 비전",
            "items": [
                "AI 비전 및 목표의 명확성",
                "AI 투자 및 예산 관리 체계",
                "AI 활용 사례 포트폴리오 관리",
                "AI ROI 측정 체계"
            ]
        },
        {
            "id": "organization",
            "name": "조직 및 역량",
            "items": [
                "AI 전담 조직 및 역할 정의",
                "AI 인력 확보 및 역량 수준",
                "AI 교육 및 역량 개발 프로그램",
                "변화 관리 및 AI 문화"
            ]
        },
        {
            "id": "data_tech",
            "name": "데이터 및 기술",
            "items": [
                "데이터 인프라 및 접근성",
                "데이터 품질 및 거버넌스",
                "MLOps 플랫폼 활용 수준",
                "클라우드 활용 및 확장성"
            ]
        },
        {
            "id": "process",
            "name": "프로세스 및 거버넌스",
            "items": [
                "AI 개발 방법론 표준화",
                "모델 검증 및 배포 승인 절차",
                "AI 윤리 및 리스크 관리",
                "모니터링 및 운영 체계"
            ]
        }
    ]
}

# 산업별 AI 적용 템플릿
INDUSTRY_TEMPLATES = {
    "manufacturing": {
        "name": "제조업",
        "use_cases": [
            {"name": "품질 검사 자동화", "roi_range": "높음", "complexity": "중간"},
            {"name": "예지 정비", "roi_range": "높음", "complexity": "중간"},
            {"name": "공정 최적화", "roi_range": "매우 높음", "complexity": "높음"},
            {"name": "수요 예측", "roi_range": "중간", "complexity": "중간"}
        ]
    },
    "finance": {
        "name": "금융업",
        "use_cases": [
            {"name": "신용 평가", "roi_range": "높음", "complexity": "중간"},
            {"name": "이상 거래 탐지", "roi_range": "높음", "complexity": "중간"},
            {"name": "고객 서비스 자동화", "roi_range": "중간", "complexity": "낮음"},
            {"name": "투자 분석", "roi_range": "매우 높음", "complexity": "높음"}
        ]
    },
    "healthcare": {
        "name": "의료/헬스케어",
        "use_cases": [
            {"name": "의료 영상 분석", "roi_range": "높음", "complexity": "높음"},
            {"name": "신약 개발", "roi_range": "매우 높음", "complexity": "매우 높음"},
            {"name": "개인 맞춤 의료", "roi_range": "높음", "complexity": "높음"},
            {"name": "환자 모니터링", "roi_range": "중간", "complexity": "중간"}
        ]
    },
    "retail": {
        "name": "유통/물류",
        "use_cases": [
            {"name": "수요 예측", "roi_range": "높음", "complexity": "중간"},
            {"name": "개인화 추천", "roi_range": "높음", "complexity": "중간"},
            {"name": "물류 최적화", "roi_range": "높음", "complexity": "중간"},
            {"name": "자동화 물류센터", "roi_range": "매우 높음", "complexity": "높음"}
        ]
    }
}


# MLOps 기술적 구현 표준 (제5장)
MLOPS_STANDARDS = {
    "overview": {
        "title": "MLOps 기술적 구현 표준",
        "description": "AI 모델 개발(Dev), 배포(Ops), 운영 및 모니터링을 자동화하고 표준화하여, AI 시스템의 신뢰성, 확장성, 효율성을 확보하기 위한 기술적 구현 방안"
    },
    "sections": [
        {
            "id": "data_management",
            "name": "5.2 데이터 관리 및 준비",
            "name_en": "Data Management & Preparation",
            "description": "AI 시스템의 근간이 되는 데이터의 수집, 검증 및 특성(Feature) 관리를 자동화하고 표준화합니다.",
            "areas": [
                {
                    "name": "데이터 수집 및 통합",
                    "standard": "데이터 레이크 또는 데이터 웨어하우스와의 표준 API 또는 커넥터를 사용한 데이터 수집 파이프라인 구축",
                    "tools": ["Apache Airflow", "Apache Spark", "AWS Glue", "Azure Data Factory"]
                },
                {
                    "name": "데이터 검증 (Data Validation)",
                    "standard": "데이터 스키마, 통계적 분포, 품질 지표에 대한 자동화된 검증 모듈 구현. 기준 미달 시 파이프라인 중단 및 알림 발생",
                    "tools": ["Great Expectations", "TensorFlow Data Validation", "Deequ"]
                },
                {
                    "name": "특성 저장소 (Feature Store)",
                    "standard": "모델 학습 및 서비스에 필요한 특성을 표준화된 형식으로 저장 및 관리. 오프라인/온라인 환경 간 일관성 보장",
                    "tools": ["Feast", "Tecton", "Hopsworks", "AWS SageMaker Feature Store"]
                },
                {
                    "name": "데이터 버전 관리 (DVC)",
                    "standard": "모델 학습에 사용된 데이터 세트 전체를 버전별로 관리하여 재현성 확보",
                    "tools": ["DVC", "LakeFS", "Delta Lake", "Apache Iceberg"]
                }
            ]
        },
        {
            "id": "model_development",
            "name": "5.3 모델 개발 및 훈련",
            "name_en": "Model Development & Training",
            "description": "모델 코딩, 학습 환경 설정, 실험 관리 및 버전 관리를 자동화하고 체계화합니다.",
            "areas": [
                {
                    "name": "모델 개발 환경",
                    "standard": "모든 개발 및 학습 환경을 Docker 또는 Kubernetes 기반의 표준 컨테이너 이미지로 통일",
                    "tools": ["Docker", "Kubernetes", "AWS EKS", "Google GKE"]
                },
                {
                    "name": "실험 관리 (Experiment Tracking)",
                    "standard": "모델 코드, 학습 매개변수, 성능 지표, 학습 로그 등을 자동으로 기록하고 중앙 집중식으로 관리",
                    "tools": ["MLflow", "Weights & Biases", "Neptune.ai", "Comet ML"]
                },
                {
                    "name": "모델 버전 관리",
                    "standard": "학습 완료된 모델 아티팩트를 모델 레지스트리에 성능 및 메타데이터와 함께 등록하고 버전 관리",
                    "tools": ["MLflow Model Registry", "AWS SageMaker Model Registry", "Vertex AI Model Registry"]
                },
                {
                    "name": "하이퍼파라미터 최적화",
                    "standard": "자동화된 튜닝 프레임워크를 사용하여 최적의 하이퍼파라미터 조합 탐색",
                    "tools": ["Optuna", "Ray Tune", "Hyperopt", "Keras Tuner"]
                }
            ]
        },
        {
            "id": "model_evaluation",
            "name": "5.4 모델 평가 및 검증",
            "name_en": "Model Evaluation & Validation",
            "description": "모델의 성능과 품질을 자동으로 평가하고 검증합니다.",
            "areas": [
                {
                    "name": "성능 지표 자동 평가",
                    "standard": "기술적 지표(F1 Score, AUC 등)와 비즈니스 지표(ROI, 전환율 등)를 정의하고 자동 평가",
                    "tools": ["scikit-learn metrics", "TensorFlow Model Analysis", "Evidently"]
                },
                {
                    "name": "모델 설명 가능성 (XAI)",
                    "standard": "LIME, SHAP 등 XAI 기법을 적용하여 모델의 의사결정 요인 및 특성 중요도 산출",
                    "tools": ["SHAP", "LIME", "Captum", "InterpretML"]
                },
                {
                    "name": "오류 및 이상 탐지 검증",
                    "standard": "엣지 케이스 또는 잠재적 윤리 문제를 유발할 수 있는 데이터에 대한 견고성 테스트 자동화",
                    "tools": ["Checklist", "ART (Adversarial Robustness Toolbox)", "Fairlearn"]
                },
                {
                    "name": "배포 승인 게이트",
                    "standard": "평가 지표가 최소 성능 기준을 충족하고 윤리/위험 평가를 통과한 모델만 배포 진행",
                    "tools": ["MLflow", "Kubeflow Pipelines", "Custom CI/CD Gates"]
                }
            ]
        },
        {
            "id": "model_deployment",
            "name": "5.5 모델 배포 및 서비스",
            "name_en": "Model Deployment & Serving",
            "description": "모델을 프로덕션 환경에 안전하고 효율적으로 배포합니다.",
            "areas": [
                {
                    "name": "지속적 배포 (CD)",
                    "standard": "모델 검증 완료 시 자동으로 프로덕션 환경에 배포되는 파이프라인 구축",
                    "tools": ["Jenkins", "GitLab CI/CD", "Argo CD", "Tekton"]
                },
                {
                    "name": "서비스 구조 표준화",
                    "standard": "모든 모델은 RESTful API 또는 gRPC를 통해 표준화된 엔드포인트 제공",
                    "tools": ["FastAPI", "TensorFlow Serving", "Triton Inference Server", "Seldon Core"]
                },
                {
                    "name": "배포 전략",
                    "standard": "Canary Deployment 또는 Blue/Green Deployment 전략 구현",
                    "tools": ["Istio", "Argo Rollouts", "AWS App Mesh", "Flagger"]
                },
                {
                    "name": "A/B 테스트",
                    "standard": "새 모델과 기존 모델 간의 성능 비교를 위한 자동 트래픽 분산 및 모니터링",
                    "tools": ["Istio", "Ambassador", "Split.io", "LaunchDarkly"]
                }
            ]
        },
        {
            "id": "model_monitoring",
            "name": "5.6 모델 모니터링 및 재학습",
            "name_en": "Model Monitoring & Retraining",
            "description": "운영 중인 모델의 성능을 지속적으로 모니터링하고 필요시 재학습합니다.",
            "areas": [
                {
                    "name": "실시간 성능 모니터링",
                    "standard": "응답 지연 시간, 처리량, 시스템 오류율 및 모델 정확도를 실시간 추적",
                    "tools": ["Prometheus", "Grafana", "Datadog", "New Relic"]
                },
                {
                    "name": "데이터/개념 드리프트 감지",
                    "standard": "운영 데이터의 통계적 분포 변화 및 개념 드리프트 자동 감지",
                    "tools": ["Evidently", "NannyML", "Alibi Detect", "WhyLabs"]
                },
                {
                    "name": "자동 재학습 트리거",
                    "standard": "모델 성능 저하 또는 드리프트가 임계치 초과 시 자동 재학습 파이프라인 트리거",
                    "tools": ["Kubeflow Pipelines", "Apache Airflow", "AWS Step Functions"]
                },
                {
                    "name": "피드백 루프",
                    "standard": "프로덕션 예측 결과 및 현업 피드백을 새로운 학습 데이터로 수집하여 모델 개선",
                    "tools": ["Label Studio", "Prodigy", "Snorkel", "Custom Feedback Systems"]
                }
            ]
        },
        {
            "id": "security_governance",
            "name": "5.7 보안 및 거버넌스 통합",
            "name_en": "Security & Governance Integration",
            "description": "MLOps 파이프라인 전반에 보안과 거버넌스를 통합합니다.",
            "areas": [
                {
                    "name": "접근 통제 (Access Control)",
                    "standard": "각 MLOps 구성 요소 및 데이터에 대한 접근 권한을 최소 권한 원칙으로 제한, RBAC 구현",
                    "tools": ["Keycloak", "AWS IAM", "Azure AD", "Open Policy Agent"]
                },
                {
                    "name": "파이프라인 감사 추적",
                    "standard": "데이터 준비부터 모델 배포까지 모든 작업 단계와 변경 사항을 자동 기록",
                    "tools": ["MLflow Tracking", "Apache Atlas", "DataHub", "OpenLineage"]
                },
                {
                    "name": "보안 스캐닝",
                    "standard": "모델 코드 및 컨테이너 이미지에 대한 보안 취약점 스캐닝을 CI/CD 파이프라인에 통합",
                    "tools": ["Snyk", "Trivy", "Anchore", "SonarQube"]
                }
            ]
        }
    ]
}

# 필수 인력 구성 및 조직 체계 (제6장)
PERSONNEL_ORGANIZATION = {
    "overview": {
        "title": "필수 인력 구성 및 조직 체계",
        "description": "AI 컨설팅 전문기업으로서 고객사를 성공적으로 지원하기 위해 4개 전문 영역의 핵심 인력을 확보하고, AI 전략 수립부터 MLOps 구축 및 운영, 거버넌스 수립까지 엔드-투-엔드 서비스를 제공할 수 있는 팀 구조를 목표로 합니다."
    },
    "teams": [
        {
            "id": "strategy_pmo",
            "name": "6.2 전략 및 프로젝트 관리",
            "name_en": "Strategy & PMO",
            "description": "고객사의 비즈니스 요구사항을 AI 솔루션으로 전환하고, 프로젝트 전체를 관리하며 고객과의 소통을 담당합니다.",
            "roles": [
                {
                    "role_id": "em",
                    "role_name": "Engagement Manager (EM)",
                    "responsibilities": [
                        "프로젝트 총괄 책임자",
                        "고객 관계 관리",
                        "예산/일정 관리",
                        "최종 산출물 검토 및 품질 보증"
                    ],
                    "competencies": [
                        "컨설팅 경험(10년 이상)",
                        "비즈니스 전략 이해",
                        "리더십",
                        "계약 관리"
                    ]
                },
                {
                    "role_id": "strategist",
                    "role_name": "AI Strategist",
                    "responsibilities": [
                        "AI 비전 및 전략 수립",
                        "비즈니스 가치(ROI) 분석",
                        "AI 활용 사례 발굴 및 우선순위 결정"
                    ],
                    "competencies": [
                        "경영학/경제학 기반",
                        "AI 기술 트렌드 이해",
                        "산업 특화 지식"
                    ]
                },
                {
                    "role_id": "ba",
                    "role_name": "Business Analyst (BA)",
                    "responsibilities": [
                        "고객사의 현행 업무 프로세스 분석",
                        "상세 요구사항 정의 및 문서화"
                    ],
                    "competencies": [
                        "프로세스 분석 능력",
                        "시스템 설계 지식",
                        "커뮤니케이션 스킬"
                    ]
                }
            ]
        },
        {
            "id": "tech_dev",
            "name": "6.3 기술 및 모델 개발",
            "name_en": "Technology & Development",
            "description": "실제 AI 모델을 개발하고, MLOps 파이프라인 및 솔루션 코드를 구현하는 역할을 담당합니다.",
            "roles": [
                {
                    "role_id": "lead_ds",
                    "role_name": "Lead Data Scientist",
                    "responsibilities": [
                        "AI 모델링 방법론 총괄",
                        "모델 아키텍처 설계",
                        "알고리즘 선택",
                        "모델 성능 최적화 및 검증"
                    ],
                    "competencies": [
                        "고급 통계학 및 ML/DL 지식",
                        "Python/R",
                        "벤치마킹 경험"
                    ]
                },
                {
                    "role_id": "mle",
                    "role_name": "ML Engineer (MLE)",
                    "responsibilities": [
                        "AI 모델의 프로덕션 환경 적용",
                        "MLOps 파이프라인 구축",
                        "서비스 API 구현 및 시스템 통합"
                    ],
                    "competencies": [
                        "소프트웨어 엔지니어링",
                        "MLOps 프레임워크",
                        "클라우드 서비스 이해"
                    ]
                },
                {
                    "role_id": "swe",
                    "role_name": "Software Engineer",
                    "responsibilities": [
                        "AI 서비스의 백엔드/프론트엔드 시스템 구축",
                        "레거시 시스템 통합 모듈 개발",
                        "API 설계"
                    ],
                    "competencies": [
                        "마이크로 서비스 아키텍처",
                        "시스템 통합(SI) 경험",
                        "DevOps"
                    ]
                }
            ]
        },
        {
            "id": "data_infra",
            "name": "6.4 데이터 및 인프라",
            "name_en": "Data & Infrastructure",
            "description": "AI 모델 개발의 기반이 되는 데이터 인프라 구축, 데이터 품질 관리 및 보안을 담당합니다.",
            "roles": [
                {
                    "role_id": "de",
                    "role_name": "Data Engineer",
                    "responsibilities": [
                        "데이터 파이프라인 설계 및 구축(ETL/ELT)",
                        "Feature Store 구축",
                        "데이터 레이크 관리"
                    ],
                    "competencies": [
                        "대규모 데이터 처리(Spark, Hadoop)",
                        "SQL/NoSQL",
                        "클라우드 데이터 서비스"
                    ]
                },
                {
                    "role_id": "infra",
                    "role_name": "Cloud/Infra Architect",
                    "responsibilities": [
                        "AI 시스템을 위한 클라우드 인프라 설계",
                        "리소스 확장성",
                        "보안 및 비용 최적화"
                    ],
                    "competencies": [
                        "AWS, Azure, GCP 인증 및 경험",
                        "Kubernetes"
                    ]
                },
                {
                    "role_id": "steward",
                    "role_name": "Data Steward/Curator",
                    "responsibilities": [
                        "데이터 거버넌스 정책 준수 확인",
                        "메타데이터 관리",
                        "데이터 적법성 및 보안 감사 지원"
                    ],
                    "competencies": [
                        "데이터 관리 지식(DAMA)",
                        "개인정보 보호법",
                        "컴플라이언스 이해"
                    ]
                }
            ]
        },
        {
            "id": "governance",
            "name": "6.5 거버넌스 및 전문성",
            "name_en": "Governance & Expertise",
            "description": "AI 시스템의 윤리적, 법적, 그리고 산업 전문성을 보장합니다.",
            "roles": [
                {
                    "role_id": "ethics",
                    "role_name": "AI Ethics Officer",
                    "responsibilities": [
                        "AI 윤리 정책 수립 및 검토",
                        "편향성/공정성 감사",
                        "규제 준수 모니터링"
                    ],
                    "competencies": [
                        "AI 윤리/법률 지식",
                        "리스크 관리",
                        "규제 분석"
                    ]
                },
                {
                    "role_id": "domain",
                    "role_name": "Domain Expert",
                    "responsibilities": [
                        "산업별 전문 지식 제공",
                        "비즈니스 요구사항 검증",
                        "AI 결과물 현업 적용성 평가"
                    ],
                    "competencies": [
                        "해당 산업 경력 (10년 이상)",
                        "현업 프로세스 이해",
                        "변화 관리 경험"
                    ]
                },
                {
                    "role_id": "qa",
                    "role_name": "QA Engineer",
                    "responsibilities": [
                        "AI 모델 및 시스템 품질 검증",
                        "테스트 자동화 구축",
                        "성능/부하 테스트"
                    ],
                    "competencies": [
                        "테스트 자동화",
                        "ML 테스트 방법론",
                        "CI/CD 통합"
                    ]
                }
            ]
        }
    ]
}


settings = Settings()
