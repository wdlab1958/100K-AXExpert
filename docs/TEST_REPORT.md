# AI Consulting Assistant Platform - 전체 기능 테스트 리포트
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

**테스트 일시:** 2026-02-17 21:10 ~ 21:30 KST
**서버 주소:** http://localhost:8001
**테스트 대상:** 대시보드 전체 메뉴 및 워크스페이스 기능 (125개 API 라우트)
**테스트 방법:** curl 기반 자동화 API 테스트 + HTML 렌더링 검증

---

## 종합 결과

| 구분 | 전체 | Pass | Fail (코드 버그) | Fail (LLM 의존) | 통과율 |
|------|------|------|-----------------|-----------------|--------|
| **전체** | **145** | **139** | **4** | **2** | **95.9%** |

| 카테고리 | 전체 | Pass | Fail | 비고 |
|----------|------|------|------|------|
| A. 시스템/설정 API | 8 | 8 | 0 | |
| B. HTML 페이지 렌더링 | 3 | 3 | 0 | |
| C. 보안 모듈 API | 19 | 16 | 3 | 라우트 순서 버그 |
| D. 프로젝트 CRUD | 11 | 11 | 0 | |
| E. Stage 1~5 저장/조회 | 30 | 30 | 0 | |
| F. 분석/보고서/거버넌스 | 32 | 29 | 3 | LLM 의존 2건, 코드 버그 1건 |
| G. 사이드바 메뉴 키워드 | 19 | 19 | 0 | |
| H. JS/CSS 참조 | 3 | 3 | 0 | |
| I. 정적 자산 접근 | 15 | 15 | 0 | |
| J. 보안 템플릿 세부 | 5 | 5 | 0 | |

---

## A. 시스템 및 설정 API (8/8 Pass)

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| A01 | `/api/v1/health` | GET | 200 | **Pass** | healthy, timestamp, version 정상 |
| A02 | `/api/v1/config/industries` | GET | 200 | **Pass** | 산업 분류 7개 반환 |
| A03 | `/api/v1/config/company-sizes` | GET | 200 | **Pass** | 기업 규모 4개 반환 |
| A04 | `/api/v1/config/consulting-stages` | GET | 200 | **Pass** | 5단계 프레임워크 반환 |
| A05 | `/api/v1/config/mlops-standards` | GET | 200 | **Pass** | MLOps 표준 프레임워크 반환 |
| A06 | `/api/v1/config/personnel-organization` | GET | 200 | **Pass** | 인력 구성 프레임워크 반환 |
| A07 | `/api/v1/framework/config/personnel-organization` | GET | 200 | **Pass** | Framework 인력 구성 반환 |
| A08 | `/api/v1/agents/status` | GET | 200 | **Pass** | 에이전트 상태 5개 반환 |

---

## B. HTML 페이지 렌더링 (3/3 Pass)

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| B01 | `/` | GET | 200 | **Pass** | 메인 대시보드 HTML 정상 렌더링 |
| B02 | `/docs` | GET | 200 | **Pass** | Swagger UI 정상 |
| B03 | `/redoc` | GET | 200 | **Pass** | ReDoc 정상 |

---

## C. 보안 모듈 API (16/19 Pass)

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| C01 | `/api/security/sensitivity-levels` | GET | 200 | **Pass** | 민감도 레벨 반환 |
| C02 | `/api/security/templates` | GET | 200 | **Pass** | 13개 템플릿 반환 |
| C03 | `/api/security/templates/categories` | GET | 404 | **Fail** | `/{template_id}` 라우트가 먼저 매칭됨 |
| C04 | `/api/security/templates/summary` | GET | 404 | **Fail** | 동일 라우트 순서 문제 |
| C05 | `/api/security/templates/search?q=risk` | GET | 404 | **Fail** | 동일 라우트 순서 문제 |
| C06 | `/api/security/classify` | POST | 200 | **Pass** | 데이터 분류 정상 동작 |
| C07 | `/api/security/sanitize` | POST | 200 | **Pass** | 데이터 익명화 정상 동작 |
| C08 | `/api/security/route` | POST | 200 | **Pass** | 쿼리 라우팅 정상 (context=dict) |
| C09 | `/api/security/routing-decisions` | GET | 200 | **Pass** | 라우팅 이력 반환 |
| C10 | `/api/security/providers` | GET | 200 | **Pass** | 프로바이더 목록 반환 |
| C11 | `/api/security/audit/logs` | GET | 200 | **Pass** | 감사 로그 반환 |
| C12 | `/api/security/audit/stats` | GET | 200 | **Pass** | 감사 통계 반환 |
| C13 | `/api/security/audit/event-types` | GET | 200 | **Pass** | 이벤트 유형 반환 |
| C14 | `/api/security/audit/alerts` | GET | 200 | **Pass** | 알림 목록 반환 |
| C15 | `/api/security/audit/daily-report` | GET | 200 | **Pass** | 일간 리포트 반환 |
| C16 | `/api/security/audit/weekly-report` | GET | 200 | **Pass** | 주간 리포트 반환 |
| C17 | `/api/security/audit/monthly-report` | GET | 200 | **Pass** | 월간 리포트 반환 |
| C18 | `/api/security/monitoring/checklist` | GET | 200 | **Pass** | 모니터링 체크리스트 반환 |
| C19 | `/api/security/reports/list` | GET | 200 | **Pass** | 보고서 목록 반환 |

