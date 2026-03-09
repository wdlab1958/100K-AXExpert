# 서버 실행 및 API 라우팅 확인 보고서
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

## 📋 개요
AI Consulting Assistant Platform의 frontend와 backend 서버 실행 및 모든 API endpoint 라우팅 확인

## ✅ 라우터 등록 현황

### main.py에서 등록된 라우터
```python
# API 라우터 등록
app.include_router(api_router)          # /api/v1
app.include_router(security_router)      # /api/security
app.include_router(framework_router)     # /api/v1/framework
```

### 등록된 라우터 상세

#### 1. API Router (`src/api/routes.py`)
- **Prefix**: `/api/v1`
- **태그**: `AI Consulting`
- **주요 엔드포인트**:
  - 프로젝트 관리: `/api/v1/projects`
  - 성숙도 진단: `/api/v1/projects/{project_id}/maturity-assessment`
  - 기회 발굴: `/api/v1/projects/{project_id}/opportunities`
  - 로드맵: `/api/v1/projects/{project_id}/roadmap`
  - 시나리오 분석: `/api/v1/projects/{project_id}/scenarios`
  - 피드백: `/api/v1/projects/{project_id}/feedback`
  - 보고서: `/api/v1/projects/{project_id}/reports`
  - 전체 컨설팅: `/api/v1/projects/{project_id}/run-full-consultation`
  - 채팅: `/api/v1/projects/{project_id}/chat`
  - 헬스체크: `/api/v1/health`
  - MLOps 표준: `/api/v1/config/mlops-standards`
  - 인력 구성: `/api/v1/config/personnel-organization`

#### 2. Security Router (`src/api/security_routes.py`)
- **Prefix**: `/api/security`
- **태그**: `Security`
- **주요 엔드포인트**:
  - 데이터 분류: `/api/security/classify`
  - 데이터 익명화: `/api/security/sanitize`
  - 질의 라우팅: `/api/security/route`
  - 온라인 LLM 제공자: `/api/security/providers`
  - 온라인 LLM 질의: `/api/security/query/online`
  - 감사 로그: `/api/security/audit/logs`
  - 템플릿: `/api/security/templates`
  - 모니터링 체크리스트: `/api/security/monitoring/checklist`

#### 3. Framework Router (`src/api/consulting_framework_routes.py`)
- **Prefix**: `/api/v1/framework`
- **태그**: `Consulting Framework`
- **포함된 Stage 라우터**:
  - Stage 1: `/api/v1/framework/projects/{project_id}/stage1`
  - Stage 2: `/api/v1/framework/projects/{project_id}/stage2`
  - Stage 3: `/api/v1/framework/projects/{project_id}/stage3`
  - Stage 4: `/api/v1/framework/projects/{project_id}/stage4`
  - Stage 5: `/api/v1/framework/projects/{project_id}/stage5`

- **주요 엔드포인트**:
  - 프로젝트 관리: `/api/v1/framework/projects`
  - 프로젝트 요약: `/api/v1/framework/projects/{project_id}/summary`
  - Stage별 데이터 저장/조회
  - 거버넌스 평가: `/api/v1/framework/projects/{project_id}/governance/*`
  - MLOps 표준: `/api/v1/framework/projects/{project_id}/mlops-standards`
  - 인력 구성: `/api/v1/framework/projects/{project_id}/personnel-organization`
  - 시나리오 분석: `/api/v1/framework/projects/{project_id}/scenarios/analyze`
  - 보고서 생성: `/api/v1/framework/projects/{project_id}/report/generate`

### Stage별 라우터 상세

#### Stage 1 (`src/api/stage1/routes.py`)
- **Prefix**: `/projects/{project_id}/stage1`
- **엔드포인트**:
  - 성숙도 진단: `POST/GET /maturity-assessment`
  - 기회 발굴: `POST/GET /opportunities`
  - 로드맵: `POST/GET /roadmap`
  - AI 분석: `POST /maturity-assessment/analyze`, `/opportunities/analyze`, `/roadmap/analyze`

#### Stage 2 (`src/api/stage2/routes.py`)
- **Prefix**: `/projects/{project_id}/stage2`
- **엔드포인트**:
  - 요건 정의: `POST/GET /requirements`
  - 아키텍처: `POST/GET /architecture`
  - 거버넌스: `POST/GET /governance`

#### Stage 3 (`src/api/stage3/routes.py`)
- **Prefix**: `/projects/{project_id}/stage3`
- **엔드포인트**:
  - PoC: `POST/GET /poc`
  - 플랫폼: `POST/GET /platform`
  - 통합: `POST/GET /integration`

#### Stage 4 (`src/api/stage4/routes.py`)
- **Prefix**: `/projects/{project_id}/stage4`
- **엔드포인트**:
  - 파일럿: `POST/GET /pilot`
  - 변화 관리: `POST/GET /change-management`
  - 확산: `POST/GET /scale`

#### Stage 5 (`src/api/stage5/routes.py`)
- **Prefix**: `/projects/{project_id}/stage5`
- **엔드포인트**:
  - 모니터링: `POST/GET /monitoring`
  - 개선: `POST/GET /improvement`

## 🚀 서버 실행 방법

### 방법 1: run.sh 스크립트 사용 (권장)
```bash
cd /home/wdlab/Project/ai_project/ai_consulting
bash run.sh
```

