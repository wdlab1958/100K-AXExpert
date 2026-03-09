"""
AI Consulting Platform - Query Templates
표준화된 컨설팅 질의 템플릿 시스템
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import re

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')


class TemplateCategory(str, Enum):
    """템플릿 카테고리"""
    STRATEGY = "strategy"           # 전략 수립
    ARCHITECTURE = "architecture"   # 아키텍처 설계
    TECHNOLOGY = "technology"       # 기술 선택
    ROI_ANALYSIS = "roi_analysis"   # ROI 분석
    RISK_ASSESSMENT = "risk"        # 리스크 평가
    BEST_PRACTICE = "best_practice" # Best Practice
    COMPARISON = "comparison"       # 비교 분석
    IMPLEMENTATION = "implementation" # 구현 가이드


class SecurityLevel(str, Enum):
    """템플릿 보안 레벨"""
    ONLINE_SAFE = "online_safe"     # 온라인 전송 안전
    REQUIRES_SANITIZATION = "sanitize"  # 익명화 필요
    LOCAL_ONLY = "local_only"       # 로컬 전용


@dataclass
class QueryTemplate:
    """질의 템플릿"""
    template_id: str
    name: str
    category: TemplateCategory
    security_level: SecurityLevel
    template_text: str
    description: str
    variables: List[str] = field(default_factory=list)
    example_values: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    online_providers: List[str] = field(default_factory=list)  # 추천 온라인 제공자
    created_at: datetime = field(default_factory=datetime.now)

    def render(self, values: Dict[str, Any]) -> str:
        """템플릿 렌더링"""
        result = self.template_text
        for var, value in values.items():
            placeholder = f"{{{var}}}"
            result = result.replace(placeholder, str(value))
        return result

    def get_missing_variables(self, values: Dict[str, Any]) -> List[str]:
        """누락된 변수 확인"""
        return [var for var in self.variables if var not in values]


class QueryTemplateManager:
    """질의 템플릿 관리자"""

    def __init__(self):
        self._templates: Dict[str, QueryTemplate] = {}
        self._init_default_templates()

    def _init_default_templates(self):
        """기본 템플릿 초기화"""

        # ===========================================
        # 전략 관련 템플릿
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="strategy_ai_roadmap",
            name="AI 도입 로드맵 수립",
            category=TemplateCategory.STRATEGY,
            security_level=SecurityLevel.LOCAL_ONLY,
            template_text="""
{industry} 산업의 {company_size} 기업을 위한 AI 도입 로드맵을 수립해 주세요.

현재 상황:
- AI 성숙도 레벨: {maturity_level}
- 연간 IT 예산: {it_budget}
- 주요 비즈니스 목표: {business_goals}

다음 내용을 포함해 주세요:
1. 단계별 추진 전략 (1년/3년/5년)
2. 우선순위 Use Case 도출
3. 필요 자원 및 역량 분석
4. 예상 투자 대비 효과
5. 주요 마일스톤 및 KPI
""",
            description="기업 맞춤형 AI 도입 로드맵 수립",
            variables=["industry", "company_size", "maturity_level", "it_budget", "business_goals"],
            example_values={
                "industry": "제조",
                "company_size": "중견기업",
                "maturity_level": "Level 2 (Developing)",
                "it_budget": "50억원",
                "business_goals": "생산성 향상, 품질 개선"
            },
            tags=["전략", "로드맵", "AI도입"]
        ))

        self.add_template(QueryTemplate(
            template_id="strategy_maturity_assessment",
            name="AI 성숙도 평가",
            category=TemplateCategory.STRATEGY,
            security_level=SecurityLevel.LOCAL_ONLY,
            template_text="""
{company_type} 유형의 기업 AI 성숙도를 평가해 주세요.

평가 영역:
1. 데이터 인프라: {data_infra_status}
2. 기술 역량: {tech_capability}
3. 조직 문화: {org_culture}
4. 거버넌스: {governance_status}

