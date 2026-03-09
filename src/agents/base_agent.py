"""
AI Consulting Assistant Platform - Base Agent
모든 컨설팅 에이전트의 기반 클래스
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
import uuid


class AgentMessage(BaseModel):
    """에이전트 메시지"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    sender: str
    receiver: str
    content: str
    message_type: str = "text"  # text, task, result, feedback, approval_request
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.now)


class AgentState(BaseModel):
    """에이전트 상태"""
    agent_id: str
    agent_name: str
    status: str = "idle"  # idle, working, waiting, completed, error
    current_task: Optional[str] = None
    progress: float = 0.0
    messages: List[AgentMessage] = Field(default_factory=list)
    context: Dict[str, Any] = Field(default_factory=dict)
    results: Dict[str, Any] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)


class BaseConsultingAgent(ABC):
    """컨설팅 에이전트 기반 클래스"""

    def __init__(
        self,
        agent_id: str,
        name: str,
        role: str,
        description: str,
        llm_provider=None
    ):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.description = description
        self.llm_provider = llm_provider

        self.state = AgentState(
            agent_id=agent_id,
            agent_name=name
        )

        # 다른 에이전트들과의 연결
        self.connected_agents: Dict[str, 'BaseConsultingAgent'] = {}

    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """태스크 실행 (서브클래스에서 구현)"""
        pass

    @abstractmethod
    def get_system_prompt(self) -> str:
        """에이전트별 시스템 프롬프트 반환"""
        pass

    async def process_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """메시지 처리"""
        self.state.messages.append(message)

        if message.message_type == "task":
            return await self._handle_task(message)
        elif message.message_type == "feedback":
            return await self._handle_feedback(message)
        elif message.message_type == "approval_request":
            return await self._handle_approval_request(message)
        else:
            return await self._handle_general_message(message)

    async def _handle_task(self, message: AgentMessage) -> AgentMessage:
        """태스크 메시지 처리"""
        self.state.status = "working"
        self.state.current_task = message.content

        try:
            task_data = message.metadata.get("task_data", {})
            result = await self.execute(task_data)

            self.state.status = "completed"
            self.state.results[message.id] = result

            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"태스크 완료: {message.content}",
                message_type="result",
                metadata={"result": result}
            )
        except Exception as e:
            self.state.status = "error"
            self.state.errors.append(str(e))

            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=f"태스크 실패: {str(e)}",
                message_type="error",
                metadata={"error": str(e)}
            )

    async def _handle_feedback(self, message: AgentMessage) -> Optional[AgentMessage]:
        """피드백 메시지 처리"""
        # 피드백을 컨텍스트에 저장
        self.state.context["last_feedback"] = {
            "content": message.content,
            "from": message.sender,
            "timestamp": message.timestamp.isoformat()
        }
        return None

    async def _handle_approval_request(self, message: AgentMessage) -> Optional[AgentMessage]:
        """승인 요청 처리"""
        # 기본 구현: 자동 승인 (실제로는 인간 검토 필요)
        self.state.context["pending_approval"] = {
            "request": message.content,
            "from": message.sender,
            "timestamp": message.timestamp.isoformat()
        }
        return None

    async def _handle_general_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """일반 메시지 처리"""
        # LLM을 사용하여 응답 생성
        if self.llm_provider:
            response = await self.llm_provider.generate(
                prompt=message.content,
                system_prompt=self.get_system_prompt()
            )
            return AgentMessage(
                sender=self.agent_id,
                receiver=message.sender,
                content=response,
                message_type="text"
            )
        return None

    def send_message(self, receiver_id: str, content: str, message_type: str = "text", metadata: Dict = None) -> AgentMessage:
        """메시지 전송"""
        message = AgentMessage(
            sender=self.agent_id,
            receiver=receiver_id,
            content=content,
            message_type=message_type,
            metadata=metadata or {}
        )
        self.state.messages.append(message)
        return message

    def connect_agent(self, agent: 'BaseConsultingAgent'):
        """다른 에이전트와 연결"""
        self.connected_agents[agent.agent_id] = agent

    def update_context(self, key: str, value: Any):
        """컨텍스트 업데이트"""
        self.state.context[key] = value

    def get_context(self, key: str, default: Any = None) -> Any:
        """컨텍스트 조회"""
        return self.state.context.get(key, default)

    def to_dict(self) -> Dict[str, Any]:
        """에이전트 정보를 딕셔너리로 변환"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role,
            "description": self.description,
            "status": self.state.status,
            "current_task": self.state.current_task,
            "progress": self.state.progress
        }
