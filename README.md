# 100K-AX Expert - AI/AX 10만 전문인력 양성 플랫폼

> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

멀티 에이전트 기반 AI 컨설팅 & AX 전문인력 양성 엔터프라이즈 플랫폼

---

**문서 버전**: 4.0
**최종 수정일**: 2026년 3월 9일
**Update Date**: March 9, 2026
**Editor**: Brian Lee / 100K AX Expert Team

---

## 개요

기업의 AI 전환(AX: AI Transformation)을 지원하는 전문 컨설팅 및 **10만 AX 전문인력 양성** 통합 플랫폼입니다.
Ollama 기반의 Local LLM과 **7개 멀티 에이전트 프레임워크**를 활용하여
AI 컨설팅 전문 업체가 고객사에게 체계적이고 효율적인 컨설팅 서비스를 제공하며,
**100K 목표 달성을 위한 AX 전문가 발굴 · 양성 · 인증 체계**를 운영합니다.

### 플랫폼 핵심 목표

| 목표 | 설명 |
|------|------|
| **100K 인재 양성** | 10만 명 AX 전문인력 양성 (Beginner → Master 5단계 인증) |
| **AX 기회 발굴** | 7개 산업 도메인 × 10개 부서 AX 과제 템플릿 기반 기회 발굴 |
| **체계적 컨설팅** | 5단계 컨설팅 프레임워크 + 4대 국제 표준 기반 거버넌스 |
| **AI 멀티 에이전트** | 7개 프레임워크 통합 오케스트레이션 |

### 국제 표준 기반 거버넌스 프레임워크

| 표준 | 명칭 | 플랫폼 적용 영역 |
|------|------|-----------------|
| **ISO/IEC 42001** | AI 관리 시스템 | AIMS 체크리스트, AI 정책 관리 |
| **ISO/IEC 23053** | ML 기반 AI 시스템 프레임워크 | ML 파이프라인 체크리스트, 생명주기 관리 |
| **ISO/IEC 24030** | AI 시스템 역량 평가 | 성숙도 진단, 공정성 메트릭, 위험 평가 |
| **ISO/IEC 38500** | IT 거버넌스 | EDM 사이클, 6대 원칙, 경영진 대시보드 |

## 기술 스택

| 분류 | 기술 |
|------|------|
| **LLM** | Ollama (llama3.2:3b, Local) |
| **멀티 에이전트** | LangGraph, CrewAI, AutoGen (AG2) |
| **고급 프레임워크** | DSPy, LangChain (LCEL), LlamaIndex (RAG) |
| **Native Orchestrator** | 100K-AX Expert 자체 순차 오케스트레이터 (5 에이전트) |
| **Backend** | FastAPI + Uvicorn, Python 3.12 |
| **Frontend** | Jinja2 + HTML5, Bootstrap 5 Dark Theme (Glassmorphism), Chart.js |
| **Database** | SQLite (aiosqlite) |
| **서버 포트** | 8001 |
| **APP_VERSION** | 2.0.0 |

## 멀티 에이전트 프레임워크 (7개)

```
                        [100K-AX Expert Orchestrator]
                              │
          ┌───────┬───────┬───┴───┬───────┬──────────┬───────────┐
          │       │       │       │       │          │           │
     LangGraph  CrewAI  AutoGen  DSPy  LangChain  LlamaIndex  Native
     StateGraph  Role   GroupChat Sig/  LCEL       RAG        Sequential
     Workflow   Based   Dialog   CoT   Pipeline   Workflow   Orchestrator
          │       │       │       │       │          │           │
          └───────┴───────┴───┬───┴───────┴──────────┴───────────┘
                              │
                        [Ollama LLM]
                       (llama3.2:3b)
```

| 프레임워크 | 유형 | 에이전트/모듈 | 특징 |
|-----------|------|-------------|------|
| **LangGraph** | StateGraph | 5 에이전트, 8 노드 | 조건부 엣지, 품질 기반 재시도 |
| **CrewAI** | Role-Based | 5 에이전트, 6 태스크 | Sequential/Hierarchical 프로세스 |
| **AutoGen (AG2)** | GroupChat | 5 에이전트 | RoundRobin/Selector 모드 |
| **DSPy** | Signatures | 5 Signature, 5 CoT Module | 프로그래밍 방식 프롬프트 최적화 |
| **LangChain** | LCEL Pipeline | 5 Chain, PromptTemplate | ChatHistory, Callbacks |
| **LlamaIndex** | RAG Workflow | 4 ISO 표준(15문서) | VectorStore, SentenceSplitter |
| **Native** | Sequential | 5 컨설팅 에이전트 | 100K-AX Expert 자체 구현 오케스트레이터 |

