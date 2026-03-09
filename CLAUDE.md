# 100K-AX Expert Platform - CLAUDE.md
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team
# AI/AX 10만 전문인력 양성 플랫폼 개발 가이드

> 이 파일은 AI 코딩 어시스턴트(Claude Code)가 본 프로젝트의 코드를 이해하고
> 일관성 있게 수정·확장할 수 있도록 작성된 프로젝트 컨텍스트 문서입니다.

---

## 1. 프로젝트 개요

| 항목 | 내용 |
|------|------|
| **프로젝트명** | 100K-AX Expert (AI/AX 10만 전문인력 양성 플랫폼) |
| **목적** | 대한민국 산업 현장 실무자 10만명을 AI/AX 전문가로 양성 |
| **원본 프로젝트** | 100K-AX Expert - AI Consulting Enterprise Platform |
| **기술 스택** | FastAPI + Jinja2/Bootstrap 5 + Ollama LLM + 멀티에이전트 (7 프레임워크) |
| **Python 버전** | 3.12+ |
| **서버 포트** | 8001 |
| **정책 근거** | 이재명 정부 AI/AX 인력 양성 정책, AI 예산 10.1조원, AI 3대 강국 도약 |
| **핵심 철학** | "AI/AX 전문가는 교실이 아닌 현업의 실무에서 만들어진다" |

---

## 2. 핵심 디자인 원칙

### 2.1 현업 중심 AX 전문가 양성 패러다임
- 대학/교육기관 중심이 아닌, **도메인 전문성을 보유한 현업 실무자**가 AI/AX 역량을 획득
- 멀티 에이전트 AI가 부족한 인간 컨설턴트를 대체하여 10만명 규모 동시 컨설팅 제공
- AX Discovery → AI Consulting → Report → 반복학습 → 전문가 인증의 사이클

### 2.2 온프레미스 보안 우선
- Nvidia RTX 5090 기반 AI Appliance로 완전 로컬 운영 지원
- Air-gapped 환경 지원, 기업 데이터 외부 유출 Zero
- 하이브리드(Local/Online) LLM 라우팅 지원

### 2.3 산업 도메인 다양성
- 제조, 금융, 공공, 유통/물류, 의료, 교육, 국방/방산 등 전 산업 도메인 지원
- 산업별 Knowledge Base + Fine-tuned LoRA 어댑터
- 부서별 세분화 AX 접근 (기업당 135~275건 AX 과제)

---

## 3. 프로젝트 구조

