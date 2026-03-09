"""
LangChain 확장 모듈 - LCEL Chain, PromptTemplate, ChatMessageHistory 활용
기존 단순 Ollama 래퍼에서 LangChain의 핵심 기능을 적극 활용하는 확장 모듈

주요 기능:
- PromptTemplate: 구조화된 프롬프트 템플릿 관리
- LCEL (LangChain Expression Language): 파이프라인 체이닝
- ChatMessageHistory: 대화 컨텍스트 유지
- StrOutputParser: 구조화된 출력 파싱
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import asyncio

from langchain_community.llms import Ollama
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables import RunnablePassthrough

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings
from src.utils.consulting_logger import get_consulting_logger


# ==================== 프롬프트 템플릿 ====================

MATURITY_PROMPT = PromptTemplate(
    input_variables=["company_name", "industry", "company_details"],
    template="""당신은 AI 성숙도 진단 전문 컨설턴트입니다.

다음 기업의 AI 성숙도를 진단하세요.

[기업명] {company_name}
[산업] {industry}
[기업 상세 정보]
{company_details}

[진단 기준]
- Level 1 (초기): AI 활동이 산발적
- Level 2 (반복 가능): 최소 관리 체계 보유
- Level 3 (정의됨): 전사 표준 프로세스 존재
- Level 4 (관리됨): KPI 기반 정량적 관리
- Level 5 (최적화됨): AI가 비즈니스 핵심 동력

4대 영역(전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스)에 대해 레벨을 평가하고 근거를 제시하세요.
""",
)

USE_CASE_PROMPT = PromptTemplate(
    input_variables=["industry", "maturity_summary", "company_capabilities"],
    template="""당신은 AI 활용 사례 발굴 전문가입니다.

[산업 분류] {industry}
[AI 성숙도 진단 요약]
{maturity_summary}
[기업 역량]
{company_capabilities}

위 기업에 적합한 AI 활용 사례를 발굴하세요.
각 Use Case에 대해 다음을 포함하세요:
1. Use Case 이름
2. 기대 효과 (ROI 수준)
3. 구현 복잡도
4. 우선순위 추천
5. 주요 성공 요인
""",
)

ROI_PROMPT = PromptTemplate(
    input_variables=["investment", "use_cases", "period", "company_context"],
    template="""당신은 AI 투자 ROI 분석 전문가입니다.

[투자 규모] {investment}
[분석 기간] {period}개월
[도입 예정 Use Case]
{use_cases}
[기업 컨텍스트]
{company_context}

다음을 분석하세요:
1. 예상 ROI (%)
2. 투자 회수 기간
3. 효과 분류 (비용 절감, 매출 증가, 생산성 향상)
4. 위험 요소
""",
)

RISK_PROMPT = PromptTemplate(
    input_variables=["company_summary", "use_cases", "maturity_level"],
    template="""당신은 AI 도입 리스크 평가 전문가입니다.

[기업 요약] {company_summary}
[도입 Use Case] {use_cases}
[현재 AI 성숙도] {maturity_level}

4대 리스크 영역을 평가하세요:
1. 기술 리스크 (기술 역량, 인프라, 통합)
2. 조직 리스크 (변화 관리, 인력, 문화)
3. 비즈니스 리스크 (ROI 불확실성, 시장 변화)
4. 운영 리스크 (모니터링, 유지보수, 보안)

각 리스크에 대해 심각도(높음/중간/낮음)와 완화 전략을 제시하세요.
""",
)

REPORT_PROMPT = PromptTemplate(
    input_variables=["maturity_result", "use_case_result", "roi_result", "risk_result"],
    template="""당신은 AI 컨설팅 보고서 작성 전문가입니다.

다음 분석 결과를 종합하여 경영진 보고서를 작성하세요.

[AI 성숙도 진단]
{maturity_result}

[Use Case 발굴]
{use_case_result}

[ROI 분석]
{roi_result}

[리스크 평가]
{risk_result}

