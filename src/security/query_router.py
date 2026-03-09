"""
AI Consulting Platform - Query Router
질의 라우팅 및 하이브리드 LLM 처리
"""
from typing import Dict, List, Any, Optional, Tuple
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime
import asyncio
import hashlib

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.security.data_classifier import (
    DataClassifier, ClassificationResult, SensitivityLevel,
    get_data_classifier
)
from src.security.data_sanitizer import (
    DataSanitizer, ContextSeparator, SanitizedResult,
    get_data_sanitizer, get_context_separator
)


class RoutingDecision(str, Enum):
    """라우팅 결정"""
    LOCAL_ONLY = "local_only"           # Local LLM만 사용
    ONLINE_ALLOWED = "online_allowed"   # Online LLM 직접 사용 가능
    HYBRID = "hybrid"                   # 하이브리드 (익명화 후 Online + Local 결합)
    BLOCKED = "blocked"                 # 차단 (극비 정보 포함)


class QueryType(str, Enum):
    """질의 유형"""
    TECH_QUESTION = "tech_question"         # 기술 질문
    BEST_PRACTICE = "best_practice"         # Best Practice 조회
    TREND_INFO = "trend_info"               # 트렌드/최신 정보
    COMPARISON = "comparison"               # 비교 분석
    IMPLEMENTATION = "implementation"       # 구현 가이드
    BUSINESS_ANALYSIS = "business_analysis" # 비즈니스 분석
    CUSTOMER_SPECIFIC = "customer_specific" # 고객 특화 분석
    GENERAL = "general"                     # 일반


@dataclass
class RoutingResult:
    """라우팅 결과"""
    decision: RoutingDecision
    query_type: QueryType
    original_query: str
    processed_query: str
    local_context: Dict[str, Any] = field(default_factory=dict)
    online_query: Optional[str] = None
    sensitivity_level: SensitivityLevel = SensitivityLevel.PUBLIC
    reasoning: str = ""
    session_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "decision": self.decision.value,
            "query_type": self.query_type.value,
            "sensitivity_level": self.sensitivity_level.name,
            "can_use_online": self.decision in [RoutingDecision.ONLINE_ALLOWED, RoutingDecision.HYBRID],
            "requires_local": self.decision in [RoutingDecision.LOCAL_ONLY, RoutingDecision.HYBRID],
            "reasoning": self.reasoning,
            "session_id": self.session_id
        }