---

## D. 프로젝트 CRUD (11/11 Pass)

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| D01 | `/api/v1/framework/projects` | GET | 200 | **Pass** | 프로젝트 목록 조회 |
| D02 | `/api/v1/framework/projects` | POST | 200 | **Pass** | 신규 프로젝트 생성 (project-67f70477) |
| D03 | `/api/v1/framework/projects/create-sample` | POST | 200 | **Pass** | 샘플 프로젝트 생성 (sample-ff3db3a7) |
| D04 | `/api/v1/framework/projects` | GET | 200 | **Pass** | 생성 후 목록 확인 (4개) |
| D05 | `/api/v1/framework/projects/{id}` | GET | 200 | **Pass** | 프로젝트 상세 조회 |
| D06 | `/api/v1/framework/projects/{id}/summary` | GET | 200 | **Pass** | 단계별 진행률 포함 요약 |
| D07 | `/api/v1/framework/projects/{id}/duplicate` | POST | 200 | **Pass** | 프로젝트 복제 성공 |
| D08 | `/api/v1/framework/projects/{dup_id}` | DELETE | 200 | **Pass** | 복제본 삭제 성공 |
| D09 | `/api/v1/framework/projects` | GET | 200 | **Pass** | 삭제 후 목록 확인 |
| D10 | `/api/v1/projects/{id}` | GET | 200 | **Pass** | v1 API 프로젝트 조회 |
| D11 | `/api/v1/projects/{id}/status` | GET | 200 | **Pass** | 프로젝트 상태 (STRATEGY, stage 1) |

---

## E. Stage 1~5 저장/조회 (30/30 Pass)

### Stage 1: AI 비전 및 전략 수립

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| E01 | `/stage1/maturity-assessment` | POST | 200 | **Pass** | 4개 영역 점수 자동 계산 (전략 3.0, 조직 2.5, 데이터 2.5, 프로세스 2.25) |
| E02 | `/stage1/maturity-assessment` | GET | 200 | **Pass** | 저장된 데이터 정확히 반환 |
| E03 | `/stage1/opportunities` | POST | 200 | **Pass** | 기회 저장, ID 자동 부여 (OPP-proj-001) |
| E04 | `/stage1/opportunities` | GET | 200 | **Pass** | 기회 목록 반환 |
| E05 | `/stage1/roadmap` | POST | 200 | **Pass** | 비전/목표/KPI/단계 저장 |
| E06 | `/stage1/roadmap` | GET | 200 | **Pass** | 로드맵 전체 구조 반환 |

### Stage 2: Use Case 및 설계 정의

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| E07 | `/stage2/requirements` | POST | 200 | **Pass** | 요건 정의 저장 |
| E08 | `/stage2/requirements` | GET | 200 | **Pass** | 저장된 요건 반환 |
| E09 | `/stage2/architecture` | POST | 200 | **Pass** | 아키텍처 저장 (flat→nested 구조 변환 주의) |
| E10 | `/stage2/architecture` | GET | 200 | **Pass** | 아키텍처 반환 |
| E11 | `/stage2/governance` | POST | 200 | **Pass** | 거버넌스 저장 (flat→nested 구조 변환 주의) |
| E12 | `/stage2/governance` | GET | 200 | **Pass** | 거버넌스 반환 |

