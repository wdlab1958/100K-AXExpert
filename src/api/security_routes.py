"""
AI Consulting Platform - Security API Routes
보안 설정 및 하이브리드 LLM 관련 API
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.security.data_classifier import (
    DataClassifier, SensitivityLevel, get_data_classifier
)
from src.security.data_sanitizer import (
    DataSanitizer, get_data_sanitizer, get_context_separator
)
from src.security.query_router import (
    QueryRouter, RoutingDecision, get_query_router
)
from src.security.online_llm_provider import (
    OnlineLLMProvider, LLMConfig, get_online_llm_manager
)
from src.security.audit_logger import (
    AuditEventType, SeverityLevel as AuditSeverity,
    AuditEvent, get_audit_logger
)
from src.security.query_templates import (
    TemplateCategory, SecurityLevel as TemplateSecurityLevel,
    get_template_manager
)


router = APIRouter(prefix="/api/security", tags=["Security"])


# ===========================================
# Request/Response Models
# ===========================================

class ClassifyRequest(BaseModel):
    text: str = Field(..., description="분류할 텍스트")


class ClassifyResponse(BaseModel):
    classification_id: str
    overall_level: str
    overall_level_value: int
    can_send_online: bool
    requires_sanitization: bool
    entity_count: int
    entities_by_type: Dict[str, List[Dict[str, Any]]]


class SanitizeRequest(BaseModel):
    text: str = Field(..., description="익명화할 텍스트")
    session_id: Optional[str] = None


class SanitizeResponse(BaseModel):
    session_id: str
    original_length: int
    sanitized_text: str
    sanitized_length: int
    mapping_count: int
    context_data: Dict[str, Any]


class RouteRequest(BaseModel):
    query: str = Field(..., description="라우팅할 질의")
    context: Optional[Dict[str, Any]] = None
    force_local: bool = False


class RouteResponse(BaseModel):
    session_id: str
    decision: str
    query_type: str
    sensitivity_level: str
    can_use_online: bool
    requires_local: bool
    reasoning: str
    online_query: Optional[str] = None


class OnlineLLMConfigRequest(BaseModel):
    provider: str
    api_key: str
    model: Optional[str] = None
    enabled: bool = True
    priority: int = 1
    max_tokens: int = 4000
    temperature: float = 0.7


class OnlineLLMQueryRequest(BaseModel):
    query: str
    provider: Optional[str] = None
    max_tokens: int = 2000
    temperature: float = 0.7
    system_prompt: Optional[str] = None


class AuditLogRequest(BaseModel):
    event_types: Optional[List[str]] = None
    severity: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    session_id: Optional[str] = None
    limit: int = 100


class TemplateRenderRequest(BaseModel):
    template_id: str
    values: Dict[str, Any]


# ===========================================
# Data Classification Endpoints
# ===========================================

@router.post("/classify", response_model=ClassifyResponse)
async def classify_data(request: ClassifyRequest):
    """텍스트 민감도 분류"""
    classifier = get_data_classifier()
    result = classifier.classify(request.text)
    summary = classifier.get_sensitivity_summary(result)

    # 감사 로깅
    logger = get_audit_logger()
    logger.log_classification(
        session_id=result.classification_id,
        sensitivity_level=result.overall_sensitivity.name,
        entity_count=len(result.detected_entities),
        can_send_online=result.can_send_online
    )

    return ClassifyResponse(**summary)


@router.get("/sensitivity-levels")
async def get_sensitivity_levels():
    """민감도 레벨 정보 조회"""
    return {
        "levels": [
            {
                "level": SensitivityLevel.PUBLIC.value,
                "name": "PUBLIC",
                "description": "공개 정보 - Online 전송 허용",
                "color": "green"
            },
            {
                "level": SensitivityLevel.INTERNAL.value,
                "name": "INTERNAL",
                "description": "내부용 - 익명화 후 Online 허용",
                "color": "yellow"
            },
            {
                "level": SensitivityLevel.CONFIDENTIAL.value,
                "name": "CONFIDENTIAL",
                "description": "기밀 - Local Only",
                "color": "orange"
            },
            {
                "level": SensitivityLevel.TOP_SECRET.value,
                "name": "TOP_SECRET",
                "description": "극비 - Local Only, 외부 전송 금지",
                "color": "red"
            }
        ]
    }


# ===========================================
# Data Sanitization Endpoints
# ===========================================

@router.post("/sanitize", response_model=SanitizeResponse)
async def sanitize_data(request: SanitizeRequest):
    """데이터 익명화 처리"""
    sanitizer = get_data_sanitizer()
    result = sanitizer.sanitize(request.text, request.session_id)

    # 감사 로깅
    logger = get_audit_logger()
    if result.mappings:
        logger.log_sensitive_data_detected(
            session_id=result.session_id,
            entity_types=[m.entity_type for m in result.mappings],
            blocked=False
        )

    return SanitizeResponse(
        session_id=result.session_id,
        original_length=len(result.original_text),
        sanitized_text=result.sanitized_text,
        sanitized_length=len(result.sanitized_text),
        mapping_count=len(result.mappings),
        context_data=result.context_data
    )


@router.post("/restore/{session_id}")
async def restore_data(session_id: str, sanitized_text: str):
    """익명화된 데이터 복원"""
    sanitizer = get_data_sanitizer()
    restored = sanitizer.restore(sanitized_text, session_id)

    if restored is None:
        raise HTTPException(
            status_code=404,
            detail="Session mapping not found"
        )

    return {"restored_text": restored}


@router.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """세션 매핑 삭제"""
    sanitizer = get_data_sanitizer()
    sanitizer.clear_session(session_id)
    return {"status": "cleared", "session_id": session_id}


# ===========================================
# Query Routing Endpoints
# ===========================================

@router.post("/route", response_model=RouteResponse)
async def route_query(request: RouteRequest):
    """질의 라우팅 결정"""
    router_instance = get_query_router()
    result = router_instance.route(
        request.query,
        request.context,
        request.force_local
    )

    # 감사 로깅
    logger = get_audit_logger()
    logger.log(AuditEvent(
        event_type=AuditEventType.QUERY_ROUTED,
        severity=AuditSeverity.INFO,
        message=f"Query routed: {result.decision.value}",
        details=result.to_dict(),
        session_id=result.session_id
    ))

    return RouteResponse(
        session_id=result.session_id,
        decision=result.decision.value,
        query_type=result.query_type.value,
        sensitivity_level=result.sensitivity_level.name,
        can_use_online=result.decision in [RoutingDecision.ONLINE_ALLOWED, RoutingDecision.HYBRID],
        requires_local=result.decision in [RoutingDecision.LOCAL_ONLY, RoutingDecision.HYBRID],
        reasoning=result.reasoning,
        online_query=result.online_query
    )


@router.get("/routing-decisions")
async def get_routing_decisions():
    """라우팅 결정 유형 조회"""
    return {
        "decisions": [
            {
                "value": RoutingDecision.LOCAL_ONLY.value,
                "description": "Local LLM만 사용",
                "use_online": False,
                "use_local": True
            },
            {
                "value": RoutingDecision.ONLINE_ALLOWED.value,
                "description": "Online LLM 직접 사용 가능",
                "use_online": True,
                "use_local": False
            },
            {
                "value": RoutingDecision.HYBRID.value,
                "description": "익명화 후 Online + Local 결합",
                "use_online": True,
                "use_local": True
            },
            {
                "value": RoutingDecision.BLOCKED.value,
                "description": "차단 (극비 정보 포함)",
                "use_online": False,
                "use_local": False
            }
        ]
    }


# ===========================================
# Online LLM Provider Endpoints
# ===========================================

def get_provider_description(provider: OnlineLLMProvider) -> str:
    """제공자 설명"""
    descriptions = {
        OnlineLLMProvider.CLAUDE: "Anthropic Claude - 고급 추론 및 안전성",
        OnlineLLMProvider.CHATGPT: "OpenAI GPT-4 - 범용 고성능 모델",
        OnlineLLMProvider.GEMINI: "Google Gemini - 멀티모달 지원",
        OnlineLLMProvider.COHERE: "Cohere - 엔터프라이즈 NLP 특화",
        OnlineLLMProvider.PERPLEXITY: "Perplexity - 실시간 검색 연동",
        OnlineLLMProvider.AZURE_OPENAI: "Azure OpenAI - 엔터프라이즈 보안"
    }
    return descriptions.get(provider, "")


def get_provider_models(provider: OnlineLLMProvider) -> List[str]:
    """제공자별 사용 가능한 모델 목록"""
    models_map = {
        OnlineLLMProvider.CLAUDE: [
            "claude-3-5-sonnet-20241022",
            "claude-3-5-haiku-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307"
        ],
        OnlineLLMProvider.CHATGPT: [
            "gpt-4-turbo-preview",
            "gpt-4",
            "gpt-4-32k",
            "gpt-3.5-turbo",
            "gpt-3.5-turbo-16k"
        ],
        OnlineLLMProvider.GEMINI: [
            "gemini-1.5-pro",
            "gemini-1.5-flash",
            "gemini-pro",
            "gemini-pro-vision"
        ],
        OnlineLLMProvider.COHERE: [
            "command-r-plus",
            "command-r",
            "command",
            "command-light"
        ],
        OnlineLLMProvider.PERPLEXITY: [
            "llama-3.1-sonar-large-128k-online",
            "llama-3.1-sonar-small-128k-online",
            "llama-3-sonar-large-128k-online",
            "llama-3-sonar-small-128k-online"
        ],
        OnlineLLMProvider.AZURE_OPENAI: [
            "gpt-4",
            "gpt-4-turbo",
            "gpt-35-turbo",
            "gpt-35-turbo-16k"
        ]
    }
    return models_map.get(provider, [])


# 더 구체적인 경로를 먼저 정의 (FastAPI 경로 매칭 순서)
@router.get("/providers/{provider_id}/models")
async def get_provider_models_endpoint(provider_id: str):
    """제공자별 사용 가능한 모델 목록 조회"""
    try:
        provider = OnlineLLMProvider(provider_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_id}"
        )
    
    models = get_provider_models(provider)
    return {
        "provider": provider_id,
        "models": models
    }


@router.get("/providers")
async def get_providers():
    """온라인 LLM 제공자 목록"""
    manager = get_online_llm_manager()
    return {
        "available_providers": [
            {
                "id": p.value,
                "name": p.name,
                "description": get_provider_description(p)
            }
            for p in OnlineLLMProvider
        ],
        "configured_providers": list(manager.get_available_providers())
    }


@router.post("/providers/configure")
async def configure_provider(config: OnlineLLMConfigRequest):
    """온라인 LLM 제공자 설정"""
    try:
        provider = OnlineLLMProvider(config.provider)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {config.provider}"
        )

    manager = get_online_llm_manager()
    llm_config = LLMConfig(
        provider=provider,
        api_key=config.api_key,
        model=config.model or "",
        enabled=config.enabled,
        max_tokens=config.max_tokens,
        temperature=config.temperature
    )
    manager.configure(llm_config)

    # 감사 로깅
    logger = get_audit_logger()
    logger.log(AuditEvent(
        event_type=AuditEventType.PROVIDER_ENABLED if config.enabled else AuditEventType.PROVIDER_DISABLED,
        severity=AuditSeverity.WARNING,
        message=f"Provider configured: {config.provider}",
        details={"provider": config.provider, "enabled": config.enabled}
    ))

    return {
        "status": "configured",
        "provider": config.provider,
        "enabled": config.enabled
    }


@router.delete("/providers/{provider_name}")
async def remove_provider(provider_name: str):
    """온라인 LLM 제공자 제거"""
    try:
        provider = OnlineLLMProvider(provider_name)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid provider: {provider_name}"
        )

    manager = get_online_llm_manager()
    # Remove from configs and clients
    if provider in manager.configs:
        del manager.configs[provider]
    if provider in manager.clients:
        del manager.clients[provider]
    if manager.default_provider == provider:
        manager.default_provider = None

    # 감사 로깅
    logger = get_audit_logger()
    logger.log(AuditEvent(
        event_type=AuditEventType.PROVIDER_DISABLED,
        severity=AuditSeverity.WARNING,
        message=f"Provider removed: {provider_name}",
        details={"provider": provider_name}
    ))

    return {"status": "removed", "provider": provider_name}


@router.post("/query/online")
async def query_online_llm(request: OnlineLLMQueryRequest):
    """온라인 LLM 질의 (보안 체크 포함)"""
    # 1. 라우팅 결정
    query_router = get_query_router()
    routing_result = query_router.route(request.query)

    # 2. 차단된 경우
    if routing_result.decision == RoutingDecision.BLOCKED:
        raise HTTPException(
            status_code=403,
            detail="Query contains top-secret information and cannot be sent online"
        )

    # 3. Local Only인 경우
    if routing_result.decision == RoutingDecision.LOCAL_ONLY:
        raise HTTPException(
            status_code=400,
            detail="Query requires local processing only. Use /api/consulting/query instead."
        )

    # 4. 온라인 질의 준비
    manager = get_online_llm_manager()

    # 제공자 선택
    provider = None
    if request.provider:
        try:
            provider = OnlineLLMProvider(request.provider)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid provider: {request.provider}"
            )

    # 5. 질의 실행 (Hybrid면 익명화된 쿼리 사용)
    query_to_send = routing_result.online_query or request.query

    # 감사 로깅 - 온라인 호출 시작
    logger = get_audit_logger()
    logger.log_online_llm_call(
        session_id=routing_result.session_id,
        provider=provider.value if provider else "auto",
        model="default",
        query_hash=routing_result.session_id[:8],
        sanitized=routing_result.decision == RoutingDecision.HYBRID
    )

    # 6. LLM 호출
    import time
    start_time = time.time()

    try:
        response = await manager.generate(
            prompt=query_to_send,
            system_prompt=request.system_prompt,
            provider=provider
        )

        latency_ms = (time.time() - start_time) * 1000

        # 감사 로깅 - 응답 기록
        total_tokens = 0
        if response.usage:
            total_tokens = response.usage.get("input_tokens", 0) + response.usage.get("output_tokens", 0)
        logger.log_llm_response(
            session_id=routing_result.session_id,
            provider=response.provider.value,
            success=response.success,
            latency_ms=latency_ms,
            tokens_used=total_tokens
        )

        return {
            "session_id": routing_result.session_id,
            "routing_decision": routing_result.decision.value,
            "provider": response.provider.value,
            "model": response.model,
            "response": response.content,
            "latency_ms": latency_ms,
            "was_sanitized": routing_result.decision == RoutingDecision.HYBRID
        }

    except Exception as e:
        latency_ms = (time.time() - start_time) * 1000
        logger.log_llm_response(
            session_id=routing_result.session_id,
            provider=provider.value if provider else "unknown",
            success=False,
            latency_ms=latency_ms
        )
        raise HTTPException(
            status_code=500,
            detail=f"LLM query failed: {str(e)}"
        )


# ===========================================
# Audit Log Endpoints
# ===========================================

@router.get("/audit/logs")
async def get_audit_logs(
    event_type: Optional[str] = None,
    severity: Optional[str] = None,
    session_id: Optional[str] = None,
    limit: int = 100
):
    """감사 로그 조회"""
    logger = get_audit_logger()

    # 필터링
    event_types = None
    if event_type:
        try:
            event_types = [AuditEventType(event_type)]
        except ValueError:
            pass

    severity_level = None
    if severity:
        try:
            severity_level = AuditSeverity(severity)
        except ValueError:
            pass

    events = logger.get_events(
        event_types=event_types,
        severity=severity_level,
        session_id=session_id,
        limit=limit
    )

    return {
        "total": len(events),
        "events": [e.to_dict() for e in events]
    }


@router.get("/audit/stats")
async def get_audit_stats(period_hours: int = 24):
    """감사 통계 조회"""
    logger = get_audit_logger()
    return logger.get_stats(period_hours)


@router.get("/audit/daily-report")
async def get_daily_report(date: Optional[str] = None):
    """일간 감사 보고서"""
    logger = get_audit_logger()

    target_date = None
    if date:
        try:
            target_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    return logger.get_daily_report(target_date)


@router.get("/audit/weekly-report")
async def get_weekly_report(start_date: Optional[str] = None):
    """주간 감사 보고서"""
    logger = get_audit_logger()

    target_date = None
    if start_date:
        try:
            target_date = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid date format. Use YYYY-MM-DD"
            )

    return logger.get_weekly_report(target_date)


@router.get("/audit/monthly-report")
async def get_monthly_report(year: Optional[int] = None, month: Optional[int] = None):
    """월간 감사 보고서"""
    logger = get_audit_logger()

    target_date = None
    if year and month:
        try:
            target_date = datetime(year, month, 1)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid year or month"
            )

    return logger.get_monthly_report(target_date)


@router.get("/audit/alerts")
async def get_alerts(
    acknowledged: Optional[bool] = None,
    alert_type: Optional[str] = None,
    limit: int = 50
):
    """보안 알림 조회"""
    logger = get_audit_logger()
    alerts = logger.get_alerts(acknowledged, alert_type, limit)

    return {
        "total": len(alerts),
        "alerts": [
            {
                "alert_id": a.alert_id,
                "event_id": a.event.event_id,
                "alert_type": a.alert_type,
                "description": a.description,
                "recommended_action": a.recommended_action,
                "acknowledged": a.acknowledged,
                "acknowledged_by": a.acknowledged_by,
                "acknowledged_at": a.acknowledged_at.isoformat() if a.acknowledged_at else None,
                "created_at": a.created_at.isoformat()
            }
            for a in alerts
        ]
    }


@router.post("/audit/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(alert_id: str, user_id: str = "admin"):
    """알림 확인 처리"""
    logger = get_audit_logger()
    success = logger.acknowledge_alert(alert_id, user_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail="Alert not found"
        )

    return {"status": "acknowledged", "alert_id": alert_id}


@router.get("/audit/event-types")
async def get_event_types():
    """감사 이벤트 유형 목록"""
    return {
        "event_types": [
            {"value": e.value, "name": e.name}
            for e in AuditEventType
        ]
    }


# ===========================================
# Query Template Endpoints
# ===========================================

@router.get("/templates")
async def get_templates(
    category: Optional[str] = None,
    security_level: Optional[str] = None
):
    """질의 템플릿 목록 조회"""
    manager = get_template_manager()

    cat = None
    if category:
        try:
            cat = TemplateCategory(category)
        except ValueError:
            pass

    sec = None
    if security_level:
        try:
            sec = TemplateSecurityLevel(security_level)
        except ValueError:
            pass

    templates = manager.list_templates(category=cat, security_level=sec)

    return {
        "total": len(templates),
        "templates": [
            {
                "template_id": t.template_id,
                "name": t.name,
                "category": t.category.value,
                "security_level": t.security_level.value,
                "description": t.description,
                "variables": t.variables,
                "tags": t.tags,
                "online_providers": t.online_providers
            }
            for t in templates
        ]
    }


# 정적 경로를 /{template_id} 파라미터 경로보다 먼저 등록 (BUG-001 fix)
@router.get("/templates/search")
async def search_templates(keyword: str):
    """템플릿 검색"""
    manager = get_template_manager()
    templates = manager.search_templates(keyword)

    return {
        "keyword": keyword,
        "total": len(templates),
        "templates": [
            {
                "template_id": t.template_id,
                "name": t.name,
                "category": t.category.value,
                "description": t.description,
                "tags": t.tags
            }
            for t in templates
        ]
    }


@router.get("/templates/summary")
async def get_template_summary():
    """템플릿 현황 요약"""
    manager = get_template_manager()
    return manager.get_template_summary()


@router.get("/templates/categories")
async def get_template_categories():
    """템플릿 카테고리 목록"""
    return {
        "categories": [
            {"value": c.value, "name": c.name}
            for c in TemplateCategory
        ]
    }


@router.post("/templates/render")
async def render_template(request: TemplateRenderRequest):
    """템플릿 렌더링"""
    manager = get_template_manager()

    try:
        rendered = manager.render_template(request.template_id, request.values)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    if rendered is None:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    return {
        "template_id": request.template_id,
        "rendered_query": rendered
    }


@router.get("/templates/{template_id}")
async def get_template(template_id: str):
    """템플릿 상세 조회"""
    manager = get_template_manager()
    template = manager.get_template(template_id)

    if not template:
        raise HTTPException(
            status_code=404,
            detail="Template not found"
        )

    return {
        "template_id": template.template_id,
        "name": template.name,
        "category": template.category.value,
        "security_level": template.security_level.value,
        "template_text": template.template_text,
        "description": template.description,
        "variables": template.variables,
        "example_values": template.example_values,
        "tags": template.tags,
        "online_providers": template.online_providers
    }


# ===========================================
# Monitoring Checklist Endpoints
# ===========================================

class MonitoringChecklistRequest(BaseModel):
    """모니터링 체크리스트 저장 요청"""
    checklist: Dict[str, bool] = Field(..., description="체크리스트 상태")


class SaveReportRequest(BaseModel):
    """보고서 저장 요청"""
    report_type: str = Field(..., description="보고서 유형 (daily, weekly, monthly)")
    report_data: Dict[str, Any] = Field(..., description="보고서 데이터")


@router.get("/monitoring/checklist")
async def get_monitoring_checklist():
    """모니터링 체크리스트 조회"""
    import json
    from pathlib import Path
    
    checklist_file = Path("data/monitoring_checklist.json")
    if checklist_file.exists():
        try:
            with open(checklist_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    "status": "success",
                    "checklist": data.get("checklist", {}),
                    "last_updated": data.get("last_updated")
                }
        except Exception as e:
            return {
                "status": "error",
                "message": str(e),
                "checklist": {}
            }
    
    # 기본값 반환
    return {
        "status": "success",
        "checklist": {
            "checkAuditLog": False,
            "checkAlerts": False,
            "checkProvider": False,
            "checkUsage": False,
            "checkPatterns": False
        },
        "last_updated": None
    }


@router.post("/monitoring/checklist")
async def save_monitoring_checklist(request: MonitoringChecklistRequest):
    """모니터링 체크리스트 저장"""
    import json
    from pathlib import Path
    
    checklist_file = Path("data/monitoring_checklist.json")
    checklist_file.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        data = {
            "checklist": request.checklist,
            "last_updated": datetime.now().isoformat()
        }
        
        with open(checklist_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # 감사 로깅
        logger = get_audit_logger()
        logger.log(AuditEvent(
            event_type=AuditEventType.CONFIG_CHANGED,
            severity=AuditSeverity.INFO,
            message="Monitoring checklist updated",
            details={"checklist": request.checklist}
        ))
        
        return {
            "status": "success",
            "message": "모니터링 체크리스트가 저장되었습니다.",
            "checklist": request.checklist,
            "last_updated": data["last_updated"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save checklist: {str(e)}"
        )


@router.post("/reports/save")
async def save_report(request: SaveReportRequest):
    """보고서 저장"""
    import json
    from pathlib import Path
    
    reports_dir = Path("reports")
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # 파일명 생성
        report_data = request.report_data
        if request.report_type == 'daily':
            filename = f"daily_report_{report_data.get('date', datetime.now().strftime('%Y-%m-%d'))}.json"
        elif request.report_type == 'weekly':
            period = report_data.get('period', {})
            filename = f"weekly_report_{period.get('start_date', datetime.now().strftime('%Y-%m-%d'))}.json"
        elif request.report_type == 'monthly':
            period = report_data.get('period', {})
            filename = f"monthly_report_{period.get('year', datetime.now().year)}_{period.get('month', datetime.now().month)}.json"
        else:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        report_file = reports_dir / filename
        
        # 보고서 데이터 저장
        save_data = {
            "report_type": request.report_type,
            "report_data": report_data,
            "saved_at": datetime.now().isoformat()
        }
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 감사 로깅
        logger = get_audit_logger()
        logger.log(AuditEvent(
            event_type=AuditEventType.CONFIG_CHANGED,
            severity=AuditSeverity.INFO,
            message=f"Report saved: {request.report_type}",
            details={"filename": filename, "report_type": request.report_type}
        ))
        
        return {
            "status": "success",
            "message": "보고서가 저장되었습니다.",
            "filename": filename,
            "saved_at": save_data["saved_at"]
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to save report: {str(e)}"
        )


@router.get("/reports/list")
async def list_reports(report_type: Optional[str] = None):
    """저장된 보고서 목록 조회"""
    import json
    from pathlib import Path
    
    reports_dir = Path("reports")
    if not reports_dir.exists():
        return {
            "status": "success",
            "reports": []
        }
    
    reports = []
    for report_file in reports_dir.glob("*.json"):
        try:
            with open(report_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if report_type is None or data.get("report_type") == report_type:
                    reports.append({
                        "filename": report_file.name,
                        "report_type": data.get("report_type"),
                        "saved_at": data.get("saved_at"),
                        "file_path": str(report_file)
                    })
        except Exception:
            continue
    
    # 최신순 정렬
    reports.sort(key=lambda x: x.get("saved_at", ""), reverse=True)
    
    return {
        "status": "success",
        "reports": reports
    }
