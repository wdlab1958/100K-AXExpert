"""
AutoGen (AG2) 기반 멀티 에이전트 대화형 협업 오케스트레이터
GroupChat을 활용한 에이전트 간 대화 기반 협업 및 합의 도출 지원

AutoGen 0.7.x (AG2) API 사용 - autogen_agentchat, autogen_ext
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat
from autogen_agentchat.conditions import MaxMessageTermination, TextMentionTermination
from autogen_ext.models.ollama import OllamaChatCompletionClient

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.agents.strategy_analyst import StrategyAnalystAgent
from src.agents.usecase_designer import UseCaseDesignerAgent
from src.agents.roi_analyst import ROIAnalystAgent
from src.agents.risk_assessor import RiskAssessorAgent
from src.agents.report_generator import ReportGeneratorAgent
from src.core.llm_provider import get_llm_provider
from src.utils.consulting_logger import get_consulting_logger
from config.settings import settings


class AutoGenOrchestrator:
    """AutoGen (AG2) 기반 대화형 멀티 에이전트 오케스트레이터

    AutoGen의 GroupChat 패턴을 활용하여 5개 컨설팅 에이전트가
    대화를 통해 분석 결과를 도출하고 합의에 도달합니다.

    특징:
    - RoundRobin / Selector 기반 GroupChat
    - 에이전트 간 대화 기반 협업 (단방향 호출이 아닌 양방향 소통)
    - Ollama 네이티브 통합 (autogen_ext.models.ollama)
    - 메시지 종료 조건 (MaxMessage, TextMention)
    """

    def __init__(self):
        self.logger = get_consulting_logger()
        self.llm_provider = get_llm_provider()

        # AutoGen용 Ollama 클라이언트
        self.model_client = OllamaChatCompletionClient(
            model=settings.OLLAMA_MODEL,
            host=settings.OLLAMA_BASE_URL,
        )

        # 기존 100K-AX Expert 에이전트 (규칙 기반 로직 재사용)
        self.native_agents = {
            "strategy": StrategyAnalystAgent(self.llm_provider),
            "designer": UseCaseDesignerAgent(self.llm_provider),
            "roi": ROIAnalystAgent(self.llm_provider),
            "risk": RiskAssessorAgent(self.llm_provider),
            "report": ReportGeneratorAgent(self.llm_provider),
        }

        # AutoGen 에이전트 생성
        self.autogen_agents = self._create_agents()

    def _create_agents(self) -> Dict[str, AssistantAgent]:
        """AutoGen AssistantAgent 생성"""
        agents = {}

        agents["strategy_analyst"] = AssistantAgent(
            name="StrategyAnalyst",
            model_client=self.model_client,
            system_message="""당신은 AI 전략 분석가입니다.
역할: AI 성숙도 진단, 기회 발굴, 전략 수립
전문성: 4대 영역(전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스) 진단
원칙: 객관적이고 데이터 기반의 분석, 실현 가능한 목표 설정
다른 에이전트의 분석을 참고하여 의견을 제시하세요. 한국어로 답변하세요.""",
        )

        agents["use_case_designer"] = AssistantAgent(
            name="UseCaseDesigner",
            model_client=self.model_client,
            system_message="""당신은 AI Use Case 설계자입니다.
역할: 상세 요건 정의, 기술 아키텍처 설계, 거버넌스 체계 수립
전문성: 데이터 파이프라인, MLOps, 모델 서빙 아키텍처
원칙: 비즈니스-기술 정합성, 확장성, 유지보수성
전략 분석가의 결과를 바탕으로 구체적인 설계를 제안하세요. 한국어로 답변하세요.""",
        )

        agents["roi_analyst"] = AssistantAgent(
            name="ROIAnalyst",
            model_client=self.model_client,
            system_message="""당신은 ROI 분석 전문가입니다.
역할: 투자 대비 효과 분석, TCO 분석, 재무적 타당성 검토
전문성: NPV, IRR, Payback Period, 정량적/정성적 ROI 분석
원칙: 보수적 가정, 균형있는 평가, 리스크 반영
설계된 Use Case의 재무적 가치를 분석하세요. 한국어로 답변하세요.""",
        )

        agents["risk_assessor"] = AssistantAgent(
            name="RiskAssessor",
            model_client=self.model_client,
            system_message="""당신은 리스크 평가 전문가입니다.
