"""
Stage 1: 성숙도 진단 관련 로직
"""
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any, List
import json

from ..common.database import get_project, update_project
from ..common.helpers import calc_avg_score
from .models import MaturityAssessmentInput


async def save_maturity_assessment(project_id: str, assessment: MaturityAssessmentInput):
    """AI 성숙도 진단 저장"""
    # 영역별 점수 계산
    strategy_score = calc_avg_score(assessment.strategy)
    org_score = calc_avg_score(assessment.organization)
    data_score = calc_avg_score(assessment.data_technology)
    process_score = calc_avg_score(assessment.process)

    overall_score = (strategy_score + org_score + data_score + process_score) / 4
    overall_level = min(5, max(1, round(overall_score)))

    maturity_data = {
        "assessment_date": datetime.now().isoformat(),
        "scores": {
            "strategy": {
                "score": round(strategy_score, 2),
                "items": assessment.strategy
            },
            "organization": {
                "score": round(org_score, 2),
                "items": assessment.organization
            },
            "data_technology": {
                "score": round(data_score, 2),
                "items": assessment.data_technology
            },
            "process": {
                "score": round(process_score, 2),
                "items": assessment.process
            }
        },
        "overall_score": round(overall_score, 2),
        "overall_level": overall_level,
        "notes": assessment.notes
    }

    update_project(project_id, {"stage1_maturity": maturity_data})

    return {
        "status": "success",
        "message": "성숙도 진단이 저장되었습니다.",
        "maturity": maturity_data
    }