### 방법 2: 직접 실행
```bash
cd /home/wdlab/Project/ai_project/ai_consulting
source venv/bin/activate
python3 main.py --host 0.0.0.0 --port 8001
```

### 방법 3: uvicorn 직접 실행
```bash
cd /home/wdlab/Project/ai_project/ai_consulting
source venv/bin/activate
uvicorn main:app --host 0.0.0.0 --port 8001
```

### 방법 4: 백그라운드 실행
```bash
cd /home/wdlab/Project/ai_project/ai_consulting
source venv/bin/activate
nohup python3 main.py --host 0.0.0.0 --port 8001 > server_8001.log 2>&1 &
```

## 📍 서버 접속 정보

- **Frontend**: http://localhost:8001
- **API 문서 (Swagger)**: http://localhost:8001/docs
- **API 문서 (ReDoc)**: http://localhost:8001/redoc
- **OpenAPI JSON**: http://localhost:8001/openapi.json

## ✅ API 엔드포인트 확인 방법

### 1. 헬스체크
```bash
curl http://localhost:8001/api/v1/health
```

### 2. OpenAPI 스펙 확인
```bash
curl http://localhost:8001/openapi.json | python3 -m json.tool
```

### 3. 등록된 라우트 확인 (Python)
```python
from main import app
for route in app.routes:
    if hasattr(route, 'path') and hasattr(route, 'methods'):
        print(f"{list(route.methods)} {route.path}")
```

## 📊 라우팅 통계

- **총 라우터 수**: 3개 (api_router, security_router, framework_router)
- **Stage별 라우터**: 5개 (stage1~stage5)
- **예상 총 API 엔드포인트 수**: 100개 이상

## 🔍 주요 기능별 API 엔드포인트

### 프로젝트 관리
- `POST /api/v1/framework/projects` - 프로젝트 생성
- `GET /api/v1/framework/projects` - 프로젝트 목록
- `GET /api/v1/framework/projects/{project_id}` - 프로젝트 조회
- `DELETE /api/v1/framework/projects/{project_id}` - 프로젝트 삭제

### Stage 1: AI 비전 및 전략 수립
- `POST /api/v1/framework/projects/{project_id}/stage1/maturity-assessment` - 성숙도 진단 저장
- `GET /api/v1/framework/projects/{project_id}/stage1/maturity-assessment` - 성숙도 진단 조회
- `POST /api/v1/framework/projects/{project_id}/stage1/opportunities` - 기회 발굴 저장
- `POST /api/v1/framework/projects/{project_id}/stage1/roadmap` - 로드맵 저장

### Stage 2: Use Case 및 설계 정의
- `POST /api/v1/framework/projects/{project_id}/stage2/requirements` - 요건 정의
- `POST /api/v1/framework/projects/{project_id}/stage2/architecture` - 아키텍처 설계
- `POST /api/v1/framework/projects/{project_id}/stage2/governance` - 거버넌스 수립

### Stage 3: 플랫폼 및 솔루션 구축
- `POST /api/v1/framework/projects/{project_id}/stage3/poc` - PoC 계획
- `POST /api/v1/framework/projects/{project_id}/stage3/platform` - 플랫폼 구축
- `POST /api/v1/framework/projects/{project_id}/stage3/integration` - 통합 설정

### Stage 4: 파일럿 및 확산
- `POST /api/v1/framework/projects/{project_id}/stage4/pilot` - 파일럿 계획
- `POST /api/v1/framework/projects/{project_id}/stage4/change-management` - 변화 관리
- `POST /api/v1/framework/projects/{project_id}/stage4/scale` - 확산 계획

### Stage 5: 운영, 모니터링 및 개선
- `POST /api/v1/framework/projects/{project_id}/stage5/monitoring` - 모니터링 설정
- `POST /api/v1/framework/projects/{project_id}/stage5/improvement` - 개선 계획

### 보안 및 거버넌스
- `POST /api/security/classify` - 데이터 분류
- `POST /api/security/sanitize` - 데이터 익명화
- `POST /api/security/route` - 질의 라우팅
- `GET /api/security/audit/logs` - 감사 로그 조회

### 보고서 및 분석
- `POST /api/v1/framework/projects/{project_id}/report/generate` - 보고서 생성
- `GET /api/v1/framework/projects/{project_id}/report` - 보고서 조회
- `POST /api/v1/framework/projects/{project_id}/scenarios/analyze` - 시나리오 분석

## ✅ 확인 사항

1. ✅ 모든 라우터가 main.py에 등록됨
2. ✅ Stage별 라우터가 framework_router에 포함됨
3. ✅ CORS 미들웨어 설정 완료
4. ✅ 정적 파일 및 템플릿 설정 완료
5. ✅ API 문서 자동 생성 설정 완료

## 📝 참고사항

- 서버는 기본적으로 포트 8001에서 실행됩니다
- 가상환경 활성화가 필요할 수 있습니다
- Ollama가 실행 중이어야 LLM 기능이 정상 작동합니다
- 모든 API 엔드포인트는 `/docs`에서 확인할 수 있습니다

## 🎯 다음 단계

1. 서버 실행 확인
2. 각 API 엔드포인트 테스트
3. Frontend와의 연동 확인
4. 에러 로그 모니터링

