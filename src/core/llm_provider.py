"""
AI Consulting Assistant Platform - LLM Provider
Ollama 기반 Local LLM 연동 모듈
"""
import asyncio
from typing import Optional, List, Dict, Any
from langchain_community.llms import Ollama
from langchain_community.embeddings import OllamaEmbeddings
from langchain_core.language_models.base import BaseLanguageModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')
from config.settings import settings


class LLMProvider:
    """Ollama 기반 LLM 제공자"""

    def __init__(
        self,
        model: str = None,
        base_url: str = None,
        temperature: float = 0.7,
        top_p: float = 0.9,
    ):
        self.model = model or settings.OLLAMA_MODEL
        self.base_url = base_url or settings.OLLAMA_BASE_URL
        self.temperature = temperature
        self.top_p = top_p

        self._llm: Optional[Ollama] = None
        self._embeddings: Optional[OllamaEmbeddings] = None

    @property
    def llm(self) -> Ollama:
        """LLM 인스턴스 (지연 초기화)"""
        if self._llm is None:
            self._llm = Ollama(
                model=self.model,
                base_url=self.base_url,
                temperature=self.temperature,
                top_p=self.top_p,
            )
        return self._llm

    @property
    def embeddings(self) -> OllamaEmbeddings:
        """임베딩 모델 인스턴스"""
        if self._embeddings is None:
            self._embeddings = OllamaEmbeddings(
                model=settings.OLLAMA_EMBEDDING_MODEL,
                base_url=self.base_url,
            )
        return self._embeddings

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs
    ) -> str:
        """텍스트 생성"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}"

        # 동기 호출을 비동기로 래핑
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.llm.invoke(full_prompt)
        )
        return result

    async def generate_with_context(
        self,
        prompt: str,
        context: List[Dict[str, str]],
        system_prompt: Optional[str] = None,
    ) -> str:
        """컨텍스트를 포함한 텍스트 생성"""
        context_text = "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in context
        ])

        full_prompt = f"{context_text}\n\nHuman: {prompt}"
        return await self.generate(full_prompt, system_prompt)

    async def embed_text(self, text: str) -> List[float]:
        """텍스트 임베딩"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.embeddings.embed_query(text)
        )
        return result

    async def embed_documents(self, documents: List[str]) -> List[List[float]]:
        """문서 배치 임베딩"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            None,
            lambda: self.embeddings.embed_documents(documents)
        )
        return result


class ConsultingLLMProvider(LLMProvider):
    """AI 컨설팅 전용 LLM 제공자 (프롬프트 최적화)"""

    # 컨설팅 전문가 시스템 프롬프트
    CONSULTING_SYSTEM_PROMPT = """당신은 기업 AI 전환(AX) 전문 컨설턴트입니다.
다음 역할과 원칙을 따르세요:

[역할]
- AI 인프라 도입 및 구축 전문 컨설턴트
- AI 성숙도 진단 및 전략 수립 전문가
- MLOps 및 AI 거버넌스 전문가
- 산업별 AI 적용 사례 전문가

[원칙]
1. 객관적이고 데이터 기반의 분석을 제공합니다.
2. 고객사의 실제 상황과 리소스를 고려한 실현 가능한 제안을 합니다.
3. 리스크와 기회를 균형있게 평가합니다.
4. 명확하고 구조화된 형태로 결과를 제시합니다.
5. 한국어로 전문적이면서도 이해하기 쉽게 설명합니다.

[컨설팅 프레임워크]
- 1단계: AI 비전 및 전략 수립
- 2단계: Use Case 및 설계 정의
- 3단계: 플랫폼 및 솔루션 구축
- 4단계: 파일럿 및 확산
- 5단계: 운영, 모니터링 및 개선
"""

    async def consult(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        task_type: str = "general"
    ) -> str:
        """컨설팅 질의 처리"""
        task_prompts = {
            "maturity_assessment": "AI 성숙도 진단을 수행하세요. 4대 핵심 영역(전략, 조직, 데이터/기술, 프로세스)을 평가하세요.",
            "use_case_analysis": "AI 활용 사례를 분석하고 가치-실행 용이성 매트릭스로 우선순위를 결정하세요.",
            "roi_analysis": "투자 대비 효과(ROI) 분석을 수행하세요. 정량적/정성적 효과를 모두 고려하세요.",
            "risk_assessment": "리스크 분석을 수행하세요. 기술적, 조직적, 비즈니스, 운영적 리스크를 평가하세요.",
            "roadmap_planning": "AI 도입 로드맵을 수립하세요. 단기/중기/장기 계획을 포함하세요.",
            "architecture_design": "AI 시스템 아키텍처를 설계하세요. 데이터, 모델, 서빙, 모니터링 레이어를 포함하세요.",
            "general": "전문 컨설턴트로서 질문에 답변하세요."
        }

        task_prompt = task_prompts.get(task_type, task_prompts["general"])

        context_str = ""
        if context:
            context_str = f"\n\n[컨텍스트 정보]\n{self._format_context(context)}"

        full_prompt = f"{task_prompt}{context_str}\n\n[질문]\n{query}"

        return await self.generate(full_prompt, self.CONSULTING_SYSTEM_PROMPT)

    def _format_context(self, context: Dict[str, Any]) -> str:
        """컨텍스트 정보 포맷팅"""
        lines = []
        for key, value in context.items():
            if isinstance(value, dict):
                lines.append(f"- {key}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            elif isinstance(value, list):
                lines.append(f"- {key}: {', '.join(str(v) for v in value)}")
            else:
                lines.append(f"- {key}: {value}")
        return "\n".join(lines)


# 싱글톤 인스턴스
_llm_provider: Optional[ConsultingLLMProvider] = None


def get_llm_provider() -> ConsultingLLMProvider:
    """LLM Provider 싱글톤 인스턴스 반환"""
    global _llm_provider
    if _llm_provider is None:
        _llm_provider = ConsultingLLMProvider()
    return _llm_provider