## 주요 기능

### Phase 01: 5단계 컨설팅 프레임워크

| 단계 | 명칭 | 핵심 목표 |
|------|------|----------|
| 1단계 | AI 비전 및 전략 수립 | 성숙도 진단, 기회 발굴, 로드맵 수립 |
| 2단계 | Use Case 및 설계 정의 | 요구사항, 아키텍처, 거버넌스 설계 |
| 3단계 | 플랫폼 및 솔루션 구축 | PoC 검증, 플랫폼 구축, 시스템 통합 |
| 4단계 | 파일럿 및 확산 | 파일럿 운영, 변화관리, 전사 확산 |
| 5단계 | 운영 및 개선 | 모니터링, 지속 개선, 거버넌스 검토 |

### Phase 02: AI 에이전트 상태 대시보드

7개 멀티 에이전트 프레임워크를 통합 모니터링하는 대시보드:

- **요약 카드 행**: 7개 프레임워크 미니 상태카드 (아이콘 + 상태 dot + 에이전트 수)
- **상세 카드 그리드**: 각 프레임워크별 설명, 기능 태그, 에이전트/모듈 목록, 액션 버튼
- **SVG 협업 구조도**: 100K-AX Expert Orchestrator → 7 Frameworks → Ollama LLM 3계층 아키텍처
- **상태 조회**: 버튼 클릭 시 3개 Health API 병렬 호출로 실시간 상태 활성화
- **개별 프레임워크 조회/실행 테스트**: 카드 단위 상태 조회 및 POST 실행 테스트

### Phase 03: ISO 표준 거버넌스

#### ISO 42001 AIMS & ISO 23053 ML 프레임워크
- AI 관리 시스템 체크리스트, ML 파이프라인 생명주기 관리

#### ISO 24030 AI 시스템 평가 도구
- 평가 대시보드, 성숙도 진단 설문
- AI 시스템 인벤토리, 위험 평가 매트릭스
- 공정성 메트릭, 거버넌스 체크리스트
- 평가 보고서 생성, 개선 로드맵

#### ISO 38500 IT 거버넌스
- EDM 사이클 관리 (Evaluate-Direct-Monitor)
- 6대 원칙 체크리스트, RACI 매트릭스
- AI 포트폴리오 관리, 경영진 대시보드

### Phase 04: AX 전문가 양성 (신규)

100K 목표 달성을 위한 AX 전문인력 발굴 · 양성 · 인증 통합 모듈입니다.

#### AX 기회 발굴 (AX Discovery)

| 기능 | 설명 |
|------|------|
| **AX 기회 발굴** | 프로세스 입력 기반 AX 기회 자동 발굴 (4차원 분석: automation_potential, impact_score, feasibility, roi_estimate) |
| **부서별 AX 템플릿** | 10개 부서(경영기획, 인사, 재무, 마케팅, 영업, 생산, 물류, R&D, IT, 고객서비스) × AX 과제 템플릿 |
| **도메인 지식 베이스** | 7개 산업 도메인(제조, 금융, 공공, 물류, 의료, 교육, 국방) 규제/프로세스/Best Practice |

#### 학습 진도 관리 (AX Training & Certification)

| 기능 | 설명 |
|------|------|
| **양성 현황 대시보드** | 100K 목표 대비 진행률, 등록 사용자/기업/과제 KPI, 인증 레벨별 분포 차트 |
| **사용자 관리** | AX 실무자 등록, 필터링/검색, 상세 프로필 (레벨/점수/Gap/과제/뱃지) |
| **5단계 인증 체계** | Beginner → Practitioner → Specialist → Expert → Master 인증 레벨 |
| **기업 AX 현황** | 기업별 AX 도입 KPI, 부서별 달성 테이블, 인력 레벨 분포 |

