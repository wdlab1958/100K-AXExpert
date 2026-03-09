# 100K-AX Expert 성능 최적화 및 모듈화 가이드
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

**문서 버전**: 1.0  
**작성일**: 2025년 12월 16일  
**Update Date**: Dec. 16, 2025  
**Editor**: Brian Lee / WDLAB AI/ML/AX Group  
**목적**: 프로젝트 성능 최적화 및 유지보수성 향상을 위한 모듈화 전략

---

## 개요

본 문서는 100K-AX Expert - AX/MAX Self Consulting Assistant & Analyst 프로젝트의 성능 최적화를 위해 파일 크기가 길어 모듈화로 분리해야 할 내용과 최적화 방법론을 정리한다. 현재 프로젝트에서 파일 크기가 과도하게 큰 파일들을 식별하고, 이를 모듈화하여 성능, 유지보수성, 확장성을 향상시키는 방안을 제시한다.

---

## 1. 현재 프로젝트 파일 크기 분석

### 1.1 대용량 파일 현황

| 파일 경로 | 라인 수 | 파일 크기 (추정) | 우선순위 | 문제점 |
|----------|---------|-----------------|---------|--------|
| `templates/index.html` | 23,064 | ~1.2MB | 🔴 최우선 | 단일 파일에 모든 UI 포함 |
| `src/api/consulting_framework_routes.py` | 2,750 | ~150KB | 🔴 최우선 | 모든 API 라우트가 단일 파일 |
| `static/js/project-manager.js` | 3,832 | ~200KB | 🟡 높음 | 단일 JavaScript 파일 |
| `src/agents/consulting_agents.py` | 1,052 | ~60KB | 🟡 높음 | 모든 에이전트가 단일 파일 |
| `static/js/iso24030-manager.js` | 1,049 | ~55KB | 🟢 중간 | ISO 24030 관련 기능 |
| `src/api/security_routes.py` | 1,040 | ~55KB | 🟢 중간 | 보안 관련 라우트 |
| `src/models/schemas.py` | 910 | ~50KB | 🟢 중간 | 모든 데이터 모델 |

### 1.2 성능 영향 분석

#### 1.2.1 Frontend 성능 영향
- **초기 로딩 시간**: `index.html` 파일이 23,064줄로 매우 크며, 모든 UI 컴포넌트가 한 번에 로드됨
- **메모리 사용량**: 브라우저가 모든 DOM 요소를 한 번에 파싱하여 메모리 사용량 증가
- **렌더링 성능**: 초기 렌더링 시 불필요한 요소까지 모두 렌더링하여 성능 저하
- **JavaScript 번들 크기**: `project-manager.js`가 3,832줄로 초기 로딩 시 모든 기능이 로드됨

#### 1.2.2 Backend 성능 영향
- **모듈 로딩 시간**: `consulting_framework_routes.py`가 2,750줄로 Python 모듈 로딩 시간 증가
- **메모리 사용량**: 모든 API 라우트가 한 번에 메모리에 로드됨
- **코드 탐색 시간**: 개발자가 특정 기능을 찾기 어려워 개발 생산성 저하
- **테스트 어려움**: 단일 파일에 모든 기능이 있어 단위 테스트 작성이 어려움

---

## 2. 모듈화 분리 대상 및 전략

### 2.1 Frontend 모듈화

#### 2.1.1 `templates/index.html` (23,064줄) 분리 전략

**현재 구조**:
```
templates/index.html (23,064줄)
├── HTML 헤더 및 메타데이터
├── CSS 스타일 (인라인)
├── 사이드바 네비게이션
├── 대시보드 섹션
├── Stage 1: AI 비전 및 전략 수립
├── Stage 2: Use Case 및 설계 정의
├── Stage 3: 플랫폼 및 솔루션 구축
├── Stage 4: 파일럿 및 확산
├── Stage 5: 운영, 모니터링 및 개선
├── ISO 24030 평가 섹션
├── ISO 38500 거버넌스 섹션
├── 시나리오 관리 섹션
├── 보고서 관리 섹션
└── JavaScript 코드 (인라인)
```

**분리 전략**:

