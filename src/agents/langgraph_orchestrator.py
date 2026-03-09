"""
LangGraph 기반 멀티 에이전트 워크플로우 오케스트레이터
StateGraph를 활용한 조건부 분기, 상태 관리, 반복 실행 지원
"""
from typing import Optional, List, Dict, Any, Annotated, Literal
from datetime import datetime
import asyncio
import json
import operator

from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.agents.base_agent import BaseConsultingAgent, AgentMessage
from src.agents.strategy_analyst import StrategyAnalystAgent
from src.agents.usecase_designer import UseCaseDesignerAgent
from src.agents.roi_analyst import ROIAnalystAgent
from src.agents.risk_assessor import RiskAssessorAgent
from src.agents.report_generator import ReportGeneratorAgent
from src.core.llm_provider import get_llm_provider
from src.utils.consulting_logger import get_consulting_logger


# ==================== LangGraph 상태 정의 ====================

class ConsultingGraphState(TypedDict):
    """LangGraph 워크플로우 상태"""
    project_id: str
    company_profile: Dict[str, Any]

    # 단계별 결과
    maturity_assessment: Optional[Dict[str, Any]]
    opportunities: Optional[Dict[str, Any]]
    roadmap: Optional[Dict[str, Any]]
    use_case_designs: List[Dict[str, Any]]
    roi_analysis: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    report: Optional[Dict[str, Any]]

    # 워크플로우 제어
    current_stage: str
    iteration_count: int
    quality_score: float
    max_iterations: int
    errors: List[str]
    messages: Annotated[list, add_messages]

    # 메타데이터
    started_at: str
    completed_at: Optional[str]
    execution_log: List[Dict[str, Any]]


# ==================== LangGraph 오케스트레이터 ====================

