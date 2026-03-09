"""
AI Consulting Platform - Data Classifier
민감 정보 분류 및 탐지 시스템
"""
import re
from typing import List, Dict, Any, Tuple, Optional
from enum import IntEnum
from dataclasses import dataclass, field
from datetime import datetime
import hashlib

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')


class SensitivityLevel(IntEnum):
    """민감도 등급"""
    PUBLIC = 1       # Level 1: 공개 (Green) - Online 허용
    INTERNAL = 2     # Level 2: 내부용 (Yellow) - 익명화 후 Online 허용
    CONFIDENTIAL = 3 # Level 3: 기밀 (Orange) - Local Only
    TOP_SECRET = 4   # Level 4: 극비 (Red) - Local Only, 절대 외부 전송 X


@dataclass
class DetectedEntity:
    """탐지된 엔티티"""
    text: str
    entity_type: str
    sensitivity_level: SensitivityLevel
    start_pos: int
    end_pos: int
    confidence: float = 1.0
    replacement: Optional[str] = None


@dataclass
class ClassificationResult:
    """분류 결과"""
    original_text: str
    overall_sensitivity: SensitivityLevel
    detected_entities: List[DetectedEntity] = field(default_factory=list)
    can_send_online: bool = False
    requires_sanitization: bool = False
    classification_time: datetime = field(default_factory=datetime.now)
    classification_id: str = ""

    def __post_init__(self):
        if not self.classification_id:
            self.classification_id = hashlib.md5(
                f"{self.original_text[:100]}{self.classification_time.isoformat()}".encode()
            ).hexdigest()[:12]