```
100K-Expert/
├── main.py                      # FastAPI 진입점 (포트 8001)
├── config/
│   └── settings.py              # 앱 설정 (APP_NAME, Ollama, DB 등)
├── src/
│   ├── agents/                  # AI 에이전트 구현
│   │   ├── base_agent.py        # 추상 베이스 클래스
│   │   ├── consulting_agents.py # 5개 컨설팅 에이전트 정의
│   │   ├── agent_orchestrator.py       # Native 순차 오케스트레이터
│   │   ├── langgraph_orchestrator.py   # LangGraph StateGraph
│   │   ├── crewai_orchestrator.py      # CrewAI 역할 기반
│   │   ├── autogen_orchestrator.py     # AutoGen AG2 GroupChat
│   │   ├── strategy_analyst.py
│   │   ├── usecase_designer.py
│   │   ├── roi_analyst.py
│   │   ├── risk_assessor.py
│   │   └── report_generator.py
│   ├── api/                     # API 라우트 (145+ 엔드포인트)
│   │   ├── routes.py            # 핵심 API (34 엔드포인트)
│   │   ├── consulting_framework_routes.py  # 5단계 프레임워크
│   │   ├── multi_agent_routes.py           # 멀티에이전트
│   │   ├── advanced_framework_routes.py    # DSPy/LangChain/LlamaIndex
│   │   ├── security_routes.py             # 보안/감사
│   │   └── stage1~5/           # 각 단계별 세부 라우트
│   ├── core/                    # LLM 프로바이더
│   │   ├── llm_provider.py      # Ollama 연동
│   │   ├── hybrid_llm_provider.py  # 하이브리드 LLM
│   │   ├── dspy_provider.py
│   │   ├── langchain_chains.py
│   │   └── llamaindex_rag.py
│   ├── models/                  # Pydantic 데이터 모델
│   ├── security/                # 보안 모듈
│   │   ├── audit_logger.py
│   │   ├── data_classifier.py
│   │   ├── data_sanitizer.py
│   │   └── query_router.py
│   ├── services/                # 보고서 생성 서비스
│   └── utils/                   # 유틸리티
├── templates/                   # Jinja2 HTML 템플릿
│   ├── index.html               # 메인 SPA (대시보드)
│   ├── includes/                # 공통 파셜
│   │   ├── _sidebar.html
│   │   ├── _sidebar_nav.html
│   │   ├── _sidebar_start.html
│   │   └── _sidebar_stages.html
│   ├── stage1~5/               # 5단계 워크스페이스
│   ├── iso24030/               # ISO 24030 AI 역량 평가
│   └── iso38500/               # ISO 38500 IT 거버넌스
├── static/
│   ├── css/project-manager.css  # 메인 스타일시트
│   └── js/
│       ├── project-manager-modular.js  # 모듈형 JS
│       ├── iso24030-manager.js
│       └── iso38500-manager.js
├── data/                        # 런타임 데이터
│   ├── audit_logs/
│   ├── consulting_logs/
│   ├── index/                   # 벡터 스토어
│   └── standards/               # ISO 표준 문서
├── docs/                        # 프로젝트 문서
├── reports/                     # 생성된 보고서
└── tests/                       # 테스트 파일
```

---

## 4. 기술 스택 및 의존성

### 4.1 Backend
| 기술 | 용도 | 비고 |
|------|------|------|
| FastAPI | REST API 서버 | uvicorn, 비동기 지원 |
| Ollama | 로컬 LLM 서빙 | llama3.2:latest 기본 |
| SQLite + aiosqlite | 데이터베이스 | 비동기 지원 |
| Pydantic | 데이터 검증 | BaseSettings 설정 관리 |

### 4.2 Frontend
| 기술 | 용도 |
|------|------|
| Jinja2 | 서버사이드 템플릿 |
| Bootstrap 5 | UI 프레임워크 |
| Chart.js | 데이터 시각화 |
| Dark Theme + Glassmorphism | 디자인 시스템 |

### 4.3 AI/ML 프레임워크 (7개)
| 프레임워크 | 패턴 | 역할 |
|-----------|------|------|
| **Native** | Sequential | 100K-AX Expert 자체 5개 에이전트 오케스트레이터 |
| **LangGraph** | StateGraph | 상태 기반 워크플로우 (8 노드) |
| **CrewAI** | Role-based | 역할 기반 에이전트 협업 (6 태스크) |
| **AutoGen AG2** | GroupChat | 그룹 채팅 기반 대화 (5 에이전트) |
| **DSPy** | Signatures/CoT | 프롬프트 자동 최적화 (5 시그니처) |
| **LangChain** | LCEL Pipeline | 체인 기반 추론 (5 체인) |
| **LlamaIndex** | RAG Workflow | ISO 표준 문서 기반 RAG (15 문서) |

### 4.4 보안
| 기술 | 용도 |
|------|------|
| AES-256-GCM | 데이터 암호화 (at rest) |
| TLS 1.3 | 통신 암호화 (in transit) |
| JWT + OAuth 2.0 | 인증/인가 |
| RBAC | 역할 기반 접근 제어 |
| Audit Logger | 전체 접근/변경 이력 관리 |

---

## 5. 코드 재활용 규칙

