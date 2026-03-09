"""
100K-AX Expert Platform - Domain Knowledge Base Manager
Phase 3: 산업별 도메인 지식 관리 및 LoRA 어댑터 관리
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

import logging
from typing import Optional

logger = logging.getLogger("domain_kb")


# ============================================================
# 산업별 Knowledge Base
# ============================================================
DOMAIN_KNOWLEDGE_BASE: dict[str, dict] = {
    "manufacturing": {
        "name": "제조업",
        "name_en": "Manufacturing",
        "regulations": ["ISO 9001", "IATF 16949", "HACCP", "ISO 14001", "ISO 45001"],
        "key_processes": [
            "생산 계획", "공정 관리", "품질 검사", "설비 보전",
            "자재 관리", "물류", "안전 관리"
        ],
        "ax_best_practices": [
            {"title": "AI 비전 검사", "description": "딥러닝 기반 외관 불량 자동 판별", "roi_range": "150~300%", "complexity": "medium"},
            {"title": "설비 예지보전", "description": "진동/온도 센서 데이터 기반 고장 예측", "roi_range": "100~250%", "complexity": "medium"},
            {"title": "공정 파라미터 최적화", "description": "강화학습 기반 최적 공정 조건 탐색", "roi_range": "200~500%", "complexity": "high"},
            {"title": "수요 예측", "description": "시계열 분석 기반 생산 수요 예측", "roi_range": "80~150%", "complexity": "medium"},
            {"title": "자동화 생산 스케줄링", "description": "최적화 알고리즘 기반 생산 일정 자동 편성", "roi_range": "100~200%", "complexity": "high"},
        ],
        "lora_adapter": "lora-manufacturing-v1.0",
        "kb_documents": 5000,
    },
    "finance": {
        "name": "금융업",
        "name_en": "Finance",
        "regulations": ["Basel III", "금융소비자보호법", "신용정보법", "전자금융거래법", "자본시장법"],
        "key_processes": [
            "여신 심사", "리스크 관리", "자산 운용", "고객 서비스",
            "컴플라이언스", "이상거래 탐지", "보험 심사"
        ],
        "ax_best_practices": [
            {"title": "AI 신용 평가", "description": "대안 데이터 활용 AI 신용 스코어링", "roi_range": "100~200%", "complexity": "high"},
            {"title": "이상거래 탐지", "description": "실시간 거래 패턴 분석 기반 FDS", "roi_range": "200~400%", "complexity": "high"},
            {"title": "로보어드바이저", "description": "AI 기반 자산 배분 및 투자 자문", "roi_range": "50~150%", "complexity": "high"},
            {"title": "챗봇 상담", "description": "LLM 기반 금융 상품 상담 자동화", "roi_range": "80~200%", "complexity": "medium"},
        ],
        "lora_adapter": "lora-finance-v1.0",
        "kb_documents": 3000,
    },
    "public": {
        "name": "공공기관",
        "name_en": "Public Sector",
        "regulations": ["행정절차법", "전자정부법", "개인정보보호법", "공공데이터법", "정보공개법"],
        "key_processes": [
            "민원 처리", "정책 분석", "예산 관리", "인사 관리",
            "조달", "복지 서비스", "규제 관리"
        ],
        "ax_best_practices": [
            {"title": "AI 민원 자동 분류", "description": "NLP 기반 민원 자동 분류 및 라우팅", "roi_range": "100~200%", "complexity": "medium"},
            {"title": "정책 영향 분석", "description": "AI 기반 정책 시뮬레이션 및 영향 예측", "roi_range": "50~100%", "complexity": "high"},
            {"title": "AI 복지 추천", "description": "시민 프로파일 기반 맞춤형 복지 추천", "roi_range": "80~150%", "complexity": "medium"},
        ],
        "lora_adapter": "lora-public-v1.0",
        "kb_documents": 2000,
    },
    "logistics": {
        "name": "유통/물류",
        "name_en": "Logistics & Retail",
        "regulations": ["물류정책기본법", "대규모유통업법", "전자상거래소비자보호법"],
        "key_processes": [
            "수요 예측", "재고 관리", "배송 최적화", "창고 관리",
            "고객 분석", "가격 최적화", "반품 관리"
        ],
        "ax_best_practices": [
            {"title": "수요 예측", "description": "딥러닝 기반 다변량 수요 예측", "roi_range": "100~250%", "complexity": "medium"},
            {"title": "배송 경로 최적화", "description": "강화학습 기반 최적 배송 경로", "roi_range": "80~200%", "complexity": "high"},
            {"title": "개인화 추천", "description": "협업 필터링 + 콘텐츠 기반 추천 하이브리드", "roi_range": "150~300%", "complexity": "medium"},
            {"title": "동적 가격 책정", "description": "실시간 수요/공급 기반 가격 최적화", "roi_range": "100~200%", "complexity": "high"},
        ],
        "lora_adapter": "lora-logistics-v1.0",
        "kb_documents": 3000,
    },
    "healthcare": {
        "name": "의료/헬스케어",
        "name_en": "Healthcare",
        "regulations": ["의료법", "약사법", "개인정보보호법", "생명윤리법", "의료기기법"],
        "key_processes": [
            "진단 보조", "의료 영상 분석", "신약 개발", "환자 모니터링",
            "EMR 관리", "병원 운영 최적화", "임상 시험"
        ],
        "ax_best_practices": [
            {"title": "의료 영상 AI 분석", "description": "CT/MRI 영상 자동 판독 보조", "roi_range": "100~300%", "complexity": "high"},
            {"title": "환자 위험도 예측", "description": "EMR 데이터 기반 위험 환자 조기 경보", "roi_range": "100~200%", "complexity": "medium"},
            {"title": "AI 약물 상호작용 검사", "description": "처방 약물 간 상호작용 자동 검출", "roi_range": "50~150%", "complexity": "medium"},
        ],
        "lora_adapter": "lora-healthcare-v1.0",
        "kb_documents": 2000,
    },
    "education": {
        "name": "교육",
        "name_en": "Education",
        "regulations": ["교육기본법", "고등교육법", "평생교육법", "학점인정법"],
        "key_processes": [
            "교육과정 설계", "학습 평가", "학생 관리", "교수법 개선",
            "온라인 교육", "진로 상담", "행정 업무"
        ],
        "ax_best_practices": [
            {"title": "적응형 학습 시스템", "description": "학습자 수준별 맞춤 콘텐츠 제공", "roi_range": "80~150%", "complexity": "high"},
            {"title": "AI 자동 채점", "description": "서술형 답안 자동 채점 및 피드백", "roi_range": "100~200%", "complexity": "medium"},
            {"title": "학습 이탈 예측", "description": "학습 패턴 분석 기반 이탈 위험 조기 경보", "roi_range": "50~100%", "complexity": "medium"},
        ],
        "lora_adapter": "lora-education-v1.0",
        "kb_documents": 1000,
    },
    "defense": {
        "name": "국방/방산",
        "name_en": "Defense",
        "regulations": ["방위사업법", "군사기밀보호법", "국방개혁법", "방산기술보호법"],
        "key_processes": [
            "위협 분석", "군수 관리", "전력 운용", "정보 분석",
            "시뮬레이션 훈련", "장비 정비", "사이버 방어"
        ],
        "ax_best_practices": [
            {"title": "AI 위협 탐지", "description": "다중 센서 데이터 융합 기반 위협 탐지", "roi_range": "N/A (안보 가치)", "complexity": "high"},
            {"title": "군수 수요 예측", "description": "AI 기반 군수 물자 수요 예측 및 최적 배분", "roi_range": "100~200%", "complexity": "medium"},
            {"title": "시뮬레이션 훈련", "description": "AI 적응형 시뮬레이션 훈련 시스템", "roi_range": "80~200%", "complexity": "high"},
        ],
        "lora_adapter": "lora-defense-v1.0",
        "kb_documents": 0,  # 보안 등급 별도
    },
}


class DomainKBManager:
    """도메인 Knowledge Base 관리자"""

    def __init__(self):
        self.domains = DOMAIN_KNOWLEDGE_BASE

    def get_domain_info(self, domain: str) -> Optional[dict]:
        """도메인 정보 조회"""
        return self.domains.get(domain)

    def list_domains(self) -> list[dict]:
        """전체 도메인 목록"""
        return [
            {
                "id": key,
                "name": info["name"],
                "name_en": info["name_en"],
                "regulations_count": len(info["regulations"]),
                "best_practices_count": len(info["ax_best_practices"]),
                "kb_documents": info["kb_documents"],
                "lora_adapter": info["lora_adapter"],
            }
            for key, info in self.domains.items()
        ]

    def get_best_practices(self, domain: str) -> list[dict]:
        """도메인별 AX 베스트 프랙티스"""
        info = self.domains.get(domain, {})
        return info.get("ax_best_practices", [])

    def get_regulations(self, domain: str) -> list[str]:
        """도메인별 규제/표준 목록"""
        info = self.domains.get(domain, {})
        return info.get("regulations", [])

    def get_key_processes(self, domain: str) -> list[str]:
        """도메인별 핵심 프로세스"""
        info = self.domains.get(domain, {})
        return info.get("key_processes", [])

    def get_lora_adapter(self, domain: str) -> Optional[str]:
        """도메인별 LoRA 어댑터명"""
        info = self.domains.get(domain, {})
        return info.get("lora_adapter")

    def search_best_practices(self, query: str) -> list[dict]:
        """전체 도메인에서 베스트 프랙티스 검색"""
        results = []
        for domain_id, info in self.domains.items():
            for bp in info.get("ax_best_practices", []):
                if query.lower() in bp["title"].lower() or query.lower() in bp["description"].lower():
                    results.append({**bp, "domain": domain_id, "domain_name": info["name"]})
        return results


# 싱글톤
_kb_manager: DomainKBManager | None = None


def get_domain_kb_manager() -> DomainKBManager:
    global _kb_manager
    if _kb_manager is None:
        _kb_manager = DomainKBManager()
    return _kb_manager