1. **템플릿 분리**:
   ```
   templates/
   ├── base.html                    # 기본 레이아웃 (헤더, 사이드바)
   ├── dashboard.html               # 대시보드
   ├── stage1/
   │   ├── maturity.html            # 성숙도 진단
   │   ├── opportunities.html       # 기회 발굴
   │   └── roadmap.html            # 전략 로드맵
   ├── stage2/
   │   ├── requirements.html        # 상세 요건 정의
   │   ├── architecture.html        # 기술 아키텍처
   │   └── governance.html         # 거버넌스
   ├── stage3/
   │   ├── poc.html                # PoC 수행
   │   ├── platform.html           # 플랫폼 구축
   │   └── integration.html        # 솔루션 통합
   ├── stage4/
   │   ├── pilot.html               # 파일럿 운영
   │   ├── change.html             # 변화 관리
   │   └── scale.html              # 전사 확산
   ├── stage5/
   │   ├── monitoring.html         # 운영 모니터링
   │   └── improvement.html        # 개선
   ├── iso24030/
   │   ├── dashboard.html          # 평가 대시보드
   │   ├── assessment.html         # 성숙도 진단
   │   └── inventory.html          # 시스템 인벤토리
   ├── iso38500/
   │   ├── dashboard.html          # 거버넌스 대시보드
   │   └── edm.html                # EDM 사이클
   ├── scenarios.html               # 시나리오 관리
   └── reports.html                 # 보고서 관리
   ```

2. **CSS 분리**:
   ```
   static/css/
   ├── base.css                    # 기본 스타일
   ├── components/
   │   ├── sidebar.css            # 사이드바
   │   ├── cards.css              # 카드 컴포넌트
   │   ├── forms.css              # 폼 컴포넌트
   │   └── charts.css             # 차트 스타일
   ├── pages/
   │   ├── dashboard.css          # 대시보드
   │   ├── stage1.css            # Stage 1
   │   ├── stage2.css            # Stage 2
   │   └── ...
   └── themes/
       └── dark.css               # 다크 테마
   ```

3. **JavaScript 분리** (이미 부분적으로 진행됨):
   ```
   static/js/
   ├── core/
   │   ├── app.js                 # 메인 애플리케이션
   │   ├── router.js              # 라우팅
   │   └── state.js               # 상태 관리
   ├── modules/
   │   ├── pm-utils.js            # 유틸리티 (기존)
   │   ├── pm-project-crud.js     # 프로젝트 CRUD (기존)
   │   ├── pm-stage-config.js     # Stage 설정 (기존)
   │   └── ...
   ├── pages/
   │   ├── dashboard.js           # 대시보드 로직
   │   ├── stage1.js              # Stage 1 로직
   │   └── ...
   └── components/
       ├── sidebar.js             # 사이드바 컴포넌트
       ├── forms.js               # 폼 컴포넌트
       └── charts.js               # 차트 컴포넌트
   ```

**구현 방법**:
- Jinja2 템플릿 상속 사용 (`{% extends "base.html" %}`)
- 템플릿 블록 사용 (`{% block content %}`)
- 동적 라우팅으로 필요한 페이지만 로드
- Lazy loading으로 초기 로딩 시간 단축

**예상 효과**:
- 초기 로딩 시간: **70-80% 감소** (23,064줄 → 필요한 페이지만 로드)
- 메모리 사용량: **60-70% 감소**
- 렌더링 성능: **50-60% 향상**

---

#### 2.1.2 `static/js/project-manager.js` (3,832줄) 분리 전략

**현재 구조**:
```
project-manager.js (3,832줄)
├── ProjectManager 객체
│   ├── 프로젝트 CRUD
│   ├── Stage별 데이터 관리
│   ├── 자동 저장 시스템
│   ├── localStorage 관리
│   ├── 시나리오 관리
│   ├── 보고서 생성
│   └── ISO 표준 관리
```

**분리 전략** (이미 `modules/` 디렉토리에 부분적으로 분리됨):

