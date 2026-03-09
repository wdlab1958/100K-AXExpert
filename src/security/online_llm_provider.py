"""
AI Consulting Platform - Online LLM Provider
다중 온라인 LLM API 통합 (Claude, ChatGPT, Gemini, Cohere, Perplexity, Azure)
"""
import asyncio
import httpx
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')


class OnlineLLMProvider(str, Enum):
    """온라인 LLM 제공자"""
    CLAUDE = "claude"
    CHATGPT = "chatgpt"
    GEMINI = "gemini"
    COHERE = "cohere"
    PERPLEXITY = "perplexity"
    AZURE_OPENAI = "azure_openai"


@dataclass
class LLMConfig:
    """LLM 설정"""
    provider: OnlineLLMProvider
    api_key: str
    model: str = ""
    base_url: str = ""
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60
    enabled: bool = True

    # Azure 전용
    azure_endpoint: str = ""
    azure_deployment: str = ""
    api_version: str = "2024-02-01"


@dataclass
class LLMResponse:
    """LLM 응답"""
    content: str
    provider: OnlineLLMProvider
    model: str
    usage: Dict[str, int] = field(default_factory=dict)
    latency_ms: float = 0
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = True
    error: Optional[str] = None


class BaseLLMClient(ABC):
    """LLM 클라이언트 기본 클래스"""

    def __init__(self, config: LLMConfig):
        self.config = config

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        """텍스트 생성"""
        pass

    @abstractmethod
    def get_default_model(self) -> str:
        """기본 모델 반환"""
        pass