### Stage 3: 솔루션 구축

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| E13 | `/stage3/poc` | POST | 200 | **Pass** | PoC 계획 저장, status=planned |
| E14 | `/stage3/poc` | GET | 200 | **Pass** | PoC 계획 반환 |
| E15 | `/stage3/platform` | POST | 200 | **Pass** | 플랫폼 구성 저장 |
| E16 | `/stage3/platform` | GET | 200 | **Pass** | 플랫폼 구성 반환 |
| E17 | `/stage3/integration` | POST | 200 | **Pass** | 통합 설정 저장 |
| E18 | `/stage3/integration` | GET | 200 | **Pass** | 통합 설정 반환 |

### Stage 4: 파일럿 및 확산

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| E19 | `/stage4/pilot` | POST | 200 | **Pass** | 파일럿 계획 저장 |
| E20 | `/stage4/pilot` | GET | 200 | **Pass** | 파일럿 계획 반환 |
| E21 | `/stage4/change-management` | POST | 200 | **Pass** | 변화관리 4개 영역 저장 |
| E22 | `/stage4/change-management` | GET | 200 | **Pass** | 변화관리 반환 |
| E23 | `/stage4/scale` | POST | 200 | **Pass** | 확산 계획 저장 |
| E24 | `/stage4/scale` | GET | 200 | **Pass** | 확산 계획 반환 |

### Stage 5: 운영 및 개선

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| E25 | `/stage5/monitoring` | POST | 200 | **Pass** | 모니터링 설정 저장 |
| E26 | `/stage5/monitoring` | GET | 200 | **Pass** | 모니터링 설정 반환 |
| E27 | `/stage5/improvement` | POST | 200 | **Pass** | 개선 계획 저장 |
| E28 | `/stage5/improvement` | GET | 200 | **Pass** | 개선 계획 반환 |
| E29 | `/stage5/governance-review` | POST | 200 | **Pass** | 거버넌스 검토 저장 |
| E30 | `/stage5/governance-review` | GET | 200 | **Pass** | 거버넌스 검토 반환 |

---

## F. 분석/보고서/거버넌스/협업 (29/32 Pass)

### 시나리오 분석

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F01 | `/framework/.../scenarios/analyze` | POST | 200 | **Pass** | 3개 시나리오 생성 (보수/균형/적극) |
| F02 | `/framework/.../scenarios` | GET | 200 | **Pass** | 저장된 시나리오 반환 |

### 보고서 생성

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F03 | `/framework/.../report/generate` | POST | 200 | **Pass** | 7개 섹션 포함 보고서 생성 |
| F04 | `/framework/.../report` | GET | 200 | **Pass** | 생성된 보고서 조회 |
| F05 | `/framework/.../report/download` | GET | 200 | **Pass** | HTML 보고서 다운로드 |

### 방법론

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F06 | `/methodology/detailed-maturity` | POST | 200 | **Pass** | 16개 항목 평가, overall=2.56, gap 계산 |
| F07 | `/methodology/detailed-maturity` | GET | 200 | **Pass** | 평가 결과 반환 |
| F08 | `/methodology/value-mapping` | POST | 200 | **Pass** | 3개 과제 분류 (quick_win/strategic/fill_in) |
| F09 | `/methodology/value-mapping` | GET | 200 | **Pass** | 매핑 결과 반환 |

### AI 거버넌스 프레임워크

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F10 | `/governance/core-areas` | POST | 200 | **Pass** | 3대 핵심영역 평가, overall=69.4 |
| F11 | `/governance/core-areas` | GET | 200 | **Pass** | 핵심영역 평가 반환 |
| F12 | `/governance/components` | POST | 200 | **Pass** | 7대 구성요소 평가, 69.0 "Developing" |
| F13 | `/governance/components` | GET | 200 | **Pass** | 구성요소 평가 반환 |
| F14 | `/governance/assessment` | POST | 200 | **Pass** | 종합 평가 72.5점 "양호" |
| F15 | `/governance/assessment` | GET | 200 | **Pass** | 종합 평가 반환 |
| F16 | `/governance/summary` | GET | 200 | **Pass** | 전체 거버넌스 요약 반환 |