현재 AI 활용 현황:
{current_ai_usage}

CMMI 기반 5단계 성숙도 모델을 기준으로:
- 현재 성숙도 레벨 판정
- 영역별 강점/약점 분석
- 다음 레벨 도달을 위한 개선 과제
- 벤치마크 대비 포지션
""",
            description="CMMI 기반 AI 성숙도 평가",
            variables=["company_type", "data_infra_status", "tech_capability", "org_culture", "governance_status", "current_ai_usage"],
            example_values={
                "company_type": "금융서비스",
                "data_infra_status": "데이터 웨어하우스 구축 완료, 일부 데이터 레이크 운영",
                "tech_capability": "ML 엔지니어 3명, 데이터 사이언티스트 5명",
                "org_culture": "데이터 기반 의사결정 초기 단계",
                "governance_status": "AI 윤리 가이드라인 미수립",
                "current_ai_usage": "고객 세분화, 이탈 예측 모델 운영 중"
            },
            tags=["성숙도", "평가", "CMMI"]
        ))

        # ===========================================
        # 아키텍처 관련 템플릿
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="arch_mlops_design",
            name="MLOps 아키텍처 설계",
            category=TemplateCategory.ARCHITECTURE,
            security_level=SecurityLevel.REQUIRES_SANITIZATION,
            template_text="""
{scale_level} 규모의 MLOps 플랫폼 아키텍처를 설계해 주세요.

요구사항:
- 예상 모델 수: {model_count}
- 일일 추론 요청: {daily_inference}
- 배포 환경: {deployment_env}
- 기존 인프라: {existing_infra}

다음 컴포넌트별 설계를 포함해 주세요:
1. Feature Store 아키텍처
2. Model Registry 설계
3. 학습/추론 파이프라인
4. 모니터링 및 관측성
5. CI/CD 자동화
6. 보안 및 거버넌스
""",
            description="MLOps 플랫폼 아키텍처 설계",
            variables=["scale_level", "model_count", "daily_inference", "deployment_env", "existing_infra"],
            example_values={
                "scale_level": "중대형",
                "model_count": "50개 이상",
                "daily_inference": "1000만 건",
                "deployment_env": "하이브리드 클라우드 (AWS + On-premise)",
                "existing_infra": "Kubernetes, Spark, Airflow"
            },
            tags=["MLOps", "아키텍처", "플랫폼"],
            online_providers=["claude", "chatgpt"]
        ))

        self.add_template(QueryTemplate(
            template_id="arch_data_platform",
            name="AI 데이터 플랫폼 설계",
            category=TemplateCategory.ARCHITECTURE,
            security_level=SecurityLevel.REQUIRES_SANITIZATION,
            template_text="""
{industry} 산업용 AI 데이터 플랫폼 아키텍처를 설계해 주세요.

데이터 현황:
- 일일 데이터 생성량: {daily_data_volume}
- 주요 데이터 소스: {data_sources}
- 데이터 유형: {data_types}

요구사항:
- 실시간 처리 필요: {realtime_required}
- 데이터 보존 기간: {retention_period}
- 규제 준수: {compliance_requirements}

