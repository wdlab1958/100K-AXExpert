"""
Use Case Designer Agent
Use Case 설계자 에이전트 - 상세 요건 정의, 기술 아키텍처 설계, 거버넌스 체계 수립
"""
from typing import Optional, List, Dict, Any
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from .base_agent import BaseConsultingAgent
from src.utils.consulting_logger import get_consulting_logger


class UseCaseDesignerAgent(BaseConsultingAgent):
    """2단계: Use Case 설계자 에이전트
    상세 요건 정의, 기술 아키텍처 설계, 거버넌스 체계 수립
    """

    def __init__(self, llm_provider=None):
        super().__init__(
            agent_id="use_case_designer",
            name="Use Case 설계자",
            role="Use Case Designer",
            description="AI Use Case의 상세 요건을 정의하고, 기술 아키텍처를 설계하며, 거버넌스 체계를 수립합니다.",
            llm_provider=llm_provider
        )
        self.logger = get_consulting_logger()

    def get_system_prompt(self) -> str:
        return """당신은 AI 솔루션 설계 전문가입니다.

[전문 영역]
1. AI Use Case 상세 요건 정의 (비즈니스 목표, 성공 기준, 데이터 요구사항)
2. 기술 아키텍처 설계 (데이터 파이프라인, MLOps, 모델 서빙)
3. AI 거버넌스 및 윤리 체계 수립

[설계 원칙]
- 비즈니스 요구사항과 기술 구현의 정합성 확보
- 확장성과 유지보수성을 고려한 아키텍처
- 보안, 프라이버시, 윤리적 고려사항 반영
"""

    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Use Case 설계 태스크 실행"""
        task_type = task.get("type", "design")

        if task_type == "requirements_definition":
            return await self._define_requirements(task.get("use_case"))
        elif task_type == "architecture_design":
            return await self._design_architecture(task.get("use_case"), task.get("requirements"))
        elif task_type == "governance_setup":
            return await self._setup_governance(task.get("use_case"))
        else:
            return await self._general_design(task)

    async def _define_requirements(self, use_case: Dict[str, Any]) -> Dict[str, Any]:
        """상세 요건 정의"""
        requirements = {
            "business_requirements": {
                "objectives": [],
                "success_criteria": [],
                "kpis": []
            },
            "functional_requirements": {
                "input_data": [],
                "output_format": [],
                "processing_logic": []
            },
            "non_functional_requirements": {
                "performance": {
                    "response_time_ms": 1000,
                    "throughput": "100 req/sec",
                    "availability": "99.9%"
                },
                "scalability": "horizontal",
                "security": []
            },
            "data_requirements": {
                "required_data_sources": [],
                "data_volume": "",
                "data_quality_criteria": []
            },
            "integration_requirements": []
        }

        if self.llm_provider:
            prompt = f"""다음 AI Use Case에 대한 상세 요건을 정의해주세요:
Use Case: {json.dumps(use_case, ensure_ascii=False)}

요건 정의 항목:
1. 비즈니스 목표 및 성공 기준
2. 기능 요구사항 (입력, 출력, 처리 로직)
3. 비기능 요구사항 (성능, 확장성, 보안)
4. 데이터 요구사항
5. 통합 요구사항"""

            response = await self.llm_provider.generate(prompt, self.get_system_prompt())
            requirements["llm_analysis"] = response

        return requirements

    async def _design_architecture(self, use_case: Dict, requirements: Dict) -> Dict[str, Any]:
        """기술 아키텍처 설계"""
        architecture = {
            "layers": {
                "data_layer": {
                    "components": ["Data Lake/Warehouse", "Feature Store", "Data Pipeline"],
                    "technologies": ["Apache Spark", "Delta Lake", "Airflow"]
                },
                "ml_layer": {
                    "components": ["Model Training", "Experiment Tracking", "Model Registry"],
                    "technologies": ["PyTorch/TensorFlow", "MLflow", "Kubeflow"]
                },
                "serving_layer": {
                    "components": ["Model Serving", "API Gateway", "Load Balancer"],
                    "technologies": ["TorchServe/Triton", "Kong", "Kubernetes"]
                },
                "monitoring_layer": {
                    "components": ["Performance Monitoring", "Drift Detection", "Alerting"],
                    "technologies": ["Prometheus", "Grafana", "Evidently AI"]
                }
            },
            "data_flow": [],
            "deployment_topology": "",
            "security_architecture": []
        }

        return architecture

    async def _setup_governance(self, use_case: Dict) -> Dict[str, Any]:
        """거버넌스 체계 수립"""
        governance = {
            "organization": {
                "governance_committee": True,
                "roles": ["AI Model Owner", "Data Steward", "Ethics Officer"]
            },
            "policies": {
                "data_privacy": [],
                "model_validation": [],
                "deployment_approval": []
            },
            "processes": {
                "bias_review": "모델 개발 전 데이터 편향성 평가 필수",
                "explainability": "XAI 기법 적용 의무화",
                "audit_trail": "모든 의사결정 기록 및 추적"
            },
            "risk_management": {
                "risk_classification": ["저", "중", "고"],
                "mitigation_strategies": [],
                "fallback_plan": "Human-in-the-Loop 체계 구축"
            }
        }

        return governance

    async def _general_design(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """일반 설계 태스크"""
        if self.llm_provider:
            prompt = task.get("query", "")
            context = task.get("context", {})
            response = await self.llm_provider.consult(prompt, context, "architecture_design")
            return {"design": response}
        return {"error": "LLM provider not configured"}

