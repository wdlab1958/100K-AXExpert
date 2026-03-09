"""
LlamaIndex Workflow 기반 RAG (Retrieval-Augmented Generation) 모듈
ISO 표준 문서 기반 컨설팅 근거 강화 시스템

주요 기능:
- ISO 42001, 38500, 24030, 23053 표준 문서 인덱싱
- Workflow 기반 RAG 파이프라인
- 컨설팅 분석에 표준 근거 연결
- Ollama 로컬 LLM/임베딩 통합
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path
import json
import asyncio

from llama_index.core import (
    VectorStoreIndex,
    SimpleDirectoryReader,
    Settings as LISettings,
    StorageContext,
    load_index_from_storage,
    Document,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core.workflow import Workflow, step, Event, StartEvent, StopEvent
from llama_index.llms.ollama import Ollama as LIOllama
from llama_index.embeddings.ollama import OllamaEmbedding

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings
from src.utils.consulting_logger import get_consulting_logger


# ==================== Workflow 이벤트 정의 ====================

class QueryEvent(Event):
    """RAG 질의 이벤트"""
    query: str
    query_type: str  # maturity, use_case, roi, risk, governance


class RetrievalEvent(Event):
    """문서 검색 결과 이벤트"""
    query: str
    query_type: str
    retrieved_nodes: list
    source_info: list


class GenerationEvent(Event):
    """생성 결과 이벤트"""
    query: str
    query_type: str
    response: str
    sources: list


# ==================== LlamaIndex RAG Workflow ====================

class ConsultingRAGWorkflow(Workflow):
    """ISO 표준 기반 컨설팅 RAG 워크플로우

    LlamaIndex Workflow를 활용한 3단계 RAG 파이프라인:
    1. Query Processing: 질의 분석 및 최적화
    2. Retrieval: 관련 표준 문서 검색
    3. Generation: 근거 기반 분석 결과 생성
    """

    def __init__(self, index: VectorStoreIndex, llm, **kwargs):
        super().__init__(**kwargs)
        self.index = index
        self.llm = llm
        self.query_engine = index.as_query_engine(
            similarity_top_k=5,
            llm=llm,
        )
        self.retriever = index.as_retriever(similarity_top_k=5)

    @step
    async def process_query(self, ev: StartEvent) -> QueryEvent:
        """1단계: 질의 분석 및 최적화"""
        query = ev.get("query", "")
        query_type = ev.get("query_type", "general")

        # 질의 유형별 컨텍스트 보강
        enhanced_queries = {
            "maturity": f"AI 성숙도 진단 관련 ISO 표준 요구사항 및 평가 기준: {query}",
            "use_case": f"AI 활용 사례 및 산업별 도입 효과: {query}",
            "roi": f"AI 투자 효과 분석 및 비즈니스 가치 평가 기준: {query}",
            "risk": f"AI 도입 리스크 평가 및 거버넌스 요구사항: {query}",
            "governance": f"AI 거버넌스 체계 및 IT 거버넌스 원칙: {query}",
            "mlops": f"ML 파이프라인 및 모델 운영 표준: {query}",
        }

        enhanced_query = enhanced_queries.get(query_type, query)

        return QueryEvent(query=enhanced_query, query_type=query_type)

    @step
    async def retrieve_documents(self, ev: QueryEvent) -> RetrievalEvent:
        """2단계: 관련 표준 문서 검색"""
        nodes = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.retriever.retrieve(ev.query),
        )

        source_info = []
        for node in nodes:
            source_info.append({
                "text": node.get_text()[:300],
                "score": node.get_score() if hasattr(node, 'get_score') else 0.0,
                "metadata": node.metadata if hasattr(node, 'metadata') else {},
            })

        return RetrievalEvent(
            query=ev.query,
            query_type=ev.query_type,
            retrieved_nodes=nodes,
            source_info=source_info,
        )

    @step
    async def generate_response(self, ev: RetrievalEvent) -> StopEvent:
        """3단계: 근거 기반 분석 결과 생성"""
        # 검색된 문서 컨텍스트 구성
        context_parts = []
        for node in ev.retrieved_nodes:
            text = node.get_text()
            context_parts.append(text[:500])

        context = "\n\n---\n\n".join(context_parts)

        # LLM 기반 답변 생성
        prompt = f"""다음 ISO 표준 문서를 참조하여 질의에 답변하세요.