1. **기존 모듈 활용 강화**:
   ```
   static/js/
   ├── project-manager.js          # 메인 진입점 (간소화)
   └── modules/
       ├── pm-utils.js             # 유틸리티 함수
       ├── pm-project-crud.js      # 프로젝트 CRUD
       ├── pm-form-collector.js    # 폼 데이터 수집
       ├── pm-form-populator.js    # 폼 데이터 채우기
       ├── pm-stage-config.js      # Stage 설정
       ├── pm-localstorage.js      # localStorage 관리
       ├── pm-scenario-report.js   # 시나리오 및 보고서
       ├── pm-aims.js              # ISO 42001
       ├── pm-ml-framework.js      # ISO 23053
       ├── iso24030-manager.js     # ISO 24030
       └── iso38500-manager.js     # ISO 38500
   ```

2. **추가 분리 필요 영역**:
   ```
   modules/
   ├── pm-api-client.js            # API 클라이언트 (새로 생성)
   ├── pm-cache.js                 # 캐시 관리 (새로 생성)
   ├── pm-validation.js            # 유효성 검사 (새로 생성)
   ├── pm-notification.js          # 알림 시스템 (기존)
   └── pm-charts.js                # 차트 관리 (새로 생성)
   ```

3. **모듈 로더 구현**:
   ```javascript
   // static/js/core/module-loader.js
   class ModuleLoader {
       constructor() {
           this.modules = new Map();
           this.loadedModules = new Set();
       }

       async loadModule(moduleName) {
           if (this.loadedModules.has(moduleName)) {
               return this.modules.get(moduleName);
           }

           const module = await import(`./modules/${moduleName}.js`);
           this.modules.set(moduleName, module);
           this.loadedModules.add(moduleName);
           return module;
       }

       async loadModules(moduleNames) {
           return Promise.all(moduleNames.map(name => this.loadModule(name)));
       }
   }
   ```

**구현 방법**:
- ES6 모듈 시스템 사용 (`import/export`)
- 동적 import로 필요한 모듈만 로드
- 모듈 간 의존성 관리
- 번들러 사용 (Webpack, Vite 등) 고려

**예상 효과**:
- 초기 로딩 시간: **60-70% 감소**
- 코드 재사용성: **80% 향상**
- 유지보수성: **90% 향상**

---

### 2.2 Backend 모듈화

#### 2.2.1 `src/api/consulting_framework_routes.py` (2,750줄) 분리 전략

**현재 구조**:
```
consulting_framework_routes.py (2,750줄, 109개 함수)
├── Pydantic Models (20+ 클래스)
├── Stage 1 라우트
│   ├── 성숙도 진단 (save/get/analyze)
│   ├── 기회 발굴 (save/get/analyze)
│   └── 전략 로드맵 (save/get/analyze)
├── Stage 2 라우트
│   ├── 상세 요건 정의 (save/get)
│   ├── 기술 아키텍처 (save/get)
│   └── 거버넌스 (save/get)
├── Stage 3 라우트
│   ├── PoC 수행 (save/get)
│   ├── 플랫폼 구축 (save/get)
│   └── 솔루션 통합 (save/get)
├── Stage 4 라우트
│   ├── 파일럿 운영 (save/get)
│   ├── 변화 관리 (save/get)
│   └── 전사 확산 (save/get)
├── Stage 5 라우트
│   ├── 운영 모니터링 (save/get)
│   └── 개선 (save/get)
└── 헬퍼 함수들 (50+ 함수)
```

**분리 전략**:

1. **라우터 분리**:
   ```
   src/api/
   ├── __init__.py
   ├── routes.py                   # 메인 라우터 (간소화)
   ├── consulting_framework_routes.py  # 레거시 (점진적 제거)
   ├── stage1/
   │   ├── __init__.py
   │   ├── routes.py               # Stage 1 라우터
   │   ├── models.py                # Stage 1 Pydantic 모델
   │   ├── maturity.py              # 성숙도 진단 로직
   │   ├── opportunities.py         # 기회 발굴 로직
   │   └── roadmap.py               # 전략 로드맵 로직
   ├── stage2/
   │   ├── __init__.py
   │   ├── routes.py                # Stage 2 라우터
   │   ├── models.py                # Stage 2 Pydantic 모델
   │   ├── requirements.py          # 상세 요건 정의 로직
   │   ├── architecture.py          # 기술 아키텍처 로직
   │   └── governance.py            # 거버넌스 로직
   ├── stage3/
   │   ├── __init__.py
   │   ├── routes.py                # Stage 3 라우터
   │   ├── models.py                # Stage 3 Pydantic 모델
   │   ├── poc.py                   # PoC 수행 로직
   │   ├── platform.py              # 플랫폼 구축 로직
   │   └── integration.py           # 솔루션 통합 로직
   ├── stage4/
   │   ├── __init__.py
   │   ├── routes.py                # Stage 4 라우터
   │   ├── models.py                # Stage 4 Pydantic 모델
   │   ├── pilot.py                 # 파일럿 운영 로직
   │   ├── change_management.py     # 변화 관리 로직
   │   └── scale.py                 # 전사 확산 로직
   ├── stage5/
   │   ├── __init__.py
   │   ├── routes.py                # Stage 5 라우터
   │   ├── models.py                # Stage 5 Pydantic 모델
   │   ├── monitoring.py            # 운영 모니터링 로직
   │   └── improvement.py           # 개선 로직
   └── common/
       ├── __init__.py
       ├── models.py                # 공통 Pydantic 모델
       ├── helpers.py                # 공통 헬퍼 함수
       └── database.py              # 데이터베이스 유틸리티
   ```

2. **라우터 통합 예시**:
   ```python
   # src/api/routes.py
   from fastapi import APIRouter
   from .stage1.routes import router as stage1_router
   from .stage2.routes import router as stage2_router
   # ... 기타 stage 라우터

   router = APIRouter(prefix="/api/v1/framework", tags=["Consulting Framework"])
   router.include_router(stage1_router, prefix="/stage1", tags=["Stage 1"])
   router.include_router(stage2_router, prefix="/stage2", tags=["Stage 2"])
   # ... 기타 stage 라우터
   ```

3. **Stage별 라우터 예시**:
   ```python
   # src/api/stage1/routes.py
   from fastapi import APIRouter, HTTPException
   from .models import MaturityAssessmentInput, OpportunityInput, RoadmapInput
   from .maturity import save_maturity_assessment, get_maturity_assessment, analyze_maturity
   from .opportunities import save_opportunities, get_opportunities, analyze_opportunities
   from .roadmap import save_roadmap, get_roadmap, analyze_roadmap

   router = APIRouter()

   @router.post("/projects/{project_id}/maturity-assessment")
   async def save_maturity(project_id: str, assessment: MaturityAssessmentInput):
       return await save_maturity_assessment(project_id, assessment)

   # ... 기타 라우트
   ```

**구현 방법**:
- FastAPI의 `APIRouter`를 사용한 모듈화
- 각 Stage를 독립적인 패키지로 분리
- 공통 로직은 `common/` 디렉토리로 추출
- 점진적 마이그레이션 (레거시 코드 유지하면서 새 구조로 전환)

**예상 효과**:
- 모듈 로딩 시간: **50-60% 감소**
- 코드 탐색 시간: **80% 감소**
- 테스트 작성 용이성: **90% 향상**
- 유지보수성: **85% 향상**

---

#### 2.2.2 `src/agents/consulting_agents.py` (1,052줄) 분리 전략

**현재 구조**:
```
consulting_agents.py (1,052줄, 5개 클래스)
├── BaseConsultingAgent (기본 클래스)
├── StrategyAnalystAgent
├── UseCaseDesignerAgent
├── ROIAnalystAgent
├── RiskAssessorAgent
└── ReportGeneratorAgent
```

**분리 전략**:

1. **에이전트별 파일 분리**:
   ```
   src/agents/
   ├── __init__.py
   ├── base_agent.py               # BaseConsultingAgent (기존)
   ├── strategy_analyst.py         # StrategyAnalystAgent
   ├── usecase_designer.py         # UseCaseDesignerAgent
   ├── roi_analyst.py              # ROIAnalystAgent
   ├── risk_assessor.py            # RiskAssessorAgent
   ├── report_generator.py         # ReportGeneratorAgent
   └── agent_factory.py            # 에이전트 팩토리
   ```