### 5.1 브랜드명 규칙
- 프로젝트 브랜드: **100K-AX Expert**
- 풀네임: "100K-AX Expert - AI/AX 10만 전문인력 양성 플랫폼"
- 축약형: "100K-AX Expert Platform"
- 기존 "100K-AX Expert" 참조는 모두 "100K-AX Expert"로 변경됨
- sys.path 경로: `/home/ubuntu-02/ai_project/100K-Expert`

### 5.2 코딩 컨벤션
```python
# 파일 상단 sys.path 설정 (필수)
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

# Pydantic 모델 사용
from pydantic import BaseModel, Field

# 비동기 함수 우선 사용
async def my_endpoint():
    ...

# 타입 힌트 사용
def analyze(data: dict[str, Any]) -> AnalysisResult:
    ...
```

### 5.3 API 엔드포인트 규칙
- 기본 경로: `/api/v1/`
- 보안 경로: `/api/security/`
- 프로젝트 CRUD: `/api/v1/projects/{project_id}/`
- 멀티에이전트: `/api/v1/multi-agent/`
- 고급 프레임워크: `/api/v1/advanced-frameworks/`
- RESTful 규칙 준수, JSON 응답

### 5.4 템플릿 규칙
- Jinja2 include 패턴 사용 (sidebar → _sidebar_nav → _sidebar_start + _sidebar_stages + _sidebar_iso)
- 다크 테마 CSS 변수 사용 (--bg-primary, --brand-primary 등)
- Bootstrap 5 + Bootstrap Icons
- Glassmorphism + Gradient + Glow 이펙트 유지

### 5.5 에이전트 구현 규칙
- `BaseConsultingAgent` 추상 클래스 상속
- 각 에이전트는 독립적 분석 수행 후 결과를 오케스트레이터에 반환
- Ollama LLM Provider 통해 LLM 호출
- 결과는 Pydantic 모델로 구조화

---

## 6. AX 전문가 양성 체계 (100K-AX Expert 고유)

### 6.1 DX-to-AX 전환 프레임워크
| Level | 단계 | 설명 |
|-------|------|------|
| 0 | Manual | 수기 작업, 엑셀, 경험 의존 |
| 1 | Digital (DX) | 전산화, 시스템 도입, 표준화 |
| 2 | Data-Driven | 데이터 기반 의사결정 |
| 3 | AI-Augmented | AI 보조 의사결정, 자동화 |
| 4 | Autonomous (Full AX) | AI 자율 운영, 지속 학습 |

### 6.2 전문가 인증 등급 (5단계)
| 등급 | 요건 | 역량 |
|------|------|------|
| AX Beginner | 기본 교육 + AX 과제 5건+ | AX 개념 이해 |
| AX Practitioner | 과제 20건+ ROI 달성 10건+ | 독립 수행 |
| AX Specialist | 과제 50건+ 전환율 30%+ | 부서 AX 리더 |
| AX Expert | 과제 100건+ 타부서 컨설팅 | 전사 AX 전략 |
| AX Master | Expert + 외부 컨설팅 | 산업 도메인 전문가 |

### 6.3 멀티 에이전트 컨설팅 (6개 역할)
1. **Industry Domain Expert Agent** - 산업 도메인 전문 지식 (RAG + LoRA)
2. **ROI Analyst Agent** - NPV, IRR, Payback Period 분석
3. **Risk Assessment Agent** - FMEA, Monte Carlo 시뮬레이션
4. **Implementation Architect Agent** - 기술 아키텍처, 구현 로드맵
5. **Change Management Agent** - 조직 변화 관리
6. **Report Generator Agent** - 통합 보고서 생성 (DOCX/PDF/PPTX)

---

## 7. 사이드바 네비게이션 구조

```
START
├── 대시보드
└── 새 프로젝트

PHASE 01: 기반 설정
└── 컨설팅 방법론
    ├── 방법론 개요
    ├── 성숙도 진단 방법
    └── 가치-실행 매핑

PHASE 02: 5단계 프레임워크
├── Stage 1: 전략 수립 → 성숙도 진단 & 기회 발굴
├── Stage 2: 설계 정의 → 요건 & 아키텍처 설계
├── Stage 3: 솔루션 구축 → PoC & 플랫폼 구축
├── Stage 4: 파일럿 & 확산 → 파일럿 운영 & 확산
└── Stage 5: 운영 & 최적화 → 모니터링 & 개선

PHASE 03: ISO 표준
├── ISO 24030: AI 시스템 역량 평가
└── ISO 38500: IT 거버넌스
```