역할: 기술적/조직적/비즈니스/운영적 리스크 평가 및 완화 전략 수립
전문성: 리스크 등급화, 예방/대응/복구 전략, ISO 31000 프레임워크
원칙: 종합적 접근, 실행 가능한 완화 전략
다른 에이전트의 분석에서 잠재 리스크를 식별하고 완화 전략을 제시하세요. 한국어로 답변하세요.""",
        )

        agents["report_generator"] = AssistantAgent(
            name="ReportGenerator",
            model_client=self.model_client,
            system_message="""당신은 보고서 작성 전문가입니다.
역할: 컨설팅 결과 종합, Executive Summary 작성
전문성: 경영진/실무자 보고서, 데이터 기반 서술, 핵심 메시지 전달
원칙: 명확성, 간결성, 전문성
모든 에이전트의 분석을 종합하여 최종 보고서를 작성하세요.
최종 보고서 작성이 완료되면 반드시 'TERMINATE'를 포함하여 대화를 종료하세요.
한국어로 답변하세요.""",
        )

        return agents

    async def run_consultation(
        self,
        project_id: str,
        company_profile: Dict[str, Any],
        chat_mode: str = "round_robin",
        max_messages: int = 12,
    ) -> Dict[str, Any]:
        """AutoGen GroupChat 기반 컨설팅 실행"""
        self.logger.info(f"[AutoGen] 컨설팅 시작 (모드: {chat_mode}): {project_id}", project_id)
        started_at = datetime.now().isoformat()

        # 규칙 기반 분석 선행 실행
        native_results = await self._run_native_analysis(project_id, company_profile)

        # GroupChat 실행을 위한 초기 메시지 구성
        company_info = json.dumps(company_profile, ensure_ascii=False, indent=2, default=str)
        native_summary = self._summarize_native_results(native_results)

        initial_message = f"""[AI 컨설팅 프로젝트 시작]

프로젝트 ID: {project_id}

기업 정보:
{company_info}

규칙 기반 사전 분석 결과:
{native_summary}