2. **에이전트 팩토리 패턴**:
   ```python
   # src/agents/agent_factory.py
   from .strategy_analyst import StrategyAnalystAgent
   from .usecase_designer import UseCaseDesignerAgent
   from .roi_analyst import ROIAnalystAgent
   from .risk_assessor import RiskAssessorAgent
   from .report_generator import ReportGeneratorAgent

   class AgentFactory:
       @staticmethod
       def create_agent(agent_type: str, **kwargs):
           agents = {
               "strategy_analyst": StrategyAnalystAgent,
               "usecase_designer": UseCaseDesignerAgent,
               "roi_analyst": ROIAnalystAgent,
               "risk_assessor": RiskAssessorAgent,
               "report_generator": ReportGeneratorAgent,
           }
           agent_class = agents.get(agent_type)
           if not agent_class:
               raise ValueError(f"Unknown agent type: {agent_type}")
           return agent_class(**kwargs)
   ```

**예상 효과**:
- 코드 탐색 시간: **70% 감소**
- 유지보수성: **80% 향상**
- 테스트 용이성: **85% 향상**

---

#### 2.2.3 `src/models/schemas.py` (910줄) 분리 전략

**현재 구조**:
```
schemas.py (910줄)
├── Enum 클래스들 (IndustryType, CompanySize, 등)
├── 프로젝트 관련 모델
├── Stage별 모델들
└── ISO 표준 관련 모델들
```

**분리 전략**:

1. **도메인별 모델 분리**:
   ```
   src/models/
   ├── __init__.py
   ├── enums.py                    # 모든 Enum 클래스
   ├── project.py                  # 프로젝트 관련 모델
   ├── stage1.py                   # Stage 1 모델
   ├── stage2.py                   # Stage 2 모델
   ├── stage3.py                   # Stage 3 모델
   ├── stage4.py                   # Stage 4 모델
   ├── stage5.py                   # Stage 5 모델
   ├── iso24030.py                 # ISO 24030 모델
   ├── iso38500.py                 # ISO 38500 모델
   └── common.py                   # 공통 모델
   ```

**예상 효과**:
- 모델 탐색 시간: **75% 감소**
- 유지보수성: **80% 향상**

---

## 3. 성능 최적화 방법론

### 3.1 Frontend 최적화

#### 3.1.1 코드 분할 (Code Splitting)

**전략**:
- 라우트 기반 코드 분할: 각 Stage별로 별도 번들 생성
- 컴포넌트 기반 코드 분할: 큰 컴포넌트를 별도 번들로 분리
- 동적 import 사용: 필요한 시점에만 모듈 로드

**구현 예시**:
```javascript
// 동적 import 사용
const loadStage1 = async () => {
    const { Stage1Manager } = await import('./pages/stage1.js');
    return Stage1Manager;
};

// 라우터에서 사용
router.on('/stage1', async () => {
    const Stage1Manager = await loadStage1();
    Stage1Manager.init();
});
```

**예상 효과**:
- 초기 번들 크기: **60-70% 감소**
- 초기 로딩 시간: **50-60% 감소**

---

#### 3.1.2 Lazy Loading

**전략**:
- 이미지 Lazy Loading: 화면에 보이는 이미지만 로드
- 컴포넌트 Lazy Loading: 스크롤 시 컴포넌트 로드
- 데이터 Lazy Loading: 필요한 데이터만 요청

**구현 예시**:
```javascript
// Intersection Observer를 사용한 Lazy Loading
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            loadComponent(entry.target);
            observer.unobserve(entry.target);
        }
    });
});

document.querySelectorAll('.lazy-load').forEach(el => {
    observer.observe(el);
});
```

**예상 효과**:
- 초기 로딩 시간: **40-50% 감소**
- 메모리 사용량: **30-40% 감소**

---

#### 3.1.3 캐싱 전략

**전략**:
- 브라우저 캐싱: 정적 리소스는 브라우저 캐시 활용
- Service Worker: 오프라인 지원 및 캐싱
- API 응답 캐싱: 동일한 요청은 캐시에서 반환

**구현 예시**:
```javascript
// API 응답 캐싱
const apiCache = new Map();

async function fetchWithCache(url, options) {
    const cacheKey = `${url}:${JSON.stringify(options)}`;
    
    if (apiCache.has(cacheKey)) {
        const cached = apiCache.get(cacheKey);
        if (Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5분
            return cached.data;
        }
    }
    
    const response = await fetch(url, options);
    const data = await response.json();
    
    apiCache.set(cacheKey, {
        data,
        timestamp: Date.now()
    });
    
    return data;
}
```