### MLOps 표준

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F17 | `/framework/.../mlops-standards` | GET | 200 | **Pass** | 초기 빈 데이터 반환 |
| F18 | `/framework/.../mlops-standards` | POST | 200 | **Pass** | MLOps 표준 저장, maturity=3.5 |
| F19 | `/framework/.../mlops-standards/analyze` | POST | 200 | **Pass** | 분석 결과 반환 |

### 인력 구성

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F20 | `/framework/.../personnel-organization` | GET | 200 | **Pass** | 초기 빈 데이터 반환 |
| F21 | `/framework/.../personnel-organization` | POST | 200 | **Pass** | 6개 역할 저장, 현재 7명/목표 18명 |
| F22 | `/framework/.../personnel-organization/gap-analysis` | POST | 200 | **Pass** | Gap 11명 (61.1%), 12개월 타임라인 |

### 협업/피드백

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F23 | `/api/v1/projects/{id}/feedback` | POST | 200 | **Pass** | 피드백 저장 (스키마 수정 후 성공) |
| F24 | `/api/v1/projects/{id}/feedback` | GET | 200 | **Pass** | 피드백 이력 1건 반환 |

### AI 챗 & 전체 컨설팅

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F25 | `/api/v1/projects/{id}/chat` | POST | 200 | **Fail** | LLM 의존: Ollama llama3.1:8b 모델 미설치 |
| F26 | `/api/v1/projects/{id}/run-full-consultation` | POST | 500 | **Fail** | LLM 의존: Ollama llama3.1:8b 모델 미설치 |

### Stage 1 AI 분석

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F27 | `/stage1/maturity-assessment/analyze` | POST | 200 | **Pass** | Level 1 평가, 권고사항 4건 |
| F28 | `/stage1/opportunities/analyze` | POST | 200 | **Pass** | 기회 1건 분석 |
| F29 | `/stage1/roadmap/analyze` | POST | 200 | **Pass** | 완성도 100%, 목표 2건 |

### v1 API MLOps/인력

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| F30 | `/api/v1/projects/{id}/mlops-standards` | GET | 200 | **Pass** | MLOps 표준 스키마 반환 |
| F31 | `/api/v1/projects/{id}/mlops-standards` | POST | 500 | **Fail** | 코드 버그: `ConsultingOrchestrator.update_project` 미구현 |
| F32 | `/api/v1/projects/{id}/personnel-organization` | GET | 200 | **Pass** | 인력 구성 반환 |

---

## G. 사이드바 메뉴 키워드 검증 (19/19 Pass)

| # | 메뉴 항목 | 결과 | 비고 |
|---|-----------|------|------|
| G01 | Dashboard (dashboard) | **Pass** | HTML에 존재 |
| G02 | 새 프로젝트 (new-project) | **Pass** | HTML에 존재 |
| G03 | Stage 1 (stage1) | **Pass** | HTML에 존재 |
| G04 | Stage 2 (stage2) | **Pass** | HTML에 존재 |
| G05 | Stage 3 (stage3) | **Pass** | HTML에 존재 |
| G06 | Stage 4 (stage4) | **Pass** | HTML에 존재 |
| G07 | Stage 5 (stage5) | **Pass** | HTML에 존재 |
| G08 | ISO 42001 (aims-dashboard) | **Pass** | HTML에 존재 |
| G09 | ISO 24030 (iso24030) | **Pass** | HTML에 존재 |
| G10 | ISO 38500 (iso38500) | **Pass** | HTML에 존재 |
| G11 | ISO 23053 (ml-framework) | **Pass** | HTML에 존재 |
| G12 | MLOps 표준 (mlops-standards) | **Pass** | HTML에 존재 |
| G13 | 인력 구성 (personnel-organization) | **Pass** | HTML에 존재 |
| G14 | 시나리오 분석 (scenarios) | **Pass** | HTML에 존재 |
| G15 | 보고서 (reports) | **Pass** | HTML에 존재 |
| G16 | 보안 (security) | **Pass** | HTML에 존재 |
| G17 | 에이전트 (agents) | **Pass** | HTML에 존재 |
| G18 | 설정 (settings) | **Pass** | HTML에 존재 |
| G19 | 협업 (collaboration) | **Pass** | HTML에 존재 |

---

## H. JS/CSS 참조 검증 (3/3 Pass)