class LangGraphOrchestrator:
    """LangGraph StateGraph 기반 컨설팅 워크플로우 오케스트레이터

    기존 ConsultingOrchestrator의 순차 실행을 그래프 기반 조건부 워크플로우로 대체합니다.
    - 조건부 분기: 품질 점수에 따라 재분석 또는 다음 단계 진행
    - 상태 관리: TypedDict 기반 중앙 집중식 상태 관리
    - 반복 실행: 품질 기준 미달 시 자동 재시도 (최대 N회)
    """

    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.logger = get_consulting_logger()

        # 기존 에이전트 재사용
        self.agents = {
            "strategy": StrategyAnalystAgent(self.llm_provider),
            "designer": UseCaseDesignerAgent(self.llm_provider),
            "roi": ROIAnalystAgent(self.llm_provider),
            "risk": RiskAssessorAgent(self.llm_provider),
            "report": ReportGeneratorAgent(self.llm_provider),
        }

        # 그래프 빌드
        self.graph = self._build_graph()
        self.compiled_graph = self.graph.compile()

    def _build_graph(self) -> StateGraph:
        """LangGraph StateGraph 구성"""
        graph = StateGraph(ConsultingGraphState)

        # 노드 추가 (노드 이름은 상태 키와 충돌하지 않도록 접두사 사용)
        graph.add_node("node_strategy", self._strategy_analysis_node)
        graph.add_node("node_opportunity", self._opportunity_discovery_node)
        graph.add_node("node_roadmap", self._roadmap_planning_node)
        graph.add_node("node_design", self._use_case_design_node)
        graph.add_node("node_roi", self._roi_analysis_node)
        graph.add_node("node_risk", self._risk_assessment_node)
        graph.add_node("node_quality", self._quality_check_node)
        graph.add_node("node_report", self._report_generation_node)

        # 엣지 정의
        graph.add_edge(START, "node_strategy")
        graph.add_edge("node_strategy", "node_opportunity")
        graph.add_edge("node_opportunity", "node_roadmap")
        graph.add_edge("node_roadmap", "node_design")
        graph.add_edge("node_design", "node_roi")
        graph.add_edge("node_roi", "node_risk")
        graph.add_edge("node_risk", "node_quality")

        # 조건부 엣지: 품질 검사 결과에 따라 분기
        graph.add_conditional_edges(
            "node_quality",
            self._should_continue_or_report,
            {
                "retry_strategy": "node_strategy",
                "report": "node_report",
            }
        )

        graph.add_edge("node_report", END)

        return graph

    # ==================== 노드 구현 ====================

    async def _strategy_analysis_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """1단계: AI 전략 분석 (성숙도 진단)"""
        self.logger.info("[LangGraph] 전략 분석 노드 실행", state.get("project_id", ""))

        from src.models.schemas import CompanyProfile
        company = CompanyProfile(**state["company_profile"])

        try:
            result = await self.agents["strategy"].execute({
                "type": "maturity_assessment",
                "company_profile": company,
            })

            log_entry = {
                "node": "strategy_analysis",
                "status": "success",
                "timestamp": datetime.now().isoformat(),
                "overall_level": result.get("overall_level", 0),
            }

            return {
                "maturity_assessment": result,
                "current_stage": "strategy_analysis",
                "execution_log": state.get("execution_log", []) + [log_entry],
            }
        except Exception as e:
            return {
                "errors": state.get("errors", []) + [f"전략 분석 실패: {str(e)}"],
                "execution_log": state.get("execution_log", []) + [{
                    "node": "strategy_analysis",
                    "status": "error",
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                }],
            }

    async def _opportunity_discovery_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """1단계: AI 도입 기회 발굴"""
        self.logger.info("[LangGraph] 기회 발굴 노드 실행", state.get("project_id", ""))

        from src.models.schemas import CompanyProfile
        company = CompanyProfile(**state["company_profile"])

        try:
            result = await self.agents["strategy"].execute({
                "type": "opportunity_identification",
                "company_profile": company,
            })

            return {
                "opportunities": result,
                "current_stage": "opportunity_discovery",
                "execution_log": state.get("execution_log", []) + [{
                    "node": "opportunity_discovery",
                    "status": "success",
                    "opportunity_count": len(result.get("opportunities", [])),
                    "timestamp": datetime.now().isoformat(),
                }],
            }
        except Exception as e:
            return {
                "errors": state.get("errors", []) + [f"기회 발굴 실패: {str(e)}"],
            }

    async def _roadmap_planning_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """1단계: AI 도입 로드맵 수립"""
        self.logger.info("[LangGraph] 로드맵 수립 노드 실행", state.get("project_id", ""))

        from src.models.schemas import CompanyProfile
        company = CompanyProfile(**state["company_profile"])
        use_cases = state.get("opportunities", {}).get("opportunities", [])

        try:
            result = await self.agents["strategy"].execute({
                "type": "roadmap_planning",
                "company_profile": company,
                "use_cases": use_cases,
            })

            return {
                "roadmap": result,
                "current_stage": "roadmap_planning",
                "execution_log": state.get("execution_log", []) + [{
                    "node": "roadmap_planning",
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }],
            }
        except Exception as e:
            return {
                "errors": state.get("errors", []) + [f"로드맵 수립 실패: {str(e)}"],
            }

    async def _use_case_design_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """2단계: Use Case 설계"""
        self.logger.info("[LangGraph] Use Case 설계 노드 실행", state.get("project_id", ""))

        opportunities = state.get("opportunities", {}).get("opportunities", [])
        designs = []

        for i, use_case in enumerate(opportunities[:3]):  # 상위 3개만
            try:
                req = await self.agents["designer"].execute({
                    "type": "requirements_definition",
                    "use_case": use_case,
                })
                arch = await self.agents["designer"].execute({
                    "type": "architecture_design",
                    "use_case": use_case,
                    "requirements": req,
                })
                gov = await self.agents["designer"].execute({
                    "type": "governance_setup",
                    "use_case": use_case,
                })
                designs.append({
                    "use_case": use_case,
                    "requirements": req,
                    "architecture": arch,
                    "governance": gov,
                })
            except Exception as e:
                designs.append({"use_case": use_case, "error": str(e)})

        return {
            "use_case_designs": designs,
            "current_stage": "use_case_design",
            "execution_log": state.get("execution_log", []) + [{
                "node": "use_case_design",
                "status": "success",
                "design_count": len(designs),
                "timestamp": datetime.now().isoformat(),
            }],
        }

    async def _roi_analysis_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """ROI 분석"""
        self.logger.info("[LangGraph] ROI 분석 노드 실행", state.get("project_id", ""))

        company = state.get("company_profile", {})
        budget = company.get("financial_resources", {}).get("ai_investment_budget", 1000000)

        try:
            result = await self.agents["roi"].execute({
                "type": "roi_calculation",
                "investment": budget,
                "expected_benefits": {
                    "cost_reduction": budget * 0.3,
                    "revenue_increase": budget * 0.2,
                    "productivity_gain": budget * 0.15,
                },
                "period_months": 36,
            })

            return {
                "roi_analysis": result,
                "current_stage": "roi_analysis",
                "execution_log": state.get("execution_log", []) + [{
                    "node": "roi_analysis",
                    "status": "success",
                    "roi_percent": result.get("metrics", {}).get("roi_percent", 0),
                    "timestamp": datetime.now().isoformat(),
                }],
            }
        except Exception as e:
            return {
                "errors": state.get("errors", []) + [f"ROI 분석 실패: {str(e)}"],
            }

    async def _risk_assessment_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """리스크 평가"""
        self.logger.info("[LangGraph] 리스크 평가 노드 실행", state.get("project_id", ""))

        from src.models.schemas import CompanyProfile
        company = CompanyProfile(**state["company_profile"])
        use_cases = state.get("opportunities", {}).get("opportunities", [])

        try:
            result = await self.agents["risk"].execute({
                "type": "full_assessment",
                "company_profile": company,
                "use_cases": use_cases,
            })

            return {
                "risk_assessment": result,
                "current_stage": "risk_assessment",
                "execution_log": state.get("execution_log", []) + [{
                    "node": "risk_assessment",
                    "status": "success",
                    "risk_level": result.get("risk_level", "unknown"),
                    "timestamp": datetime.now().isoformat(),
                }],
            }
        except Exception as e:
            return {
                "errors": state.get("errors", []) + [f"리스크 평가 실패: {str(e)}"],
            }

    async def _quality_check_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """품질 검사 노드: 전체 분석 결과의 완성도 평가"""
        self.logger.info("[LangGraph] 품질 검사 노드 실행", state.get("project_id", ""))

        score = 0.0
        checks = {}

        # 성숙도 진단 완성도
        maturity = state.get("maturity_assessment")
        if maturity and "scores" in maturity:
            score += 20
            checks["maturity"] = "pass"
        else:
            checks["maturity"] = "fail"

        # 기회 발굴 완성도
        opps = state.get("opportunities")
        if opps and len(opps.get("opportunities", [])) > 0:
            score += 20
            checks["opportunities"] = "pass"
        else:
            checks["opportunities"] = "fail"

        # 로드맵 완성도
        roadmap = state.get("roadmap")
        if roadmap:
            score += 15
            checks["roadmap"] = "pass"
        else:
            checks["roadmap"] = "fail"

        # ROI 분석 완성도
        roi = state.get("roi_analysis")
        if roi and "metrics" in roi:
            score += 25
            checks["roi"] = "pass"
        else:
            checks["roi"] = "fail"

        # 리스크 평가 완성도
        risk = state.get("risk_assessment")
        if risk and "risks_by_category" in risk:
            score += 20
            checks["risk"] = "pass"
        else:
            checks["risk"] = "fail"

        iteration = state.get("iteration_count", 0) + 1

        return {
            "quality_score": score,
            "iteration_count": iteration,
            "current_stage": "quality_check",
            "execution_log": state.get("execution_log", []) + [{
                "node": "quality_check",
                "status": "success",
                "quality_score": score,
                "checks": checks,
                "iteration": iteration,
                "timestamp": datetime.now().isoformat(),
            }],
        }

    async def _report_generation_node(self, state: ConsultingGraphState) -> Dict[str, Any]:
        """보고서 생성"""
        self.logger.info("[LangGraph] 보고서 생성 노드 실행", state.get("project_id", ""))

        report_data = {
            "overview": {
                "project_id": state.get("project_id", ""),
                "company": state.get("company_profile", {}).get("name", "Unknown"),
            },
            "assessment": state.get("maturity_assessment"),
            "use_cases": state.get("opportunities", {}).get("opportunities", []),
            "roi_analysis": state.get("roi_analysis"),
            "risk_assessment": state.get("risk_assessment"),
            "roadmap": state.get("roadmap"),
        }

        try:
            result = await self.agents["report"].execute({
                "report_type": "executive_summary",
                "data": report_data,
            })

            return {
                "report": result,
                "current_stage": "completed",
                "completed_at": datetime.now().isoformat(),
                "execution_log": state.get("execution_log", []) + [{
                    "node": "report_generation",
                    "status": "success",
                    "timestamp": datetime.now().isoformat(),
                }],
            }
        except Exception as e:
            return {
                "report": {"error": str(e), "status": "failed"},
                "errors": state.get("errors", []) + [f"보고서 생성 실패: {str(e)}"],
            }

    # ==================== 조건부 엣지 ====================

    def _should_continue_or_report(self, state: ConsultingGraphState) -> str:
        """품질 점수에 따라 재시도 또는 보고서 생성 결정"""
        quality_score = state.get("quality_score", 0)
        iteration = state.get("iteration_count", 0)
        max_iter = state.get("max_iterations", 2)

        if quality_score >= 60 or iteration >= max_iter:
            self.logger.info(
                f"[LangGraph] 보고서 생성 진행 (품질: {quality_score}, 반복: {iteration})",
                state.get("project_id", ""),
            )
            return "report"
        else:
            self.logger.info(
                f"[LangGraph] 재분석 필요 (품질: {quality_score}, 반복: {iteration}/{max_iter})",
                state.get("project_id", ""),
            )
            return "retry_strategy"

    # ==================== 실행 API ====================

    async def run_consultation(
        self,
        project_id: str,
        company_profile: Dict[str, Any],
        max_iterations: int = 2,
    ) -> Dict[str, Any]:
        """전체 컨설팅 워크플로우 실행"""
        self.logger.info(f"[LangGraph] 컨설팅 워크플로우 시작: {project_id}", project_id)

        initial_state: ConsultingGraphState = {
            "project_id": project_id,
            "company_profile": company_profile,
            "maturity_assessment": None,
            "opportunities": None,
            "roadmap": None,
            "use_case_designs": [],
            "roi_analysis": None,
            "risk_assessment": None,
            "report": None,
            "current_stage": "start",
            "iteration_count": 0,
            "quality_score": 0.0,
            "max_iterations": max_iterations,
            "errors": [],
            "messages": [],
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "execution_log": [],
        }

        # LangGraph 비동기 실행
        final_state = await self.compiled_graph.ainvoke(initial_state)

        self.logger.info(
            f"[LangGraph] 워크플로우 완료 - 품질: {final_state.get('quality_score', 0)}, "
            f"반복: {final_state.get('iteration_count', 0)}",
            project_id,
        )

        return {
            "framework": "langgraph",
            "project_id": project_id,
            "status": "completed" if final_state.get("report") else "failed",
            "quality_score": final_state.get("quality_score", 0),
            "iteration_count": final_state.get("iteration_count", 0),
            "results": {
                "maturity_assessment": final_state.get("maturity_assessment"),
                "opportunities": final_state.get("opportunities"),
                "roadmap": final_state.get("roadmap"),
                "use_case_designs": final_state.get("use_case_designs", []),
                "roi_analysis": final_state.get("roi_analysis"),
                "risk_assessment": final_state.get("risk_assessment"),
                "report": final_state.get("report"),
            },
            "execution_log": final_state.get("execution_log", []),
            "errors": final_state.get("errors", []),
            "started_at": final_state.get("started_at"),
            "completed_at": final_state.get("completed_at"),
        }

    def get_graph_visualization(self) -> Dict[str, Any]:
        """그래프 구조 시각화 데이터 반환"""
        return {
            "nodes": [
                {"id": "node_strategy", "label": "전략 분석 (성숙도 진단)", "stage": 1},
                {"id": "node_opportunity", "label": "기회 발굴", "stage": 1},
                {"id": "node_roadmap", "label": "로드맵 수립", "stage": 1},
                {"id": "node_design", "label": "Use Case 설계", "stage": 2},
                {"id": "node_roi", "label": "ROI 분석", "stage": 3},
                {"id": "node_risk", "label": "리스크 평가", "stage": 3},
                {"id": "node_quality", "label": "품질 검사", "stage": "control"},
                {"id": "node_report", "label": "보고서 생성", "stage": 4},
            ],
            "edges": [
                {"from": "START", "to": "node_strategy"},
                {"from": "node_strategy", "to": "node_opportunity"},
                {"from": "node_opportunity", "to": "node_roadmap"},
                {"from": "node_roadmap", "to": "node_design"},
                {"from": "node_design", "to": "node_roi"},
                {"from": "node_roi", "to": "node_risk"},
                {"from": "node_risk", "to": "node_quality"},
                {"from": "node_quality", "to": "node_report", "condition": "quality >= 60 or max_iter"},
                {"from": "node_quality", "to": "node_strategy", "condition": "quality < 60 (retry)"},
                {"from": "node_report", "to": "END"},
            ],
        }


# 싱글톤 인스턴스
_langgraph_orchestrator: Optional[LangGraphOrchestrator] = None


def get_langgraph_orchestrator() -> LangGraphOrchestrator:
    """LangGraph Orchestrator 싱글톤 인스턴스 반환"""
    global _langgraph_orchestrator
    if _langgraph_orchestrator is None:
        _langgraph_orchestrator = LangGraphOrchestrator()
    return _langgraph_orchestrator