**예상 효과**:
- API 호출 횟수: **50-60% 감소**
- 응답 시간: **70-80% 감소** (캐시 히트 시)

---

#### 3.1.4 번들 최적화

**전략**:
- Tree Shaking: 사용하지 않는 코드 제거
- Minification: 코드 압축
- Compression: Gzip/Brotli 압축

**구현 방법**:
- Webpack 또는 Vite 사용
- 프로덕션 빌드 시 자동 최적화

**예상 효과**:
- 번들 크기: **40-50% 감소**
- 전송 시간: **50-60% 감소**

---

### 3.2 Backend 최적화

#### 3.2.1 데이터베이스 최적화

**전략**:
- 인덱싱: 자주 조회하는 필드에 인덱스 추가
- 쿼리 최적화: N+1 문제 해결, JOIN 최적화
- 연결 풀링: 데이터베이스 연결 재사용

**구현 예시**:
```python
# SQLite 인덱스 추가
CREATE INDEX idx_project_id ON projects(project_id);
CREATE INDEX idx_created_at ON projects(created_at);

# 연결 풀링 (향후 PostgreSQL 전환 시)
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20
)
```

**예상 효과**:
- 쿼리 성능: **50-70% 향상**
- 동시 접속 처리: **200-300% 향상**

---

#### 3.2.2 API 응답 최적화

**전략**:
- 응답 압축: Gzip 압축
- 페이징: 대량 데이터는 페이징 처리
- 필드 선택: 필요한 필드만 반환

**구현 예시**:
```python
from fastapi.middleware.gzip import GZipMiddleware

app.add_middleware(GZipMiddleware, minimum_size=1000)

# 페이징 처리
@router.get("/projects")
async def get_projects(page: int = 1, page_size: int = 20):
    skip = (page - 1) * page_size
    projects = await db.projects.find().skip(skip).limit(page_size)
    return {
        "items": projects,
        "total": await db.projects.count(),
        "page": page,
        "page_size": page_size
    }
```

**예상 효과**:
- 응답 크기: **60-70% 감소** (압축 시)
- 응답 시간: **30-40% 감소**

---

#### 3.2.3 비동기 처리 최적화

**전략**:
- 비동기 작업 큐: 긴 작업은 백그라운드 처리
- 캐싱: 자주 사용하는 데이터 캐싱
- 배치 처리: 여러 요청을 배치로 처리

**구현 예시**:
```python
from celery import Celery

celery_app = Celery('100K-AXExpert')

@celery_app.task
def generate_report_async(project_id: str):
    # 긴 작업을 백그라운드에서 처리
    report = generate_report(project_id)
    return report

# API에서 사용
@router.post("/projects/{project_id}/reports")
async def create_report(project_id: str):
    task = generate_report_async.delay(project_id)
    return {"task_id": task.id, "status": "processing"}
```

**예상 효과**:
- API 응답 시간: **80-90% 감소** (비동기 작업 시)
- 사용자 경험: **대폭 향상**

---

#### 3.2.4 메모리 최적화

**전략**:
- 지연 로딩: 필요한 시점에만 모듈 로드
- 메모리 캐싱: 자주 사용하는 데이터만 메모리에 보관
- 가비지 컬렉션 최적화: 불필요한 객체 제거

**구현 예시**:
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def get_project_config(project_id: str):
    # 자주 사용하는 설정은 캐싱
    return load_project_config(project_id)