async def get_maturity_assessment(project_id: str):
    """AI 성숙도 진단 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "maturity": {}}

    return {
        "status": "success",
        "maturity": project.get("stage1_maturity", {})
    }


async def analyze_maturity_with_ai(project_id: str, assessment: MaturityAssessmentInput):
    """AI 기반 성숙도 진단 분석"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # 에이전트 오케스트레이터 가져오기
        from src.agents.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()

        # 프로젝트 정보 가져오기
        company_profile = project.get("company_profile", {})
        
        # 성숙도 진단 데이터를 기반으로 AI 분석 수행
        # StrategyAnalystAgent를 사용하여 분석
        strategy_agent = orchestrator.agents.get("strategy")
        
        if not strategy_agent:
            # 에이전트가 없으면 기본 분석 수행
            return await _perform_basic_maturity_analysis(assessment, project)
        
        # AI 분석 수행
        analysis_result = await _perform_ai_maturity_analysis(
            strategy_agent, 
            assessment, 
            company_profile
        )

        # 분석 결과 저장
        analysis_data = {
            "analysis_date": datetime.now().isoformat(),
            "assessment_data": assessment.model_dump(),
            "analysis_result": analysis_result
        }
        
        # 프로젝트에 분석 결과 저장
        existing_maturity = project.get("stage1_maturity", {})
        existing_maturity["ai_analysis"] = analysis_data
        update_project(project_id, {"stage1_maturity": existing_maturity})

        return {
            "status": "success",
            "message": "AI 성숙도 분석이 완료되었습니다.",
            "analysis": analysis_result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 분석 중 오류 발생: {str(e)}")


async def _perform_ai_maturity_analysis(
    strategy_agent,
    assessment: MaturityAssessmentInput,
    company_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """AI 에이전트를 사용한 성숙도 분석"""
    try:
        # 영역별 점수 계산
        strategy_score = calc_avg_score(assessment.strategy)
        org_score = calc_avg_score(assessment.organization)
        data_score = calc_avg_score(assessment.data_technology)
        process_score = calc_avg_score(assessment.process)
        
        overall_score = (strategy_score + org_score + data_score + process_score) / 4
        overall_level = min(5, max(1, round(overall_score)))

        # AI 분석을 위한 컨텍스트 구성
        analysis_context = {
            "scores": {
                "strategy": {
                    "score": round(strategy_score, 2),
                    "items": assessment.strategy
                },
                "organization": {
                    "score": round(org_score, 2),
                    "items": assessment.organization
                },
                "data_technology": {
                    "score": round(data_score, 2),
                    "items": assessment.data_technology
                },
                "process": {
                    "score": round(process_score, 2),
                    "items": assessment.process
                }
            },
            "overall_score": round(overall_score, 2),
            "overall_level": overall_level,
            "company_profile": company_profile
        }

        # LLM을 통한 심층 분석 (가능한 경우)
        recommendations = []
        priority_improvements = []
        strengths = []
        weaknesses = []

        # 영역별 분석
        if strategy_score < 3:
            recommendations.append("AI 비전 및 전략 수립 워크숍을 통해 명확한 AI 전략을 수립하세요.")
            priority_improvements.append("전략 및 비전 영역: AI 투자 계획 및 ROI 측정 체계 구축")
            weaknesses.append("전략 및 비전: AI 전략 명확성 부족")
        else:
            strengths.append("전략 및 비전: AI 전략이 어느 정도 수립되어 있음")

        if org_score < 3:
            recommendations.append("AI 전문 인력 채용 또는 외부 파트너십을 통해 역량을 보강하세요.")
            priority_improvements.append("조직 및 역량 영역: AI 전문 인력 확보 및 교육 체계 구축")
            weaknesses.append("조직 및 역량: AI 전문 인력 부족")
        else:
            strengths.append("조직 및 역량: AI 인력 기반이 구축되어 있음")

        if data_score < 3:
            recommendations.append("데이터 인프라 현대화 및 클라우드 도입을 검토하세요.")
            priority_improvements.append("데이터 및 기술 영역: 데이터 품질 개선 및 MLOps 플랫폼 도입")
            weaknesses.append("데이터 및 기술: 데이터 인프라 및 품질 관리 체계 부족")
        else:
            strengths.append("데이터 및 기술: 데이터 인프라가 구축되어 있음")

        if process_score < 3:
            recommendations.append("AI 거버넌스 체계 수립 및 표준 프로세스를 정의하세요.")
            priority_improvements.append("프로세스 및 거버넌스 영역: AI 개발 방법론 표준화 및 모니터링 체계 구축")
            weaknesses.append("프로세스 및 거버넌스: AI 개발 프로세스 표준화 부족")
        else:
            strengths.append("프로세스 및 거버넌스: AI 프로세스가 표준화되어 있음")

        # LLM 에이전트를 통한 추가 분석 시도
        if strategy_agent and hasattr(strategy_agent, 'llm_provider') and strategy_agent.llm_provider:
            try:
                prompt = f"""다음 AI 성숙도 진단 결과를 분석하고 구체적인 개선 권장사항을 제시해주세요.

[성숙도 진단 결과]
- 전략 및 비전: {strategy_score:.2f}/5.0
- 조직 및 역량: {org_score:.2f}/5.0
- 데이터 및 기술: {data_score:.2f}/5.0
- 프로세스 및 거버넌스: {process_score:.2f}/5.0
- 종합 성숙도: {overall_level}단계

[분석 요청]
1. 각 영역별 강점과 약점 분석
2. 우선 개선 과제 3-5개 제시
3. 실현 가능한 구체적 권장사항 제시

JSON 형식으로 응답해주세요."""
                
                llm_response = await strategy_agent.llm_provider.generate(
                    prompt, 
                    strategy_agent.get_system_prompt()
                )
                
                # LLM 응답 파싱 (간단한 텍스트 추출)
                if llm_response:
                    # LLM 응답에서 추가 인사이트 추출 시도
                    if "권장" in llm_response or "개선" in llm_response:
                        # LLM 응답을 권장사항에 추가
                        recommendations.append(f"AI 분석: {llm_response[:200]}...")
            except Exception as e:
                # LLM 분석 실패 시 기본 분석 결과 사용
                pass

        return {
            "overall_level": overall_level,
            "overall_score": round(overall_score, 2),
            "scores": analysis_context["scores"],
            "recommendations": recommendations,
            "priority_improvements": priority_improvements,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "analysis_summary": f"현재 AI 성숙도는 {overall_level}단계입니다. {len(priority_improvements)}개 영역에서 개선이 필요합니다."
        }
    except Exception as e:
        # 에러 발생 시 기본 분석 반환
        return await _perform_basic_maturity_analysis(assessment, {})


async def _perform_basic_maturity_analysis(
    assessment: MaturityAssessmentInput,
    project: Dict[str, Any]
) -> Dict[str, Any]:
    """기본 성숙도 분석 (AI 에이전트 없이)"""
    strategy_score = calc_avg_score(assessment.strategy)
    org_score = calc_avg_score(assessment.organization)
    data_score = calc_avg_score(assessment.data_technology)
    process_score = calc_avg_score(assessment.process)
    
    overall_score = (strategy_score + org_score + data_score + process_score) / 4
    overall_level = min(5, max(1, round(overall_score)))

    recommendations = []
    if strategy_score < 3:
        recommendations.append("전략 및 비전 영역 개선이 필요합니다.")
    if org_score < 3:
        recommendations.append("조직 및 역량 영역 강화가 필요합니다.")
    if data_score < 3:
        recommendations.append("데이터 및 기술 인프라 개선이 필요합니다.")
    if process_score < 3:
        recommendations.append("프로세스 및 거버넌스 체계 수립이 필요합니다.")

    return {
        "overall_level": overall_level,
        "overall_score": round(overall_score, 2),
        "scores": {
            "strategy": {"score": round(strategy_score, 2), "items": assessment.strategy},
            "organization": {"score": round(org_score, 2), "items": assessment.organization},
            "data_technology": {"score": round(data_score, 2), "items": assessment.data_technology},
            "process": {"score": round(process_score, 2), "items": assessment.process}
        },
        "recommendations": recommendations,
        "priority_improvements": recommendations,
        "strengths": [],
        "weaknesses": []
    }