class ClaudeClient(BaseLLMClient):
    """Anthropic Claude API 클라이언트"""

    def get_default_model(self) -> str:
        return "claude-3-5-sonnet-20241022"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                headers = {
                    "x-api-key": self.config.api_key,
                    "anthropic-version": "2023-06-01",
                    "content-type": "application/json"
                }

                data = {
                    "model": model,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature,
                    "messages": [{"role": "user", "content": prompt}]
                }

                if system_prompt:
                    data["system"] = system_prompt

                response = await client.post(
                    "https://api.anthropic.com/v1/messages",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                return LLMResponse(
                    content=result["content"][0]["text"],
                    provider=OnlineLLMProvider.CLAUDE,
                    model=model,
                    usage={
                        "input_tokens": result.get("usage", {}).get("input_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("output_tokens", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.CLAUDE,
                model=model,
                success=False,
                error=str(e)
            )


class ChatGPTClient(BaseLLMClient):
    """OpenAI ChatGPT API 클라이언트"""

    def get_default_model(self) -> str:
        return "gpt-4-turbo-preview"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }

                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                return LLMResponse(
                    content=result["choices"][0]["message"]["content"],
                    provider=OnlineLLMProvider.CHATGPT,
                    model=model,
                    usage={
                        "input_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("completion_tokens", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.CHATGPT,
                model=model,
                success=False,
                error=str(e)
            )


class GeminiClient(BaseLLMClient):
    """Google Gemini API 클라이언트"""

    def get_default_model(self) -> str:
        return "gemini-1.5-pro"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"

                full_prompt = prompt
                if system_prompt:
                    full_prompt = f"{system_prompt}\n\n{prompt}"

                data = {
                    "contents": [{"parts": [{"text": full_prompt}]}],
                    "generationConfig": {
                        "maxOutputTokens": self.config.max_tokens,
                        "temperature": self.config.temperature
                    }
                }

                response = await client.post(
                    url,
                    params={"key": self.config.api_key},
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                content = result["candidates"][0]["content"]["parts"][0]["text"]

                return LLMResponse(
                    content=content,
                    provider=OnlineLLMProvider.GEMINI,
                    model=model,
                    usage={
                        "input_tokens": result.get("usageMetadata", {}).get("promptTokenCount", 0),
                        "output_tokens": result.get("usageMetadata", {}).get("candidatesTokenCount", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.GEMINI,
                model=model,
                success=False,
                error=str(e)
            )


class CohereClient(BaseLLMClient):
    """Cohere API 클라이언트"""

    def get_default_model(self) -> str:
        return "command-r-plus"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }

                data = {
                    "model": model,
                    "message": prompt,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }

                if system_prompt:
                    data["preamble"] = system_prompt

                response = await client.post(
                    "https://api.cohere.ai/v1/chat",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                return LLMResponse(
                    content=result["text"],
                    provider=OnlineLLMProvider.COHERE,
                    model=model,
                    usage={
                        "input_tokens": result.get("meta", {}).get("tokens", {}).get("input_tokens", 0),
                        "output_tokens": result.get("meta", {}).get("tokens", {}).get("output_tokens", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.COHERE,
                model=model,
                success=False,
                error=str(e)
            )


class PerplexityClient(BaseLLMClient):
    """Perplexity API 클라이언트"""

    def get_default_model(self) -> str:
        return "llama-3.1-sonar-large-128k-online"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                headers = {
                    "Authorization": f"Bearer {self.config.api_key}",
                    "Content-Type": "application/json"
                }

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                data = {
                    "model": model,
                    "messages": messages,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }

                response = await client.post(
                    "https://api.perplexity.ai/chat/completions",
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                return LLMResponse(
                    content=result["choices"][0]["message"]["content"],
                    provider=OnlineLLMProvider.PERPLEXITY,
                    model=model,
                    usage={
                        "input_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("completion_tokens", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.PERPLEXITY,
                model=model,
                success=False,
                error=str(e)
            )


class AzureOpenAIClient(BaseLLMClient):
    """Azure OpenAI API 클라이언트"""

    def get_default_model(self) -> str:
        return "gpt-4"

    async def generate(self, prompt: str, system_prompt: str = None) -> LLMResponse:
        start_time = datetime.now()
        model = self.config.model or self.get_default_model()

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                url = f"{self.config.azure_endpoint}/openai/deployments/{self.config.azure_deployment}/chat/completions"

                headers = {
                    "api-key": self.config.api_key,
                    "Content-Type": "application/json"
                }

                messages = []
                if system_prompt:
                    messages.append({"role": "system", "content": system_prompt})
                messages.append({"role": "user", "content": prompt})

                data = {
                    "messages": messages,
                    "max_tokens": self.config.max_tokens,
                    "temperature": self.config.temperature
                }

                response = await client.post(
                    url,
                    params={"api-version": self.config.api_version},
                    headers=headers,
                    json=data
                )
                response.raise_for_status()
                result = response.json()

                latency = (datetime.now() - start_time).total_seconds() * 1000

                return LLMResponse(
                    content=result["choices"][0]["message"]["content"],
                    provider=OnlineLLMProvider.AZURE_OPENAI,
                    model=model,
                    usage={
                        "input_tokens": result.get("usage", {}).get("prompt_tokens", 0),
                        "output_tokens": result.get("usage", {}).get("completion_tokens", 0)
                    },
                    latency_ms=latency
                )

        except Exception as e:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.AZURE_OPENAI,
                model=model,
                success=False,
                error=str(e)
            )


class OnlineLLMManager:
    """온라인 LLM 관리자"""

    CLIENT_MAP = {
        OnlineLLMProvider.CLAUDE: ClaudeClient,
        OnlineLLMProvider.CHATGPT: ChatGPTClient,
        OnlineLLMProvider.GEMINI: GeminiClient,
        OnlineLLMProvider.COHERE: CohereClient,
        OnlineLLMProvider.PERPLEXITY: PerplexityClient,
        OnlineLLMProvider.AZURE_OPENAI: AzureOpenAIClient
    }

    DEFAULT_MODELS = {
        OnlineLLMProvider.CLAUDE: "claude-3-5-sonnet-20241022",
        OnlineLLMProvider.CHATGPT: "gpt-4-turbo-preview",
        OnlineLLMProvider.GEMINI: "gemini-1.5-pro",
        OnlineLLMProvider.COHERE: "command-r-plus",
        OnlineLLMProvider.PERPLEXITY: "llama-3.1-sonar-large-128k-online",
        OnlineLLMProvider.AZURE_OPENAI: "gpt-4"
    }

    def __init__(self):
        self.configs: Dict[OnlineLLMProvider, LLMConfig] = {}
        self.clients: Dict[OnlineLLMProvider, BaseLLMClient] = {}
        self.default_provider: Optional[OnlineLLMProvider] = None

    def configure(self, config: LLMConfig):
        """LLM 설정 등록"""
        self.configs[config.provider] = config

        # 클라이언트 생성
        client_class = self.CLIENT_MAP.get(config.provider)
        if client_class:
            self.clients[config.provider] = client_class(config)

        # 첫 번째로 등록된 것을 기본값으로
        if self.default_provider is None and config.enabled:
            self.default_provider = config.provider

    def set_default_provider(self, provider: OnlineLLMProvider):
        """기본 제공자 설정"""
        if provider in self.clients:
            self.default_provider = provider

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """사용 가능한 제공자 목록"""
        return [
            {
                "provider": provider.value,
                "model": self.configs[provider].model or self.DEFAULT_MODELS.get(provider, ""),
                "enabled": self.configs[provider].enabled,
                "is_default": provider == self.default_provider
            }
            for provider in self.configs.keys()
        ]

    async def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        provider: OnlineLLMProvider = None
    ) -> LLMResponse:
        """텍스트 생성"""
        target_provider = provider or self.default_provider

        if not target_provider:
            return LLMResponse(
                content="",
                provider=OnlineLLMProvider.CLAUDE,
                model="",
                success=False,
                error="No LLM provider configured"
            )

        client = self.clients.get(target_provider)
        if not client:
            return LLMResponse(
                content="",
                provider=target_provider,
                model="",
                success=False,
                error=f"Provider {target_provider.value} not configured"
            )

        config = self.configs.get(target_provider)
        if not config or not config.enabled:
            return LLMResponse(
                content="",
                provider=target_provider,
                model="",
                success=False,
                error=f"Provider {target_provider.value} is disabled"
            )

        return await client.generate(prompt, system_prompt)

    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: str = None,
        providers: List[OnlineLLMProvider] = None
    ) -> LLMResponse:
        """폴백을 포함한 텍스트 생성"""
        if not providers:
            providers = list(self.clients.keys())

        for provider in providers:
            response = await self.generate(prompt, system_prompt, provider)
            if response.success:
                return response

        return LLMResponse(
            content="",
            provider=providers[0] if providers else OnlineLLMProvider.CLAUDE,
            model="",
            success=False,
            error="All providers failed"
        )


# 싱글톤 인스턴스
_manager: Optional[OnlineLLMManager] = None


def get_online_llm_manager() -> OnlineLLMManager:
    """OnlineLLMManager 싱글톤 인스턴스"""
    global _manager
    if _manager is None:
        _manager = OnlineLLMManager()
    return _manager