[참조 문서]
{context}

[질의]
{ev.query}

[답변 지침]
- ISO 표준의 구체적 조항을 인용하여 근거를 제시하세요
- 한국어로 전문적이면서도 이해하기 쉽게 작성하세요
- 실무적으로 적용 가능한 구체적 가이드라인을 포함하세요
"""

        response = await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self.llm.complete(prompt),
        )

        return StopEvent(result={
            "query": ev.query,
            "query_type": ev.query_type,
            "response": str(response),
            "sources": ev.source_info,
            "source_count": len(ev.source_info),
        })


# ==================== LlamaIndex RAG Provider ====================

class LlamaIndexRAGProvider:
    """LlamaIndex 기반 ISO 표준 RAG 제공자

    ISO 표준 문서를 인덱싱하고 RAG 파이프라인을 통해
    컨설팅 분석에 표준 근거를 연결합니다.
    """

    STANDARDS_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "standards"
    INDEX_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "index"

    def __init__(self):
        self.logger = get_consulting_logger()
        self._index: Optional[VectorStoreIndex] = None
        self._workflow: Optional[ConsultingRAGWorkflow] = None

        # LlamaIndex LLM 및 임베딩 설정
        self.llm = LIOllama(
            model=settings.OLLAMA_MODEL,
            base_url=settings.OLLAMA_BASE_URL,
            request_timeout=120.0,
        )

        # 임베딩 모델: nomic-embed-text가 없으면 LLM 모델을 임베딩에도 사용
        embed_model_name = settings.OLLAMA_EMBEDDING_MODEL
        try:
            import httpx
            resp = httpx.get(f"{settings.OLLAMA_BASE_URL}/api/tags", timeout=5)
            available_models = [m["name"] for m in resp.json().get("models", [])]
            if embed_model_name not in available_models and f"{embed_model_name}:latest" not in available_models:
                embed_model_name = settings.OLLAMA_MODEL  # LLM 모델을 임베딩에도 사용
        except Exception:
            embed_model_name = settings.OLLAMA_MODEL

        self.embed_model = OllamaEmbedding(
            model_name=embed_model_name,
            base_url=settings.OLLAMA_BASE_URL,
        )

        # LlamaIndex 글로벌 설정
        LISettings.llm = self.llm
        LISettings.embed_model = self.embed_model
        LISettings.chunk_size = 512
        LISettings.chunk_overlap = 50

    @property
    def index(self) -> VectorStoreIndex:
        """인덱스 인스턴스 (지연 초기화)"""
        if self._index is None:
            self._index = self._load_or_create_index()
        return self._index

    @property
    def workflow(self) -> ConsultingRAGWorkflow:
        """RAG 워크플로우 인스턴스"""
        if self._workflow is None:
            self._workflow = ConsultingRAGWorkflow(
                index=self.index,
                llm=self.llm,
                timeout=120,
            )
        return self._workflow

    def _load_or_create_index(self) -> VectorStoreIndex:
        """인덱스 로드 또는 생성"""
        self.INDEX_DIR.mkdir(parents=True, exist_ok=True)

        # 기존 인덱스가 있으면 로드 시도
        docstore_path = self.INDEX_DIR / "docstore.json"
        if docstore_path.exists():
            try:
                self.logger.info("[LlamaIndex] 기존 인덱스 로드", "")
                storage_context = StorageContext.from_defaults(
                    persist_dir=str(self.INDEX_DIR),
                )
                return load_index_from_storage(storage_context)
            except Exception as e:
                self.logger.info(f"[LlamaIndex] 인덱스 로드 실패, 재생성: {e}", "")

        # 새 인덱스 생성
        return self._create_index()

    def _create_index(self) -> VectorStoreIndex:
        """ISO 표준 문서 인덱싱"""
        self.logger.info("[LlamaIndex] ISO 표준 문서 인덱싱 시작", "")

        self.STANDARDS_DIR.mkdir(parents=True, exist_ok=True)

        # 문서 읽기
        if not any(self.STANDARDS_DIR.glob("*.md")):
            self.logger.info("[LlamaIndex] 표준 문서 없음 - 빈 인덱스 생성", "")
            return VectorStoreIndex.from_documents([
                Document(text="ISO 표준 문서가 아직 로드되지 않았습니다.", metadata={"source": "empty"}),
            ])

        reader = SimpleDirectoryReader(
            input_dir=str(self.STANDARDS_DIR),
            required_exts=[".md", ".txt"],
            recursive=True,
        )
        documents = reader.load_data()

        self.logger.info(f"[LlamaIndex] {len(documents)}개 문서 로드 완료", "")

        # 노드 파서
        splitter = SentenceSplitter(chunk_size=512, chunk_overlap=50)

        # 인덱스 생성
        index = VectorStoreIndex.from_documents(
            documents,
            transformations=[splitter],
        )

        # 인덱스 저장
        index.storage_context.persist(persist_dir=str(self.INDEX_DIR))
        self.logger.info("[LlamaIndex] 인덱스 저장 완료", "")

        return index

    def rebuild_index(self) -> Dict[str, Any]:
        """인덱스 재구축"""
        self.logger.info("[LlamaIndex] 인덱스 재구축", "")
        self._index = self._create_index()
        self._workflow = None  # 워크플로우 재초기화 필요

        doc_count = 0
        try:
            doc_count = len(self._index.docstore.docs)
        except Exception:
            pass

        return {
            "status": "rebuilt",
            "documents": doc_count,
            "index_dir": str(self.INDEX_DIR),
        }

    async def query(
        self, query: str, query_type: str = "general"
    ) -> Dict[str, Any]:
        """RAG 워크플로우를 통한 질의 처리"""
        self.logger.info(f"[LlamaIndex] RAG 질의: {query_type}", "")

        result = await self.workflow.run(query=query, query_type=query_type)

        return {
            "framework": "llamaindex",
            "pipeline": "rag_workflow",
            "query_type": query_type,
            "response": result.get("response", ""),
            "sources": result.get("sources", []),
            "source_count": result.get("source_count", 0),
            "timestamp": datetime.now().isoformat(),
        }

    async def get_standard_evidence(
        self, topic: str, query_type: str = "general"
    ) -> Dict[str, Any]:
        """컨설팅 분석에 대한 표준 근거 검색"""
        evidence_queries = {
            "maturity": f"AI 성숙도 진단 시 적용해야 할 ISO 표준 요구사항과 평가 기준은? 주제: {topic}",
            "use_case": f"AI 활용 사례 선정 및 설계 시 참조해야 할 ISO 표준 가이드라인은? 주제: {topic}",
            "roi": f"AI 투자 대비 효과 분석 시 참고해야 할 국제 표준 프레임워크는? 주제: {topic}",
            "risk": f"AI 도입 리스크 평가에 적용할 수 있는 ISO 표준 리스크 관리 체계는? 주제: {topic}",
            "governance": f"AI 거버넌스 체계 수립 시 참조해야 할 ISO 표준 원칙 및 프레임워크는? 주제: {topic}",
            "mlops": f"MLOps 구축 시 ISO 표준이 요구하는 모델 라이프사이클 관리 방안은? 주제: {topic}",
        }

        query = evidence_queries.get(query_type, f"ISO 표준에서 다음 주제에 대한 가이드라인: {topic}")

        return await self.query(query, query_type)

    async def run_full_rag_consultation(
        self, company_profile: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전체 RAG 기반 컨설팅 파이프라인 실행"""
        self.logger.info("[LlamaIndex] 전체 RAG 컨설팅 시작", company_profile.get("name", ""))
        started_at = datetime.now().isoformat()

        industry = company_profile.get("industry", "manufacturing")
        company_name = company_profile.get("name", "Unknown")
        results = {}
        errors = []

        # 1. 성숙도 진단 근거 검색
        try:
            results["maturity_evidence"] = await self.get_standard_evidence(
                f"{industry} 산업의 {company_name} AI 성숙도 진단",
                "maturity",
            )
        except Exception as e:
            errors.append(f"성숙도 근거 검색 실패: {str(e)}")
            results["maturity_evidence"] = {"error": str(e)}

        # 2. Use Case 표준 근거
        try:
            results["use_case_evidence"] = await self.get_standard_evidence(
                f"{industry} 산업 AI 활용 사례 및 도입 효과",
                "use_case",
            )
        except Exception as e:
            errors.append(f"Use Case 근거 검색 실패: {str(e)}")
            results["use_case_evidence"] = {"error": str(e)}

        # 3. 거버넌스 표준 근거
        try:
            results["governance_evidence"] = await self.get_standard_evidence(
                f"AI 거버넌스 체계 및 윤리 프레임워크",
                "governance",
            )
        except Exception as e:
            errors.append(f"거버넌스 근거 검색 실패: {str(e)}")
            results["governance_evidence"] = {"error": str(e)}

        # 4. 리스크 관리 표준 근거
        try:
            results["risk_evidence"] = await self.get_standard_evidence(
                f"AI 도입 리스크 관리 및 완화 전략",
                "risk",
            )
        except Exception as e:
            errors.append(f"리스크 근거 검색 실패: {str(e)}")
            results["risk_evidence"] = {"error": str(e)}

        # 5. MLOps 표준 근거
        try:
            results["mlops_evidence"] = await self.get_standard_evidence(
                f"ML 파이프라인 구축 및 모델 운영 표준",
                "mlops",
            )
        except Exception as e:
            errors.append(f"MLOps 근거 검색 실패: {str(e)}")
            results["mlops_evidence"] = {"error": str(e)}

        self.logger.info("[LlamaIndex] 전체 RAG 컨설팅 완료", company_profile.get("name", ""))

        return {
            "framework": "llamaindex",
            "pipeline": "full_rag_consultation",
            "status": "completed" if not errors else "completed_with_errors",
            "results": results,
            "errors": errors,
            "standards_referenced": [
                "ISO/IEC 42001:2023 (AI 경영시스템)",
                "ISO/IEC 38500:2024 (IT 거버넌스)",
                "ISO/IEC TR 24030:2021 (AI 활용 사례)",
                "ISO/IEC 23053:2022 (ML 프레임워크)",
            ],
            "started_at": started_at,
            "completed_at": datetime.now().isoformat(),
        }

    def get_index_info(self) -> Dict[str, Any]:
        """인덱스 및 RAG 구성 정보 반환"""
        doc_count = 0
        try:
            doc_count = len(self.index.docstore.docs)
        except Exception:
            pass

        standards_files = list(self.STANDARDS_DIR.glob("*.md"))

        return {
            "framework": "llamaindex",
            "llm_model": settings.OLLAMA_MODEL,
            "embed_model": settings.OLLAMA_EMBEDDING_MODEL,
            "index_dir": str(self.INDEX_DIR),
            "standards_dir": str(self.STANDARDS_DIR),
            "indexed_documents": doc_count,
            "standard_files": [f.name for f in standards_files],
            "standards": [
                {
                    "id": "iso_42001",
                    "name": "ISO/IEC 42001:2023",
                    "title": "AI 경영시스템 (AIMS)",
                    "description": "AI 개발/사용 조직의 리스크 및 기회 관리 체계",
                },
                {
                    "id": "iso_38500",
                    "name": "ISO/IEC 38500:2024",
                    "title": "IT 거버넌스",
                    "description": "IT/AI 거버넌스 원칙 및 EDM 모델",
                },
                {
                    "id": "iso_24030",
                    "name": "ISO/IEC TR 24030:2021",
                    "title": "AI 활용 사례 분석",
                    "description": "산업별 AI 적용 사례 및 도입 효과",
                },
                {
                    "id": "iso_23053",
                    "name": "ISO/IEC 23053:2022",
                    "title": "ML 프레임워크",
                    "description": "ML 파이프라인 단계, 데이터 품질, 모델 거버넌스",
                },
            ],
            "workflow": {
                "name": "ConsultingRAGWorkflow",
                "steps": ["process_query", "retrieve_documents", "generate_response"],
                "description": "ISO 표준 기반 3단계 RAG 파이프라인",
            },
            "features": [
                "ISO 표준 문서 벡터 인덱싱",
                "Workflow 기반 RAG 파이프라인",
                "컨설팅 유형별 질의 최적화",
                "표준 근거 자동 연결",
                "Ollama 로컬 LLM/임베딩 통합",
            ],
        }


# 싱글톤 인스턴스
_rag_provider: Optional[LlamaIndexRAGProvider] = None


def get_rag_provider() -> LlamaIndexRAGProvider:
    """LlamaIndex RAG Provider 싱글톤 인스턴스 반환"""
    global _rag_provider
    if _rag_provider is None:
        _rag_provider = LlamaIndexRAGProvider()
    return _rag_provider