#### 5단계 AX 인증 레벨

| 레벨 | 명칭 | 요건 | 색상 |
|------|------|------|------|
| 1 | **AX Beginner** | 기본 AI/AX 이해, 입문 과제 완료 | Gray |
| 2 | **AX Practitioner** | AX 과제 3건 이상 수행, 기본 도구 활용 | Green |
| 3 | **AX Specialist** | 도메인별 AX 전문성, 과제 10건+ 완료 | Blue |
| 4 | **AX Expert** | 복합 AX 프로젝트 리드, ROI 달성 실적 | Amber |
| 5 | **AX Master** | AX 전략 수립/교육, 기업 AX 전환 총괄 | Purple |

#### 대시보드 AX 모니터링 (메인 대시보드 통합)

운영 현황 대시보드에 AX 전문가 양성 모니터링 섹션이 통합되어 있습니다:

- **100K 목표 진행률**: 전체 등록 인원 / 100,000명 달성률 프로그레스바
- **KPI 카드 (4개)**: 등록 사용자, 참여 기업, 수행 과제, 과제 완료율
- **인증 레벨별 분포**: Master~Beginner 5단계 수평 프로그레스바
- **산업 도메인별 현황**: 7개 도메인 Doughnut 차트 (Chart.js)
- **빠른 이동 버튼**: AX 기회 발굴, 학습 진도 관리, 인증 레벨, 기업 AX 현황

### Phase 05: 기술 & 조직

- AI 성숙도 진단 (4대 핵심 영역, CMMI 기반 5단계)
- AI 도입 기회 발굴 (산업별 Use Case 템플릿)
- 시나리오 분석 (보수적/균형/적극적 3가지 시나리오)
- ROI 분석 / 리스크 평가 (TCO, NPV, IRR, Payback Period)
- 보고서 자동 생성 (Executive Summary / 전체 컨설팅 보고서)
- MLOps 표준, 인력/조직 구성

### Phase 06: 분석 & 산출물

- 보안 감사 대시보드 (감사 로그, 보안 제공자, 민감도 수준)
- 설정 관리
- AI 전문가 상담

## AI 에이전트 구성 (Native)

| # | 에이전트 | 역할 |
|---|---------|------|
| 1 | **AI 전략 분석가** (Strategy Analyst) | AI 성숙도 진단, 전략 분석, 로드맵 수립 |
| 2 | **Use Case 설계자** (Use Case Designer) | Use Case 설계, 아키텍처 정의 |
| 3 | **ROI 분석가** (ROI Analyst) | 투자 효과 분석, TCO/NPV/IRR 계산 |
| 4 | **리스크 평가 전문가** (Risk Assessor) | 리스크 평가 및 완화 전략 수립 |
| 5 | **보고서 생성 전문가** (Report Generator) | 컨설팅 보고서 자동 생성 |

## API 엔드포인트 (171개)

### 시스템
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/api/v1/health` | 시스템 헬스체크 |
| GET | `/api/v1/agents/status` | Native 에이전트 상태 |

### 멀티 에이전트 (`/api/v1/multi-agent/`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/frameworks` | 프레임워크 목록 |
| GET | `/health` | LangGraph/CrewAI/AutoGen 헬스체크 |
| GET | `/langgraph/info` | LangGraph 정보 |
| GET | `/langgraph/graph` | LangGraph 그래프 시각화 |
| POST | `/langgraph/run` | LangGraph 실행 |
| GET | `/crewai/info` | CrewAI 정보 |
| POST | `/crewai/run` | CrewAI 실행 |
| GET | `/autogen/info` | AutoGen 정보 |
| POST | `/autogen/run` | AutoGen 실행 |

### 고급 프레임워크 (`/api/v1/advanced-frameworks/`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/overview` | 프레임워크 개요 |
| GET | `/health` | DSPy/LangChain/LlamaIndex 헬스체크 |
| GET | `/dspy/info` | DSPy 정보 |
| POST | `/dspy/run` | DSPy 실행 (maturity) |
| GET | `/langchain/info` | LangChain 정보 |
| POST | `/langchain/run` | LangChain 실행 |
| GET | `/llamaindex/info` | LlamaIndex 정보 |
| POST | `/llamaindex/query` | LlamaIndex RAG 질의 |
| POST | `/llamaindex/rebuild-index` | 인덱스 재구축 |