class QueryRouter:
    """질의 라우터 - Local/Online LLM 라우팅 결정"""

    # 온라인 허용 질의 패턴
    ONLINE_ALLOWED_PATTERNS = [
        # 기술 질문
        r'(?:최신|2024|2025|최근)\s*(?:트렌드|동향|기술)',
        r'(?:비교|차이점|장단점).*(?:프레임워크|라이브러리|플랫폼)',
        r'(?:추천|권장).*(?:도구|툴|솔루션|아키텍처)',
        r'(?:어떻게|방법).*(?:구현|구축|설정|배포)',
        r'(?:Best\s*Practice|모범\s*사례|성공\s*사례)',
        r'(?:벤치마크|성능\s*비교|테스트\s*결과)',

        # 기술 키워드
        r'(?:MLOps|DevOps|CI/CD|Kubernetes|Docker)',
        r'(?:AWS|GCP|Azure|클라우드)',
        r'(?:PyTorch|TensorFlow|LangChain|LlamaIndex)',
        r'(?:Feature\s*Store|Model\s*Registry|ML\s*Pipeline)',

        # 일반 정보
        r'(?:오픈소스|라이선스|가격|비용)\s*(?:정보|안내)',
        r'(?:규제|법규|컴플라이언스|GDPR|AI\s*Act)'
    ]

    # 로컬 전용 질의 패턴
    LOCAL_ONLY_PATTERNS = [
        r'(?:우리|당사|본사|자사)\s*(?:회사|기업|조직)',
        r'(?:고객|거래처|파트너)\s*(?:정보|데이터|목록)',
        r'(?:임직원|직원|인력)\s*(?:정보|현황|목록)',
        r'(?:매출|수익|재무|예산)\s*(?:정보|현황|분석)',
        r'(?:전략|계획|로드맵)\s*(?:수립|검토|분석)',
        r'(?:경쟁사|경쟁업체)\s*(?:분석|비교|정보)'
    ]

    def __init__(
        self,
        classifier: DataClassifier = None,
        sanitizer: DataSanitizer = None,
        separator: ContextSeparator = None
    ):
        self.classifier = classifier or get_data_classifier()
        self.sanitizer = sanitizer or get_data_sanitizer()
        self.separator = separator or get_context_separator()

        # 컴파일된 패턴
        import re
        self._online_patterns = [re.compile(p, re.IGNORECASE) for p in self.ONLINE_ALLOWED_PATTERNS]
        self._local_patterns = [re.compile(p, re.IGNORECASE) for p in self.LOCAL_ONLY_PATTERNS]

    def route(
        self,
        query: str,
        context: Dict[str, Any] = None,
        force_local: bool = False
    ) -> RoutingResult:
        """질의 라우팅 결정"""
        # 세션 ID 생성
        session_id = hashlib.md5(
            f"{query[:50]}{datetime.now().isoformat()}".encode()
        ).hexdigest()[:12]

        # 강제 로컬 모드
        if force_local:
            return RoutingResult(
                decision=RoutingDecision.LOCAL_ONLY,
                query_type=self._detect_query_type(query),
                original_query=query,
                processed_query=query,
                local_context=context or {},
                sensitivity_level=SensitivityLevel.CONFIDENTIAL,
                reasoning="강제 로컬 모드",
                session_id=session_id
            )

        # 민감도 분류
        classification = self.classifier.classify(query)

        # 질의 유형 판단
        query_type = self._detect_query_type(query)

        # 라우팅 결정
        decision, reasoning = self._make_decision(
            classification,
            query_type,
            query
        )

        # 결과 생성
        result = RoutingResult(
            decision=decision,
            query_type=query_type,
            original_query=query,
            processed_query=query,
            sensitivity_level=classification.overall_sensitivity,
            reasoning=reasoning,
            session_id=session_id
        )

        # 하이브리드 처리가 필요한 경우
        if decision == RoutingDecision.HYBRID:
            separated = self.separator.separate(query, context)
            result.online_query = separated["sanitized_query"]
            result.local_context = separated["local_context"]
            result.processed_query = separated["sanitized_query"]

        # 온라인 허용인 경우
        elif decision == RoutingDecision.ONLINE_ALLOWED:
            result.online_query = query
            result.local_context = context or {}

        # 로컬 전용인 경우
        else:
            result.local_context = context or {}

        return result

    def _detect_query_type(self, query: str) -> QueryType:
        """질의 유형 감지"""
        query_lower = query.lower()

        # 패턴 매칭으로 유형 판단
        if any(kw in query_lower for kw in ['최신', '트렌드', '동향', '2024', '2025']):
            return QueryType.TREND_INFO

        if any(kw in query_lower for kw in ['비교', '차이', '장단점', 'vs']):
            return QueryType.COMPARISON

        if any(kw in query_lower for kw in ['best practice', '모범 사례', '성공 사례']):
            return QueryType.BEST_PRACTICE

        if any(kw in query_lower for kw in ['어떻게', '방법', '구현', '구축', '설정']):
            return QueryType.IMPLEMENTATION

        if any(kw in query_lower for kw in ['우리', '당사', '고객사', '프로젝트']):
            return QueryType.CUSTOMER_SPECIFIC

        if any(kw in query_lower for kw in ['분석', '평가', '진단', 'roi', '효과']):
            return QueryType.BUSINESS_ANALYSIS

        if any(kw in query_lower for kw in ['기술', '프레임워크', '라이브러리', '아키텍처']):
            return QueryType.TECH_QUESTION

        return QueryType.GENERAL

    def _make_decision(
        self,
        classification: ClassificationResult,
        query_type: QueryType,
        query: str
    ) -> Tuple[RoutingDecision, str]:
        """라우팅 결정 생성"""
        sensitivity = classification.overall_sensitivity

        # Level 4 (극비) - 차단 또는 로컬 전용
        if sensitivity == SensitivityLevel.TOP_SECRET:
            return (
                RoutingDecision.LOCAL_ONLY,
                f"극비 정보 포함 (탐지된 민감 정보: {len(classification.detected_entities)}건)"
            )

        # Level 3 (기밀) - 로컬 전용
        if sensitivity == SensitivityLevel.CONFIDENTIAL:
            # 기술 질문이면 하이브리드 고려
            if query_type in [QueryType.TECH_QUESTION, QueryType.TREND_INFO,
                             QueryType.COMPARISON, QueryType.BEST_PRACTICE]:
                return (
                    RoutingDecision.HYBRID,
                    "기밀 정보 포함, 익명화 후 기술 질의 온라인 처리"
                )
            return (
                RoutingDecision.LOCAL_ONLY,
                "기밀 정보 포함, 로컬 전용 처리"
            )

        # Level 2 (내부용) - 익명화 후 온라인 가능
        if sensitivity == SensitivityLevel.INTERNAL:
            return (
                RoutingDecision.HYBRID,
                "내부 정보 포함, 익명화 후 온라인 처리"
            )

        # Level 1 (공개) - 온라인 허용
        # 추가 검증: 로컬 전용 패턴 체크
        for pattern in self._local_patterns:
            if pattern.search(query):
                return (
                    RoutingDecision.LOCAL_ONLY,
                    "고객 특화 질의, 로컬 처리 권장"
                )

        # 온라인 패턴 체크
        for pattern in self._online_patterns:
            if pattern.search(query):
                return (
                    RoutingDecision.ONLINE_ALLOWED,
                    "기술/트렌드 질의, 온라인 처리 허용"
                )

        # 기본값: 질의 유형에 따라 결정
        if query_type in [QueryType.TECH_QUESTION, QueryType.TREND_INFO,
                         QueryType.COMPARISON, QueryType.BEST_PRACTICE,
                         QueryType.IMPLEMENTATION]:
            return (
                RoutingDecision.ONLINE_ALLOWED,
                "기술 관련 질의, 온라인 처리 허용"
            )

        return (
            RoutingDecision.LOCAL_ONLY,
            "일반 질의, 로컬 처리"
        )

    def get_routing_summary(self, result: RoutingResult) -> Dict[str, Any]:
        """라우팅 결과 요약"""
        return {
            "session_id": result.session_id,
            "decision": result.decision.value,
            "query_type": result.query_type.value,
            "sensitivity": result.sensitivity_level.name,
            "reasoning": result.reasoning,
            "can_online": result.decision in [RoutingDecision.ONLINE_ALLOWED, RoutingDecision.HYBRID],
            "online_query_preview": result.online_query[:100] if result.online_query else None,
            "timestamp": result.timestamp.isoformat()
        }


# 싱글톤 인스턴스
_router: Optional[QueryRouter] = None


def get_query_router() -> QueryRouter:
    """QueryRouter 싱글톤 인스턴스"""
    global _router
    if _router is None:
        _router = QueryRouter()
    return _router
