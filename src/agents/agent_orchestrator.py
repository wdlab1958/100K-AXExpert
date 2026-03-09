"""
AI Consulting Assistant Platform - Agent Orchestrator
LangGraph 기반 멀티 에이전트 협업 오케스트레이터
"""
from typing import Optional, List, Dict, Any, Annotated, TypedDict
from datetime import datetime
import asyncio
import uuid
from enum import Enum

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from src.agents.base_agent import BaseConsultingAgent, AgentMessage, AgentState
from src.agents.strategy_analyst import StrategyAnalystAgent
from src.agents.usecase_designer import UseCaseDesignerAgent
from src.agents.roi_analyst import ROIAnalystAgent
from src.agents.risk_assessor import RiskAssessorAgent
from src.agents.report_generator import ReportGeneratorAgent
from src.models.schemas import (
    CompanyProfile, ConsultingProject, ConsultingStage,
    Scenario, ScenarioParameters, HumanFeedback, MaturityAssessment
)
from src.core.llm_provider import get_llm_provider
from src.utils.consulting_logger import get_consulting_logger


class WorkflowState(TypedDict):
    """워크플로우 상태"""
    project_id: str
    current_stage: ConsultingStage
    company_profile: Dict[str, Any]
    maturity_assessment: Optional[Dict[str, Any]]
    use_cases: List[Dict[str, Any]]
    scenarios: List[Dict[str, Any]]
    selected_scenario: Optional[str]
    roi_analysis: Optional[Dict[str, Any]]
    risk_assessment: Optional[Dict[str, Any]]
    reports: List[Dict[str, Any]]
    human_feedback: List[Dict[str, Any]]
    pending_approval: bool
    messages: List[Dict[str, Any]]
    errors: List[str]


