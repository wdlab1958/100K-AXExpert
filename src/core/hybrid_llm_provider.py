"""
Hybrid LLM Provider
온라인 LLM(Claude 등)과 로컬 LLM(Ollama)을 하이브리드로 사용
"""
import asyncio
from typing import Optional, List, Dict, Any
from enum import Enum

import sys
sys.path.append('/home/wdlab/ai_project/ai_consulting')

from src.core.llm_provider import LLMProvider
from src.security.online_llm_provider import (
    get_online_llm_manager,
    OnlineLLMProvider,
    LLMResponse
)


class LLMProviderType(str, Enum):
    """LLM 제공자 유형"""
    ONLINE = "online"  # Claude, ChatGPT 등
    LOCAL = "local"    # Ollama
    HYBRID = "hybrid"  # 온라인 우선, 실패 시 로컬


class HybridLLMProvider:
    """하이브리드 LLM 제공자 - 온라인/로컬 LLM 통합"""

    def __init__(self, prefer_online: bool = True):
        """
        Args:
            prefer_online: True면 온라인 우선, False면 로컬 우선
        """
        self.prefer_online = prefer_online
        self.local_provider = LLMProvider()
        self.online_manager = get_online_llm_manager()

    def is_online_available(self) -> bool:
        """온라인 LLM 사용 가능 여부 확인"""
        providers = self.online_manager.get_available_providers()
        # Claude가 활성화되어 있는지 확인
        for provider in providers:
            if provider['provider'] == 'claude' and provider['enabled']:
                return True
        return False

    async def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        use_online: Optional[bool] = None,
        **kwargs
    ) -> str:
        """텍스트 생성 (하이브리드)

        Args:
            prompt: 생성할 텍스트 프롬프트
            system_prompt: 시스템 프롬프트
            use_online: True면 온라인 강제, False면 로컬 강제, None이면 자동
        """
        # 사용자 명시적 선택이 있으면 우선
        if use_online is not None:
            if use_online:
                return await self._generate_online(prompt, system_prompt)
            else:
                return await self._generate_local(prompt, system_prompt)

        # 자동 선택 (하이브리드)
        if self.prefer_online and self.is_online_available():
            try:
                result = await self._generate_online(prompt, system_prompt)
                if result:
                    return result
            except Exception as e:
                print(f"온라인 LLM 실패, 로컬로 폴백: {e}")

        # 온라인 실패 또는 로컬 우선 시 로컬 사용
        return await self._generate_local(prompt, system_prompt)

    async def _generate_online(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """온라인 LLM으로 생성 (Claude 우선)"""
        response: LLMResponse = await self.online_manager.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=OnlineLLMProvider.CLAUDE  # Claude 사용
        )

        if response.success:
            return response.content
        else:
            raise Exception(f"온라인 LLM 생성 실패: {response.error}")

    async def _generate_local(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """로컬 LLM으로 생성 (Ollama)"""
        return await self.local_provider.generate(prompt, system_prompt)

    async def generate_structured_content(
        self,
        section_title: str,
        section_description: str,
        context: Dict[str, Any],
        temperature: float = 0.7
    ) -> str:
        """구조화된 콘텐츠 생성 (보고서 섹션용)"""

        company_name = context.get('company_name', '귀사')
        industry = context.get('industry', 'IT 서비스')
        project_name = context.get('project_name', 'AI 프로젝트')

        system_prompt = """당신은 전문적인 AI 컨설팅 보고서 작성 전문가입니다.

[작성 원칙]
1. 특수문자 '#', '*'는 절대 사용하지 마세요
2. 제목은 숫자와 한글로만 표시 (예: "1.1 조직 현황")
3. 강조는 「 」로 표현 (예: 「AI 성숙도」)
4. 상세하고 구체적인 설명 작성
5. 전문적이고 품격있는 문체 사용
6. 실무에 적용 가능한 구체적인 내용 포함
"""

        prompt = f"""다음 보고서 섹션을 작성해주세요:

[섹션 제목]
{section_title}

[섹션 설명]
{section_description}

[컨텍스트]
- 기업명: {company_name}
- 산업 분야: {industry}
- 프로젝트: {project_name}

[작성 요구사항]
1. 제목 아래 3-4개 문단으로 상세하게 작성
2. 각 문단은 5-7줄 분량
3. 구체적인 예시와 설명 포함
4. 리스트 사용 시 '•'로 시작
5. 특수문자 '#', '*' 절대 금지
6. 전문적이고 설득력 있는 내용

지금 작성해주세요:"""

        return await self.generate(prompt, system_prompt)


# 싱글톤 인스턴스
_hybrid_provider: Optional[HybridLLMProvider] = None


def get_hybrid_llm_provider() -> HybridLLMProvider:
    """하이브리드 LLM Provider 싱글톤 인스턴스"""
    global _hybrid_provider
    if _hybrid_provider is None:
        _hybrid_provider = HybridLLMProvider(prefer_online=True)
    return _hybrid_provider