# 사용 후 캐시 클리어
get_project_config.cache_clear()
```

**예상 효과**:
- 메모리 사용량: **30-40% 감소**
- 응답 시간: **20-30% 향상** (캐시 히트 시)

---

## 4. 구현 로드맵

### 4.1 Phase 1: Frontend 모듈화 (2-3주)

**목표**: `index.html` 및 JavaScript 파일 모듈화

**작업 내용**:
1. 템플릿 분리 (1주)
   - `base.html` 생성
   - Stage별 템플릿 분리
   - CSS 분리
2. JavaScript 모듈화 (1주)
   - 기존 모듈 구조 정리
   - 추가 모듈 분리
   - 모듈 로더 구현
3. 번들러 설정 (3일)
   - Webpack 또는 Vite 설정
   - 프로덕션 빌드 설정

**예상 효과**:
- 초기 로딩 시간: **60-70% 감소**
- 코드 유지보수성: **80% 향상**

---

### 4.2 Phase 2: Backend 모듈화 (3-4주)

**목표**: API 라우트 및 에이전트 모듈화

**작업 내용**:
1. API 라우트 분리 (2주)
   - Stage별 라우터 생성
   - 모델 분리
   - 공통 로직 추출
2. 에이전트 분리 (1주)
   - 에이전트별 파일 분리
   - 팩토리 패턴 구현
3. 모델 분리 (3일)
   - 도메인별 모델 분리
   - Enum 분리

**예상 효과**:
- 모듈 로딩 시간: **50-60% 감소**
- 코드 탐색 시간: **80% 감소**

---

### 4.3 Phase 3: 성능 최적화 (2-3주)

**목표**: 성능 최적화 적용

**작업 내용**:
1. Frontend 최적화 (1주)
   - 코드 분할 적용
   - Lazy Loading 구현
   - 캐싱 전략 적용
2. Backend 최적화 (1주)
   - 데이터베이스 최적화
   - API 응답 최적화
   - 비동기 처리 구현
3. 모니터링 설정 (3일)
   - 성능 모니터링 도구 설정
   - 메트릭 수집

**예상 효과**:
- 전체 성능: **50-60% 향상**
- 사용자 경험: **대폭 향상**

---

## 5. 모니터링 및 측정

### 5.1 성능 메트릭

**Frontend 메트릭**:
- 초기 로딩 시간 (First Contentful Paint, FCP)
- 상호작용 가능 시간 (Time to Interactive, TTI)
- 번들 크기
- 메모리 사용량

**Backend 메트릭**:
- API 응답 시간
- 데이터베이스 쿼리 시간
- 메모리 사용량
- CPU 사용률

### 5.2 측정 도구

**Frontend**:
- Lighthouse: 성능 측정
- Chrome DevTools: 프로파일링
- Webpack Bundle Analyzer: 번들 분석

**Backend**:
- FastAPI의 내장 프로파일링
- Python의 `cProfile`: 성능 프로파일링
- 데이터베이스 쿼리 로깅

---

## 6. 주의사항 및 권고사항

### 6.1 주의사항

1. **점진적 마이그레이션**: 기존 코드를 한 번에 모두 변경하지 말고 점진적으로 마이그레이션
2. **하위 호환성**: 기존 API 엔드포인트는 유지하면서 새 구조로 전환
3. **테스트**: 각 모듈화 단계마다 충분한 테스트 수행
4. **문서화**: 모듈 구조 변경 시 문서 업데이트

### 6.2 권고사항

1. **코드 리뷰**: 모듈화 작업은 코드 리뷰를 통해 검증
2. **성능 테스트**: 각 단계마다 성능 테스트 수행
3. **사용자 피드백**: 변경 사항에 대한 사용자 피드백 수집
4. **지속적 개선**: 모니터링 결과를 바탕으로 지속적 개선

---

## 7. 결론

본 문서는 100K-AX Expert 프로젝트의 성능 최적화를 위한 모듈화 전략을 제시하였다. 주요 내용은 다음과 같다:

1. **대용량 파일 식별**: `index.html` (23,064줄), `consulting_framework_routes.py` (2,750줄) 등 대용량 파일 식별
2. **모듈화 전략**: Frontend 및 Backend 모듈화 전략 제시
3. **성능 최적화 방법론**: 코드 분할, Lazy Loading, 캐싱 등 최적화 방법 제시
4. **구현 로드맵**: 3단계로 나눈 구현 계획 제시

이러한 최적화를 통해 프로젝트의 성능, 유지보수성, 확장성을 크게 향상시킬 수 있을 것으로 예상된다.

---

**문서 끝**

**Copyright © 2025 WDLAB AI/ML/AX Group. All rights reserved.**

