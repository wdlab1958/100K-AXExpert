"""
AI Consulting Platform - Data Sanitizer
데이터 익명화/비식별화 처리 시스템
"""
import re
import hashlib
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.security.data_classifier import (
    DataClassifier, ClassificationResult, DetectedEntity,
    SensitivityLevel, get_data_classifier
)


class SanitizationStrategy(str, Enum):
    """익명화 전략"""
    SUBSTITUTION = "substitution"      # 대체
    GENERALIZATION = "generalization"  # 일반화
    SUPPRESSION = "suppression"        # 억제 (제거)
    PERTURBATION = "perturbation"      # 노이즈 추가
    MASKING = "masking"                # 마스킹


@dataclass
class SanitizationMapping:
    """익명화 매핑 정보"""
    original: str
    sanitized: str
    entity_type: str
    strategy: SanitizationStrategy
    mapping_id: str = ""

    def __post_init__(self):
        if not self.mapping_id:
            self.mapping_id = hashlib.md5(
                f"{self.original}{self.entity_type}".encode()
            ).hexdigest()[:8]


@dataclass
class SanitizedResult:
    """익명화 결과"""
    original_text: str
    sanitized_text: str
    mappings: List[SanitizationMapping] = field(default_factory=list)
    context_data: Dict[str, Any] = field(default_factory=dict)
    sanitization_time: datetime = field(default_factory=datetime.now)
    session_id: str = ""

    def get_reverse_mapping(self) -> Dict[str, str]:
        """역매핑 (복원용)"""
        return {m.sanitized: m.original for m in self.mappings}