### AX 기회 발굴 (`/api/v1/ax-discovery/`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| POST | `/discover` | AX 기회 발굴 실행 |
| GET | `/templates` | 전체 부서 AX 과제 템플릿 |
| GET | `/templates/{department}` | 부서별 AX 과제 템플릿 |
| GET | `/domains` | 산업 도메인 목록 (7개) |
| GET | `/domains/{domain}` | 도메인 상세 정보 |
| GET | `/domains/{domain}/best-practices` | 도메인 Best Practice |
| GET | `/domains/{domain}/processes` | 도메인 핵심 프로세스 |
| GET | `/domains/{domain}/regulations` | 도메인 규제/표준 |
| GET | `/best-practices/search?query=` | Best Practice 검색 |

### AX 학습 진도 관리 (`/api/v1/training/`)
| Method | Endpoint | 설명 |
|--------|----------|------|
| GET | `/stats` | 플랫폼 전체 통계 (100K 목표 대비 진행률) |
| POST | `/users` | AX 실무자 등록 |
| GET | `/users` | 실무자 목록 (필터: company_id, department) |
| GET | `/users/{user_id}` | 실무자 상세 정보 |
| GET | `/users/{user_id}/summary` | 학습 진도 요약 |
| GET | `/users/{user_id}/certification` | 인증 레벨 및 Gap 분석 |
| POST | `/users/{user_id}/tasks` | AX 과제 할당 |
| GET | `/users/{user_id}/tasks` | 사용자 과제 목록 |
| POST | `/users/{user_id}/tasks/{task_id}/start` | 과제 시작 |
| POST | `/users/{user_id}/tasks/{task_id}/complete` | 과제 완료 |
| GET | `/departments/{company_id}/{department}` | 부서별 AX 현황 |
| GET | `/enterprise/{company_id}` | 기업 전체 AX 대시보드 |
| GET | `/certification/levels` | 인증 레벨 정의 (5단계) |

### 5단계 프레임워크 (`/api/v1/framework/projects/{id}/`)
- Stage 1: `stage1/maturity-assessment`, `stage1/opportunities`, `stage1/roadmap` (GET/POST + analyze)
- Stage 2: `stage2/requirements`, `stage2/architecture`, `stage2/governance` (GET/POST)
- Stage 3: `stage3/poc`, `stage3/platform`, `stage3/integration` (GET/POST)
- Stage 4: `stage4/pilot`, `stage4/change-management`, `stage4/scale` (GET/POST)
- Stage 5: `stage5/monitoring`, `stage5/improvement`, `stage5/governance-review` (GET/POST)
- 공통: `summary`, `report`, `scenarios`, `methodology/*`, `governance/*`

### 보안 (`/api/security/`)
- `audit/logs`, `audit/stats`, `audit/alerts`, `audit/daily-report`, `audit/weekly-report`, `audit/monthly-report`
- `providers`, `sensitivity-levels`, `routing-decisions`
- `templates`, `templates/categories`, `templates/summary`
- `monitoring/checklist`

## 프로젝트 구조

