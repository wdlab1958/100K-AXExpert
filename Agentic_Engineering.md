# 100K-AX Expert Platform - Agentic Engineering 개발 방법론
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

> AI/AX 10만 전문인력 양성 플랫폼의 Phase 기반 에이전틱 엔지니어링 개발 방법론

---

## 목차

1. [개발 방법론 개요](#1-개발-방법론-개요)
2. [Phase 0: 기반 구축 (Foundation)](#2-phase-0-기반-구축)
3. [Phase 1: 코어 엔진 개발 (Core Engine)](#3-phase-1-코어-엔진-개발)
4. [Phase 2: AX 전문가 양성 모듈 (Training Module)](#4-phase-2-ax-전문가-양성-모듈)
5. [Phase 3: 도메인 확장 (Domain Expansion)](#5-phase-3-도메인-확장)
6. [Phase 4: 파일럿 & 대규모 배포 (Pilot & Scale)](#6-phase-4-파일럿--대규모-배포)
7. [Phase 5: 생태계 확장 (Ecosystem)](#7-phase-5-생태계-확장)
8. [에이전틱 아키텍처 설계 원칙](#8-에이전틱-아키텍처-설계-원칙)
9. [멀티 에이전트 오케스트레이션 상세](#9-멀티-에이전트-오케스트레이션-상세)
10. [품질 보증 & 테스트 전략](#10-품질-보증--테스트-전략)
11. [배포 & 운영 전략](#11-배포--운영-전략)

---

## 1. 개발 방법론 개요

### 1.1 에이전틱 엔지니어링이란?

에이전틱 엔지니어링(Agentic Engineering)은 AI 에이전트를 중심으로 소프트웨어 시스템을 설계·구현·운영하는 공학 방법론이다. 기존 소프트웨어 엔지니어링과 다른 점은 다음과 같다:

| 구분 | 전통 소프트웨어 | 에이전틱 엔지니어링 |
|------|----------------|---------------------|
| 실행 주체 | 정적 코드 | 자율 AI 에이전트 |
| 의사결정 | 규칙 기반 (if-else) | LLM 기반 추론 |
| 흐름 제어 | 하드코딩된 워크플로우 | 동적 오케스트레이션 |
| 학습 | 별도 ML 파이프라인 | 실시간 컨텍스트 학습 |
| 협업 | API 호출 | 에이전트 간 대화/위임 |
| 품질 관리 | 유닛 테스트 | 프롬프트 검증 + 출력 평가 |

### 1.2 100K-AX Expert 개발 철학

```
┌─────────────────────────────────────────────────────────┐
│  "AI/AX 전문가는 교실이 아닌 현업의 실무에서 만들어진다"  │
│                                                         │
│  현업 실무자 + 100K-AX Expert Platform                   │
│  → 업무 중 AX 기회 발굴                                  │
│  → 멀티 에이전트 AI 컨설팅                                │
│  → 구현 & 반복 학습                                       │
│  → AI/AX 전문가 (6~12개월)                               │
└─────────────────────────────────────────────────────────┘
```

### 1.3 Phase 전체 로드맵

```
Phase 0        Phase 1        Phase 2        Phase 3        Phase 4        Phase 5
기반 구축       코어 엔진       양성 모듈       도메인 확장     파일럿/배포     생태계
(Month 1)      (Month 2)      (Month 3)      (Month 4~5)    (Month 6~8)    (Month 9~24)
   │              │              │              │              │              │
   ▼              ▼              ▼              ▼              ▼              ▼
 인프라          AX 엔진        Training       금융/공공/      1,000기업      10,000기업
 아키텍처        컨설팅 엔진     Progress       유통/의료       배포           100,000명
 프로토타입      보고서 엔진     인증 체계      LoRA 학습       정부사업연계    해외진출
```

---

## 2. Phase 0: 기반 구축

### 2.1 목표
핵심 인프라 및 기본 에이전트 프레임워크 구축

### 2.2 작업 항목

| # | 작업 | 세부 내용 | 산출물 | 상태 |
|---|------|----------|--------|------|
| 0-1 | 아키텍처 설계 확정 | 시스템 전체 설계, API 규격, DB 스키마 | Architecture Design Doc | ✅ 완료 |
| 0-2 | FastAPI 기반 서버 구축 | RESTful API, CORS, 미들웨어 설정 | main.py + routes | ✅ 완료 |
| 0-3 | 프론트엔드 SPA 구축 | Jinja2 + Bootstrap 5 Dark Theme | templates/ + static/ | ✅ 완료 |
| 0-4 | Ollama LLM 연동 | 로컬 LLM 서빙 인프라 | llm_provider.py | ✅ 완료 |
| 0-5 | 5단계 컨설팅 프레임워크 | 전략→설계→구축→파일럿→운영 | config/settings.py | ✅ 완료 |
| 0-6 | 보안 모듈 구축 | 감사 로깅, 데이터 분류/비식별화 | security/ 모듈 | ✅ 완료 |
| 0-7 | 7개 AI 프레임워크 통합 | LangGraph, CrewAI, AutoGen, DSPy, LangChain, LlamaIndex, Native | agents/ + core/ | ✅ 완료 |
| 0-8 | ISO 표준 통합 | 42001, 23053, 24030, 38500 | data/standards/ | ✅ 완료 |
| 0-9 | 브랜드 전환 | 100K-AX Expert → 100K-AX Expert | 전체 파일 | ✅ 완료 |

### 2.3 아키텍처 다이어그램

```
┌──────────────────────────────────────────────────────────┐
│                    100K-AX Expert Platform                │
├──────────────────────────────────────────────────────────┤
│  Frontend Layer                                          │
│  ┌─────────────┐ ┌──────────┐ ┌────────────────────┐    │
│  │ Dashboard    │ │ Stage1~5 │ │ ISO 24030/38500    │    │
│  │ (index.html) │ │ 워크스페이스│ │ Assessment       │    │
│  └──────┬──────┘ └─────┬────┘ └────────┬───────────┘    │
│         └──────────────┼───────────────┘                 │
│                        ▼                                 │
│  API Gateway (FastAPI)                                   │
│  ┌──────────┐ ┌────────────┐ ┌──────────┐ ┌──────────┐  │
│  │ routes   │ │ framework  │ │ multi-   │ │ security │  │
│  │ .py      │ │ _routes.py │ │ agent    │ │ _routes  │  │
│  └────┬─────┘ └─────┬──────┘ └────┬─────┘ └────┬─────┘  │
│       └──────────────┼─────────────┼────────────┘        │
│                      ▼                                   │
│  Agent Orchestration Layer                               │
│  ┌─────────────────────────────────────────────────┐     │
│  │ 100K-AX Expert Orchestrator                      │     │
│  │ ┌─────────┐ ┌────────┐ ┌────────┐ ┌──────────┐ │     │
│  │ │LangGraph│ │ CrewAI │ │AutoGen │ │ Native   │ │     │
│  │ │StateGraph│ │ Roles  │ │GroupChat│ │Sequential│ │     │
│  │ └────┬────┘ └───┬────┘ └───┬────┘ └────┬─────┘ │     │
│  │      └──────────┼──────────┼────────────┘       │     │
│  │ ┌─────────┐ ┌────────┐ ┌──────────┐            │     │
│  │ │  DSPy   │ │LangChain│ │LlamaIndex│            │     │
│  │ │  CoT    │ │  LCEL  │ │   RAG    │            │     │
│  │ └─────────┘ └────────┘ └──────────┘            │     │
│  └──────────────────────┬──────────────────────────┘     │
│                         ▼                                │
│  LLM Engine                                              │
│  ┌──────────────────────────────────────────────┐        │
│  │ Ollama (Local)      │ Online LLM (Optional)  │        │
│  │ llama3.2 / Qwen 72B │ Claude / GPT-4         │        │
│  │ DeepSeek-R1 70B     │ (보안 라우팅 적용)      │        │
│  └──────────────────────────────────────────────┘        │
│                                                          │
│  Data Layer                                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐    │
│  │ SQLite   │ │ ChromaDB │ │ Redis    │ │ Qdrant   │    │
│  │ (관계형) │ │ (벡터)   │ │ (캐시)   │ │ (임베딩) │    │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘    │
└──────────────────────────────────────────────────────────┘
```

### 2.4 핵심 설계 결정

| 결정 사항 | 선택 | 근거 |
|----------|------|------|
| 프론트엔드 | Jinja2 SPA (Not React/Vue) | 서버사이드 렌더링으로 배포 단순화, AI Appliance 환경 최적 |
| LLM | Ollama 로컬 우선 | Air-gapped 보안, 기업 데이터 유출 방지 |
| DB | SQLite | AI Appliance 단일 서버 환경, 설치 무의존성 |
| 에이전트 | 7개 프레임워크 병렬 지원 | 각 프레임워크의 강점을 과제별로 활용 |
| 보안 | 3중 보호 | 데이터 분류 → 비식별화 → 감사 로깅 |

---

## 3. Phase 1: 코어 엔진 개발

### 3.1 목표
100K-AX Expert 핵심 AX 컨설팅 엔진 구현

### 3.2 작업 항목

| # | 작업 | 세부 내용 | 산출물 |
|---|------|----------|--------|
| 1-1 | AX Discovery Module | 업무 프로세스 분석 → AX 기회 자동 식별 | Discovery Engine v1.0 |
| 1-2 | Multi-Agent Consulting | 6개 에이전트 협업 워크플로우 구현 | Consulting Engine v1.0 |
| 1-3 | ROI/Risk 분석 엔진 | NPV, IRR, FMEA 분석 자동화 | Analytics Engine v1.0 |
| 1-4 | Report Generation | DOCX/PDF/PPTX 보고서 자동 생성 | Report Engine v1.0 |
| 1-5 | 3-Tier Memory 구현 | Redis(단기) + PostgreSQL(중기) + Qdrant(장기) | Memory System v1.0 |
| 1-6 | 제조 도메인 KB 구축 | 제조업 AX 사례, 규제, 표준 데이터 수집 | Manufacturing KB v1.0 |

### 3.3 AX Discovery Module 상세

```python
# AX Discovery 워크플로우
class AXDiscoveryWorkflow:
    """업무 프로세스를 분석하여 AX 기회를 자동 식별"""

    async def analyze_process(self, business_process: BusinessProcess) -> list[AXOpportunity]:
        """
        1. 현재 업무 프로세스의 As-Is 분석
        2. 각 단계별 AX 적합도 점수 산출
           - ROI 잠재력 (가중치 30%)
           - 구현 난이도 (가중치 25%)
           - 데이터 가용성 (가중치 25%)
           - 조직 준비도 (가중치 20%)
        3. AX 기회 우선순위 정렬
        4. Top-N 기회에 대한 상세 분석
        """
```

### 3.4 멀티에이전트 컨설팅 워크플로우 (LangGraph StateGraph)

```python
# AXConsultingState 정의
class AXConsultingState(TypedDict):
    company_profile: dict          # 기업 프로필
    department: str                # 대상 부서
    business_process: dict         # 업무 프로세스
    ax_opportunities: list         # 발굴된 AX 기회
    selected_opportunity: dict     # 선택된 AX 기회
    domain_analysis: dict          # 도메인 분석 결과
    roi_analysis: dict             # ROI 분석 결과
    risk_assessment: dict          # 리스크 평가 결과
    implementation_plan: dict      # 구현 계획
    change_management: dict        # 변화 관리 전략
    final_report: dict             # 최종 보고서
    training_progress: dict        # 학습 진도
    iteration_count: int           # 반복 횟수

# StateGraph 워크플로우
workflow = StateGraph(AXConsultingState)
workflow.add_node("intake", intake_node)
workflow.add_node("discovery", discovery_node)
workflow.add_node("prioritize", prioritize_node)
workflow.add_node("domain_analyze", domain_node)
workflow.add_node("roi_analyze", roi_node)
workflow.add_node("risk_assess", risk_node)
workflow.add_node("design_impl", implementation_node)
workflow.add_node("change_mgmt", change_node)
workflow.add_node("generate_report", report_node)
workflow.add_node("track_progress", training_node)

# 조건부 분기: ROI 미달 시 다음 기회로
workflow.add_conditional_edges(
    "roi_analyze",
    lambda state: "risk_assess" if state["roi_analysis"]["approved"] else "prioritize"
)
```

---

## 4. Phase 2: AX 전문가 양성 모듈

### 4.1 목표
실무자별 AX 역량 성장 추적 및 전문가 인증 체계 구현

### 4.2 작업 항목

| # | 작업 | 세부 내용 | 산출물 |
|---|------|----------|--------|
| 2-1 | Training Progress Tracker | 실무자별 AX 과제 수행 이력 관리 | Tracker Module |
| 2-2 | 역량 성장 시각화 | 레이더 차트, 성장 곡선, 비교 분석 | Dashboard Component |
| 2-3 | 전문가 인증 시스템 | 5등급 자동 산정 (Beginner→Master) | Certification Engine |
| 2-4 | 학습 콘텐츠 관리 | AX 과제별 학습 가이드, 베스트 프랙티스 | Content CMS |
| 2-5 | 부서별 AX 현황판 | 부서 전체 AX 전환율, 과제 현황 | Dept Dashboard |
| 2-6 | 기업 AX 성과 대시보드 | Before/After KPI, ROI 달성 추적 | Enterprise Dashboard |

### 4.3 전문가 인증 알고리즘

```python
class CertificationEngine:
    """AX 전문가 등급 자동 산정"""

    LEVELS = {
        "AX Beginner":      {"min_tasks": 5,   "min_roi_tasks": 0,  "min_conversion": 0},
        "AX Practitioner":  {"min_tasks": 20,  "min_roi_tasks": 10, "min_conversion": 0},
        "AX Specialist":    {"min_tasks": 50,  "min_roi_tasks": 25, "min_conversion": 0.3},
        "AX Expert":        {"min_tasks": 100, "min_roi_tasks": 50, "min_conversion": 0.5},
        "AX Master":        {"min_tasks": 100, "min_roi_tasks": 50, "min_conversion": 0.5,
                            "external_consulting": True},
    }

    def evaluate(self, user: UserProfile) -> CertificationLevel:
        """
        평가 기준:
        1. 완료된 AX 과제 수
        2. ROI 달성 과제 수
        3. 부서 AX 전환율
        4. 외부 컨설팅 경험 (Master 등급)
        5. 동료 평가 점수 (가산점)
        """
```

### 4.4 학습 진도 데이터 모델

```python
class TrainingProgress(BaseModel):
    user_id: str
    company_id: str
    department: str
    current_level: str                    # AX Beginner ~ AX Master
    total_tasks_completed: int            # 총 완료 AX 과제 수
    roi_achieved_tasks: int               # ROI 달성 과제 수
    dept_conversion_rate: float           # 부서 AX 전환율
    skill_radar: dict[str, float]         # 역량별 점수 (0~100)
    growth_history: list[GrowthPoint]     # 성장 이력
    badges: list[str]                     # 획득 배지
    next_level_requirements: dict         # 다음 등급 요건
```

---

## 5. Phase 3: 도메인 확장

### 5.1 목표
제조 외 금융, 공공, 유통, 물류, 의료 도메인 확장

### 5.2 도메인별 Knowledge Base 구축

| 도메인 | KB 내용 | 규제/표준 | LoRA 학습 데이터 |
|--------|---------|----------|-----------------|
| **제조** | HACCP, 품질관리, 공정최적화, SCM | ISO 9001, IATF 16949 | 제조 AX 사례 5,000건 |
| **금융** | Basel III, 여신/수신, 보험, 자산운용 | 금융위원회 규제 | 금융 AX 사례 3,000건 |
| **공공** | 행정절차, 민원, 조달, 복지 | 행정절차법, 전자정부법 | 공공 AX 사례 2,000건 |
| **유통/물류** | SCM, WMS, 배송 최적화 | 물류정책 | 유통 AX 사례 3,000건 |
| **의료** | EMR, 진단보조, 신약개발 | 의료법, 개인정보보호법 | 의료 AX 사례 2,000건 |
| **교육** | LMS, 교육과정, 평가 | 교육기본법 | 교육 AX 사례 1,000건 |
| **국방/방산** | 방위사업, 군수체계 | 방위사업법, 보안규정 | (보안 등급 별도) |

### 5.3 Domain Fine-tuned LoRA 어댑터

```python
# 산업별 LoRA 어댑터 동적 로딩
class DomainLoRAManager:
    """
    산업별 특화 LoRA 어댑터를 동적으로 로딩하여
    범용 LLM 위에 도메인 전문성을 추가
    """
    ADAPTERS = {
        "manufacturing": "lora-manufacturing-v1.0",
        "finance": "lora-finance-v1.0",
        "public": "lora-public-v1.0",
        "logistics": "lora-logistics-v1.0",
        "healthcare": "lora-healthcare-v1.0",
        "education": "lora-education-v1.0",
    }

    async def load_adapter(self, domain: str) -> None:
        """기업의 산업 도메인에 맞는 LoRA 어댑터 동적 로딩"""
```

### 5.4 부서별 세분화 AX 과제 템플릿

| 부서 | AX 과제 예시 | 예상 과제 수 |
|------|-------------|-------------|
| 제품/기술 개발 연구소 | 설계 자동화, 시뮬레이션 최적화, 특허 분석 | 20~40건 |
| 생산기술연구소 | 공정 파라미터 최적화, 설비 예지보전 | 15~30건 |
| 생산부 | 생산 스케줄링, 불량 예측, 작업지시 자동화 | 20~50건 |
| 품질관리부 | AI 검사, SPC 고도화, 불량 원인 분석 | 15~30건 |
| 자재부 | 수요 예측, 재고 최적화, 발주 자동화 | 10~20건 |
| 경영부 | 경영분석 자동화, 의사결정 지원 | 10~15건 |
| 재무/인사관리부 | 재무 예측, 채용 분석, 급여 최적화 | 10~20건 |
| 영업/마케팅 | 고객 세분화, 매출 예측, 캠페인 최적화 | 15~30건 |
| 수출부 | 환율 예측, 물류 최적화, 통관 자동화 | 10~20건 |
| 고객지원부 | AI 챗봇, VOC 분석, 이슈 예측 | 10~20건 |
| **합계** | | **135~275건** |

---

## 6. Phase 4: 파일럿 & 대규모 배포

### 6.1 목표
파일럿 5개 기업 운영 → 1,000개 기업 본격 배포

### 6.2 파일럿 운영 계획

| 단계 | 내용 | 기간 |
|------|------|------|
| 기업 선정 | 제조(2), 금융(1), 공공(1), 유통(1) | 2주 |
| AI Appliance 설치 | 온사이트 하드웨어 설치 및 환경 구성 | 1주/기업 |
| 파일럿 운영 | 기업별 3개 부서, 부서별 10건 AX 과제 | 8주 |
| 피드백 수집/반영 | 사용성, 정확도, 유용성 평가 | 2주 |
| 모델 튜닝 | 파일럿 데이터 기반 LoRA 파인튜닝 | 2주 |

### 6.3 AI Appliance 하드웨어 제품 등급

| 등급 | 대상 | GPU | 동시 사용자 | 가격대 |
|------|------|-----|-----------|--------|
| 100K-AX-S | 소기업 (50명 이하) | RTX 5090 x 1 | ~10명 | 15~20M KRW |
| 100K-AX-M | 중기업 (50~200명) | RTX 5090 x 2 | ~30명 | 30~40M KRW |
| 100K-AX-L | 중견기업 (200명+) | RTX 5090 x 4 | ~100명 | 60~80M KRW |
| 100K-AX-E | 대기업/기관 | H100 x 2+ | 커스텀 | 별도 견적 |

### 6.4 정부 지원사업 연계

| 부처 | 사업명 | 지원 규모 |
|------|--------|----------|
| 중소벤처기업부 | 스마트공장 고도화 | 기업당 최대 1.5억 |
| 과학기술정보통신부 | AI 바우처 | 기업당 최대 3억 |
| 고용노동부 | 직업훈련 혁신 | 교육비 지원 |
| 산업통상자원부 | 산업디지털전환 | 기업당 최대 5억 |
| 지자체 | 지역 스마트 제조 혁신 | 지역별 상이 |

---

## 7. Phase 5: 생태계 확장

### 7.1 목표
10,000개 기업, 100,000명 전문가 양성 달성

### 7.2 확장 계획

| 영역 | 내용 | 목표 시점 |
|------|------|----------|
| 산업별 AX 허브 | 제조AX허브, 금융AX허브 등 운영 | Year 2 |
| AX 전문가 커뮤니티 | 전문가 네트워크, 사례 공유 | Year 2 |
| AX 마켓플레이스 | 성공 사례 템플릿, KB 거래 | Year 3 |
| 지역 AX 센터 | 광역시별 체험/교육 센터 | Year 3 |
| 해외 시장 진출 | ASEAN, 중동 시장 | Year 4 |
| 국가공인 인증 연계 | AI/AX 전문가 국가자격 | Year 5 |

### 7.3 기대 성과

| 지표 | 5년 목표 |
|------|---------|
| AI/AX 전문가 양성 | 100,000명 |
| 참여 기업 수 | 10,000+ |
| 기업당 AX 과제 수행 | 150건 (평균) |
| AX 구현 생산성 향상 | 15~30% |
| 기업당 연간 비용 절감 | 2~5억원 |
| 전체 경제적 효과 | 2~5조원/년 |

---

## 8. 에이전틱 아키텍처 설계 원칙

### 8.1 에이전트 설계 5원칙

#### 원칙 1: 단일 책임 (Single Responsibility)
각 에이전트는 하나의 명확한 역할만 수행한다.
```
✅ ROI Analyst Agent → ROI 분석만 수행
✅ Risk Assessment Agent → 리스크 평가만 수행
❌ General Agent → ROI + Risk + Report 모두 수행
```

#### 원칙 2: 오케스트레이터 중심 (Orchestrator-Centric)
에이전트 간 직접 통신하지 않고, 오케스트레이터를 통해 협업한다.
```
Agent A ──→ Orchestrator ──→ Agent B
           (상태 관리)
           (흐름 제어)
           (결과 통합)
```

#### 원칙 3: 상태 기반 흐름 (State-Driven Flow)
LangGraph StateGraph로 워크플로우 상태를 명시적으로 관리한다.
```
intake → discovery → prioritize → domain_analyze → roi_analyze
                                                       │
                                              ┌────────┴────────┐
                                              │ ROI 승인?        │
                                              ├─── Yes → risk_assess → design_impl → report
                                              └─── No  → prioritize (다음 기회)
```

#### 원칙 4: 프롬프트 모듈화 (Modular Prompts)
에이전트의 시스템 프롬프트는 외부 파일로 관리하여 코드 변경 없이 최적화한다.
```
prompts/
├── strategy_analyst.yaml
├── roi_analyst.yaml
├── risk_assessor.yaml
├── domain_expert.yaml
├── implementation_architect.yaml
├── change_management.yaml
└── report_generator.yaml
```

#### 원칙 5: Human-in-the-Loop (HITL)
핵심 의사결정 지점에서 인간 검증을 필수화한다.
```
자동 처리: AX 기회 발굴, 초기 ROI 추정
인간 확인: 최종 ROI 승인, 구현 방법론 선택, 보고서 최종 검토
인간 주도: 예산 승인, 조직 변화 결정, 전략 방향 확정
```

### 8.2 3-Tier Memory 시스템

| 계층 | 기술 | 저장 내용 | TTL |
|------|------|----------|-----|
| Short-Term | Redis | 현재 세션 컨텍스트, 진행 중 분석 | 세션 종료 시 |
| Medium-Term | PostgreSQL | AX 과제 이력, 부서/기업별 프로파일 | 영구 |
| Long-Term | Qdrant Vector DB | AX 베스트 프랙티스, 성공 패턴 임베딩 | 영구 |

### 8.3 Hybrid LLM 라우팅

```python
class QueryRouter:
    """데이터 민감도에 따른 LLM 라우팅"""

    ROUTING_RULES = {
        "CRITICAL":     "local_only",    # 기업 기밀 → Ollama 로컬
        "HIGH":         "local_only",    # 개인정보 → Ollama 로컬
        "MEDIUM":       "local_prefer",  # 일반 업무 → 로컬 우선, 필요시 온라인
        "LOW":          "any",           # 공개 정보 → 온라인 가능
        "PUBLIC":       "online_prefer", # 공개 정보 → 온라인 우선 (비용 최적화)
    }
```

---

## 9. 멀티 에이전트 오케스트레이션 상세

### 9.1 7개 프레임워크 활용 전략

| 프레임워크 | 최적 용도 | 활용 시나리오 |
|-----------|----------|-------------|
| **Native** | 기본 순차 분석 | 단순 성숙도 진단, 빠른 ROI 추정 |
| **LangGraph** | 복잡 워크플로우 | AX 전체 컨설팅 파이프라인, 조건부 분기 |
| **CrewAI** | 역할 기반 협업 | 멀티 도메인 분석, 부서 간 AX 연계 |
| **AutoGen AG2** | 토론/합의 | 리스크 평가, 전략 옵션 비교 |
| **DSPy** | 프롬프트 최적화 | 보고서 품질 자동 개선, 답변 정확도 향상 |
| **LangChain** | 체인 추론 | 단계적 분석, 데이터 변환 파이프라인 |
| **LlamaIndex** | 문서 RAG | ISO 표준 참조, 규제 검색, 사례 검색 |

### 9.2 에이전트 상세 역할

#### Industry Domain Expert Agent
```yaml
역할: 해당 산업/부서 전문 지식 제공
RAG: 산업별 규제, 표준, 베스트 프랙티스 KB 참조
동적 전문성: 업종별 Fine-tuned LoRA 어댑터 로딩
출력:
  - 도메인 분석 리포트
  - 규제 체크리스트
  - 업종별 AX 사례
```

#### ROI Analyst Agent
```yaml
역할: 투자 대비 효과 정량 분석
입력: 현재 비용 구조, 인력 배치, 프로세스 소요 시간
분석: NPV, IRR, Payback Period, 민감도 분석
출력:
  - ROI 분석 보고서
  - 투자 우선순위 매트릭스
  - 민감도 분석 차트
```

#### Risk Assessment Agent
```yaml
역할: 기술적/조직적/법률적/재무적 리스크 평가
분석: FMEA, Monte Carlo 시뮬레이션
출력:
  - 리스크 매트릭스 (발생확률 × 영향도)
  - 대응 전략
  - 모니터링 지표
```

#### Implementation Architect Agent
```yaml
역할: 구현 방법론 및 기술 스택 설계
분석: 현재 IT 인프라, 데이터 가용성, 조직 역량
출력:
  - 기술 아키텍처 설계서
  - 구현 로드맵 (Phase별)
  - 자원 배분 계획
```

#### Change Management Agent
```yaml
역할: 조직 변화 관리 전략
분석: 조직 문화, 저항 요인, 이해관계자 매핑
출력:
  - 변화 관리 계획
  - 커뮤니케이션 전략
  - 교육 프로그램
```

#### Report Generator Agent
```yaml
역할: 모든 에이전트 출력의 통합 보고서 생성
형식: DOCX, PDF, PPTX, 대시보드
특징:
  - 경영진용/실무자용 자동 분리
  - 시각화 차트 자동 생성
  - 다국어 지원 (한/영)
```

---

## 10. 품질 보증 & 테스트 전략

### 10.1 테스트 레벨

| 레벨 | 대상 | 방법 | 자동화 |
|------|------|------|--------|
| Unit Test | 개별 함수/모듈 | pytest | ✅ CI/CD |
| Integration Test | API 엔드포인트 | httpx + pytest | ✅ CI/CD |
| Agent Test | 에이전트 출력 품질 | LLM-as-Judge | ✅ 주기적 |
| E2E Test | 전체 워크플로우 | Playwright + Manual | 🔄 반자동 |
| Load Test | 동시 사용자 처리 | Locust | 📋 배포 전 |
| Security Test | 보안 취약점 | OWASP ZAP | 📋 배포 전 |

### 10.2 에이전트 품질 평가 기준

```python
class AgentQualityMetrics:
    """에이전트 출력 품질 평가"""

    CRITERIA = {
        "accuracy":     "산업 도메인 지식의 정확성 (사실 오류 없음)",
        "relevance":    "질문/맥락에 대한 관련성",
        "completeness": "분석 항목의 완전성 (누락 없음)",
        "actionability":"구체적이고 실행 가능한 제안",
        "consistency":  "반복 실행 시 결과 일관성",
        "format":       "보고서 형식 준수, 구조화된 출력",
    }

    # 각 기준 1~5점, 합계 30점 만점, 최소 24점(80%) 이상 Pass
```

### 10.3 테스트 체크리스트

- [ ] 모든 145+ API 엔드포인트 응답 확인
- [ ] 7개 멀티에이전트 프레임워크 개별 실행
- [ ] 5단계 컨설팅 워크플로우 end-to-end
- [ ] 보고서 생성 (DOCX/PDF) 정상 출력
- [ ] 사이드바 전체 네비게이션 동작
- [ ] ISO 24030/38500 평가 워크스페이스
- [ ] 보안 모듈 (분류/비식별화/감사로깅)
- [ ] Ollama LLM 연동 (정상/장애 상황)
- [ ] 동시 접속 10명 이상 안정성

---

## 11. 배포 & 운영 전략

### 11.1 AI Appliance 배포 절차

```
1. 하드웨어 설치 (4U 랙마운트)
   └── 전원, 네트워크 연결
2. OS 부팅 (Ubuntu 24.04 LTS)
   └── 보안 패치 적용
3. 100K-AX Expert Platform 자동 시작
   └── systemd 서비스 등록
4. 초기 설정 마법사
   └── 기업 프로필, 부서 정보, 관리자 계정
5. LLM 모델 검증
   └── Ollama 상태 확인, 모델 로드 테스트
6. 파일럿 과제 실행
   └── 샘플 AX 과제로 전체 파이프라인 검증
```

### 11.2 운영 모니터링

```
┌─────────────────────────────────────┐
│ 100K-AX Expert Monitoring Dashboard │
├─────────────────────────────────────┤
│ System Health                       │
│  CPU: ██████░░░░ 62%               │
│  GPU: ████████░░ 85%               │
│  RAM: █████░░░░░ 48%               │
│  Disk: ███░░░░░░░ 32%              │
│                                     │
│ LLM Status                         │
│  Ollama: ● Online                  │
│  Model: Qwen 2.5 72B ● Loaded     │
│  Avg Response: 3.2s                │
│                                     │
│ Platform Usage                     │
│  Active Users: 12                  │
│  AX Tasks Today: 47               │
│  Reports Generated: 8             │
│  Avg Session: 45min               │
└─────────────────────────────────────┘
```

### 11.3 자동 업데이트 (오프라인)

Air-gapped 환경을 위한 오프라인 업데이트 패키지 방식:
1. USB/외장 드라이브로 업데이트 패키지 전달
2. 무결성 검증 (SHA-256 해시)
3. 자동 백업 → 업데이트 적용 → 검증 → 롤백 옵션

---

## 부록: 정책 연계 매핑

| 정부 정책 | 100K-AX Expert 기능 | 연계 방안 |
|----------|---------------------|----------|
| AI 고급인재 1.1만명 양성 | AX Expert/Master 등급 인증 | 국가인증 연계 |
| 첨단산업 인력 3.3만명 | 7개 산업 도메인 KB | 산업별 특화 양성 |
| AI 한글화 | 전 국민 AX Beginner 교육 | 온라인 교육 모듈 |
| AI 바우처 3억 | AI Appliance + 컨설팅 | 정부 지원사업 연계 |
| 스마트공장 고도화 | 제조 AX Discovery | 중기부 사업 연계 |
| 지역 AI 인재 양성 | 지역 AX 센터 | 지자체 협력 |

---

*문서 버전: 2.0*
*작성일: 2026-03-09*
*작성: WDLAB AI/ML/AX Group*
*Copyright (c) 2026 WDLAB*