class DataSanitizer:
    """데이터 익명화 처리기"""

    # 엔티티 유형별 대체어 템플릿
    SUBSTITUTION_TEMPLATES = {
        "COMPANY_NAME": ["[기업 A]", "[기업 B]", "[기업 C]", "[고객사]", "[파트너사]"],
        "PERSON_NAME": ["[담당자]", "[관계자]", "[임원]", "[직원]"],
        "EMAIL": ["[이메일]", "example@domain.com"],
        "PHONE": ["[전화번호]", "000-0000-0000"],
        "MOBILE": ["[휴대폰]", "010-0000-0000"],
        "ADDRESS": ["[주소]", "[본사 소재지]"],
        "DEPARTMENT": ["[부서]", "[조직]"],
        "PROJECT_NAME": ["[프로젝트]", "[사업]"],
        "FINANCIAL_AMOUNT": ["[금액]", "[투자액]"],
        "EMPLOYEE_COUNT": ["[인원]", "[직원 수]"],
        "REVENUE": ["[매출]", "[수익]"],
        "RESIDENT_ID": "[주민번호]",
        "CREDIT_CARD": "[카드번호]",
        "BANK_ACCOUNT": "[계좌번호]",
        "PASSWORD": "[비밀번호]",
        "API_KEY": "[API키]",
        "INTERNAL_IP": "[내부IP]",
        "BUSINESS_REG": "[사업자번호]"
    }

    # 일반화 규칙
    GENERALIZATION_RULES = {
        "FINANCIAL_AMOUNT": {
            "ranges": [
                (0, 10, "10억 미만"),
                (10, 100, "10-100억"),
                (100, 1000, "100-1000억"),
                (1000, 10000, "1000억-1조"),
                (10000, float('inf'), "1조 이상")
            ]
        },
        "EMPLOYEE_COUNT": {
            "ranges": [
                (0, 50, "50명 미만 (소기업)"),
                (50, 300, "50-300명 (중소기업)"),
                (300, 1000, "300-1000명 (중견기업)"),
                (1000, float('inf'), "1000명 이상 (대기업)")
            ]
        }
    }

    def __init__(self, classifier: DataClassifier = None):
        self.classifier = classifier or get_data_classifier()
        self._entity_counters: Dict[str, int] = {}
        self._session_mappings: Dict[str, List[SanitizationMapping]] = {}

    def sanitize(
        self,
        text: str,
        session_id: str = None,
        strategy_overrides: Dict[str, SanitizationStrategy] = None
    ) -> SanitizedResult:
        """텍스트 익명화 처리"""
        # 세션 ID 생성
        if not session_id:
            session_id = hashlib.md5(
                f"{text[:50]}{datetime.now().isoformat()}".encode()
            ).hexdigest()[:12]

        # 분류 수행
        classification = self.classifier.classify(text)

        # 익명화가 필요 없으면 원본 반환
        if not classification.requires_sanitization and classification.can_send_online:
            return SanitizedResult(
                original_text=text,
                sanitized_text=text,
                session_id=session_id
            )

        # 엔티티를 위치 역순으로 정렬 (뒤에서부터 대체하여 위치 오류 방지)
        sorted_entities = sorted(
            classification.detected_entities,
            key=lambda e: e.start_pos,
            reverse=True
        )

        sanitized_text = text
        mappings = []

        for entity in sorted_entities:
            # 전략 결정
            strategy = self._determine_strategy(
                entity,
                strategy_overrides
            )

            # 대체 텍스트 생성
            replacement = self._generate_replacement(
                entity,
                strategy,
                session_id
            )

            # 텍스트 대체
            sanitized_text = (
                sanitized_text[:entity.start_pos] +
                replacement +
                sanitized_text[entity.end_pos:]
            )

            # 매핑 기록
            mappings.append(SanitizationMapping(
                original=entity.text,
                sanitized=replacement,
                entity_type=entity.entity_type,
                strategy=strategy
            ))

        # 세션 매핑 저장
        self._session_mappings[session_id] = mappings

        # 컨텍스트 데이터 추출
        context_data = self._extract_context(classification, mappings)

        return SanitizedResult(
            original_text=text,
            sanitized_text=sanitized_text,
            mappings=mappings,
            context_data=context_data,
            session_id=session_id
        )

    def _determine_strategy(
        self,
        entity: DetectedEntity,
        overrides: Dict[str, SanitizationStrategy] = None
    ) -> SanitizationStrategy:
        """엔티티에 대한 익명화 전략 결정"""
        # 오버라이드 확인
        if overrides and entity.entity_type in overrides:
            return overrides[entity.entity_type]

        # 민감도에 따른 기본 전략
        if entity.sensitivity_level == SensitivityLevel.TOP_SECRET:
            return SanitizationStrategy.SUPPRESSION

        if entity.sensitivity_level == SensitivityLevel.CONFIDENTIAL:
            return SanitizationStrategy.SUBSTITUTION

        if entity.entity_type in ["FINANCIAL_AMOUNT", "EMPLOYEE_COUNT", "REVENUE"]:
            return SanitizationStrategy.GENERALIZATION

        return SanitizationStrategy.SUBSTITUTION

    def _generate_replacement(
        self,
        entity: DetectedEntity,
        strategy: SanitizationStrategy,
        session_id: str
    ) -> str:
        """대체 텍스트 생성"""
        if strategy == SanitizationStrategy.SUPPRESSION:
            return "[REDACTED]"

        if strategy == SanitizationStrategy.MASKING:
            return self._mask_text(entity.text)

        if strategy == SanitizationStrategy.GENERALIZATION:
            return self._generalize_value(entity)

        if strategy == SanitizationStrategy.SUBSTITUTION:
            return self._substitute_entity(entity, session_id)

        if strategy == SanitizationStrategy.PERTURBATION:
            return self._perturb_value(entity)

        return "[UNKNOWN]"

    def _substitute_entity(self, entity: DetectedEntity, session_id: str) -> str:
        """엔티티 대체"""
        templates = self.SUBSTITUTION_TEMPLATES.get(entity.entity_type, ["[정보]"])

        if isinstance(templates, list):
            # 세션 내에서 일관된 대체어 사용
            key = f"{session_id}_{entity.entity_type}"
            if key not in self._entity_counters:
                self._entity_counters[key] = 0

            idx = self._entity_counters[key] % len(templates)
            self._entity_counters[key] += 1
            return templates[idx]

        return templates

    def _generalize_value(self, entity: DetectedEntity) -> str:
        """값 일반화"""
        rules = self.GENERALIZATION_RULES.get(entity.entity_type)
        if not rules:
            return "[범위]"

        # 숫자 추출
        numbers = re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', entity.text)
        if not numbers:
            return "[범위]"

        value = float(numbers[0].replace(',', ''))

        # 단위 변환 (억, 조)
        if '조' in entity.text:
            value *= 10000
        elif '억' not in entity.text and '만' in entity.text:
            value /= 10000

        # 범위 찾기
        for min_val, max_val, label in rules["ranges"]:
            if min_val <= value < max_val:
                return f"[{label}]"

        return "[범위]"

    def _mask_text(self, text: str) -> str:
        """텍스트 마스킹"""
        if len(text) <= 4:
            return "*" * len(text)
        return text[:2] + "*" * (len(text) - 4) + text[-2:]

    def _perturb_value(self, entity: DetectedEntity) -> str:
        """값에 노이즈 추가"""
        numbers = re.findall(r'\d+', entity.text)
        if not numbers:
            return entity.text

        import random
        num = int(numbers[0])
        # ±10% 범위 내에서 반올림
        perturbed = round(num * random.uniform(0.9, 1.1), -len(str(num)) + 2)
        return f"약 {int(perturbed):,}"

    def _extract_context(
        self,
        classification: ClassificationResult,
        mappings: List[SanitizationMapping]
    ) -> Dict[str, Any]:
        """컨텍스트 데이터 추출 (Local 보관용)"""
        context = {
            "entity_types_found": list(set(e.entity_type for e in classification.detected_entities)),
            "sensitivity_level": classification.overall_sensitivity.name,
            "mapping_count": len(mappings),
            "original_length": len(classification.original_text)
        }

        # 엔티티 유형별 카운트
        type_counts = {}
        for entity in classification.detected_entities:
            type_counts[entity.entity_type] = type_counts.get(entity.entity_type, 0) + 1
        context["entity_counts"] = type_counts

        return context

    def restore(self, sanitized_text: str, session_id: str) -> Optional[str]:
        """익명화된 텍스트 복원"""
        mappings = self._session_mappings.get(session_id)
        if not mappings:
            return None

        restored = sanitized_text
        for mapping in mappings:
            restored = restored.replace(mapping.sanitized, mapping.original)

        return restored

    def clear_session(self, session_id: str):
        """세션 매핑 삭제"""
        if session_id in self._session_mappings:
            del self._session_mappings[session_id]


