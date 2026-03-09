"""
AI Consulting Platform - Audit Logger
보안 감사 로깅 및 모니터링 시스템
"""
import json
import hashlib
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
import asyncio
from collections import defaultdict

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings


class AuditEventType(str, Enum):
    """감사 이벤트 유형"""
    # 질의 관련
    QUERY_RECEIVED = "query_received"
    QUERY_CLASSIFIED = "query_classified"
    QUERY_SANITIZED = "query_sanitized"
    QUERY_ROUTED = "query_routed"

    # LLM 호출 관련
    LOCAL_LLM_CALL = "local_llm_call"
    ONLINE_LLM_CALL = "online_llm_call"
    LLM_RESPONSE = "llm_response"
    LLM_ERROR = "llm_error"

    # 보안 관련
    SENSITIVE_DATA_DETECTED = "sensitive_data_detected"
    DATA_BLOCKED = "data_blocked"
    POLICY_VIOLATION = "policy_violation"
    UNAUTHORIZED_ACCESS = "unauthorized_access"

    # 설정 관련
    CONFIG_CHANGED = "config_changed"
    API_KEY_ROTATED = "api_key_rotated"
    PROVIDER_ENABLED = "provider_enabled"
    PROVIDER_DISABLED = "provider_disabled"

    # 시스템 관련
    SYSTEM_START = "system_start"
    SYSTEM_STOP = "system_stop"
    ERROR = "error"