```
100K-Expert/
├── config/
│   └── settings.py                      # 플랫폼 설정 (Ollama URL, 모델 등)
├── src/
│   ├── agents/
│   │   ├── base_agent.py                # BaseConsultingAgent (ABC)
│   │   ├── consulting_agents.py         # 5개 전문 에이전트
│   │   ├── agent_orchestrator.py        # Native 순차 오케스트레이터
│   │   ├── langgraph_orchestrator.py    # LangGraph StateGraph (8 노드)
│   │   ├── crewai_orchestrator.py       # CrewAI Role-Based (Sequential/Hierarchical)
│   │   └── autogen_orchestrator.py      # AutoGen AG2 GroupChat
│   ├── api/
│   │   ├── routes.py                    # Core API 라우트
│   │   ├── consulting_framework_routes.py  # 5단계 프레임워크 라우트
│   │   ├── multi_agent_routes.py        # 멀티에이전트 라우트 (10개)
│   │   ├── advanced_framework_routes.py # 고급 프레임워크 라우트 (10개)
│   │   ├── ax_discovery_routes.py       # AX 기회 발굴 라우트 (9개)
│   │   ├── ax_training_routes.py        # AX 학습 진도 관리 라우트 (13개)
│   │   ├── security_routes.py           # 보안 모듈 라우트
│   │   └── stage1~5/                    # 단계별 라우트 모듈
│   ├── core/
│   │   ├── llm_provider.py              # Ollama LLM (LangChain 래퍼)
│   │   ├── dspy_provider.py             # DSPy Signature/CoT 모듈
│   │   ├── langchain_chains.py          # LangChain LCEL Pipeline/History
│   │   └── llamaindex_rag.py            # LlamaIndex RAG Workflow
│   ├── models/
│   │   └── schemas.py                   # Pydantic 데이터 모델 (AX 모델 포함)
│   └── services/
│       └── report_generator.py          # 보고서 생성 서비스
├── templates/
│   ├── index.html                       # 메인 SPA 대시보드 (AX 모니터링 통합)
│   ├── includes/                        # 공통 컴포넌트 (_head, _sidebar, _sidebar_nav 등)
│   ├── stage1~5/                        # 단계별 템플릿
│   ├── iso24030/                        # ISO 24030 평가 UI
│   └── iso38500/                        # ISO 38500 거버넌스 UI
├── static/
│   ├── css/
│   │   └── project-manager.css          # 100K-AX Expert Platform 스타일
│   └── js/
│       ├── project-manager-modular.js   # 메인 JS (모듈화)
│       ├── iso24030-manager.js          # ISO 24030 평가 모듈
│       ├── iso38500-manager.js          # ISO 38500 거버넌스 모듈
│       └── modules/                     # PM 서브 모듈 (crud, localstorage 등)
├── data/
│   └── standards/                       # ISO 표준 문서 (42001, 23053, 24030, 38500)
├── main.py                              # FastAPI 앱 엔트리포인트
├── requirements.txt                     # Python 의존성
└── README.md
```

## 설치 및 실행

### 사전 요구사항

- Python 3.10+ (권장: 3.12)
- Ollama (로컬 LLM 실행용)

### Ollama 설치 및 모델 준비

```bash
# Ollama 설치 (Linux)
curl -fsSL https://ollama.com/install.sh | sh

# Ollama 서버 실행
ollama serve

# 모델 다운로드 (다른 터미널에서)
ollama pull llama3.2:3b
```

### 플랫폼 실행

```bash
# 프로젝트 디렉토리로 이동
cd /home/ubuntu-02/ai_project/100K-Expert

# 가상환경 생성 및 활성화
python3 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
python3 -m uvicorn main:app --host 0.0.0.0 --port 8001
```

### 접속

- **웹 대시보드**: http://localhost:8001
- **API 문서 (Swagger)**: http://localhost:8001/docs
- **API 문서 (ReDoc)**: http://localhost:8001/redoc

## 테스트 현황

| 지표 | 값 |
|------|-----|
| 총 테스트 | 106건 |
| 통과 | 104건 |
| 실패 | 2건 (입력 스키마 불일치, 심각도 Low) |
| 성공률 | **98.1%** |
| 멀티에이전트 프레임워크 | 7개 (전체 Healthy) |
| 총 API 라우트 | **171개** |

상세 테스트 결과: [`docs/TEST_REPORT_V2.md`](./docs/TEST_REPORT_V2.md)

## 플랫폼 메뉴 구조

