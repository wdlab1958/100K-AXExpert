"""
Report Generator Agent
보고서 생성 에이전트 - 컨설팅 결과 보고서 작성
"""
from typing import Optional, List, Dict, Any
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from .base_agent import BaseConsultingAgent
from src.utils.consulting_logger import get_consulting_logger


class ReportGeneratorAgent(BaseConsultingAgent):
    """보고서 생성 에이전트
    컨설팅 결과 보고서 작성
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="report_generator",
            name="보고서 생성 전문가",
            role="Report Generator",
            description="컨설팅 결과를 종합하여 전문적인 보고서를 생성합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 컨설팅 보고서 작성 전문가입니다.

[전문 영역]
1. 경영진용 Executive Summary 작성
2. 기술 보고서 작성
3. 전략 제안서 작성
4. 실행 로드맵 문서화

[작성 원칙]
- 명확하고 간결한 문장
- 데이터 기반의 객관적 서술
- 핵심 메시지의 명확한 전달
- 전문적이면서도 이해하기 쉬운 표현
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """보고서 생성 태스크 실행"""
        report_type = task.get("report_type", "summary")

        if report_type == "executive_summary":
            return await self._generate_executive_summary(task)
        elif report_type == "full_report":
            return await self._generate_full_report(task)
        elif report_type == "strategy_proposal":
            return await self._generate_strategy_proposal(task)
        else:
            return await self._generate_custom_report(task)

    async def _generate_executive_summary(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Executive Summary 생성"""
        data = task.get("data", {})

        summary = {
            "title": "AI 컨설팅 Executive Summary",
            "sections": [
                {
                    "title": "프로젝트 개요",
                    "content": data.get("overview", "")
                },
                {
                    "title": "현황 진단 결과",
                    "content": self._summarize_assessment(data.get("assessment", {}))
                },
                {
                    "title": "핵심 제안",
                    "content": data.get("recommendations", [])
                },
                {
                    "title": "예상 효과",
                    "content": data.get("expected_benefits", {})
                },
                {
                    "title": "실행 로드맵",
                    "content": data.get("roadmap", {})
                }
            ]
        }

        return summary

    def _summarize_assessment(self, assessment: Dict) -> str:
        """진단 결과 요약"""
        if not assessment:
            return "진단 데이터가 없습니다."

        level = assessment.get("overall_level", "N/A")
        return f"AI 성숙도 Level {level}. 주요 개선 영역 식별 완료."

    async def _generate_full_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전체 보고서 생성"""
        data = task.get("data", {})

        report = {
            "title": "AI 인프라 도입 컨설팅 종합 보고서",
            "version": "1.0",
            "chapters": [
                {
                    "number": 1,
                    "title": "개요",
                    "sections": ["배경 및 목적", "프로젝트 범위", "추진 경과"]
                },
                {
                    "number": 2,
                    "title": "현황 분석",
                    "sections": ["AI 성숙도 진단", "IT 인프라 분석", "조직 역량 분석", "데이터 자산 분석"]
                },
                {
                    "number": 3,
                    "title": "AI 전략 수립",
                    "sections": ["AI 비전", "핵심 Use Case", "우선순위 결정"]
                },
                {
                    "number": 4,
                    "title": "실행 계획",
                    "sections": ["로드맵", "투자 계획", "조직 및 인력 계획"]
                },
                {
                    "number": 5,
                    "title": "기대 효과",
                    "sections": ["정량적 효과", "정성적 효과", "ROI 분석"]
                },
                {
                    "number": 6,
                    "title": "리스크 관리",
                    "sections": ["리스크 식별", "완화 전략"]
                }
            ],
            "appendices": ["용어 정의", "산출물 템플릿", "참고 자료"]
        }

        return report

    async def _generate_strategy_proposal(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전략 제안서 생성"""
        data = task.get("data", {})

        proposal = {
            "title": "AI 전환 전략 제안서",
            "sections": [
                {"title": "전략적 배경", "content": ""},
                {"title": "현황 분석 요약", "content": ""},
                {"title": "제안 전략", "content": ""},
                {"title": "실행 방안", "content": ""},
                {"title": "소요 자원", "content": ""},
                {"title": "기대 효과", "content": ""},
                {"title": "Next Steps", "content": ""}
            ]
        }

        return proposal

    async def _generate_custom_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """커스텀 보고서 생성"""
        if self.llm_provider:
            prompt = f"""다음 데이터를 기반으로 보고서를 작성해주세요:
{json.dumps(task.get('data', {}), ensure_ascii=False, indent=2)}

보고서 형식: {task.get('format', 'general')}
"""
            response = await self.llm_provider.generate(prompt, self.get_system_prompt())
            return {"report_content": response}

        return {"error": "LLM provider not configured"}