| # | 항목 | 결과 | 비고 |
|---|------|------|------|
| H01 | project-manager.js / project-manager-modular.js | **Pass** | HTML에 참조 존재 |
| H02 | Bootstrap CSS/JS | **Pass** | CDN 참조 존재 |
| H03 | Chart.js | **Pass** | 참조 존재 |

---

## I. 정적 자산 접근성 (15/15 Pass)

| # | 파일 경로 | Status | 결과 |
|---|-----------|--------|------|
| I01 | `/static/css/project-manager.css` | 200 | **Pass** |
| I02 | `/static/js/project-manager.js` | 200 | **Pass** |
| I03 | `/static/js/project-manager-modular.js` | 200 | **Pass** |
| I04 | `/static/js/modules/pm-project-crud.js` | 200 | **Pass** |
| I05 | `/static/js/modules/pm-stage-config.js` | 200 | **Pass** |
| I06 | `/static/js/modules/pm-scenario-report.js` | 200 | **Pass** |
| I07 | `/static/js/modules/pm-form-collector.js` | 200 | **Pass** |
| I08 | `/static/js/modules/pm-form-populator.js` | 200 | **Pass** |
| I09 | `/static/js/modules/pm-localstorage.js` | 200 | **Pass** |
| I10 | `/static/js/modules/pm-aims.js` | 200 | **Pass** |
| I11 | `/static/js/modules/pm-ml-framework.js` | 200 | **Pass** |
| I12 | `/static/js/modules/pm-utils.js` | 200 | **Pass** |
| I13 | `/static/js/modules/pm-notification.js` | 200 | **Pass** |
| I14 | `/static/js/iso24030-manager.js` | 200 | **Pass** |
| I15 | `/static/js/iso38500-manager.js` | 200 | **Pass** |

---

## J. 보안 템플릿 세부 테스트 (5/5 Pass)

| # | Endpoint | Method | Status | 결과 | 비고 |
|---|----------|--------|--------|------|------|
| J01 | `/api/security/templates` | GET | 200 | **Pass** | 13개 템플릿 반환 |
| J02 | `/api/security/templates/{id}` | GET | 200 | **Pass** | 템플릿 상세 반환 |
| J03 | `/api/security/providers/configure` | POST | 200 | **Pass** | 프로바이더 설정 |
| J04 | `/api/security/monitoring/checklist` | POST | 200 | **Pass** | 체크리스트 저장 |
| J05 | `/api/security/reports/save` | POST | 200 | **Pass** | 보안 보고서 저장 |

---

## 발견된 결함 상세

### BUG-001: 보안 템플릿 라우트 순서 문제 (Severity: Medium)

**영향 범위:** 3개 endpoint
**증상:** `/api/security/templates/categories`, `/summary`, `/search` 모두 404 반환
**근본 원인:** `security_routes.py`에서 `/{template_id}` 파라미터 라우트가 정적 경로(`/categories`, `/summary`, `/search`)보다 먼저 등록되어, FastAPI가 `"categories"` 등을 template_id로 해석
**수정 방법:** 정적 라우트를 `/{template_id}` 라우트 위에 배치

```python
# 수정 전 (현재)
@router.get("/templates/{template_id}")  # 이것이 먼저 매칭됨
@router.get("/templates/categories")     # 도달 불가

# 수정 후
@router.get("/templates/categories")     # 정적 경로 먼저
@router.get("/templates/summary")
@router.get("/templates/search")
@router.get("/templates/{template_id}")  # 파라미터 경로 마지막
```

### BUG-002: ConsultingOrchestrator.update_project 메서드 미구현 (Severity: Medium)

**영향 범위:** 1개 endpoint (`POST /api/v1/projects/{id}/mlops-standards`)
**증상:** HTTP 500 - `'ConsultingOrchestrator' object has no attribute 'update_project'`
**근본 원인:** `src/agents/agent_orchestrator.py`의 `ConsultingOrchestrator` 클래스에 `update_project()` 메서드 미구현
**수정 방법:** `update_project(project_id, updates)` 메서드 추가

### BUG-003: Ollama LLM 모델 미설치 (Severity: Low - 인프라)