class DataClassifier:
    """데이터 민감도 분류기"""

    # 민감 정보 패턴 정의
    SENSITIVE_PATTERNS = {
        # Level 4 (극비) - 절대 외부 전송 금지
        "resident_id": {
            "pattern": r'\d{6}[-\s]?[1-4]\d{6}',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "RESIDENT_ID",
            "description": "주민등록번호"
        },
        "credit_card": {
            "pattern": r'\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "CREDIT_CARD",
            "description": "신용카드번호"
        },
        "bank_account": {
            "pattern": r'\d{3,4}[-\s]?\d{2,4}[-\s]?\d{4,6}',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "BANK_ACCOUNT",
            "description": "계좌번호"
        },
        "password": {
            "pattern": r'(?:비밀번호|password|pwd|passwd)[\s:=]+\S+',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "PASSWORD",
            "description": "비밀번호"
        },
        "api_key": {
            "pattern": r'(?:api[_\-]?key|secret[_\-]?key|access[_\-]?token)[\s:=]+[\w\-]+',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "API_KEY",
            "description": "API 키"
        },
        "ip_address_internal": {
            "pattern": r'(?:192\.168|10\.\d{1,3}|172\.(?:1[6-9]|2\d|3[01]))\.\d{1,3}\.\d{1,3}',
            "level": SensitivityLevel.TOP_SECRET,
            "type": "INTERNAL_IP",
            "description": "내부 IP 주소"
        },

        # Level 3 (기밀) - Local Only
        "company_name_kr": {
            "pattern": r'(?:주식회사|㈜|\(주\))\s*[\w가-힣]+|[\w가-힣]+(?:주식회사|㈜|\(주\))',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "COMPANY_NAME",
            "description": "회사명 (한글)"
        },
        "company_name_en": {
            "pattern": r'[\w\s]+(?:Inc\.|Corp\.|Ltd\.|LLC|Co\.,?\s*Ltd\.)',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "COMPANY_NAME",
            "description": "회사명 (영문)"
        },
        "business_registration": {
            "pattern": r'\d{3}[-\s]?\d{2}[-\s]?\d{5}',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "BUSINESS_REG",
            "description": "사업자등록번호"
        },
        "email": {
            "pattern": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "EMAIL",
            "description": "이메일 주소"
        },
        "phone_number": {
            "pattern": r'(?:02|0\d{2})[-\s]?\d{3,4}[-\s]?\d{4}',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "PHONE",
            "description": "전화번호"
        },
        "mobile_number": {
            "pattern": r'01[0-9][-\s]?\d{3,4}[-\s]?\d{4}',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "MOBILE",
            "description": "휴대폰번호"
        },
        "person_name_title": {
            "pattern": r'[\w가-힣]{2,4}\s*(?:대표이사|대표|사장|부사장|전무|상무|이사|부장|차장|과장|대리|사원|팀장|실장|본부장|센터장|CEO|CTO|CFO|COO|CMO)',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "PERSON_NAME",
            "description": "인명 (직함 포함)"
        },
        "specific_amount_large": {
            "pattern": r'\d{1,3}(?:,\d{3})*(?:\.\d+)?\s*(?:억|조)\s*(?:원|달러|불)?',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "FINANCIAL_AMOUNT",
            "description": "금액 (억/조 단위)"
        },
        "address_detail": {
            "pattern": r'(?:서울|부산|대구|인천|광주|대전|울산|세종|경기|강원|충북|충남|전북|전남|경북|경남|제주)(?:특별시|광역시|특별자치시|도|특별자치도)?\s*[\w가-힣]+(?:구|시|군)\s*[\w가-힣]+(?:동|읍|면|로|길)\s*[\d\-]+',
            "level": SensitivityLevel.CONFIDENTIAL,
            "type": "ADDRESS",
            "description": "상세 주소"
        },

        # Level 2 (내부용) - 익명화 후 Online 허용
        "employee_count": {
            "pattern": r'(?:직원|인원|인력)\s*(?:수|규모)?\s*[:：]?\s*\d+\s*명',
            "level": SensitivityLevel.INTERNAL,
            "type": "EMPLOYEE_COUNT",
            "description": "직원 수"
        },
        "revenue_general": {
            "pattern": r'(?:매출|매출액|수익|영업이익|순이익)\s*[:：]?\s*\d+(?:,\d+)*\s*(?:만원|백만원)?',
            "level": SensitivityLevel.INTERNAL,
            "type": "REVENUE",
            "description": "매출 정보"
        },
        "project_name": {
            "pattern": r'(?:프로젝트|사업|과제)\s*(?:명|이름)?\s*[:：]?\s*["\']?[\w가-힣\s]+["\']?',
            "level": SensitivityLevel.INTERNAL,
            "type": "PROJECT_NAME",
            "description": "프로젝트명"
        },
        "department_name": {
            "pattern": r'[\w가-힣]+(?:부|팀|실|본부|센터|그룹)',
            "level": SensitivityLevel.INTERNAL,
            "type": "DEPARTMENT",
            "description": "부서명"
        }
    }

    # 고위험 키워드
    HIGH_RISK_KEYWORDS = [
        "대표이사", "CEO", "비밀", "기밀", "대외비", "내부용",
        "영업비밀", "특허", "경쟁사", "인수합병", "M&A",
        "주주", "지분", "투자자", "계약서", "MOU", "NDA"
    ]

    # 기술 질의 키워드 (Online 허용 가능 신호)
    TECH_QUERY_KEYWORDS = [
        "최신", "트렌드", "비교", "추천", "방법", "가이드",
        "아키텍처", "프레임워크", "라이브러리", "오픈소스",
        "MLOps", "DevOps", "클라우드", "AWS", "GCP", "Azure",
        "벤치마크", "성능", "Best Practice", "사례"
    ]

    def __init__(self, custom_patterns: Dict[str, Any] = None):
        self.patterns = self.SENSITIVE_PATTERNS.copy()
        if custom_patterns:
            self.patterns.update(custom_patterns)

        # 컴파일된 패턴 캐시
        self._compiled_patterns = {
            name: re.compile(info["pattern"], re.IGNORECASE)
            for name, info in self.patterns.items()
        }

    def classify(self, text: str) -> ClassificationResult:
        """텍스트 민감도 분류"""
        detected_entities = []
        max_sensitivity = SensitivityLevel.PUBLIC

        # 패턴 기반 탐지
        for pattern_name, pattern_info in self.patterns.items():
            compiled = self._compiled_patterns[pattern_name]
            for match in compiled.finditer(text):
                entity = DetectedEntity(
                    text=match.group(),
                    entity_type=pattern_info["type"],
                    sensitivity_level=pattern_info["level"],
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9
                )
                detected_entities.append(entity)

                if entity.sensitivity_level > max_sensitivity:
                    max_sensitivity = entity.sensitivity_level

        # 고위험 키워드 체크
        for keyword in self.HIGH_RISK_KEYWORDS:
            if keyword in text:
                # 고위험 키워드가 있으면 최소 CONFIDENTIAL
                if max_sensitivity < SensitivityLevel.CONFIDENTIAL:
                    max_sensitivity = SensitivityLevel.CONFIDENTIAL

        # Online 전송 가능 여부 판단
        can_send_online = max_sensitivity <= SensitivityLevel.PUBLIC
        requires_sanitization = max_sensitivity == SensitivityLevel.INTERNAL

        # 기술 질의 키워드가 있고 민감도가 INTERNAL 이하면 익명화 후 전송 가능
        has_tech_keywords = any(kw in text for kw in self.TECH_QUERY_KEYWORDS)
        if has_tech_keywords and max_sensitivity <= SensitivityLevel.INTERNAL:
            requires_sanitization = True
            can_send_online = True

        return ClassificationResult(
            original_text=text,
            overall_sensitivity=max_sensitivity,
            detected_entities=detected_entities,
            can_send_online=can_send_online or requires_sanitization,
            requires_sanitization=requires_sanitization
        )

    def get_sensitivity_summary(self, result: ClassificationResult) -> Dict[str, Any]:
        """분류 결과 요약"""
        entity_summary = {}
        for entity in result.detected_entities:
            if entity.entity_type not in entity_summary:
                entity_summary[entity.entity_type] = []
            entity_summary[entity.entity_type].append({
                "text": entity.text[:20] + "..." if len(entity.text) > 20 else entity.text,
                "level": entity.sensitivity_level.name,
                "position": f"{entity.start_pos}-{entity.end_pos}"
            })

        return {
            "classification_id": result.classification_id,
            "overall_level": result.overall_sensitivity.name,
            "overall_level_value": result.overall_sensitivity.value,
            "can_send_online": result.can_send_online,
            "requires_sanitization": result.requires_sanitization,
            "entity_count": len(result.detected_entities),
            "entities_by_type": entity_summary,
            "classification_time": result.classification_time.isoformat()
        }


# 싱글톤 인스턴스
_classifier: Optional[DataClassifier] = None


def get_data_classifier() -> DataClassifier:
    """DataClassifier 싱글톤 인스턴스"""
    global _classifier
    if _classifier is None:
        _classifier = DataClassifier()
    return _classifier
