"""
DSPy 기반 프롬프트 최적화 모듈
Signature 기반 자동 프롬프트 최적화 및 Ollama Local LLM 통합

DSPy는 프롬프트를 프로그래밍적으로 정의하고 자동 최적화하여
LLM의 출력 품질을 체계적으로 향상시킵니다.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import asyncio

import dspy

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings
from src.utils.consulting_logger import get_consulting_logger


# ==================== DSPy Signatures ====================

class MaturityAssessmentSignature(dspy.Signature):
    """기업의 AI 성숙도를 진단합니다.
    4대 핵심 영역(전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스)을 평가합니다."""

    company_info: str = dspy.InputField(desc="기업 프로필 정보 (JSON 형식)")
    industry: str = dspy.InputField(desc="기업의 산업 분류")

    strategy_score: str = dspy.OutputField(desc="전략/비전 영역 성숙도 레벨 (1-5)")
    organization_score: str = dspy.OutputField(desc="조직/역량 영역 성숙도 레벨 (1-5)")
    data_tech_score: str = dspy.OutputField(desc="데이터/기술 영역 성숙도 레벨 (1-5)")
    process_score: str = dspy.OutputField(desc="프로세스/거버넌스 영역 성숙도 레벨 (1-5)")
    overall_assessment: str = dspy.OutputField(desc="종합 평가 요약 (한국어)")
    recommendations: str = dspy.OutputField(desc="핵심 개선 권고사항 3가지 (한국어)")


class UseCaseDiscoverySignature(dspy.Signature):
    """기업에 적합한 AI 활용 사례를 발굴합니다.
    산업 특성과 기업 역량을 고려하여 최적의 Use Case를 제안합니다."""

    company_info: str = dspy.InputField(desc="기업 프로필 정보")
    industry: str = dspy.InputField(desc="산업 분류")
    maturity_level: str = dspy.InputField(desc="현재 AI 성숙도 레벨")

    use_cases: str = dspy.OutputField(desc="추천 AI Use Case 목록 (이름, 설명, ROI 예상, 복잡도)")
    prioritization: str = dspy.OutputField(desc="우선순위 근거 및 순위")
    implementation_approach: str = dspy.OutputField(desc="구현 접근 전략")


class ROIAnalysisSignature(dspy.Signature):
    """AI 투자의 ROI를 분석합니다.
    정량적/정성적 효과를 모두 고려하여 투자 타당성을 평가합니다."""

    investment_amount: str = dspy.InputField(desc="총 투자 금액 (억원)")
    use_cases: str = dspy.InputField(desc="도입 예정 AI Use Case 목록")
    period_months: str = dspy.InputField(desc="분석 기간 (개월)")

    roi_percent: str = dspy.OutputField(desc="예상 ROI (%)")
    payback_period: str = dspy.OutputField(desc="투자 회수 기간 (개월)")
    benefit_breakdown: str = dspy.OutputField(desc="효과 분류 (비용 절감, 매출 증가, 생산성 향상)")
    risk_factors: str = dspy.OutputField(desc="ROI 달성 위험 요소")


class RiskAssessmentSignature(dspy.Signature):
    """AI 도입에 따른 리스크를 평가합니다.
    기술적, 조직적, 비즈니스, 운영 리스크를 종합 분석합니다."""

    company_info: str = dspy.InputField(desc="기업 프로필 정보")
    use_cases: str = dspy.InputField(desc="도입 예정 AI Use Case 목록")

    technical_risks: str = dspy.OutputField(desc="기술 리스크 목록 및 심각도")
    organizational_risks: str = dspy.OutputField(desc="조직 리스크 목록 및 심각도")
    business_risks: str = dspy.OutputField(desc="비즈니스 리스크 목록 및 심각도")
    mitigation_strategies: str = dspy.OutputField(desc="리스크 완화 전략")
    overall_risk_level: str = dspy.OutputField(desc="종합 리스크 수준 (낮음/중간/높음)")


class ConsultingReportSignature(dspy.Signature):
    """AI 컨설팅 보고서의 경영진 요약을 생성합니다.
    전체 분석 결과를 종합하여 의사결정에 필요한 핵심 정보를 제공합니다."""

    maturity_summary: str = dspy.InputField(desc="AI 성숙도 진단 결과 요약")
    use_case_summary: str = dspy.InputField(desc="Use Case 발굴 결과 요약")
    roi_summary: str = dspy.InputField(desc="ROI 분석 결과 요약")
    risk_summary: str = dspy.InputField(desc="리스크 평가 결과 요약")

    executive_summary: str = dspy.OutputField(desc="경영진 요약 (한국어, 500자 이내)")
    key_findings: str = dspy.OutputField(desc="핵심 발견사항 5가지")
    action_items: str = dspy.OutputField(desc="즉각 실행 과제 3가지")
    strategic_direction: str = dspy.OutputField(desc="전략적 방향성 제안")


# ==================== DSPy Modules ====================

class MaturityAssessor(dspy.Module):
    """DSPy 기반 AI 성숙도 진단 모듈"""

    def __init__(self):
        super().__init__()
        self.assess = dspy.ChainOfThought(MaturityAssessmentSignature)

    def forward(self, company_info: str, industry: str):
        return self.assess(company_info=company_info, industry=industry)


class UseCaseDiscoverer(dspy.Module):
    """DSPy 기반 Use Case 발굴 모듈"""

    def __init__(self):
        super().__init__()
        self.discover = dspy.ChainOfThought(UseCaseDiscoverySignature)

    def forward(self, company_info: str, industry: str, maturity_level: str):
        return self.discover(
            company_info=company_info,
            industry=industry,
            maturity_level=maturity_level,
        )


class ROIAnalyzer(dspy.Module):
    """DSPy 기반 ROI 분석 모듈"""

    def __init__(self):
        super().__init__()
        self.analyze = dspy.ChainOfThought(ROIAnalysisSignature)

    def forward(self, investment_amount: str, use_cases: str, period_months: str):
        return self.analyze(
            investment_amount=investment_amount,
            use_cases=use_cases,
            period_months=period_months,
        )


class RiskAssessor(dspy.Module):
    """DSPy 기반 리스크 평가 모듈"""

    def __init__(self):
        super().__init__()
        self.assess = dspy.ChainOfThought(RiskAssessmentSignature)

    def forward(self, company_info: str, use_cases: str):
        return self.assess(company_info=company_info, use_cases=use_cases)


class ReportGenerator(dspy.Module):
    """DSPy 기반 컨설팅 보고서 생성 모듈"""

    def __init__(self):
        super().__init__()
        self.generate = dspy.ChainOfThought(ConsultingReportSignature)

    def forward(
        self,
        maturity_summary: str,
        use_case_summary: str,
        roi_summary: str,
        risk_summary: str,
    ):
        return self.generate(
            maturity_summary=maturity_summary,
            use_case_summary=use_case_summary,
            roi_summary=roi_summary,
            risk_summary=risk_summary,
        )


# ==================== DSPy Provider ====================

class DSPyConsultingProvider:
    """DSPy 기반 AI 컨설팅 제공자

    Ollama Local LLM과 DSPy Signature를 결합하여
    프롬프트 자동 최적화 기반의 컨설팅 분석을 수행합니다.

    주요 기능:
    - Signature 기반 구조화된 입출력 정의
    - ChainOfThought 추론으로 분석 품질 향상
    - Ollama 로컬 모델 네이티브 지원
    """

    def __init__(self):
        self.logger = get_consulting_logger()

        # DSPy LM 설정 (Ollama)
        self.lm = dspy.LM(
            model=f"ollama_chat/{settings.OLLAMA_MODEL}",
            api_base=settings.OLLAMA_BASE_URL,
            api_key="ollama",  # Ollama는 키 불필요하지만 DSPy가 요구
            temperature=0.7,
        )
        dspy.configure(lm=self.lm)

        # DSPy 모듈 초기화
        self.maturity_assessor = MaturityAssessor()
        self.use_case_discoverer = UseCaseDiscoverer()
        self.roi_analyzer = ROIAnalyzer()
        self.risk_assessor = RiskAssessor()
        self.report_generator = ReportGenerator()

    async def assess_maturity(self, company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """DSPy 기반 AI 성숙도 진단"""
        self.logger.info("[DSPy] 성숙도 진단 실행", company_profile.get("name", ""))

        company_info = json.dumps(company_profile, ensure_ascii=False, indent=2)
        industry = company_profile.get("industry", "manufacturing")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.maturity_assessor(company_info=company_info, industry=industry),
        )

        return {
            "framework": "dspy",
            "module": "maturity_assessment",
            "scores": {
                "strategy": self._parse_score(result.strategy_score),
                "organization": self._parse_score(result.organization_score),
                "data_tech": self._parse_score(result.data_tech_score),
                "process": self._parse_score(result.process_score),
            },
            "overall_assessment": result.overall_assessment,
            "recommendations": result.recommendations,
            "timestamp": datetime.now().isoformat(),
        }

    async def discover_use_cases(
        self, company_profile: Dict[str, Any], maturity_level: int
    ) -> Dict[str, Any]:
        """DSPy 기반 Use Case 발굴"""
        self.logger.info("[DSPy] Use Case 발굴 실행", company_profile.get("name", ""))

        company_info = json.dumps(company_profile, ensure_ascii=False, indent=2)
        industry = company_profile.get("industry", "manufacturing")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.use_case_discoverer(
                company_info=company_info,
                industry=industry,
                maturity_level=str(maturity_level),
            ),
        )

        return {
            "framework": "dspy",
            "module": "use_case_discovery",
            "use_cases": result.use_cases,
            "prioritization": result.prioritization,
            "implementation_approach": result.implementation_approach,
            "timestamp": datetime.now().isoformat(),
        }

    async def analyze_roi(
        self,
        investment_amount: float,
        use_cases: List[str],
        period_months: int = 36,
    ) -> Dict[str, Any]:
        """DSPy 기반 ROI 분석"""
        self.logger.info("[DSPy] ROI 분석 실행", "")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.roi_analyzer(
                investment_amount=str(investment_amount / 100000000),  # 억원 단위 변환
                use_cases=json.dumps(use_cases, ensure_ascii=False),
                period_months=str(period_months),
            ),
        )

        return {
            "framework": "dspy",
            "module": "roi_analysis",
            "roi_percent": result.roi_percent,
            "payback_period": result.payback_period,
            "benefit_breakdown": result.benefit_breakdown,
            "risk_factors": result.risk_factors,
            "timestamp": datetime.now().isoformat(),
        }

    async def assess_risk(
        self, company_profile: Dict[str, Any], use_cases: List[str]
    ) -> Dict[str, Any]:
        """DSPy 기반 리스크 평가"""
        self.logger.info("[DSPy] 리스크 평가 실행", "")

        company_info = json.dumps(company_profile, ensure_ascii=False, indent=2)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.risk_assessor(
                company_info=company_info,
                use_cases=json.dumps(use_cases, ensure_ascii=False),
            ),
        )

        return {
            "framework": "dspy",
            "module": "risk_assessment",
            "technical_risks": result.technical_risks,
            "organizational_risks": result.organizational_risks,
            "business_risks": result.business_risks,
            "mitigation_strategies": result.mitigation_strategies,
            "overall_risk_level": result.overall_risk_level,
            "timestamp": datetime.now().isoformat(),
        }

    async def generate_report(
        self,
        maturity_result: Dict[str, Any],
        use_case_result: Dict[str, Any],
        roi_result: Dict[str, Any],
        risk_result: Dict[str, Any],
    ) -> Dict[str, Any]:
        """DSPy 기반 컨설팅 보고서 생성"""
        self.logger.info("[DSPy] 보고서 생성 실행", "")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.report_generator(
                maturity_summary=json.dumps(maturity_result, ensure_ascii=False),
                use_case_summary=json.dumps(use_case_result, ensure_ascii=False),
                roi_summary=json.dumps(roi_result, ensure_ascii=False),
                risk_summary=json.dumps(risk_result, ensure_ascii=False),
            ),
        )

        return {
            "framework": "dspy",
            "module": "report_generation",
            "executive_summary": result.executive_summary,
            "key_findings": result.key_findings,
            "action_items": result.action_items,
            "strategic_direction": result.strategic_direction,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_full_consultation(
        self, company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """DSPy 기반 전체 컨설팅 파이프라인 실행"""
        self.logger.info("[DSPy] 전체 컨설팅 파이프라인 시작", company_profile.get("name", ""))
        started_at = datetime.now().isoformat()

        results = {}
        errors = []

        # 1. 성숙도 진단
        try:
            results["maturity"] = await self.assess_maturity(company_profile)
        except Exception as e:
            errors.append(f"성숙도 진단 실패: {str(e)}")
            results["maturity"] = {"error": str(e)}

        # 2. Use Case 발굴
        try:
            maturity_level = 3  # 기본값
            if "maturity" in results and "scores" in results["maturity"]:
                scores = results["maturity"]["scores"]
                maturity_level = round(sum(scores.values()) / len(scores))
            results["use_cases"] = await self.discover_use_cases(
                company_profile, maturity_level
            )
        except Exception as e:
            errors.append(f"Use Case 발굴 실패: {str(e)}")
            results["use_cases"] = {"error": str(e)}

        # 3. ROI 분석
        try:
            budget = company_profile.get("financial_resources", {}).get(
                "ai_investment_budget", 1000000000
            )
            use_case_names = []
            if isinstance(results.get("use_cases", {}).get("use_cases"), str):
                use_case_names = [results["use_cases"]["use_cases"]]
            results["roi"] = await self.analyze_roi(budget, use_case_names)
        except Exception as e:
            errors.append(f"ROI 분석 실패: {str(e)}")
            results["roi"] = {"error": str(e)}

        # 4. 리스크 평가
        try:
            results["risk"] = await self.assess_risk(company_profile, use_case_names)
        except Exception as e:
            errors.append(f"리스크 평가 실패: {str(e)}")
            results["risk"] = {"error": str(e)}

        # 5. 보고서 생성
        try:
            results["report"] = await self.generate_report(
                results.get("maturity", {}),
                results.get("use_cases", {}),
                results.get("roi", {}),
                results.get("risk", {}),
            )
        except Exception as e:
            errors.append(f"보고서 생성 실패: {str(e)}")
            results["report"] = {"error": str(e)}

        self.logger.info("[DSPy] 전체 컨설팅 파이프라인 완료", company_profile.get("name", ""))

        return {
            "framework": "dspy",
            "status": "completed" if not errors else "completed_with_errors",
            "results": results,
            "errors": errors,
            "started_at": started_at,
            "completed_at": datetime.now().isoformat(),
        }

    def get_module_info(self) -> Dict[str, Any]:
        """DSPy 모듈 구성 정보 반환"""
        return {
            "framework": "dspy",
            "version": dspy.__version__ if hasattr(dspy, "__version__") else "unknown",
            "lm_model": f"ollama_chat/{settings.OLLAMA_MODEL}",
            "lm_base_url": settings.OLLAMA_BASE_URL,
            "modules": [
                {
                    "name": "MaturityAssessor",
                    "signature": "MaturityAssessmentSignature",
                    "method": "ChainOfThought",
                    "description": "AI 성숙도 진단 (4대 영역 평가)",
                },
                {
                    "name": "UseCaseDiscoverer",
                    "signature": "UseCaseDiscoverySignature",
                    "method": "ChainOfThought",
                    "description": "AI Use Case 발굴 및 우선순위",
                },
                {
                    "name": "ROIAnalyzer",
                    "signature": "ROIAnalysisSignature",
                    "method": "ChainOfThought",
                    "description": "투자 대비 효과(ROI) 분석",
                },
                {
                    "name": "RiskAssessor",
                    "signature": "RiskAssessmentSignature",
                    "method": "ChainOfThought",
                    "description": "리스크 평가 및 완화 전략",
                },
                {
                    "name": "ReportGenerator",
                    "signature": "ConsultingReportSignature",
                    "method": "ChainOfThought",
                    "description": "경영진 보고서 생성",
                },
            ],
        }

    @staticmethod
    def _parse_score(score_str: str) -> int:
        """문자열에서 성숙도 점수 추출"""
        try:
            # 숫자만 추출
            import re
            numbers = re.findall(r'\d+', str(score_str))
            if numbers:
                score = int(numbers[0])
                return max(1, min(score, 5))
        except (ValueError, IndexError):
            pass
        return 3  # 기본값


# 싱글톤 인스턴스
_dspy_provider: Optional[DSPyConsultingProvider] = None


def get_dspy_provider() -> DSPyConsultingProvider:
    """DSPy Provider 싱글톤 인스턴스 반환"""
    global _dspy_provider
    if _dspy_provider is None:
        _dspy_provider = DSPyConsultingProvider()
    return _dspy_provider