위 정보를 바탕으로 각 전문가는 자신의 영역에서 분석을 수행하고 의견을 제시해 주세요.
전략 분석가부터 시작하여, 설계자, ROI 분석가, 리스크 전문가 순으로 분석하고,
마지막에 보고서 전문가가 종합 보고서를 작성해 주세요."""

        # 종료 조건 설정
        termination = MaxMessageTermination(max_messages) | TextMentionTermination("TERMINATE")

        # GroupChat 생성
        agent_list = list(self.autogen_agents.values())

        if chat_mode == "selector":
            team = SelectorGroupChat(
                agent_list,
                model_client=self.model_client,
                termination_condition=termination,
            )
        else:  # round_robin
            team = RoundRobinGroupChat(
                agent_list,
                termination_condition=termination,
            )

        # GroupChat 실행
        chat_messages = []
        try:
            result = await team.run(task=initial_message)

            # 메시지 수집
            for msg in result.messages:
                chat_messages.append({
                    "source": msg.source if hasattr(msg, 'source') else "unknown",
                    "content": str(msg.content) if hasattr(msg, 'content') else str(msg),
                    "type": type(msg).__name__,
                })

        except Exception as e:
            self.logger.error(f"[AutoGen] GroupChat 실행 오류: {e}", project_id)
            chat_messages.append({
                "source": "system",
                "content": f"GroupChat 실행 오류: {str(e)}",
                "type": "error",
            })

        completed_at = datetime.now().isoformat()
        self.logger.info(
            f"[AutoGen] 컨설팅 완료 - 메시지 수: {len(chat_messages)}",
            project_id,
        )

        return {
            "framework": "autogen",
            "project_id": project_id,
            "status": "completed",
            "chat_mode": chat_mode,
            "results": {
                "chat_messages": chat_messages,
                "message_count": len(chat_messages),
                "native_analysis": native_results,
            },
            "agents": [
                {"name": a.name, "type": "AssistantAgent"}
                for a in self.autogen_agents.values()
            ],
            "started_at": started_at,
            "completed_at": completed_at,
        }

    async def _run_native_analysis(
        self, project_id: str, company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """기존 100K-AX Expert 에이전트로 규칙 기반 분석 실행"""
        results = {}
        try:
            from src.models.schemas import CompanyProfile as CP
            company_obj = CP(**company_profile)

            results["maturity"] = await self.native_agents["strategy"].execute({
                "type": "maturity_assessment",
                "company_profile": company_obj,
            })
            results["opportunities"] = await self.native_agents["strategy"].execute({
                "type": "opportunity_identification",
                "company_profile": company_obj,
            })
            results["roadmap"] = await self.native_agents["strategy"].execute({
                "type": "roadmap_planning",
                "company_profile": company_obj,
                "use_cases": results["opportunities"].get("opportunities", []),
            })

            budget = company_profile.get("financial_resources", {}).get("ai_investment_budget", 1000000)
            results["roi"] = await self.native_agents["roi"].execute({
                "type": "roi_calculation",
                "investment": budget,
                "expected_benefits": {
                    "cost_reduction": budget * 0.3,
                    "revenue_increase": budget * 0.2,
                    "productivity_gain": budget * 0.15,
                },
                "period_months": 36,
            })
            results["risk"] = await self.native_agents["risk"].execute({
                "type": "full_assessment",
                "company_profile": company_obj,
                "use_cases": results["opportunities"].get("opportunities", []),
            })
        except Exception as e:
            self.logger.error(f"[AutoGen] 규칙 기반 분석 오류: {e}", project_id)
            results["error"] = str(e)

        return results

    def _summarize_native_results(self, results: Dict[str, Any]) -> str:
        """규칙 기반 분석 결과 요약 (GroupChat 컨텍스트용)"""
        lines = []

        # 성숙도
        maturity = results.get("maturity", {})
        if maturity:
            level = maturity.get("overall_level", "N/A")
            lines.append(f"- AI 성숙도 종합 레벨: {level}")
            scores = maturity.get("scores", {})
            for dim, data in scores.items():
                lines.append(f"  - {dim}: Level {data.get('level', 'N/A')} (점수: {data.get('score', 0):.1f})")

        # 기회
        opps = results.get("opportunities", {})
        if opps:
            opp_list = opps.get("opportunities", [])
            lines.append(f"- 발굴된 AI 도입 기회: {len(opp_list)}건")
            for opp in opp_list[:3]:
                lines.append(f"  - {opp.get('name', 'N/A')} (적합도: {opp.get('fit_score', 0):.0f})")

        # ROI
        roi = results.get("roi", {})
        if roi:
            metrics = roi.get("metrics", {})
            lines.append(f"- ROI: {metrics.get('roi_percent', 0):.1f}%")
            lines.append(f"- 회수 기간: {metrics.get('payback_months', 0):.0f}개월")

        # 리스크
        risk = results.get("risk", {})
        if risk:
            lines.append(f"- 리스크 레벨: {risk.get('risk_level', 'N/A')}")
            lines.append(f"- 리스크 점수: {risk.get('total_risk_score', 0):.1f}")

        return "\n".join(lines) if lines else "사전 분석 결과 없음"

    def get_agent_info(self) -> Dict[str, Any]:
        """AutoGen 에이전트 구성 정보 반환"""
        return {
            "framework": "autogen",
            "version": "AG2 0.7.x",
            "agents": [
                {
                    "id": key,
                    "name": agent.name,
                    "type": "AssistantAgent",
                    "system_message": agent._system_messages[0].content[:200] + "..."
                    if hasattr(agent, '_system_messages') and agent._system_messages
                    else "N/A",
                }
                for key, agent in self.autogen_agents.items()
            ],
            "supported_modes": ["round_robin", "selector"],
            "model": settings.OLLAMA_MODEL,
            "model_host": settings.OLLAMA_BASE_URL,
        }


# 싱글톤 인스턴스
_autogen_orchestrator: Optional[AutoGenOrchestrator] = None


def get_autogen_orchestrator() -> AutoGenOrchestrator:
    """AutoGen Orchestrator 싱글톤 인스턴스 반환"""
    global _autogen_orchestrator
    if _autogen_orchestrator is None:
        _autogen_orchestrator = AutoGenOrchestrator()
    return _autogen_orchestrator
