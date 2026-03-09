"""
100K-AX Expert Platform - Main Application
AI/AX 10만 전문인력 양성 플랫폼

기능:
- Ollama 기반 Local LLM 연동
- 5단계 AI 컨설팅 프레임워크
- 멀티 에이전트 협업 시스템 (7개 프레임워크)
- AX 기회 발굴 (AX Discovery Module)
- AX 전문가 양성 추적 & 인증 (5등급 체계)
- 산업 도메인 Knowledge Base (7개 도메인)
- 시나리오 분석 및 ROI 평가
- 인간-AI 협업 인터페이스
- 컨설팅 보고서 자동 생성
"""
import asyncio
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings
from src.api.routes import router as api_router
from src.api.security_routes import router as security_router
from src.api.consulting_framework_routes import router as framework_router
from src.api.multi_agent_routes import router as multi_agent_router
from src.api.advanced_framework_routes import router as advanced_framework_router
from src.api.ax_training_routes import router as ax_training_router
from src.api.ax_discovery_routes import router as ax_discovery_router
from src.security.audit_logger import AuditEventType, SeverityLevel, AuditEvent, get_audit_logger


# FastAPI 앱 생성
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
    ## 100K-AX Expert Platform
    ### AI/AX 10만 전문인력 양성 플랫폼

    대한민국 산업 현장 실무자를 AI/AX 전문가로 양성하는 멀티 에이전트 기반 플랫폼입니다.

    ### 핵심 기능
    * **AX 기회 발굴**: 업무 프로세스 분석 → AX 기회 자동 식별
    * **멀티 에이전트 AI 컨설팅**: 6개 전문 에이전트 협업 분석
    * **AI 성숙도 진단**: 4대 영역 (전략, 조직, 데이터/기술, 프로세스)
    * **ROI/리스크 분석**: NPV, IRR, FMEA 자동 분석
    * **전문가 양성 추적**: 5등급 인증 체계 (Beginner → Master)
    * **도메인 KB**: 7개 산업 도메인 Knowledge Base
    * **보고서 자동 생성**: DOCX/PDF/PPTX 컨설팅 보고서

    ### AI 에이전트
    * Strategy Analyst: 전략 분석 및 성숙도 진단
    * Use Case Designer: Use Case 설계 및 아키텍처 정의
    * ROI Analyst: 투자 효과 분석 (NPV, IRR, Payback)
    * Risk Assessor: 리스크 평가 및 완화 전략
    * Report Generator: 보고서 생성

    ### 정책 연계
    * 이재명 정부 AI/AX 인력 양성 정책 (AI 예산 10.1조원)
    * AI 3대 강국 도약, 'AI 한글화' 전략
    * 10만명 5년 양성 목표 (10,000기업 × 10명/기업)
    """,
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 및 템플릿 설정
BASE_DIR = Path(__file__).resolve().parent
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# API 라우터 등록
app.include_router(api_router)
app.include_router(security_router)
app.include_router(framework_router)
app.include_router(multi_agent_router)
app.include_router(advanced_framework_router)
app.include_router(ax_training_router)
app.include_router(ax_discovery_router)


# 소스맵 파일 요청 처리 미들웨어 (브라우저 확장 프로그램용)
@app.middleware("http")
async def handle_sourcemap_middleware(request: Request, call_next):
    """브라우저 확장 프로그램이 요청하는 소스맵 파일에 대해 빈 응답 반환"""
    path = str(request.url.path)
    
    # 소스맵 파일 요청인 경우 조용히 처리
    if (path.endswith('.map') or 
        '<anonymous' in path or 
        '%3Canonymous' in path or
        'installHook' in path or
        path.endswith('installHook.js.map')):
        return JSONResponse(content={}, status_code=200)
    
    # 다른 요청은 정상 처리
    response = await call_next(request)
    return response

# 소스맵 파일 요청 처리 (명시적 라우트)
@app.get("/{path:path}.map")
async def handle_sourcemap(path: str):
    """브라우저 확장 프로그램이 요청하는 소스맵 파일에 대해 빈 응답 반환"""
    return JSONResponse(content={}, status_code=200)


# 메인 페이지
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """메인 대시보드 페이지"""
    return templates.TemplateResponse("index.html", {"request": request})


# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("=" * 60)
    print(f"  {settings.APP_NAME}")
    print(f"  Version: {settings.APP_VERSION}")
    print("=" * 60)
    print(f"  Ollama URL: {settings.OLLAMA_BASE_URL}")
    print(f"  Model: {settings.OLLAMA_MODEL}")
    print("=" * 60)

    # 데이터 디렉토리 생성
    settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
    settings.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    (settings.DATA_DIR / "audit_logs").mkdir(parents=True, exist_ok=True)
    (settings.DATA_DIR / "training").mkdir(parents=True, exist_ok=True)

    # 시스템 시작 감사 로깅
    logger = get_audit_logger()
    logger.log(AuditEvent(
        event_type=AuditEventType.SYSTEM_START,
        severity=SeverityLevel.INFO,
        message="100K-AX Expert Platform started",
        details={"version": settings.APP_VERSION}
    ))

    print("  [OK] Data directories created")
    print("  [OK] Audit logging initialized")
    print("  [OK] Security module loaded")
    print("  [OK] AX Discovery module loaded")
    print("  [OK] AX Training module loaded")
    print("  [OK] Domain KB loaded (7 domains)")
    print("  [OK] Platform ready!")
    print("=" * 60)


# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    # 시스템 종료 감사 로깅
    logger = get_audit_logger()
    logger.log(AuditEvent(
        event_type=AuditEventType.SYSTEM_STOP,
        severity=SeverityLevel.INFO,
        message="100K-AX Expert Platform stopped",
        details={}
    ))
    print("Shutting down 100K-AX Expert Platform...")


# CLI 실행
def run_server(host: str = "0.0.0.0", port: int = 8001, reload: bool = True):
    """서버 실행"""
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="100K-AX Expert Platform")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind")
    parser.add_argument("--no-reload", action="store_true", help="Disable auto-reload")

    args = parser.parse_args()

    run_server(
        host=args.host,
        port=args.port,
        reload=not args.no_reload
    )
