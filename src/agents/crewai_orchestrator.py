"""
CrewAI 기반 멀티 에이전트 역할 협업 오케스트레이터
역할(Role) 기반 에이전트 팀 구성 및 순차/계층적 협업 프로세스 지원
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
import asyncio
import json
import os

# CrewAI는 초기화 시 OPENAI_API_KEY를 요구함 - Ollama만 사용하므로 더미 값 설정
if not os.environ.get("OPENAI_API_KEY"):
    os.environ["OPENAI_API_KEY"] = "sk-not-used-ollama-only"

from crewai import Agent, Task, Crew, Process
from langchain_community.llms import Ollama

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


class CrewAIOrchestrator:
    """CrewAI 기반 컨설팅 에이전트 오케스트레이터

    CrewAI의 역할(Role) 기반 에이전트 시스템을 활용하여
    5개 전문 컨설팅 에이전트의 협업을 조율합니다.

    특징:
    - 역할/목표/배경 기반 에이전트 정의
    - 순차적(Sequential) 및 계층적(Hierarchical) 프로세스 지원
    - 태스크 간 컨텍스트 자동 전달
    - Ollama 로컬 LLM 통합
    """

    def __init__(self):
        self.logger = get_consulting_logger()
        self.llm_provider = get_llm_provider()

        # CrewAI용 Ollama LLM 인스턴스
        self.llm = Ollama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            temperature=0.7,
        )

        # 기존 100K-AX Expert 에이전트 (규칙 기반 로직 재사용)
        self.native_agents = {
            "strategy": StrategyAnalystAgent(self.llm_provider),
            "designer": UseCaseDesignerAgent(self.llm_provider),
            "roi": ROIAnalystAgent(self.llm_provider),
            "risk": RiskAssessorAgent(self.llm_provider),
            "report": ReportGeneratorAgent(self.llm_provider),
        }

        # CrewAI 에이전트 생성
        self.crew_agents = self._create_agents()

    def _create_agents(self) -> Dict[str, Agent]:
        """CrewAI 에이전트 생성"""
        agents = {}

        agents["strategy_analyst"] = Agent(
            role="AI 전략 분석가",
            goal="고객사의 AI 성숙도를 정확히 진단하고, AI 도입 기회를 발굴하며, 실현 가능한 전략 및 로드맵을 수립한다.",
            backstory="""당신은 15년 경력의 AI 전략 컨설턴트입니다.
            Fortune 500 기업의 AI 전환 전략을 다수 수립한 경험이 있으며,
            특히 AI 성숙도 진단(4대 영역: 전략/비전, 조직/역량, 데이터/기술, 프로세스/거버넌스)에
            깊은 전문성을 보유하고 있습니다. 객관적이고 데이터 기반의 분석을 제공합니다.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        agents["use_case_designer"] = Agent(
            role="AI Use Case 설계자",
            goal="AI Use Case의 상세 요건을 정의하고, 최적의 기술 아키텍처를 설계하며, 거버넌스 체계를 수립한다.",
            backstory="""당신은 AI 솔루션 설계 전문가입니다.
            데이터 파이프라인, MLOps, 모델 서빙 아키텍처 설계에 풍부한 경험을 보유하고 있으며,
            비즈니스 요구사항과 기술 구현의 정합성을 확보하는 것을 중요시합니다.
            확장성, 유지보수성, 보안을 고려한 아키텍처를 설계합니다.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        agents["roi_analyst"] = Agent(
            role="ROI 분석가",
            goal="AI 투자의 정량적/정성적 ROI를 분석하고, TCO 분석 및 재무적 타당성을 검토하여 최적 투자 방안을 제시한다.",
            backstory="""당신은 AI 투자 ROI 분석 전문가입니다.
            정량적 ROI(비용 절감, 매출 증대, 생산성 향상)와 정성적 효과(고객 만족도, 경쟁력)를
            균형있게 평가하며, 보수적 가정 기반의 현실적 추정을 원칙으로 합니다.
            NPV, IRR, Payback Period 등 재무 분석 도구를 능숙하게 활용합니다.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        agents["risk_assessor"] = Agent(
            role="리스크 평가 전문가",
            goal="AI 프로젝트의 기술적, 조직적, 비즈니스, 운영적 리스크를 종합적으로 평가하고 실행 가능한 완화 전략을 수립한다.",
            backstory="""당신은 AI 프로젝트 리스크 관리 전문가입니다.
            발생 확률과 영향도를 고려한 리스크 등급화, 예방/대응/복구 관점의 종합적 접근,
            실질적이고 실행 가능한 완화 전략 제시를 전문으로 합니다.
            ISO 31000 리스크 관리 프레임워크에 기반합니다.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        agents["report_generator"] = Agent(
            role="컨설팅 보고서 전문가",
            goal="컨설팅 결과를 종합하여 경영진과 실무자 모두가 이해할 수 있는 전문적인 보고서를 생성한다.",
            backstory="""당신은 AI 컨설팅 보고서 작성 전문가입니다.
            경영진용 Executive Summary, 기술 보고서, 전략 제안서 등
            다양한 포맷의 보고서를 작성할 수 있으며, 데이터 기반의 객관적 서술과
            핵심 메시지의 명확한 전달을 중요시합니다.""",
            llm=self.llm,
            verbose=False,
            allow_delegation=False,
        )

        return agents

    def _create_tasks(self, company_profile: Dict[str, Any], project_id: str) -> List[Task]:
        """컨설팅 워크플로우 태스크 생성"""
        company_info = json.dumps(company_profile, ensure_ascii=False, indent=2, default=str)

        tasks = []

        # Task 1: AI 성숙도 진단
        task_maturity = Task(
            description=f"""다음 기업의 AI 성숙도를 진단하세요.

기업 정보:
{company_info}

진단 항목:
1. 전략 및 비전 (AI 비전 명확성, 투자 계획, 전략적 정합성)
2. 조직 및 역량 (AI 전담 인력, 프로젝트 경험, 교육 투자, 변화 관리)
3. 데이터 및 기술 (데이터 인프라, 품질, 클라우드, GPU)
4. 프로세스 및 거버넌스 (개발 방법론, 거버넌스, 보안, 모니터링)

각 영역을 Level 1-5로 평가하고, 종합 성숙도 레벨과 개선 권고사항을 제시하세요.""",
            expected_output="AI 성숙도 진단 결과: 4대 영역별 레벨, 종합 레벨, 강점/약점, 개선 권고사항",
            agent=self.crew_agents["strategy_analyst"],
        )
        tasks.append(task_maturity)

        # Task 2: AI 도입 기회 발굴
        task_opportunities = Task(
            description=f"""이전 성숙도 진단 결과를 바탕으로, 해당 기업에 적합한 AI 도입 기회를 발굴하세요.

기업 정보:
{company_info}

분석 항목:
1. 산업별 주요 AI 활용 사례 분석
2. 기업 상황에 맞는 Use Case 적합도 평가
3. 가치-실행 용이성 매트릭스 기반 우선순위 결정
4. 상위 3개 핵심 기회 영역 도출""",
            expected_output="AI 도입 기회 목록: 적합도 점수 기반 우선순위, 상위 3개 핵심 기회, ROI 잠재력",
            agent=self.crew_agents["strategy_analyst"],
            context=[task_maturity],
        )
        tasks.append(task_opportunities)

        # Task 3: Use Case 상세 설계
        task_design = Task(
            description="""이전 단계에서 발굴한 상위 Use Case에 대해 상세 설계를 수행하세요.

설계 항목:
1. 비즈니스 요구사항 정의 (목표, 성공 기준, KPI)
2. 기술 아키텍처 설계 (데이터 레이어, ML 레이어, 서빙 레이어, 모니터링)
3. AI 거버넌스 체계 (조직, 정책, 프로세스, 리스크 관리)""",
            expected_output="Use Case 상세 설계: 요건 정의서, 아키텍처 설계, 거버넌스 체계",
            agent=self.crew_agents["use_case_designer"],
            context=[task_opportunities],
        )
        tasks.append(task_design)

        # Task 4: ROI 분석
        task_roi = Task(
            description=f"""이전 단계의 Use Case 설계를 바탕으로 ROI 분석을 수행하세요.

분석 항목:
1. 투자 비용 구성 (초기 투자, 연간 운영비, 유지보수비)
2. 기대 효과 (비용 절감, 매출 증대, 생산성 향상)
3. 재무 지표 (ROI%, NPV, IRR, Payback Period)
4. 3년간 TCO 분석
5. 투자 권고사항""",
            expected_output="ROI 분석 보고서: 비용 구성, 기대 효과, 재무 지표(ROI, NPV, IRR), 투자 권고",
            agent=self.crew_agents["roi_analyst"],
            context=[task_design],
        )
        tasks.append(task_roi)

        # Task 5: 리스크 평가
        task_risk = Task(
            description=f"""이전 분석 결과를 종합하여 리스크 평가를 수행하세요.

평가 항목:
1. 기술적 리스크 (데이터 품질, 모델 성능, 시스템 통합)
2. 조직적 리스크 (인력 부족, 변화 저항, 역량 부족)
3. 비즈니스 리스크 (ROI 미달성, 시장 변화, 규제)
4. 운영적 리스크 (시스템 장애, 보안, 모델 드리프트)
5. 완화 전략 우선순위""",
            expected_output="리스크 평가 보고서: 카테고리별 리스크, 종합 위험도, 상위 5개 리스크, 완화 전략",
            agent=self.crew_agents["risk_assessor"],
            context=[task_roi],
        )
        tasks.append(task_risk)

        # Task 6: 종합 보고서 생성
        task_report = Task(
            description="""이전 모든 분석 결과를 종합하여 경영진 요약 보고서(Executive Summary)를 작성하세요.

보고서 구성:
1. 프로젝트 개요
2. 현황 진단 결과 (AI 성숙도)
3. 핵심 AI 도입 기회
4. 투자 대비 효과 (ROI)
5. 주요 리스크 및 완화 전략
6. 실행 로드맵
7. 핵심 권고사항""",
            expected_output="AI 컨설팅 Executive Summary 보고서",
            agent=self.crew_agents["report_generator"],
            context=[task_maturity, task_opportunities, task_design, task_roi, task_risk],
        )
        tasks.append(task_report)

        return tasks

    async def run_consultation(
        self,
        project_id: str,
        company_profile: Dict[str, Any],
        process_type: str = "sequential",
    ) -> Dict[str, Any]:
        """CrewAI 컨설팅 워크플로우 실행"""
        self.logger.info(f"[CrewAI] 컨설팅 시작 (프로세스: {process_type}): {project_id}", project_id)
        started_at = datetime.now().isoformat()

        # 태스크 생성
        tasks = self._create_tasks(company_profile, project_id)

        # Crew 생성
        process = Process.sequential if process_type == "sequential" else Process.hierarchical

        crew_kwargs = {
            "agents": list(self.crew_agents.values()),
            "tasks": tasks,
            "process": process,
            "verbose": False,
        }

        # 계층적 프로세스인 경우 매니저 LLM 설정
        if process_type == "hierarchical":
            crew_kwargs["manager_llm"] = self.llm

        crew = Crew(**crew_kwargs)

        # 규칙 기반 분석도 병행 실행
        from src.models.schemas import CompanyProfile as CP
        native_results = {}

        try:
            company_obj = CP(**company_profile)

            # 규칙 기반 분석 실행 (기존 에이전트 재사용)
            native_results["maturity"] = await self.native_agents["strategy"].execute({
                "type": "maturity_assessment",
                "company_profile": company_obj,
            })
            native_results["opportunities"] = await self.native_agents["strategy"].execute({
                "type": "opportunity_identification",
                "company_profile": company_obj,
            })
            native_results["roadmap"] = await self.native_agents["strategy"].execute({
                "type": "roadmap_planning",
                "company_profile": company_obj,
                "use_cases": native_results["opportunities"].get("opportunities", []),
            })

            budget = company_profile.get("financial_resources", {}).get("ai_investment_budget", 1000000)
            native_results["roi"] = await self.native_agents["roi"].execute({
                "type": "roi_calculation",
                "investment": budget,
                "expected_benefits": {
                    "cost_reduction": budget * 0.3,
                    "revenue_increase": budget * 0.2,
                    "productivity_gain": budget * 0.15,
                },
                "period_months": 36,
            })
            native_results["risk"] = await self.native_agents["risk"].execute({
                "type": "full_assessment",
                "company_profile": company_obj,
                "use_cases": native_results["opportunities"].get("opportunities", []),
            })
        except Exception as e:
            self.logger.error(f"[CrewAI] 규칙 기반 분석 오류: {e}", project_id)

        # CrewAI LLM 기반 실행
        crew_result = None
        crew_output = None
        try:
            loop = asyncio.get_event_loop()
            crew_output = await loop.run_in_executor(None, crew.kickoff)
            crew_result = str(crew_output) if crew_output else None
        except Exception as e:
            self.logger.error(f"[CrewAI] Crew 실행 오류: {e}", project_id)
            crew_result = f"CrewAI 실행 오류: {str(e)}"

        completed_at = datetime.now().isoformat()
        self.logger.info(f"[CrewAI] 컨설팅 완료: {project_id}", project_id)

        # 태스크별 결과 추출
        task_results = []
        for i, task in enumerate(tasks):
            task_results.append({
                "task_index": i,
                "agent": task.agent.role if task.agent else "unknown",
                "description": task.description[:100] + "...",
                "output": str(task.output) if hasattr(task, 'output') and task.output else None,
            })

        return {
            "framework": "crewai",
            "project_id": project_id,
            "status": "completed",
            "process_type": process_type,
            "results": {
                "crew_output": crew_result,
                "task_results": task_results,
                "native_analysis": native_results,
            },
            "agents": [
                {"role": a.role, "goal": a.goal[:100] + "..."}
                for a in self.crew_agents.values()
            ],
            "started_at": started_at,
            "completed_at": completed_at,
        }

    def get_crew_info(self) -> Dict[str, Any]:
        """CrewAI 에이전트 구성 정보 반환"""
        return {
            "framework": "crewai",
            "agents": [
                {
                    "id": key,
                    "role": agent.role,
                    "goal": agent.goal,
                    "backstory": agent.backstory[:200] + "...",
                }
                for key, agent in self.crew_agents.items()
            ],
            "supported_processes": ["sequential", "hierarchical"],
            "llm_model": settings.OLLAMA_MODEL,
        }


# 싱글톤 인스턴스
_crewai_orchestrator: Optional[CrewAIOrchestrator] = None


def get_crewai_orchestrator() -> CrewAIOrchestrator:
    """CrewAI Orchestrator 싱글톤 인스턴스 반환"""
    global _crewai_orchestrator
    if _crewai_orchestrator is None:
        _crewai_orchestrator = CrewAIOrchestrator()
    return _crewai_orchestrator