포함할 내용:
1. 데이터 수집 레이어
2. 저장소 아키텍처 (Data Lake/Lakehouse)
3. 데이터 처리 파이프라인
4. 데이터 품질 관리
5. 메타데이터 관리
6. 접근 제어 및 보안
""",
            description="AI용 데이터 플랫폼 아키텍처",
            variables=["industry", "daily_data_volume", "data_sources", "data_types", "realtime_required", "retention_period", "compliance_requirements"],
            example_values={
                "industry": "제조",
                "daily_data_volume": "5TB",
                "data_sources": "IoT 센서, ERP, MES, 품질검사",
                "data_types": "시계열, 이미지, 정형",
                "realtime_required": "예 (이상탐지용)",
                "retention_period": "5년",
                "compliance_requirements": "개인정보보호법, ISO 27001"
            },
            tags=["데이터플랫폼", "아키텍처", "DataLake"],
            online_providers=["claude", "chatgpt", "perplexity"]
        ))

        # ===========================================
        # 기술 선택 템플릿 (Online Safe)
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="tech_framework_comparison",
            name="AI 프레임워크 비교",
            category=TemplateCategory.COMPARISON,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{use_case} 용도로 {framework_list} 프레임워크들을 비교 분석해 주세요.

평가 기준:
- 학습 곡선 및 생태계
- 성능 및 확장성
- 프로덕션 적합성
- 커뮤니티 지원
- 라이선스 및 비용

특히 다음 관점에서 분석해 주세요:
{specific_concerns}

최신 2024-2025 트렌드를 반영한 추천도 부탁드립니다.
""",
            description="AI 프레임워크 비교 분석",
            variables=["use_case", "framework_list", "specific_concerns"],
            example_values={
                "use_case": "대규모 LLM 기반 애플리케이션 개발",
                "framework_list": "LangChain, LlamaIndex, Haystack",
                "specific_concerns": "RAG 구현 용이성, 멀티모달 지원, 에이전트 기능"
            },
            tags=["프레임워크", "비교", "기술선택"],
            online_providers=["claude", "chatgpt", "gemini", "perplexity"]
        ))

        self.add_template(QueryTemplate(
            template_id="tech_cloud_comparison",
            name="클라우드 AI 서비스 비교",
            category=TemplateCategory.COMPARISON,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{ai_service_type} 서비스에 대해 주요 클라우드 제공업체({cloud_providers})를 비교해 주세요.

비교 항목:
1. 기능 및 성능
2. 가격 정책 (최신 정보 기준)
3. SLA 및 가용성
4. 보안 인증
5. 리전 가용성 (특히 한국)
6. 기존 인프라 연동성

사용 시나리오: {usage_scenario}
월간 예상 사용량: {monthly_usage}
""",
            description="클라우드 AI 서비스 비교",
            variables=["ai_service_type", "cloud_providers", "usage_scenario", "monthly_usage"],
            example_values={
                "ai_service_type": "관리형 ML 플랫폼",
                "cloud_providers": "AWS SageMaker, GCP Vertex AI, Azure ML",
                "usage_scenario": "MLOps 파이프라인 구축 및 모델 서빙",
                "monthly_usage": "학습 1000 GPU시간, 추론 500만 건"
            },
            tags=["클라우드", "비교", "AI서비스"],
            online_providers=["claude", "chatgpt", "gemini", "perplexity"]
        ))

        self.add_template(QueryTemplate(
            template_id="tech_llm_selection",
            name="LLM 모델 선택 가이드",
            category=TemplateCategory.TECHNOLOGY,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{application_type} 애플리케이션을 위한 최적의 LLM 모델을 추천해 주세요.

요구사항:
- 주요 태스크: {main_tasks}
- 응답 속도 요구: {latency_requirement}
- 비용 제약: {cost_constraint}
- 배포 방식: {deployment_type}
- 보안 요구: {security_requirement}

고려할 모델:
- 상용 API: GPT-4, Claude, Gemini
- 오픈소스: Llama 3, Mistral, Qwen
- 한국어 특화: 필요시

각 옵션의 장단점과 최종 추천을 부탁드립니다.
""",
            description="용도별 LLM 모델 선택 가이드",
            variables=["application_type", "main_tasks", "latency_requirement", "cost_constraint", "deployment_type", "security_requirement"],
            example_values={
                "application_type": "기업용 챗봇",
                "main_tasks": "문서 QA, 요약, 번역",
                "latency_requirement": "3초 이내",
                "cost_constraint": "월 500만원 이하",
                "deployment_type": "API 또는 Self-hosted",
                "security_requirement": "고객 데이터 외부 전송 불가"
            },
            tags=["LLM", "모델선택", "기술선택"],
            online_providers=["claude", "chatgpt", "perplexity"]
        ))

        # ===========================================
        # ROI 분석 템플릿
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="roi_ai_investment",
            name="AI 투자 ROI 분석",
            category=TemplateCategory.ROI_ANALYSIS,
            security_level=SecurityLevel.REQUIRES_SANITIZATION,
            template_text="""
{use_case_name} AI 프로젝트의 투자 대비 효과를 분석해 주세요.

투자 계획:
- 초기 투자: {initial_investment}
- 연간 운영비: {annual_opex}
- 구축 기간: {implementation_period}

기대 효과:
- 예상 비용 절감: {cost_savings}
- 예상 매출 증대: {revenue_increase}
- 생산성 향상: {productivity_gain}

분석 요청:
1. 3년/5년 NPV 계산
2. 투자회수기간(Payback Period)
3. IRR 추정
4. 민감도 분석 (변수별 영향)
5. 리스크 조정 ROI
6. 유사 사례 벤치마크
""",
            description="AI 프로젝트 ROI 분석",
            variables=["use_case_name", "initial_investment", "annual_opex", "implementation_period", "cost_savings", "revenue_increase", "productivity_gain"],
            example_values={
                "use_case_name": "지능형 품질검사 시스템",
                "initial_investment": "15억원",
                "annual_opex": "3억원",
                "implementation_period": "12개월",
                "cost_savings": "연 8억원 (불량률 감소)",
                "revenue_increase": "연 5억원 (납기 개선)",
                "productivity_gain": "검사 인력 50% 효율화"
            },
            tags=["ROI", "투자분석", "비용효과"],
            online_providers=["claude", "chatgpt"]
        ))

        # ===========================================
        # 리스크 평가 템플릿
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="risk_ai_project",
            name="AI 프로젝트 리스크 평가",
            category=TemplateCategory.RISK_ASSESSMENT,
            security_level=SecurityLevel.REQUIRES_SANITIZATION,
            template_text="""
{project_type} AI 프로젝트의 리스크를 종합 평가해 주세요.

프로젝트 개요:
- 규모: {project_scale}
- 기간: {project_duration}
- 팀 구성: {team_composition}
- 기술 스택: {tech_stack}

평가 영역:
1. 기술 리스크 (데이터 품질, 모델 성능, 확장성)
2. 운영 리스크 (인력, 프로세스, 변화관리)
3. 비즈니스 리스크 (ROI 미달, 일정 지연, 범위 변경)
4. 규제/컴플라이언스 리스크
5. 보안 리스크
6. 벤더/파트너 리스크

각 리스크에 대해 발생 확률, 영향도, 대응 전략을 제시해 주세요.
""",
            description="AI 프로젝트 종합 리스크 평가",
            variables=["project_type", "project_scale", "project_duration", "team_composition", "tech_stack"],
            example_values={
                "project_type": "예측 유지보수 시스템",
                "project_scale": "대형 (투자 20억원 이상)",
                "project_duration": "18개월",
                "team_composition": "내부 5명 + 외부 컨설턴트",
                "tech_stack": "Python, TensorFlow, Kubernetes, AWS"
            },
            tags=["리스크", "평가", "프로젝트관리"]
        ))

        # ===========================================
        # Best Practice 템플릿 (Online Safe)
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="bp_mlops",
            name="MLOps Best Practice",
            category=TemplateCategory.BEST_PRACTICE,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{maturity_level} 성숙도 조직을 위한 MLOps Best Practice를 제시해 주세요.

