"""
Agent Factory
에이전트 팩토리 패턴 구현
"""
from typing import Optional, Dict, Any

from .strategy_analyst import StrategyAnalystAgent
from .usecase_designer import UseCaseDesignerAgent
from .roi_analyst import ROIAnalystAgent
from .risk_assessor import RiskAssessorAgent
from .report_generator import ReportGeneratorAgent


class AgentFactory:
    """에이전트 팩토리 클래스"""
    
    _agent_classes = {
        "strategy_analyst": StrategyAnalystAgent,
        "use_case_designer": UseCaseDesignerAgent,
        "roi_analyst": ROIAnalystAgent,
        "risk_assessor": RiskAssessorAgent,
        "report_generator": ReportGeneratorAgent,
    }
    
    @staticmethod
    def create_agent(agent_type: str, llm_provider=None, **kwargs):
        """에이전트 생성"""
        agent_class = AgentFactory._agent_classes.get(agent_type)
        if not agent_class:
            raise ValueError(f"Unknown agent type: {agent_type}. Available types: {list(AgentFactory._agent_classes.keys())}")
        return agent_class(llm_provider=llm_provider, **kwargs)
    
    @staticmethod
    def get_available_agents() -> list:
        """사용 가능한 에이전트 타입 목록 반환"""
        return list(AgentFactory._agent_classes.keys())
    
    @staticmethod
    def create_all_agents(llm_provider=None) -> Dict[str, Any]:
        """모든 에이전트 생성"""
        agents = {}
        for agent_type in AgentFactory._agent_classes.keys():
            agents[agent_type] = AgentFactory.create_agent(agent_type, llm_provider)
        return agents