다음 형식으로 보고서를 작성하세요:
1. 경영진 요약 (3-5문장)
2. 핵심 발견사항 (5가지)
3. 전략적 방향성
4. 즉각 실행 과제 (3가지)
5. 투자 권고사항
""",
)


# ==================== LangChain 컨설팅 Provider ====================

class LangChainConsultingProvider:
    """LangChain LCEL Chain/PromptTemplate 기반 컨설팅 제공자

    기능:
    - PromptTemplate 기반 구조화된 프롬프트 관리
    - LCEL 파이프라인으로 단계별 분석 실행
    - ChatMessageHistory로 대화 컨텍스트 유지
    """

    def __init__(self):
        self.logger = get_consulting_logger()

        # Ollama LLM
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.7,
        )

        # 출력 파서
        self.str_parser = StrOutputParser()

        # LCEL Chains (Prompt | LLM | Parser)
        self.maturity_chain = MATURITY_PROMPT | self.llm | self.str_parser
        self.use_case_chain = USE_CASE_PROMPT | self.llm | self.str_parser
        self.roi_chain = ROI_PROMPT | self.llm | self.str_parser
        self.risk_chain = RISK_PROMPT | self.llm | self.str_parser
        self.report_chain = REPORT_PROMPT | self.llm | self.str_parser

        # 대화 메모리 (프로젝트별)
        self._histories: Dict[str, ChatMessageHistory] = {}

    def get_history(self, project_id: str) -> ChatMessageHistory:
        """프로젝트별 대화 이력 반환"""
        if project_id not in self._histories:
            self._histories[project_id] = ChatMessageHistory()
        return self._histories[project_id]

    async def analyze_maturity(self, company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """LangChain LCEL Chain 기반 성숙도 진단"""
        self.logger.info("[LangChain] 성숙도 진단 Chain 실행", company_profile.get("name", ""))

        company_details = json.dumps(company_profile, ensure_ascii=False, indent=2)

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.maturity_chain.invoke({
                "company_name": company_profile.get("name", "Unknown"),
                "industry": company_profile.get("industry", "manufacturing"),
                "company_details": company_details,
            }),
        )

        return {
            "framework": "langchain",
            "chain": "maturity_chain",
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def discover_use_cases(
        self, company_profile: Dict[str, Any], maturity_summary: str
    ) -> Dict[str, Any]:
        """LangChain LCEL Chain 기반 Use Case 발굴"""
        self.logger.info("[LangChain] Use Case 발굴 Chain 실행", company_profile.get("name", ""))

        capabilities = json.dumps(
            {
                "it_infrastructure": company_profile.get("it_infrastructure", {}),
                "data_assets": company_profile.get("data_assets", {}),
                "human_resources": company_profile.get("human_resources", {}),
            },
            ensure_ascii=False,
            indent=2,
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.use_case_chain.invoke({
                "industry": company_profile.get("industry", "manufacturing"),
                "maturity_summary": maturity_summary,
                "company_capabilities": capabilities,
            }),
        )

        return {
            "framework": "langchain",
            "chain": "use_case_chain",
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def analyze_roi(
        self,
        company_profile: Dict[str, Any],
        use_cases_text: str,
        investment: float = 0,
        period: int = 36,
    ) -> Dict[str, Any]:
        """LangChain LCEL Chain 기반 ROI 분석"""
        self.logger.info("[LangChain] ROI 분석 Chain 실행", "")

        if investment == 0:
            investment = company_profile.get("financial_resources", {}).get(
                "ai_investment_budget", 1000000000
            )

        company_context = json.dumps(
            {
                "name": company_profile.get("name", "Unknown"),
                "industry": company_profile.get("industry", "manufacturing"),
                "size": company_profile.get("company_size", "medium"),
            },
            ensure_ascii=False,
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.roi_chain.invoke({
                "investment": f"{investment:,.0f}원",
                "use_cases": use_cases_text,
                "period": str(period),
                "company_context": company_context,
            }),
        )

        return {
            "framework": "langchain",
            "chain": "roi_chain",
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def assess_risk(
        self,
        company_profile: Dict[str, Any],
        use_cases_text: str,
        maturity_level: int = 3,
    ) -> Dict[str, Any]:
        """LangChain LCEL Chain 기반 리스크 평가"""
        self.logger.info("[LangChain] 리스크 평가 Chain 실행", "")

        company_summary = (
            f"{company_profile.get('name', 'Unknown')} "
            f"({company_profile.get('industry', 'manufacturing')}, "
            f"{company_profile.get('company_size', 'medium')})"
        )

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.risk_chain.invoke({
                "company_summary": company_summary,
                "use_cases": use_cases_text,
                "maturity_level": f"Level {maturity_level}",
            }),
        )

        return {
            "framework": "langchain",
            "chain": "risk_chain",
            "analysis": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def generate_report(
        self,
        maturity_result: str,
        use_case_result: str,
        roi_result: str,
        risk_result: str,
    ) -> Dict[str, Any]:
        """LangChain LCEL Chain 기반 보고서 생성"""
        self.logger.info("[LangChain] 보고서 생성 Chain 실행", "")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.report_chain.invoke({
                "maturity_result": maturity_result,
                "use_case_result": use_case_result,
                "roi_result": roi_result,
                "risk_result": risk_result,
            }),
        )

        return {
            "framework": "langchain",
            "chain": "report_chain",
            "report": result,
            "timestamp": datetime.now().isoformat(),
        }

    async def run_full_consultation(
        self, project_id: str, company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """LangChain 기반 전체 컨설팅 파이프라인 실행"""
        self.logger.info(
            f"[LangChain] 전체 컨설팅 파이프라인 시작: {project_id}",
            project_id,
        )
        started_at = datetime.now().isoformat()
        history = self.get_history(project_id)
        results = {}
        errors = []

        # 1. 성숙도 진단
        try:
            results["maturity"] = await self.analyze_maturity(company_profile)
            from langchain_core.messages import HumanMessage, AIMessage
            history.add_message(HumanMessage(content="성숙도 진단 실행"))
            history.add_message(AIMessage(content=results["maturity"].get("analysis", "")[:500]))
        except Exception as e:
            errors.append(f"성숙도 진단 실패: {str(e)}")
            results["maturity"] = {"error": str(e)}

        # 2. Use Case 발굴
        try:
            maturity_text = results.get("maturity", {}).get("analysis", "진단 결과 없음")
            results["use_cases"] = await self.discover_use_cases(
                company_profile, maturity_text[:500]
            )
            from langchain_core.messages import HumanMessage, AIMessage
            history.add_message(HumanMessage(content="Use Case 발굴 실행"))
            history.add_message(AIMessage(content=results["use_cases"].get("analysis", "")[:500]))
        except Exception as e:
            errors.append(f"Use Case 발굴 실패: {str(e)}")
            results["use_cases"] = {"error": str(e)}

        # 3. ROI 분석
        try:
            uc_text = results.get("use_cases", {}).get("analysis", "")[:500]
            results["roi"] = await self.analyze_roi(company_profile, uc_text)
            from langchain_core.messages import HumanMessage, AIMessage
            history.add_message(HumanMessage(content="ROI 분석 실행"))
            history.add_message(AIMessage(content=results["roi"].get("analysis", "")[:500]))
        except Exception as e:
            errors.append(f"ROI 분석 실패: {str(e)}")
            results["roi"] = {"error": str(e)}

        # 4. 리스크 평가
        try:
            uc_text = results.get("use_cases", {}).get("analysis", "")[:500]
            results["risk"] = await self.assess_risk(company_profile, uc_text)
            from langchain_core.messages import HumanMessage, AIMessage
            history.add_message(HumanMessage(content="리스크 평가 실행"))
            history.add_message(AIMessage(content=results["risk"].get("analysis", "")[:500]))
        except Exception as e:
            errors.append(f"리스크 평가 실패: {str(e)}")
            results["risk"] = {"error": str(e)}

        # 5. 보고서 생성
        try:
            results["report"] = await self.generate_report(
                results.get("maturity", {}).get("analysis", "N/A"),
                results.get("use_cases", {}).get("analysis", "N/A"),
                results.get("roi", {}).get("analysis", "N/A"),
                results.get("risk", {}).get("analysis", "N/A"),
            )
        except Exception as e:
            errors.append(f"보고서 생성 실패: {str(e)}")
            results["report"] = {"error": str(e)}

        self.logger.info(
            f"[LangChain] 전체 컨설팅 파이프라인 완료: {project_id}",
            project_id,
        )

        return {
            "framework": "langchain",
            "project_id": project_id,
            "status": "completed" if not errors else "completed_with_errors",
            "results": results,
            "errors": errors,
            "history_messages": len(history.messages),
            "started_at": started_at,
            "completed_at": datetime.now().isoformat(),
        }

    def get_chain_info(self) -> Dict[str, Any]:
        """LangChain 체인 구성 정보 반환"""
        return {
            "framework": "langchain",
            "llm_model": settings.OLLAMA_MODEL,
            "llm_base_url": settings.OLLAMA_BASE_URL,
            "chains": [
                {
                    "name": "maturity_chain",
                    "type": "LCEL (Prompt | LLM | StrOutputParser)",
                    "prompt_template": "MATURITY_PROMPT",
                    "description": "AI 성숙도 진단 분석",
                },
                {
                    "name": "use_case_chain",
                    "type": "LCEL (Prompt | LLM | StrOutputParser)",
                    "prompt_template": "USE_CASE_PROMPT",
                    "description": "AI Use Case 발굴",
                },
                {
                    "name": "roi_chain",
                    "type": "LCEL (Prompt | LLM | StrOutputParser)",
                    "prompt_template": "ROI_PROMPT",
                    "description": "ROI 분석",
                },
                {
                    "name": "risk_chain",
                    "type": "LCEL (Prompt | LLM | StrOutputParser)",
                    "prompt_template": "RISK_PROMPT",
                    "description": "리스크 평가",
                },
                {
                    "name": "report_chain",
                    "type": "LCEL (Prompt | LLM | StrOutputParser)",
                    "prompt_template": "REPORT_PROMPT",
                    "description": "컨설팅 보고서 생성",
                },
            ],
            "features": [
                "PromptTemplate 기반 구조화된 프롬프트",
                "LCEL 파이프라인 체이닝",
                "ChatMessageHistory 컨텍스트 유지",
                "프로젝트별 대화 기록 관리",
                "StrOutputParser 출력 파싱",
            ],
            "active_histories": len(self._histories),
        }


# 싱글톤 인스턴스
_langchain_provider: Optional[LangChainConsultingProvider] = None


def get_langchain_provider() -> LangChainConsultingProvider:
    """LangChain Provider 싱글톤 인스턴스 반환"""
    global _langchain_provider
    if _langchain_provider is None:
        _langchain_provider = LangChainConsultingProvider()
    return _langchain_provider