---

## 8. 주요 API 엔드포인트 요약

### 시스템
- `GET /api/v1/health` - 헬스체크
- `GET /api/v1/ollama/status` - Ollama 상태

### 프로젝트 CRUD
- `POST /api/v1/projects` - 생성
- `GET /api/v1/projects` - 목록
- `GET /api/v1/projects/{id}` - 조회
- `DELETE /api/v1/projects/{id}` - 삭제

### 5단계 컨설팅
- `POST /api/v1/projects/{id}/maturity-assessment` - 성숙도 진단
- `POST /api/v1/projects/{id}/opportunities` - 기회 발굴
- `POST /api/v1/projects/{id}/roadmap` - 로드맵 수립
- `POST /api/v1/projects/{id}/use-cases/{idx}/design` - 설계
- `POST /api/v1/projects/{id}/governance/*` - 거버넌스

### 멀티에이전트
- `GET /api/v1/multi-agent/frameworks` - 프레임워크 목록
- `POST /api/v1/multi-agent/langgraph/run` - LangGraph 실행
- `POST /api/v1/multi-agent/crewai/run` - CrewAI 실행
- `POST /api/v1/multi-agent/autogen/run` - AutoGen 실행
- `POST /api/v1/multi-agent/compare` - 비교 분석

### 보고서
- `POST /api/v1/projects/{id}/reports` - 생성
- `POST /api/v1/projects/{id}/reports/export` - 내보내기

### 보안
- `POST /api/security/classify` - 데이터 분류
- `POST /api/security/sanitize` - 비식별화
- `GET /api/security/audit/logs` - 감사 로그

---

## 9. 수정 시 주의사항

1. **기존 디자인 유지**: Dark Theme, Glassmorphism, Gradient/Glow 효과는 절대 변경하지 않음
2. **sys.path 통일**: 모든 파일에서 `/home/ubuntu-02/ai_project/100K-Expert` 사용
3. **설정 중앙 관리**: `config/settings.py`의 `Settings` 클래스로 모든 설정 관리
4. **에이전트 확장**: `BaseConsultingAgent` 상속 후 `analyze()` 메서드 구현
5. **라우트 등록**: `main.py`에서 `app.include_router()` 패턴 준수
6. **보안 우선**: 모든 민감 데이터 처리 시 `data_classifier.py` → `data_sanitizer.py` 파이프라인 적용
7. **한국어 우선**: UI 라벨, 에이전트 프롬프트, 보고서 모두 한국어 기본 (`DEFAULT_LANGUAGE: "ko"`)
8. **ISO 표준 준수**: ISO 42001, 23053, 24030, 38500 표준 데이터는 `data/standards/`에 위치

---

## 10. 정책 연계 핵심 키워드

- **AI 3대 강국 도약** (미국·중국과 함께)
- **AI 한글화** - 국민 모두가 AI를 한글처럼 익히는 개념
- **현업 중심 양성** - 도메인 전문가 → AX 전문가 전환
- **10만명 5년 양성** - 10,000기업 × 10명/기업
- **산업 도메인**: 제조, 금융, 공공, 유통/물류, 의료, 교육, 국방/방산
- **DX-to-AX 전환** - Level 0(Manual) → Level 4(Autonomous)
- **온프레미스 AI Appliance** - RTX 5090 기반 완전 로컬 운영
- **정부 예산 10.1조원** (2026년) - AI 인재양성 + 인프라 7.5조원

---

*최종 업데이트: 2026-03-09*
*Copyright (c) 2026 WDLAB & WDLAB AI/ML/AX Group*