현재 상황:
- ML 모델 수: {model_count}
- 배포 빈도: {deployment_frequency}
- 현재 도구: {current_tools}

다음 영역별 Best Practice를 포함해 주세요:
1. 버전 관리 (코드, 데이터, 모델)
2. 자동화된 파이프라인
3. 실험 추적 및 재현성
4. 모델 모니터링 (드리프트 감지)
5. A/B 테스트 및 점진적 배포
6. 문서화 및 거버넌스

2024-2025 최신 트렌드와 사례도 포함해 주세요.
""",
            description="MLOps 도입 Best Practice",
            variables=["maturity_level", "model_count", "deployment_frequency", "current_tools"],
            example_values={
                "maturity_level": "Level 2 (수동 ML 파이프라인)",
                "model_count": "10-20개",
                "deployment_frequency": "월 1-2회",
                "current_tools": "Jupyter, Git, 수동 배포"
            },
            tags=["MLOps", "BestPractice", "자동화"],
            online_providers=["claude", "chatgpt", "gemini", "perplexity"]
        ))

        self.add_template(QueryTemplate(
            template_id="bp_responsible_ai",
            name="책임감 있는 AI 가이드",
            category=TemplateCategory.BEST_PRACTICE,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{industry} 산업에서 책임감 있는 AI(Responsible AI) 도입 가이드를 제시해 주세요.

고려 사항:
- AI 적용 영역: {ai_applications}
- 규제 환경: {regulatory_context}
- 이해관계자: {stakeholders}

다음 주제를 포함해 주세요:
1. AI 윤리 원칙 및 프레임워크
2. 편향 탐지 및 공정성 확보
3. 설명가능한 AI(XAI) 적용
4. 개인정보보호 및 데이터 거버넌스
5. AI 위험 평가 프로세스
6. EU AI Act 등 주요 규제 대응
7. 모니터링 및 감사 체계

실무 적용 가능한 체크리스트도 포함해 주세요.
""",
            description="Responsible AI 도입 가이드",
            variables=["industry", "ai_applications", "regulatory_context", "stakeholders"],
            example_values={
                "industry": "금융",
                "ai_applications": "신용평가, 부정거래 탐지, 고객 서비스",
                "regulatory_context": "금융위원회 AI 가이드라인, 개인정보보호법",
                "stakeholders": "고객, 규제기관, 임직원"
            },
            tags=["ResponsibleAI", "윤리", "거버넌스"],
            online_providers=["claude", "chatgpt", "gemini", "perplexity"]
        ))

        # ===========================================
        # 구현 가이드 템플릿
        # ===========================================
        self.add_template(QueryTemplate(
            template_id="impl_rag_system",
            name="RAG 시스템 구현 가이드",
            category=TemplateCategory.IMPLEMENTATION,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{document_type} 문서 기반 RAG(Retrieval-Augmented Generation) 시스템 구현 가이드를 제시해 주세요.

요구사항:
- 문서 규모: {document_volume}
- 질의 유형: {query_types}
- 응답 품질 요구: {quality_requirement}
- 응답 시간 목표: {latency_target}

구현 가이드:
1. 문서 전처리 및 청킹 전략
2. 임베딩 모델 선택 (한국어 지원)
3. 벡터 DB 선택 및 인덱싱
4. 검색 전략 (Hybrid Search, Re-ranking)
5. 프롬프트 엔지니어링
6. 평가 메트릭 및 품질 개선
7. 프로덕션 배포 고려사항

최신 기법 (예: HyDE, RAPTOR) 적용 여부도 검토해 주세요.
""",
            description="RAG 시스템 구현 가이드",
            variables=["document_type", "document_volume", "query_types", "quality_requirement", "latency_target"],
            example_values={
                "document_type": "기술 매뉴얼, 계약서, 정책문서",
                "document_volume": "10만 페이지",
                "query_types": "사실 확인, 요약, 비교 분석",
                "quality_requirement": "정확도 95% 이상",
                "latency_target": "3초 이내"
            },
            tags=["RAG", "구현", "LLM"],
            online_providers=["claude", "chatgpt", "perplexity"]
        ))

        self.add_template(QueryTemplate(
            template_id="impl_ai_agent",
            name="AI Agent 구현 가이드",
            category=TemplateCategory.IMPLEMENTATION,
            security_level=SecurityLevel.ONLINE_SAFE,
            template_text="""
{agent_purpose} 목적의 AI Agent 시스템 구현 가이드를 제시해 주세요.

Agent 요구사항:
- 수행 태스크: {tasks}
- 사용 도구: {available_tools}
- 자율성 수준: {autonomy_level}
- 안전성 요구: {safety_requirements}

구현 가이드:
1. Agent 아키텍처 설계 (Single/Multi-Agent)
2. 프레임워크 선택 (LangGraph, CrewAI, AutoGen 등)
3. 도구 통합 및 API 설계
4. 메모리 및 상태 관리
5. 계획(Planning) 및 추론 전략
6. 오류 처리 및 폴백
7. Human-in-the-Loop 설계
8. 평가 및 디버깅

최신 2024-2025 Agent 연구 동향도 반영해 주세요.
""",
            description="AI Agent 시스템 구현 가이드",
            variables=["agent_purpose", "tasks", "available_tools", "autonomy_level", "safety_requirements"],
            example_values={
                "agent_purpose": "고객 서비스 자동화",
                "tasks": "문의 분류, 답변 생성, 티켓 생성, 에스컬레이션",
                "available_tools": "CRM API, 지식베이스, 이메일 시스템",
                "autonomy_level": "반자율 (중요 결정은 사람 승인)",
                "safety_requirements": "민감 정보 노출 방지, 오답 최소화"
            },
            tags=["Agent", "구현", "자동화"],
            online_providers=["claude", "chatgpt", "gemini"]
        ))

    def add_template(self, template: QueryTemplate):
        """템플릿 추가"""
        self._templates[template.template_id] = template

    def get_template(self, template_id: str) -> Optional[QueryTemplate]:
        """템플릿 조회"""
        return self._templates.get(template_id)

    def list_templates(
        self,
        category: TemplateCategory = None,
        security_level: SecurityLevel = None,
        tags: List[str] = None
    ) -> List[QueryTemplate]:
        """템플릿 목록 조회"""
        templates = list(self._templates.values())

        if category:
            templates = [t for t in templates if t.category == category]

        if security_level:
            templates = [t for t in templates if t.security_level == security_level]

        if tags:
            templates = [
                t for t in templates
                if any(tag in t.tags for tag in tags)
            ]

        return templates

    def search_templates(self, keyword: str) -> List[QueryTemplate]:
        """템플릿 검색"""
        keyword_lower = keyword.lower()
        return [
            t for t in self._templates.values()
            if keyword_lower in t.name.lower()
            or keyword_lower in t.description.lower()
            or any(keyword_lower in tag.lower() for tag in t.tags)
        ]

    def render_template(
        self,
        template_id: str,
        values: Dict[str, Any]
    ) -> Optional[str]:
        """템플릿 렌더링"""
        template = self.get_template(template_id)
        if not template:
            return None

        missing = template.get_missing_variables(values)
        if missing:
            raise ValueError(f"Missing variables: {missing}")

        return template.render(values)

    def get_online_safe_templates(self) -> List[QueryTemplate]:
        """온라인 전송 안전 템플릿 조회"""
        return self.list_templates(security_level=SecurityLevel.ONLINE_SAFE)

    def get_template_summary(self) -> Dict[str, Any]:
        """템플릿 현황 요약"""
        templates = list(self._templates.values())

        by_category = {}
        by_security = {}

        for t in templates:
            by_category[t.category.value] = by_category.get(t.category.value, 0) + 1
            by_security[t.security_level.value] = by_security.get(t.security_level.value, 0) + 1

        return {
            "total_templates": len(templates),
            "by_category": by_category,
            "by_security_level": by_security,
            "online_safe_count": len(self.get_online_safe_templates())
        }


# 싱글톤 인스턴스
_template_manager: Optional[QueryTemplateManager] = None


def get_template_manager() -> QueryTemplateManager:
    """QueryTemplateManager 싱글톤 인스턴스"""
    global _template_manager
    if _template_manager is None:
        _template_manager = QueryTemplateManager()
    return _template_manager