class ConsultingOrchestrator:
    """컨설팅 에이전트 오케스트레이터

    멀티 에이전트 협업을 조율하고, 컨설팅 워크플로우를 관리합니다.
    인간 전문가와 AI 에이전트 간의 협업을 지원합니다.
    """

    def __init__(self):
        self.llm_provider = get_llm_provider()
        self.logger = get_consulting_logger()

        # 전문 에이전트 초기화
        self.agents: Dict[str, BaseConsultingAgent] = {
            "strategy": StrategyAnalystAgent(self.llm_provider),
            "designer": UseCaseDesignerAgent(self.llm_provider),
            "roi": ROIAnalystAgent(self.llm_provider),
            "risk": RiskAssessorAgent(self.llm_provider),
            "report": ReportGeneratorAgent(self.llm_provider)
        }

        # 에이전트 간 연결
        self._connect_agents()

        # 프로젝트 상태 저장소
        self.projects: Dict[str, WorkflowState] = {}

        # 이벤트 핸들러
        self.event_handlers: Dict[str, List[callable]] = {}

    def _connect_agents(self):
        """에이전트 간 협업 연결"""
        for agent in self.agents.values():
            for other_agent in self.agents.values():
                if agent != other_agent:
                    agent.connect_agent(other_agent)

    # ==================== 프로젝트 관리 ====================

    def create_project(self, name: str, company_profile: CompanyProfile) -> str:
        """새 컨설팅 프로젝트 생성"""
        project_id = str(uuid.uuid4())

        self.projects[project_id] = WorkflowState(
            project_id=project_id,
            current_stage=ConsultingStage.STRATEGY,
            company_profile=company_profile.model_dump(),
            maturity_assessment=None,
            use_cases=[],
            scenarios=[],
            selected_scenario=None,
            roi_analysis=None,
            risk_assessment=None,
            reports=[],
            human_feedback=[],
            pending_approval=False,
            messages=[],
            errors=[]
        )

        self.logger.info(f"프로젝트 생성: {name} (ID: {project_id})", project_id)
        self._emit_event("project_created", {"project_id": project_id, "name": name})
        return project_id

    def get_project(self, project_id: str) -> Optional[WorkflowState]:
        """프로젝트 조회"""
        return self.projects.get(project_id)

    def update_project(self, project_id: str, updates: Dict[str, Any]) -> Optional[WorkflowState]:
        """프로젝트 데이터 업데이트"""
        project = self.projects.get(project_id)
        if not project:
            return None
        project.update(updates)
        return project

    def get_project_status(self, project_id: str) -> Dict[str, Any]:
        """프로젝트 상태 조회"""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}

        return {
            "project_id": project_id,
            "current_stage": project["current_stage"].name,
            "stage_number": project["current_stage"].value,
            "has_maturity_assessment": project["maturity_assessment"] is not None,
            "use_case_count": len(project["use_cases"]),
            "scenario_count": len(project["scenarios"]),
            "selected_scenario": project["selected_scenario"],
            "pending_approval": project["pending_approval"],
            "feedback_count": len(project["human_feedback"]),
            "report_count": len(project["reports"])
        }

    # ==================== 1단계: AI 전략 수립 ====================

    async def run_maturity_assessment(self, project_id: str) -> Dict[str, Any]:
        """AI 성숙도 진단 실행"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return {"error": "Project not found"}

        self.logger.agent_start("전략 분석가", "AI 성숙도 진단", project_id)
        company = CompanyProfile(**project["company_profile"])

        try:
            # Strategy Agent 실행
            result = await self.agents["strategy"].execute({
                "type": "maturity_assessment",
                "company_profile": company
            })

            # 결과 저장
            project["maturity_assessment"] = result
            self._add_message(project_id, "strategy", "maturity_assessment", result)

            self.logger.agent_complete("전략 분석가", "AI 성숙도 진단", project_id, result)

            # 이벤트 발생
            self._emit_event("maturity_assessment_completed", {
                "project_id": project_id,
                "result": result
            })

            return result
        except Exception as e:
            self.logger.agent_error("전략 분석가", "AI 성숙도 진단", e, project_id)
            raise

    async def identify_opportunities(self, project_id: str) -> Dict[str, Any]:
        """AI 도입 기회 발굴"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return {"error": "Project not found"}

        self.logger.agent_start("전략 분석가", "AI 도입 기회 발굴", project_id)
        company = CompanyProfile(**project["company_profile"])

        try:
            result = await self.agents["strategy"].execute({
                "type": "opportunity_identification",
                "company_profile": company
            })

            # Use Case 목록 업데이트
            if "opportunities" in result:
                project["use_cases"] = result["opportunities"]
                self.logger.progress(f"발굴된 기회: {len(result.get('opportunities', []))}개", project_id)

            self._add_message(project_id, "strategy", "opportunity_identification", result)
            self.logger.agent_complete("전략 분석가", "AI 도입 기회 발굴", project_id, result)

            return result
        except Exception as e:
            self.logger.agent_error("전략 분석가", "AI 도입 기회 발굴", e, project_id)
            raise

    async def create_roadmap(self, project_id: str) -> Dict[str, Any]:
        """AI 도입 로드맵 수립"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return {"error": "Project not found"}

        self.logger.agent_start("전략 분석가", "AI 도입 로드맵 수립", project_id)
        company = CompanyProfile(**project["company_profile"])

        try:
            result = await self.agents["strategy"].execute({
                "type": "roadmap_planning",
                "company_profile": company,
                "use_cases": project["use_cases"]
            })

            self._add_message(project_id, "strategy", "roadmap_planning", result)
            self.logger.agent_complete("전략 분석가", "AI 도입 로드맵 수립", project_id, result)

            return result
        except Exception as e:
            self.logger.agent_error("전략 분석가", "AI 도입 로드맵 수립", e, project_id)
            raise

    # ==================== 2단계: Use Case 설계 ====================

    async def design_use_case(self, project_id: str, use_case_index: int) -> Dict[str, Any]:
        """Use Case 상세 설계"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return {"error": "Project not found"}

        if use_case_index >= len(project["use_cases"]):
            self.logger.error(f"Use Case 인덱스 오류: {use_case_index}", project_id)
            return {"error": "Use case not found"}

        use_case = project["use_cases"][use_case_index]
        use_case_name = use_case.get("name", f"Use Case {use_case_index + 1}")
        
        self.logger.agent_start("Use Case 설계자", f"Use Case 설계: {use_case_name}", project_id)

        try:
            # 요건 정의
            self.logger.progress(f"  → 요건 정의 중...", project_id)
            requirements = await self.agents["designer"].execute({
                "type": "requirements_definition",
                "use_case": use_case
            })

            # 아키텍처 설계
            self.logger.progress(f"  → 아키텍처 설계 중...", project_id)
            architecture = await self.agents["designer"].execute({
                "type": "architecture_design",
                "use_case": use_case,
                "requirements": requirements
            })

            # 거버넌스 설정
            self.logger.progress(f"  → 거버넌스 체계 수립 중...", project_id)
            governance = await self.agents["designer"].execute({
                "type": "governance_setup",
                "use_case": use_case
            })

            result = {
                "use_case": use_case,
                "requirements": requirements,
                "architecture": architecture,
                "governance": governance
            }

            # Use Case 업데이트
            project["use_cases"][use_case_index]["design"] = result

            self._add_message(project_id, "designer", "use_case_design", result)
            self.logger.agent_complete("Use Case 설계자", f"Use Case 설계: {use_case_name}", project_id, result)

            return result
        except Exception as e:
            self.logger.agent_error("Use Case 설계자", f"Use Case 설계: {use_case_name}", e, project_id)
            raise

    # ==================== 시나리오 분석 ====================

    async def generate_scenarios(
        self,
        project_id: str,
        scenario_types: List[str] = ["conservative", "balanced", "aggressive"]
    ) -> List[Dict[str, Any]]:
        """다양한 시나리오 생성"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return [{"error": "Project not found"}]

        self.logger.agent_start("오케스트레이터", f"시나리오 생성 ({len(scenario_types)}개)", project_id)
        company = CompanyProfile(**project["company_profile"])
        budget = company.financial_resources.ai_investment_budget

        scenarios = []

        for i, scenario_type in enumerate(scenario_types, 1):
            scenario_name_map = {
                "conservative": "보수적 시나리오",
                "balanced": "균형 시나리오",
                "aggressive": "적극적 시나리오"
            }
            scenario_name = scenario_name_map.get(scenario_type, scenario_type)
            self.logger.progress(f"  → {scenario_name} 생성 중... ({i}/{len(scenario_types)})", project_id)
            
            try:
                scenario = await self._create_scenario(project_id, scenario_type, budget)
                scenarios.append(scenario)
                self.logger.progress(f"  ✅ {scenario_name} 생성 완료", project_id)
            except Exception as e:
                self.logger.error(f"시나리오 생성 실패 ({scenario_name}): {str(e)}", project_id)
                raise

        project["scenarios"] = scenarios
        self._add_message(project_id, "orchestrator", "scenario_generation", {"scenarios": scenarios})

        # 인간 검토를 위해 대기 상태로 설정
        project["pending_approval"] = True

        self.logger.agent_complete("오케스트레이터", f"시나리오 생성 ({len(scenarios)}개)", project_id)
        self.logger.info(f"생성된 시나리오: {len(scenarios)}개 (승인 대기 중)", project_id)

        self._emit_event("scenarios_generated", {
            "project_id": project_id,
            "scenario_count": len(scenarios)
        })

        return scenarios

    async def _create_scenario(
        self,
        project_id: str,
        scenario_type: str,
        base_budget: float
    ) -> Dict[str, Any]:
        """개별 시나리오 생성"""
        project = self.projects.get(project_id)

        # 시나리오 유형별 파라미터
        params_map = {
            "conservative": {
                "name": "보수적 시나리오",
                "budget_ratio": 0.6,
                "risk_appetite": "low",
                "timeline_months": 18,
                "focus": "Quick Win 과제 집중"
            },
            "balanced": {
                "name": "균형 시나리오",
                "budget_ratio": 1.0,
                "risk_appetite": "medium",
                "timeline_months": 24,
                "focus": "단기 성과와 중기 역량 구축 병행"
            },
            "aggressive": {
                "name": "적극적 시나리오",
                "budget_ratio": 1.5,
                "risk_appetite": "high",
                "timeline_months": 36,
                "focus": "비즈니스 혁신 및 전사 확산"
            }
        }

        params = params_map.get(scenario_type, params_map["balanced"])
        investment = base_budget * params["budget_ratio"]

        # Use Case 선택
        use_cases = project["use_cases"]
        selected_use_cases = self._select_use_cases_for_scenario(use_cases, scenario_type)

        # ROI 분석
        self.logger.progress(f"    → ROI 분석 중...", project_id)
        roi_result = await self.agents["roi"].execute({
            "type": "roi_calculation",
            "investment": investment,
            "expected_benefits": {
                "cost_reduction": investment * 0.3,
                "revenue_increase": investment * 0.2,
                "productivity_gain": investment * 0.15
            },
            "period_months": params["timeline_months"]
        })

        # 리스크 평가
        self.logger.progress(f"    → 리스크 평가 중...", project_id)
        company = CompanyProfile(**project["company_profile"])
        risk_result = await self.agents["risk"].execute({
            "type": "full_assessment",
            "company_profile": company,
            "use_cases": selected_use_cases
        })

        scenario = {
            "id": str(uuid.uuid4()),
            "type": scenario_type,
            "name": params["name"],
            "description": params["focus"],
            "parameters": {
                "investment_budget": investment,
                "timeline_months": params["timeline_months"],
                "risk_appetite": params["risk_appetite"]
            },
            "selected_use_cases": selected_use_cases,
            "roi_analysis": roi_result,
            "risk_assessment": risk_result,
            "overall_score": self._calculate_scenario_score(roi_result, risk_result),
            "created_at": datetime.now().isoformat()
        }

        return scenario

    def _select_use_cases_for_scenario(
        self,
        use_cases: List[Dict],
        scenario_type: str
    ) -> List[Dict]:
        """시나리오 유형에 맞는 Use Case 선택"""
        if not use_cases:
            return []

        if scenario_type == "conservative":
            # 높은 적합도, 낮은 복잡성
            return [uc for uc in use_cases if uc.get("fit_score", 0) > 60][:2]
        elif scenario_type == "balanced":
            # 상위 50%
            sorted_cases = sorted(use_cases, key=lambda x: x.get("fit_score", 0), reverse=True)
            return sorted_cases[:len(sorted_cases)//2 + 1]
        else:  # aggressive
            # 전체
            return use_cases

    def _calculate_scenario_score(
        self,
        roi_result: Dict,
        risk_result: Dict
    ) -> float:
        """시나리오 종합 점수 계산"""
        roi_score = min(roi_result.get("metrics", {}).get("roi_percent", 0) / 10, 10)
        risk_score = 10 - risk_result.get("total_risk_score", 5)

        return round((roi_score * 0.6 + risk_score * 0.4), 2)

    # ==================== 인간-AI 협업 ====================

    async def submit_human_feedback(
        self,
        project_id: str,
        feedback: HumanFeedback
    ) -> Dict[str, Any]:
        """인간 전문가 피드백 제출"""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}

        # 피드백 저장
        project["human_feedback"].append(feedback.model_dump())

        # AI 응답 생성
        ai_response = await self._process_human_feedback(project_id, feedback)

        # 피드백 처리 결과 반환
        return {
            "feedback_id": feedback.id,
            "status": "processed",
            "ai_response": ai_response,
            "action_taken": self._determine_action(feedback)
        }

    async def _process_human_feedback(
        self,
        project_id: str,
        feedback: HumanFeedback
    ) -> str:
        """인간 피드백 처리"""
        if feedback.feedback_type == "approval":
            return "승인되었습니다. 다음 단계로 진행합니다."
        elif feedback.feedback_type == "rejection":
            return "반려되었습니다. 수정 후 재제출이 필요합니다."
        elif feedback.feedback_type == "modification":
            return "수정 요청을 반영하여 재분석을 진행하겠습니다."
        elif feedback.feedback_type == "question":
            # LLM을 통한 질문 응답
            if self.llm_provider:
                response = await self.llm_provider.consult(
                    feedback.content,
                    {"project_id": project_id},
                    "general"
                )
                return response
        return "피드백이 접수되었습니다."

    def _determine_action(self, feedback: HumanFeedback) -> str:
        """피드백에 따른 액션 결정"""
        actions = {
            "approval": "proceed_to_next_stage",
            "rejection": "revise_and_resubmit",
            "modification": "apply_changes",
            "question": "provide_information"
        }
        return actions.get(feedback.feedback_type, "review")

    async def approve_scenario(
        self,
        project_id: str,
        scenario_id: str,
        approver_name: str,
        approver_role: str,
        comments: str = ""
    ) -> Dict[str, Any]:
        """시나리오 승인"""
        project = self.projects.get(project_id)
        if not project:
            return {"error": "Project not found"}

        # 시나리오 찾기
        scenario = None
        for s in project["scenarios"]:
            if s["id"] == scenario_id:
                scenario = s
                break

        if not scenario:
            return {"error": "Scenario not found"}

        # 승인 처리
        project["selected_scenario"] = scenario_id
        project["pending_approval"] = False

        # 피드백 기록
        feedback = HumanFeedback(
            feedback_type="approval",
            stage=project["current_stage"],
            content=f"시나리오 '{scenario['name']}' 승인. {comments}",
            reviewer_role=approver_role,
            reviewer_name=approver_name
        )
        project["human_feedback"].append(feedback.model_dump())

        # 다음 단계로 진행
        if project["current_stage"].value < ConsultingStage.OPERATE.value:
            project["current_stage"] = ConsultingStage(project["current_stage"].value + 1)

        self._emit_event("scenario_approved", {
            "project_id": project_id,
            "scenario_id": scenario_id,
            "approver": approver_name
        })

        return {
            "status": "approved",
            "selected_scenario": scenario,
            "next_stage": project["current_stage"].name
        }

    # ==================== 보고서 생성 ====================

    async def generate_report(
        self,
        project_id: str,
        report_type: str = "executive_summary"
    ) -> Dict[str, Any]:
        """컨설팅 보고서 생성"""
        project = self.projects.get(project_id)
        if not project:
            self.logger.error("프로젝트를 찾을 수 없습니다", project_id)
            return {"error": "Project not found"}

        report_type_name = {
            "executive_summary": "경영진 요약 보고서",
            "full_report": "전체 보고서",
            "strategy_proposal": "전략 제안서"
        }.get(report_type, report_type)

        self.logger.agent_start("보고서 생성 전문가", f"보고서 생성: {report_type_name}", project_id)

        try:
            # 보고서 데이터 수집
            self.logger.progress("  → 보고서 데이터 수집 중...", project_id)
            report_data = {
                "overview": {
                    "project_id": project_id,
                    "company": project["company_profile"].get("name", "Unknown"),
                    "industry": project["company_profile"].get("industry", "Unknown")
                },
                "assessment": project["maturity_assessment"],
                "use_cases": project["use_cases"],
                "scenarios": project["scenarios"],
                "selected_scenario": self._get_selected_scenario(project),
                "recommendations": self._compile_recommendations(project),
                "expected_benefits": self._compile_benefits(project),
                "roadmap": self._compile_roadmap(project)
            }

            # 보고서 생성
            self.logger.progress("  → 보고서 작성 중...", project_id)
            result = await self.agents["report"].execute({
                "report_type": report_type,
                "data": report_data
            })

            # 보고서 저장
            report = {
                "id": str(uuid.uuid4()),
                "type": report_type,
                "content": result,
                "generated_at": datetime.now().isoformat()
            }
            project["reports"].append(report)

            self.logger.agent_complete("보고서 생성 전문가", f"보고서 생성: {report_type_name}", project_id)
            self.logger.info(f"보고서 생성 완료 (ID: {report['id']})", project_id)

            self._emit_event("report_generated", {
                "project_id": project_id,
                "report_id": report["id"],
                "report_type": report_type
            })

            return report
        except Exception as e:
            self.logger.agent_error("보고서 생성 전문가", f"보고서 생성: {report_type_name}", e, project_id)
            raise

    def _get_selected_scenario(self, project: WorkflowState) -> Optional[Dict]:
        """선택된 시나리오 반환"""
        if not project["selected_scenario"]:
            return None

        for s in project["scenarios"]:
            if s["id"] == project["selected_scenario"]:
                return s
        return None

    def _compile_recommendations(self, project: WorkflowState) -> List[str]:
        """권고사항 종합"""
        recommendations = []

        if project["maturity_assessment"]:
            recommendations.extend(
                project["maturity_assessment"].get("recommendations", [])
            )

        if project["risk_assessment"]:
            recommendations.extend(
                project["risk_assessment"].get("mitigation_priorities", [])
            )

        return recommendations[:10]

    def _compile_benefits(self, project: WorkflowState) -> Dict[str, Any]:
        """기대 효과 종합"""
        selected = self._get_selected_scenario(project)
        if selected and "roi_analysis" in selected:
            return selected["roi_analysis"].get("benefits", {})
        return {}

    def _compile_roadmap(self, project: WorkflowState) -> Dict[str, Any]:
        """로드맵 종합"""
        # 메시지에서 로드맵 찾기
        for msg in project["messages"]:
            if msg.get("task_type") == "roadmap_planning":
                return msg.get("result", {})
        return {}

    # ==================== 전체 워크플로우 실행 ====================

    async def run_full_consultation(
        self,
        project_id: str,
        auto_approve: bool = False
    ) -> Dict[str, Any]:
        """전체 컨설팅 워크플로우 실행"""
        self.logger.info("=" * 70, project_id)
        self.logger.info("🚀 전체 컨설팅 프로세스 시작", project_id)
        self.logger.info("=" * 70, project_id)
        
        if auto_approve:
            self.logger.info("⚠️  자동 승인 모드 활성화", project_id)
        
        results = {
            "project_id": project_id,
            "stages": {}
        }

        try:
            # 1단계: 전략 수립
            self.logger.stage_start("1단계: AI 전략 수립", project_id)
            self._emit_event("stage_started", {"project_id": project_id, "stage": "strategy"})

            maturity = await self.run_maturity_assessment(project_id)
            results["stages"]["maturity_assessment"] = maturity

            opportunities = await self.identify_opportunities(project_id)
            results["stages"]["opportunities"] = opportunities

            roadmap = await self.create_roadmap(project_id)
            results["stages"]["roadmap"] = roadmap

            self.logger.stage_complete("1단계: AI 전략 수립", project_id)

            # 2단계: Use Case 설계 (상위 3개)
            self.logger.stage_start("2단계: Use Case 설계", project_id)
            self._emit_event("stage_started", {"project_id": project_id, "stage": "design"})

            project = self.projects[project_id]
            use_case_count = min(3, len(project["use_cases"]))
            self.logger.progress(f"설계할 Use Case 수: {use_case_count}개", project_id)
            
            for i in range(use_case_count):
                design = await self.design_use_case(project_id, i)
                results["stages"][f"use_case_{i}_design"] = design

            self.logger.stage_complete("2단계: Use Case 설계", project_id)

            # 시나리오 생성
            self.logger.stage_start("시나리오 분석", project_id)
            scenarios = await self.generate_scenarios(project_id)
            results["stages"]["scenarios"] = scenarios
            self.logger.stage_complete("시나리오 분석", project_id)

            # 자동 승인 모드
            if auto_approve and scenarios:
                self.logger.info("자동 승인 처리 중...", project_id)
                # 가장 높은 점수의 시나리오 선택
                best_scenario = max(scenarios, key=lambda x: x.get("overall_score", 0))
                self.logger.info(f"선택된 시나리오: {best_scenario.get('name', 'Unknown')} (점수: {best_scenario.get('overall_score', 0)})", project_id)
                
                approval = await self.approve_scenario(
                    project_id,
                    best_scenario["id"],
                    "Auto Approver",
                    "system"
                )
                results["stages"]["approval"] = approval

            # 보고서 생성
            self.logger.stage_start("보고서 생성", project_id)
            report = await self.generate_report(project_id, "executive_summary")
            results["stages"]["report"] = report
            self.logger.stage_complete("보고서 생성", project_id)

            results["status"] = "completed" if auto_approve else "pending_approval"
            results["final_status"] = self.get_project_status(project_id)

            self.logger.info("=" * 70, project_id)
            self.logger.info("✅ 전체 컨설팅 프로세스 완료", project_id)
            self.logger.info(f"최종 상태: {results['status']}", project_id)
            self.logger.info("=" * 70, project_id)

            return results
        except Exception as e:
            self.logger.error(f"컨설팅 프로세스 중 오류 발생: {str(e)}", project_id, exc_info=True)
            self.logger.info("=" * 70, project_id)
            self.logger.info("❌ 전체 컨설팅 프로세스 실패", project_id)
            self.logger.info("=" * 70, project_id)
            raise

    # ==================== 유틸리티 ====================

    def _add_message(
        self,
        project_id: str,
        agent_id: str,
        task_type: str,
        result: Dict
    ):
        """메시지 추가"""
        project = self.projects.get(project_id)
        if project:
            project["messages"].append({
                "id": str(uuid.uuid4()),
                "agent_id": agent_id,
                "task_type": task_type,
                "result": result,
                "timestamp": datetime.now().isoformat()
            })

    def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """이벤트 발생"""
        handlers = self.event_handlers.get(event_type, [])
        for handler in handlers:
            try:
                handler(data)
            except Exception as e:
                print(f"Event handler error: {e}")

    def on_event(self, event_type: str, handler: callable):
        """이벤트 핸들러 등록"""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)

    def get_agent_status(self) -> Dict[str, Any]:
        """모든 에이전트 상태 조회"""
        return {
            agent_id: agent.to_dict()
            for agent_id, agent in self.agents.items()
        }


# 싱글톤 인스턴스
_orchestrator: Optional[ConsultingOrchestrator] = None


def get_orchestrator() -> ConsultingOrchestrator:
    """Orchestrator 싱글톤 인스턴스 반환"""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = ConsultingOrchestrator()
    return _orchestrator