class SeverityLevel(str, Enum):
    """심각도 레벨"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class AuditEvent:
    """감사 이벤트"""
    event_type: AuditEventType
    severity: SeverityLevel
    message: str
    details: Dict[str, Any] = field(default_factory=dict)
    user_id: str = "system"
    session_id: str = ""
    ip_address: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    event_id: str = ""

    def __post_init__(self):
        if not self.event_id:
            self.event_id = hashlib.md5(
                f"{self.event_type.value}{self.timestamp.isoformat()}{self.message[:50]}".encode()
            ).hexdigest()[:16]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event_id": self.event_id,
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "message": self.message,
            "details": self.details,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "ip_address": self.ip_address,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SecurityAlert:
    """보안 알림"""
    alert_id: str
    event: AuditEvent
    alert_type: str
    description: str
    recommended_action: str
    acknowledged: bool = False
    acknowledged_by: str = ""
    acknowledged_at: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)


class AuditLogger:
    """감사 로거"""

    def __init__(self, log_dir: Path = None):
        self.log_dir = log_dir or (settings.DATA_DIR / "audit_logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self._events: List[AuditEvent] = []
        self._alerts: List[SecurityAlert] = []
        self._stats: Dict[str, Any] = defaultdict(int)

        # 이벤트 핸들러
        self._handlers: Dict[AuditEventType, List[callable]] = defaultdict(list)

        # 알림 규칙
        self._alert_rules: List[Dict[str, Any]] = self._init_alert_rules()

    def _init_alert_rules(self) -> List[Dict[str, Any]]:
        """기본 알림 규칙 초기화"""
        return [
            {
                "name": "sensitive_data_blocked",
                "event_types": [AuditEventType.DATA_BLOCKED, AuditEventType.POLICY_VIOLATION],
                "severity_threshold": SeverityLevel.WARNING,
                "alert_type": "SECURITY",
                "description": "민감 데이터 차단 또는 정책 위반 감지",
                "action": "데이터 내용 검토 및 보안 정책 확인 필요"
            },
            {
                "name": "online_llm_high_usage",
                "event_types": [AuditEventType.ONLINE_LLM_CALL],
                "threshold_count": 100,
                "threshold_period_hours": 1,
                "alert_type": "USAGE",
                "description": "온라인 LLM 사용량 급증",
                "action": "사용 패턴 검토 및 비용 확인"
            },
            {
                "name": "repeated_errors",
                "event_types": [AuditEventType.LLM_ERROR, AuditEventType.ERROR],
                "threshold_count": 5,
                "threshold_period_hours": 0.5,
                "alert_type": "SYSTEM",
                "description": "반복적인 오류 발생",
                "action": "시스템 상태 점검 필요"
            }
        ]

    def log(self, event: AuditEvent):
        """이벤트 로깅"""
        self._events.append(event)
        self._stats[event.event_type.value] += 1
        self._stats[f"severity_{event.severity.value}"] += 1

        # 파일 로깅
        self._write_to_file(event)

        # 핸들러 실행
        for handler in self._handlers.get(event.event_type, []):
            try:
                handler(event)
            except Exception as e:
                print(f"Handler error: {e}")

        # 알림 규칙 체크
        self._check_alert_rules(event)

    def _write_to_file(self, event: AuditEvent):
        """파일에 로그 기록"""
        date_str = event.timestamp.strftime("%Y-%m-%d")
        log_file = self.log_dir / f"audit_{date_str}.jsonl"

        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(event.to_dict(), ensure_ascii=False) + '\n')

    def _check_alert_rules(self, event: AuditEvent):
        """알림 규칙 체크"""
        for rule in self._alert_rules:
            if event.event_type in rule.get("event_types", []):
                # 심각도 체크
                if "severity_threshold" in rule:
                    severity_order = [s.value for s in SeverityLevel]
                    if severity_order.index(event.severity.value) >= \
                       severity_order.index(rule["severity_threshold"].value):
                        self._create_alert(event, rule)

                # 횟수 체크
                if "threshold_count" in rule:
                    period = timedelta(hours=rule.get("threshold_period_hours", 1))
                    recent_count = sum(
                        1 for e in self._events
                        if e.event_type in rule["event_types"]
                        and e.timestamp > datetime.now() - period
                    )
                    if recent_count >= rule["threshold_count"]:
                        self._create_alert(event, rule)

    def _create_alert(self, event: AuditEvent, rule: Dict[str, Any]):
        """알림 생성"""
        alert_id = hashlib.md5(
            f"{rule['name']}{event.event_id}".encode()
        ).hexdigest()[:12]

        # 중복 알림 체크 (최근 1시간 이내 동일 규칙)
        recent_alerts = [
            a for a in self._alerts
            if a.alert_type == rule["alert_type"]
            and a.created_at > datetime.now() - timedelta(hours=1)
        ]
        if len(recent_alerts) > 0:
            return  # 중복 알림 방지

        alert = SecurityAlert(
            alert_id=alert_id,
            event=event,
            alert_type=rule["alert_type"],
            description=rule["description"],
            recommended_action=rule["action"]
        )
        self._alerts.append(alert)

    def log_query_received(
        self,
        query: str,
        session_id: str,
        user_id: str = "user",
        ip_address: str = ""
    ):
        """질의 수신 로깅"""
        self.log(AuditEvent(
            event_type=AuditEventType.QUERY_RECEIVED,
            severity=SeverityLevel.INFO,
            message="Query received",
            details={
                "query_length": len(query),
                "query_hash": hashlib.md5(query.encode()).hexdigest()[:8]
            },
            user_id=user_id,
            session_id=session_id,
            ip_address=ip_address
        ))

    def log_classification(
        self,
        session_id: str,
        sensitivity_level: str,
        entity_count: int,
        can_send_online: bool
    ):
        """분류 결과 로깅"""
        severity = SeverityLevel.INFO
        if sensitivity_level in ["TOP_SECRET", "CONFIDENTIAL"]:
            severity = SeverityLevel.WARNING

        self.log(AuditEvent(
            event_type=AuditEventType.QUERY_CLASSIFIED,
            severity=severity,
            message=f"Query classified as {sensitivity_level}",
            details={
                "sensitivity_level": sensitivity_level,
                "entity_count": entity_count,
                "can_send_online": can_send_online
            },
            session_id=session_id
        ))

    def log_online_llm_call(
        self,
        session_id: str,
        provider: str,
        model: str,
        query_hash: str,
        sanitized: bool = True
    ):
        """온라인 LLM 호출 로깅"""
        self.log(AuditEvent(
            event_type=AuditEventType.ONLINE_LLM_CALL,
            severity=SeverityLevel.INFO,
            message=f"Online LLM call to {provider}",
            details={
                "provider": provider,
                "model": model,
                "query_hash": query_hash,
                "sanitized": sanitized
            },
            session_id=session_id
        ))

    def log_llm_response(
        self,
        session_id: str,
        provider: str,
        success: bool,
        latency_ms: float,
        tokens_used: int = 0
    ):
        """LLM 응답 로깅"""
        self.log(AuditEvent(
            event_type=AuditEventType.LLM_RESPONSE if success else AuditEventType.LLM_ERROR,
            severity=SeverityLevel.INFO if success else SeverityLevel.ERROR,
            message=f"LLM response from {provider}: {'success' if success else 'failed'}",
            details={
                "provider": provider,
                "success": success,
                "latency_ms": latency_ms,
                "tokens_used": tokens_used
            },
            session_id=session_id
        ))

    def log_sensitive_data_detected(
        self,
        session_id: str,
        entity_types: List[str],
        blocked: bool = False
    ):
        """민감 데이터 감지 로깅"""
        self.log(AuditEvent(
            event_type=AuditEventType.SENSITIVE_DATA_DETECTED,
            severity=SeverityLevel.WARNING,
            message="Sensitive data detected in query",
            details={
                "entity_types": entity_types,
                "blocked": blocked
            },
            session_id=session_id
        ))

        if blocked:
            self.log(AuditEvent(
                event_type=AuditEventType.DATA_BLOCKED,
                severity=SeverityLevel.WARNING,
                message="Data transmission blocked due to sensitive content",
                details={"entity_types": entity_types},
                session_id=session_id
            ))

    def log_config_change(
        self,
        user_id: str,
        change_type: str,
        old_value: Any,
        new_value: Any
    ):
        """설정 변경 로깅"""
        self.log(AuditEvent(
            event_type=AuditEventType.CONFIG_CHANGED,
            severity=SeverityLevel.WARNING,
            message=f"Configuration changed: {change_type}",
            details={
                "change_type": change_type,
                "old_value": str(old_value)[:100],
                "new_value": str(new_value)[:100]
            },
            user_id=user_id
        ))

    def get_events(
        self,
        event_types: List[AuditEventType] = None,
        severity: SeverityLevel = None,
        start_time: datetime = None,
        end_time: datetime = None,
        session_id: str = None,
        limit: int = 100
    ) -> List[AuditEvent]:
        """이벤트 조회"""
        filtered = self._events

        if event_types:
            filtered = [e for e in filtered if e.event_type in event_types]

        if severity:
            severity_order = [s.value for s in SeverityLevel]
            filtered = [
                e for e in filtered
                if severity_order.index(e.severity.value) >= severity_order.index(severity.value)
            ]

        if start_time:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        if session_id:
            filtered = [e for e in filtered if e.session_id == session_id]

        return sorted(filtered, key=lambda e: e.timestamp, reverse=True)[:limit]

    def get_alerts(
        self,
        acknowledged: bool = None,
        alert_type: str = None,
        limit: int = 50
    ) -> List[SecurityAlert]:
        """알림 조회"""
        filtered = self._alerts

        if acknowledged is not None:
            filtered = [a for a in filtered if a.acknowledged == acknowledged]

        if alert_type:
            filtered = [a for a in filtered if a.alert_type == alert_type]

        return sorted(filtered, key=lambda a: a.created_at, reverse=True)[:limit]

    def acknowledge_alert(self, alert_id: str, user_id: str) -> bool:
        """알림 확인 처리"""
        for alert in self._alerts:
            if alert.alert_id == alert_id:
                alert.acknowledged = True
                alert.acknowledged_by = user_id
                alert.acknowledged_at = datetime.now()
                return True
        return False

    def get_stats(
        self,
        period_hours: int = 24
    ) -> Dict[str, Any]:
        """통계 조회"""
        cutoff = datetime.now() - timedelta(hours=period_hours)
        recent_events = [e for e in self._events if e.timestamp > cutoff]

        # 이벤트 유형별 카운트
        event_counts = defaultdict(int)
        severity_counts = defaultdict(int)
        provider_counts = defaultdict(int)

        for event in recent_events:
            event_counts[event.event_type.value] += 1
            severity_counts[event.severity.value] += 1

            if event.event_type == AuditEventType.ONLINE_LLM_CALL:
                provider = event.details.get("provider", "unknown")
                provider_counts[provider] += 1

        return {
            "period_hours": period_hours,
            "total_events": len(recent_events),
            "events_by_type": dict(event_counts),
            "events_by_severity": dict(severity_counts),
            "online_calls_by_provider": dict(provider_counts),
            "unacknowledged_alerts": len([a for a in self._alerts if not a.acknowledged]),
            "timestamp": datetime.now().isoformat()
        }

    def get_daily_report(self, date: datetime = None) -> Dict[str, Any]:
        """일간 보고서 생성"""
        target_date = date or datetime.now()
        start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        events = [e for e in self._events if start <= e.timestamp < end]

        return {
            "date": start.strftime("%Y-%m-%d"),
            "summary": {
                "total_events": len(events),
                "total_queries": len([e for e in events if e.event_type == AuditEventType.QUERY_RECEIVED]),
                "online_llm_calls": len([e for e in events if e.event_type == AuditEventType.ONLINE_LLM_CALL]),
                "security_warnings": len([e for e in events if e.severity in [SeverityLevel.WARNING, SeverityLevel.ERROR]]),
                "blocked_transmissions": len([e for e in events if e.event_type == AuditEventType.DATA_BLOCKED])
            },
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "type": a.alert_type,
                    "description": a.description,
                    "acknowledged": a.acknowledged
                }
                for a in self._alerts
                if start <= a.created_at < end
            ],
            "generated_at": datetime.now().isoformat()
        }

    def get_weekly_report(self, start_date: datetime = None) -> Dict[str, Any]:
        """주간 보고서 생성"""
        if start_date is None:
            # 이번 주 월요일 찾기
            today = datetime.now()
            days_since_monday = today.weekday()
            start_date = today - timedelta(days=days_since_monday)
        
        start = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)

        events = [e for e in self._events if start <= e.timestamp < end]

        # 일별 통계
        daily_stats = defaultdict(lambda: {
            "total_events": 0,
            "total_queries": 0,
            "online_llm_calls": 0,
            "security_warnings": 0
        })

        for event in events:
            day_key = event.timestamp.strftime("%Y-%m-%d")
            daily_stats[day_key]["total_events"] += 1
            if event.event_type == AuditEventType.QUERY_RECEIVED:
                daily_stats[day_key]["total_queries"] += 1
            if event.event_type == AuditEventType.ONLINE_LLM_CALL:
                daily_stats[day_key]["online_llm_calls"] += 1
            if event.severity in [SeverityLevel.WARNING, SeverityLevel.ERROR]:
                daily_stats[day_key]["security_warnings"] += 1

        return {
            "period": {
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": (end - timedelta(days=1)).strftime("%Y-%m-%d")
            },
            "summary": {
                "total_events": len(events),
                "total_queries": len([e for e in events if e.event_type == AuditEventType.QUERY_RECEIVED]),
                "online_llm_calls": len([e for e in events if e.event_type == AuditEventType.ONLINE_LLM_CALL]),
                "security_warnings": len([e for e in events if e.severity in [SeverityLevel.WARNING, SeverityLevel.ERROR]]),
                "blocked_transmissions": len([e for e in events if e.event_type == AuditEventType.DATA_BLOCKED]),
                "average_daily_queries": round(len([e for e in events if e.event_type == AuditEventType.QUERY_RECEIVED]) / 7, 2)
            },
            "daily_breakdown": dict(daily_stats),
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "type": a.alert_type,
                    "description": a.description,
                    "acknowledged": a.acknowledged,
                    "created_at": a.created_at.strftime("%Y-%m-%d")
                }
                for a in self._alerts
                if start <= a.created_at < end
            ],
            "generated_at": datetime.now().isoformat()
        }

    def get_monthly_report(self, year: int = None, month: int = None) -> Dict[str, Any]:
        """월간 보고서 생성"""
        if year is None or month is None:
            today = datetime.now()
            year = today.year
            month = today.month

        start = datetime(year, month, 1)
        # 다음 달 첫 날
        if month == 12:
            end = datetime(year + 1, 1, 1)
        else:
            end = datetime(year, month + 1, 1)

        events = [e for e in self._events if start <= e.timestamp < end]

        # 주별 통계
        weekly_stats = defaultdict(lambda: {
            "total_events": 0,
            "total_queries": 0,
            "online_llm_calls": 0,
            "security_warnings": 0
        })

        for event in events:
            # 주 번호 계산 (월의 첫 주부터)
            week_num = ((event.timestamp.day - 1) // 7) + 1
            week_key = f"Week {week_num}"
            weekly_stats[week_key]["total_events"] += 1
            if event.event_type == AuditEventType.QUERY_RECEIVED:
                weekly_stats[week_key]["total_queries"] += 1
            if event.event_type == AuditEventType.ONLINE_LLM_CALL:
                weekly_stats[week_key]["online_llm_calls"] += 1
            if event.severity in [SeverityLevel.WARNING, SeverityLevel.ERROR]:
                weekly_stats[week_key]["security_warnings"] += 1

        return {
            "period": {
                "year": year,
                "month": month,
                "start_date": start.strftime("%Y-%m-%d"),
                "end_date": (end - timedelta(days=1)).strftime("%Y-%m-%d")
            },
            "summary": {
                "total_events": len(events),
                "total_queries": len([e for e in events if e.event_type == AuditEventType.QUERY_RECEIVED]),
                "online_llm_calls": len([e for e in events if e.event_type == AuditEventType.ONLINE_LLM_CALL]),
                "security_warnings": len([e for e in events if e.severity in [SeverityLevel.WARNING, SeverityLevel.ERROR]]),
                "blocked_transmissions": len([e for e in events if e.event_type == AuditEventType.DATA_BLOCKED]),
                "average_daily_queries": round(len([e for e in events if e.event_type == AuditEventType.QUERY_RECEIVED]) / (end - start).days, 2)
            },
            "weekly_breakdown": dict(weekly_stats),
            "alerts": [
                {
                    "alert_id": a.alert_id,
                    "type": a.alert_type,
                    "description": a.description,
                    "acknowledged": a.acknowledged,
                    "created_at": a.created_at.strftime("%Y-%m-%d")
                }
                for a in self._alerts
                if start <= a.created_at < end
            ],
            "generated_at": datetime.now().isoformat()
        }

    def on_event(self, event_type: AuditEventType, handler: callable):
        """이벤트 핸들러 등록"""
        self._handlers[event_type].append(handler)


# 싱글톤 인스턴스
_logger: Optional[AuditLogger] = None


def get_audit_logger() -> AuditLogger:
    """AuditLogger 싱글톤 인스턴스"""
    global _logger
    if _logger is None:
        _logger = AuditLogger()
    return _logger