class ContextSeparator:
    """컨텍스트 분리기 - 민감 정보와 기술 질의 분리"""

    def __init__(self, sanitizer: DataSanitizer = None):
        self.sanitizer = sanitizer or DataSanitizer()

    def separate(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """질의에서 민감 정보와 기술 질의 분리"""
        # 익명화 수행
        sanitized = self.sanitizer.sanitize(query)

        # 기술적 질의 추출
        tech_query = self._extract_tech_query(sanitized.sanitized_text)

        # 비즈니스 컨텍스트 추출
        business_context = self._extract_business_context(
            sanitized.sanitized_text,
            context
        )

        return {
            "original_query": query,
            "sanitized_query": sanitized.sanitized_text,
            "tech_query": tech_query,
            "business_context": business_context,
            "local_context": sanitized.context_data,
            "mappings": [
                {
                    "original": m.original,
                    "sanitized": m.sanitized,
                    "type": m.entity_type
                }
                for m in sanitized.mappings
            ],
            "session_id": sanitized.session_id
        }

    def _extract_tech_query(self, sanitized_text: str) -> str:
        """기술적 질의 추출"""
        # 기술 관련 키워드와 문장 추출
        tech_patterns = [
            r'(?:어떤|어떻게|무엇|추천|비교|차이|장단점|방법|가이드).*?(?:\?|$)',
            r'(?:MLOps|DevOps|AI|ML|딥러닝|머신러닝|클라우드|아키텍처).*?(?:\.|$)',
            r'(?:프레임워크|라이브러리|플랫폼|도구|툴|솔루션).*?(?:\.|$)'
        ]

        tech_sentences = []
        for pattern in tech_patterns:
            matches = re.findall(pattern, sanitized_text, re.IGNORECASE)
            tech_sentences.extend(matches)

        if tech_sentences:
            return ' '.join(tech_sentences)

        # 기술 키워드가 포함된 문장 반환
        return sanitized_text

    def _extract_business_context(
        self,
        sanitized_text: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """비즈니스 컨텍스트 추출"""
        business_context = context.copy() if context else {}

        # 산업 분류 추출
        industry_keywords = {
            "제조": "manufacturing",
            "금융": "finance",
            "의료": "healthcare",
            "유통": "retail",
            "물류": "logistics",
            "IT": "it_service"
        }

        for keyword, industry in industry_keywords.items():
            if keyword in sanitized_text:
                business_context["detected_industry"] = industry
                break

        # 규모 추출
        size_patterns = {
            r'대기업': "large",
            r'중견기업': "midsize",
            r'중소기업': "sme",
            r'스타트업': "startup"
        }

        for pattern, size in size_patterns.items():
            if re.search(pattern, sanitized_text):
                business_context["detected_size"] = size
                break

        return business_context


# 싱글톤 인스턴스
_sanitizer: Optional[DataSanitizer] = None
_separator: Optional[ContextSeparator] = None


def get_data_sanitizer() -> DataSanitizer:
    """DataSanitizer 싱글톤 인스턴스"""
    global _sanitizer
    if _sanitizer is None:
        _sanitizer = DataSanitizer()
    return _sanitizer


def get_context_separator() -> ContextSeparator:
    """ContextSeparator 싱글톤 인스턴스"""
    global _separator
    if _separator is None:
        _separator = ContextSeparator()
    return _separator