```
100K-AX Expert Platform v2.0.0
│
├── START: 대시보드
│   ├── 운영 현황 (프로젝트/성숙도/ROI/시스템 상태)
│   ├── 컨설팅 진행 현황 (5단계 Stage Progress)
│   ├── 서비스 통계 (분석/보고서/상담/리스크/컨설턴트)
│   ├── 연동 대시보드 상태 (Ollama/DB/API)
│   ├── ★ AX 전문가 양성 모니터링 ★
│   │   ├── 100K 목표 진행률 프로그레스바
│   │   ├── KPI 카드 (사용자/기업/과제/완료율)
│   │   ├── 인증 레벨별 분포 (Master~Beginner)
│   │   └── 산업 도메인별 Doughnut 차트
│   ├── AI 성숙도/Use Case 차트
│   └── 프로젝트 목록 & 워크플로우
│
├── Phase 01: 컨설팅 Stage
│   ├── Stage 1: AI 비전 및 전략 수립
│   ├── Stage 2: Use Case 및 설계 정의
│   ├── Stage 3: 플랫폼 및 솔루션 구축
│   ├── Stage 4: 파일럿 및 확산
│   └── Stage 5: 운영, 모니터링 및 개선
│
├── Phase 02: AI 에이전트 상태
│   ├── 7개 프레임워크 요약 카드
│   ├── 7개 프레임워크 상세 카드 (상태 조회/실행 테스트)
│   └── 에이전트 협업 구조 SVG 다이어그램
│
├── Phase 03: ISO 표준 체크리스트
│   ├── ISO 42001 AIMS 체크리스트
│   ├── ISO 23053 ML 프레임워크 체크리스트
│   ├── ISO 표준 전체보기
│   ├── ISO 24030 평가 (대시보드/설문/인벤토리/위험/공정성/체크리스트/보고서/로드맵)
│   └── ISO 38500 거버넌스 (대시보드/EDM/원칙/RACI/포트폴리오/경영진/성숙도)
│
├── Phase 04: AX 전문가 양성 ★ NEW ★
│   ├── AX 기회 발굴
│   │   ├── AX 기회 발굴 (프로세스 입력 → 4차원 분석)
│   │   ├── 부서별 AX 템플릿 (10개 부서)
│   │   └── 도메인 지식 베이스 (7개 산업)
│   └── 학습 진도 관리
│       ├── 양성 현황 대시보드 (100K 목표)
│       ├── 사용자 관리 (등록/필터/상세/과제)
│       ├── 인증 레벨 관리 (5단계 인증 체계)
│       └── 기업 AX 현황 (기업별 KPI/부서/분포)
│
├── Phase 05: 기술 & 조직
│   ├── 분석 결과, MLOps 표준, 인력 조직
│   └── 시나리오 분석, ROI/리스크 평가, 보고서 생성
│
├── Phase 06: 분석 & 산출물
│   ├── 보안 감사 대시보드
│   ├── 설정
│   └── AI 전문가 상담
│
└── 공통 기능
    ├── 사이드바 리사이즈, 섹션 접기/펼치기
    ├── 테마 (Dark Glassmorphism + Gradient + Glow Effects)
    └── 반응형 레이아웃 (Bootstrap 5)
```

## 라이선스

This project is for demonstration and educational purposes.

## 참고 문서

- AI 인프라 컨설팅 전문기업 설립 종합보고서
- CMMI (Capability Maturity Model Integration)
- MLOps 기술 표준
- AI 거버넌스 프레임워크
- ISO/IEC 42001:2023 - AI 관리 시스템
- ISO/IEC 23053:2022 - ML 기반 AI 시스템 프레임워크
- ISO/IEC 24030:2024 - AI 시스템 역량 평가
- ISO/IEC 38500:2024 - IT 거버넌스

---

## 문서 이력

| 버전 | 날짜 | 작성자 | 변경 내용 |
|------|------|--------|----------|
| 1.0 | 2025-11-28 | Brian Lee | 초기 문서 작성 |
| 1.1 | 2025-12-07 | Brian Lee | 프로젝트 구조 및 기능 업데이트 |
| 2.0 | 2025-12-11 | Brian Lee | ISO 24030/38500 표준 통합, 메뉴 구조 업데이트 |
| 2.1 | 2025-12-16 | Brian Lee | 문서 업데이트 및 편집자 정보 갱신 |
| 3.0 | 2026-02-17 | Brian Lee | 멀티에이전트 7개 프레임워크 통합, 에이전트 대시보드 재설계, 기술 스택/API/구조 전면 개정 |
| 4.0 | 2026-03-09 | Brian Lee | Phase 04 AX 전문가 양성 모듈 추가 (AX Discovery 9개 + Training 13개 API), 대시보드 AX 모니터링 통합, Phase 구조 재편 (6단계), 총 API 171개, 브랜딩 100K-AX Expert Platform v2.0.0 |

---

**Copyright &copy; 2025-2026 WDLAB AI/ML/AX Group. All rights reserved.**