**영향 범위:** 2개 endpoint (`/chat`, `/run-full-consultation`)
**증상:** Chat은 200 반환하지만 에러 메시지, Full Consultation은 500 반환
**근본 원인:** Ollama 서비스는 실행 중이나 `llama3.1:8b` 모델이 pull 되지 않음
**수정 방법:** `ollama pull llama3.1:8b` 실행

---

## 기능별 워크스페이스 테스트 요약

| 워크스페이스 기능 | 테스트 항목 수 | 결과 | 상태 |
|------------------|--------------|------|------|
| 대시보드 | 3 | 3 Pass | :white_check_mark: 정상 |
| 프로젝트 생성/조회/삭제/복제 | 11 | 11 Pass | :white_check_mark: 정상 |
| Stage 1: 성숙도 진단 | 2+1 | 3 Pass | :white_check_mark: 정상 |
| Stage 1: 기회 발굴 | 2+1 | 3 Pass | :white_check_mark: 정상 |
| Stage 1: 전략 로드맵 | 2+1 | 3 Pass | :white_check_mark: 정상 |
| Stage 2: 요건 정의 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 2: 아키텍처 설계 | 2 | 2 Pass | :white_check_mark: 정상 (구조 매핑 주의) |
| Stage 2: 거버넌스/윤리 | 2 | 2 Pass | :white_check_mark: 정상 (구조 매핑 주의) |
| Stage 3: PoC 계획 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 3: 플랫폼 구축 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 3: 시스템 통합 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 4: 파일럿 운영 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 4: 변화관리 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 4: 확산 계획 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 5: 모니터링 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 5: 지속 개선 | 2 | 2 Pass | :white_check_mark: 정상 |
| Stage 5: 거버넌스 검토 | 2 | 2 Pass | :white_check_mark: 정상 |
| 방법론: 상세 성숙도 | 2 | 2 Pass | :white_check_mark: 정상 |
| 방법론: 가치 매핑 | 2 | 2 Pass | :white_check_mark: 정상 |
| 시나리오 분석 | 2 | 2 Pass | :white_check_mark: 정상 |
| 보고서 생성/다운로드 | 3 | 3 Pass | :white_check_mark: 정상 |
| AI 거버넌스 (핵심영역) | 2 | 2 Pass | :white_check_mark: 정상 |
| AI 거버넌스 (구성요소) | 2 | 2 Pass | :white_check_mark: 정상 |
| AI 거버넌스 (종합평가) | 3 | 3 Pass | :white_check_mark: 정상 |
| MLOps 표준 관리 | 4 | 3 Pass, 1 Fail | :warning: BUG-002 |
| 인력 구성/Gap 분석 | 3 | 3 Pass | :white_check_mark: 정상 |
| 협업/피드백 | 2 | 2 Pass | :white_check_mark: 정상 |
| AI 컨설턴트 채팅 | 1 | 1 Fail | :x: BUG-003 (LLM) |
| 전체 컨설팅 실행 | 1 | 1 Fail | :x: BUG-003 (LLM) |
| 보안: 데이터 분류/익명화 | 3 | 3 Pass | :white_check_mark: 정상 |
| 보안: 쿼리 라우팅 | 2 | 2 Pass | :white_check_mark: 정상 |
| 보안: 감사 로그 | 5 | 5 Pass | :white_check_mark: 정상 |
| 보안: 보고서 일/주/월간 | 3 | 3 Pass | :white_check_mark: 정상 |
| 보안: 템플릿 | 5 | 2 Fail, 3 Pass | :warning: BUG-001 |
| 보안: 모니터링 | 2 | 2 Pass | :white_check_mark: 정상 |
| 정적 자산 (CSS/JS) | 15 | 15 Pass | :white_check_mark: 정상 |

---

## 결론

전체 **145개 테스트** 중 **139개 Pass (95.9%)** 로, 플랫폼의 핵심 기능은 안정적으로 동작합니다.

**코드 버그 4건** (보안 템플릿 라우트 3건 + Orchestrator 메서드 1건)은 수정이 필요하며, **LLM 의존 2건**은 Ollama 모델 설치로 해결 가능합니다.

5단계 컨설팅 프레임워크(Stage 1~5)의 모든 저장/조회 기능, 시나리오 분석, 보고서 생성, AI 거버넌스 평가, MLOps 표준 관리, 인력 Gap 분석 등 핵심 워크스페이스 기능이 정상 동작합니다.
