"""
Stage 1: 전략 로드맵 관련 로직
"""
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any, List, Optional
import json

from ..common.database import get_project, update_project
from .models import RoadmapInput


async def save_roadmap(project_id: str, roadmap: RoadmapInput):
    """로드맵 저장"""
    roadmap_data = {
        "vision": roadmap.vision,
        "goals": roadmap.goals,
        "kpis": roadmap.kpis,
        "phases": roadmap.phases,
        "created_at": datetime.now().isoformat()
    }

    update_project(project_id, {"stage1_roadmap": roadmap_data})

    return {
        "status": "success",
        "message": "로드맵이 저장되었습니다.",
        "roadmap": roadmap_data
    }


async def get_roadmap(project_id: str):
    """로드맵 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "roadmap": {}}

    return {
        "status": "success",
        "roadmap": project.get("stage1_roadmap", {})
    }


async def analyze_roadmap_with_ai(project_id: str, roadmap_data: Optional[Dict[str, Any]] = None):
    """AI 기반 로드맵 분석"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # 요청 본문에서 로드맵 데이터를 가져오거나, 프로젝트에서 가져옴
        if roadmap_data and (roadmap_data.get("vision") or roadmap_data.get("goals") or roadmap_data.get("kpis") or roadmap_data.get("phases")):
            roadmap = roadmap_data
        else:
            roadmap = project.get("stage1_roadmap", {})

        if not roadmap or (not roadmap.get("vision") and not roadmap.get("goals") and not roadmap.get("kpis") and not roadmap.get("phases")):
            raise HTTPException(status_code=400, detail="분석할 로드맵 데이터가 없습니다.")

        # 에이전트 오케스트레이터 가져오기
        from src.agents.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()

        # 프로젝트 정보 가져오기
        company_profile = project.get("company_profile", {})
        opportunities = project.get("stage1_opportunities", [])
        
        # StrategyAnalystAgent를 사용하여 분석
        strategy_agent = orchestrator.agents.get("strategy")
        
        if not strategy_agent:
            # 에이전트가 없으면 기본 분석 수행
            return await _perform_basic_roadmap_analysis(roadmap, company_profile, opportunities)
        
        # AI 분석 수행
        analysis_result = await _perform_ai_roadmap_analysis(
            strategy_agent, 
            roadmap, 
            company_profile,
            opportunities
        )

        # 분석 결과 저장
        analysis_data = {
            "analysis_date": datetime.now().isoformat(),
            "roadmap_data": roadmap,
            "analysis_result": analysis_result
        }
        
        # 프로젝트에 분석 결과 저장
        existing_roadmap = project.get("stage1_roadmap", {})
        update_project(project_id, {
            "stage1_roadmap": existing_roadmap,
            "stage1_roadmap_analysis": analysis_data
        })

        return {
            "status": "success",
            "message": "AI 로드맵 분석이 완료되었습니다.",
            "analysis": analysis_result
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 분석 중 오류 발생: {str(e)}")


async def _perform_ai_roadmap_analysis(
    strategy_agent,
    roadmap: Dict[str, Any],
    company_profile: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """AI 에이전트를 사용한 로드맵 분석"""
    try:
        vision = roadmap.get("vision", "")
        goals = roadmap.get("goals", [])
        kpis = roadmap.get("kpis", [])
        phases = roadmap.get("phases", [])
        
        # 로드맵 완성도 평가
        completeness_score = _calculate_roadmap_completeness(roadmap)
        
        # 목표 분석
        goals_analysis = _analyze_goals(goals)
        
        # KPI 분석
        kpis_analysis = _analyze_kpis(kpis)
        
        # 단계별 로드맵 분석
        phases_analysis = _analyze_phases(phases)
        
        # 비전과 목표의 정합성 분석
        alignment_analysis = _analyze_vision_goals_alignment(vision, goals)
        
        # 기회 발굴과 로드맵의 연계성 분석
        opportunity_linkage = _analyze_opportunity_linkage(opportunities, phases)
        
        recommendations = []
        strengths = []
        improvements = []
        
        # 완성도 기반 권장사항
        if completeness_score < 0.6:
            recommendations.append("로드맵의 핵심 요소(비전, 목표, KPI, 단계별 계획)를 보완하세요.")
            improvements.append("로드맵 완성도 향상 필요")
        else:
            strengths.append("로드맵의 주요 구성 요소가 잘 정의되어 있습니다.")
        
        # 목표 분석 기반 권장사항
        if goals_analysis.get("count", 0) < 3:
            recommendations.append("전략적 목표를 최소 3개 이상 구체화하세요.")
        else:
            strengths.append(f"{goals_analysis.get('count', 0)}개의 명확한 전략적 목표가 설정되어 있습니다.")
        
        # KPI 분석 기반 권장사항
        if kpis_analysis.get("count", 0) < 3:
            recommendations.append("측정 가능한 KPI를 최소 3개 이상 정의하세요.")
        else:
            strengths.append(f"{kpis_analysis.get('count', 0)}개의 KPI가 정의되어 있어 성과 측정이 가능합니다.")
        
        # 단계별 로드맵 분석 기반 권장사항
        if phases_analysis.get("total_items", 0) < 5:
            recommendations.append("단계별 로드맵에 더 많은 구체적인 과제를 추가하세요.")
        else:
            strengths.append(f"총 {phases_analysis.get('total_items', 0)}개의 과제가 단계별로 계획되어 있습니다.")
        
        # LLM 에이전트를 통한 추가 분석 시도
        if strategy_agent and hasattr(strategy_agent, 'llm_provider') and strategy_agent.llm_provider:
            try:
                prompt = f"""다음 AI 전략 및 로드맵 데이터를 분석하고 개선 권장사항을 제시해주세요.

[기업 프로필]
{json.dumps(company_profile, ensure_ascii=False, indent=2)}

[AI 비전]
{vision}

[전략적 목표]
{json.dumps(goals, ensure_ascii=False, indent=2)}

[핵심 성과 지표 (KPI)]
{json.dumps(kpis, ensure_ascii=False, indent=2)}

[단계별 로드맵]
{json.dumps(phases, ensure_ascii=False, indent=2)}

[분석 요청]
1. 비전과 목표의 정합성 평가
2. 목표의 구체성 및 측정 가능성 평가
3. KPI의 적절성 및 달성 가능성 평가
4. 단계별 로드맵의 현실성 및 실행 가능성 평가
5. 종합 개선 권장사항 제시

JSON 형식으로 응답해주세요."""
                
                llm_response = await strategy_agent.llm_provider.generate(
                    prompt, 
                    strategy_agent.get_system_prompt()
                )
                
                # LLM 응답 파싱
                if llm_response:
                    recommendations.append(f"AI 심층 분석: {llm_response[:500]}...")
            except Exception as e:
                # LLM 분석 실패 시 기본 분석 결과 사용
                pass

        return {
            "completeness_score": completeness_score,
            "vision": vision,
            "goals_analysis": goals_analysis,
            "kpis_analysis": kpis_analysis,
            "phases_analysis": phases_analysis,
            "alignment_analysis": alignment_analysis,
            "opportunity_linkage": opportunity_linkage,
            "strengths": strengths,
            "recommendations": recommendations,
            "improvements": improvements,
            "summary": f"로드맵 완성도 {completeness_score*100:.0f}%. {len(goals)}개 목표, {len(kpis)}개 KPI, {phases_analysis.get('total_items', 0)}개 과제가 계획되어 있습니다."
        }
    except Exception as e:
        # 에러 발생 시 기본 분석 반환
        return await _perform_basic_roadmap_analysis(roadmap, company_profile, opportunities)


def _calculate_roadmap_completeness(roadmap: Dict[str, Any]) -> float:
    """로드맵 완성도 점수 계산 (0.0 ~ 1.0)"""
    score = 0.0
    
    # 비전 (25%)
    if roadmap.get("vision") and roadmap.get("vision").strip():
        score += 0.25
    
    # 목표 (25%)
    goals = roadmap.get("goals", [])
    if goals and len(goals) > 0:
        score += 0.25
    
    # KPI (25%)
    kpis = roadmap.get("kpis", [])
    if kpis and len(kpis) > 0:
        score += 0.25
    
    # 단계별 계획 (25%)
    phases = roadmap.get("phases", [])
    if phases and len(phases) > 0:
        score += 0.25
    
    return score


def _analyze_goals(goals: List[Any]) -> Dict[str, Any]:
    """목표 분석"""
    if not goals:
        return {"count": 0, "quality": "low", "recommendations": []}
    
    # 목표가 문자열인지 객체인지 확인
    goal_objects = []
    for goal in goals:
        if isinstance(goal, str):
            goal_objects.append({"name": goal, "target": "", "timeline": ""})
        elif isinstance(goal, dict):
            goal_objects.append(goal)
    
    return {
        "count": len(goal_objects),
        "goals": goal_objects,
        "quality": "high" if len(goal_objects) >= 3 else "medium" if len(goal_objects) >= 1 else "low"
    }


def _analyze_kpis(kpis: List[Any]) -> Dict[str, Any]:
    """KPI 분석"""
    if not kpis:
        return {"count": 0, "quality": "low", "recommendations": []}
    
    kpi_objects = []
    for kpi in kpis:
        if isinstance(kpi, dict):
            kpi_objects.append(kpi)
        elif isinstance(kpi, str):
            kpi_objects.append({"name": kpi})
    
    measurable_count = sum(1 for kpi in kpi_objects if kpi.get("target") or kpi.get("current"))
    
    return {
        "count": len(kpi_objects),
        "kpis": kpi_objects,
        "measurable_count": measurable_count,
        "quality": "high" if measurable_count >= 3 else "medium" if measurable_count >= 1 else "low"
    }


def _analyze_phases(phases: List[Any]) -> Dict[str, Any]:
    """단계별 로드맵 분석"""
    if not phases:
        return {"total_items": 0, "phases": [], "quality": "low"}
    
    phase_objects = []
    total_items = 0
    
    for phase in phases:
        if isinstance(phase, dict):
            items = phase.get("items", [])
            if isinstance(items, str):
                items = [item.strip() for item in items.split(",") if item.strip()]
            elif not isinstance(items, list):
                items = []
            
            total_items += len(items)
            phase_objects.append({
                "name": phase.get("name", ""),
                "duration": phase.get("duration", ""),
                "items": items,
                "item_count": len(items)
            })
        elif isinstance(phase, str):
            phase_objects.append({
                "name": phase,
                "duration": "",
                "items": [],
                "item_count": 0
            })
    
    return {
        "total_items": total_items,
        "phases": phase_objects,
        "phase_count": len(phase_objects),
        "quality": "high" if total_items >= 5 else "medium" if total_items >= 2 else "low"
    }


def _analyze_vision_goals_alignment(vision: str, goals: List[Any]) -> Dict[str, Any]:
    """비전과 목표의 정합성 분석"""
    if not vision or not goals:
        return {"alignment_score": 0.0, "assessment": "데이터 부족"}
    
    # 간단한 키워드 매칭 (실제로는 LLM을 사용하는 것이 좋음)
    vision_lower = vision.lower()
    goal_texts = []
    for goal in goals:
        if isinstance(goal, str):
            goal_texts.append(goal.lower())
        elif isinstance(goal, dict):
            goal_texts.append(goal.get("name", "").lower())
    
    # 공통 키워드 찾기
    common_keywords = []
    vision_words = set(vision_lower.split())
    for goal_text in goal_texts:
        goal_words = set(goal_text.split())
        common = vision_words.intersection(goal_words)
        common_keywords.extend(common)
    
    alignment_score = min(len(set(common_keywords)) / max(len(goals), 1), 1.0)
    
    return {
        "alignment_score": alignment_score,
        "assessment": "높음" if alignment_score >= 0.5 else "중간" if alignment_score >= 0.3 else "낮음",
        "common_keywords": list(set(common_keywords))[:5]
    }


def _analyze_opportunity_linkage(opportunities: List[Dict[str, Any]], phases: List[Any]) -> Dict[str, Any]:
    """기회 발굴과 로드맵의 연계성 분석"""
    if not opportunities or not phases:
        return {"linkage_score": 0.0, "linked_count": 0, "assessment": "데이터 부족"}
    
    # 단계별 과제 추출
    phase_items = []
    for phase in phases:
        if isinstance(phase, dict):
            items = phase.get("items", [])
            if isinstance(items, list):
                phase_items.extend([item.lower() for item in items if isinstance(item, str)])
    
    # 기회명과 과제명 매칭
    linked_count = 0
    for opp in opportunities:
        opp_name = opp.get("name", "").lower()
        for item in phase_items:
            if opp_name in item or item in opp_name:
                linked_count += 1
                break
    
    linkage_score = linked_count / max(len(opportunities), 1)
    
    return {
        "linkage_score": linkage_score,
        "linked_count": linked_count,
        "total_opportunities": len(opportunities),
        "assessment": "높음" if linkage_score >= 0.7 else "중간" if linkage_score >= 0.4 else "낮음"
    }


async def _perform_basic_roadmap_analysis(
    roadmap: Dict[str, Any],
    company_profile: Dict[str, Any],
    opportunities: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """기본 로드맵 분석 (AI 에이전트 없이)"""
    completeness_score = _calculate_roadmap_completeness(roadmap)
    goals_analysis = _analyze_goals(roadmap.get("goals", []))
    kpis_analysis = _analyze_kpis(roadmap.get("kpis", []))
    phases_analysis = _analyze_phases(roadmap.get("phases", []))
    alignment_analysis = _analyze_vision_goals_alignment(roadmap.get("vision", ""), roadmap.get("goals", []))
    opportunity_linkage = _analyze_opportunity_linkage(opportunities, roadmap.get("phases", []))
    
    recommendations = []
    if completeness_score < 0.6:
        recommendations.append("로드맵의 핵심 요소를 보완하세요.")
    if goals_analysis.get("count", 0) < 3:
        recommendations.append("전략적 목표를 더 구체화하세요.")
    if kpis_analysis.get("count", 0) < 3:
        recommendations.append("측정 가능한 KPI를 추가하세요.")
    
    return {
        "completeness_score": completeness_score,
        "vision": roadmap.get("vision", ""),
        "goals_analysis": goals_analysis,
        "kpis_analysis": kpis_analysis,
        "phases_analysis": phases_analysis,
        "alignment_analysis": alignment_analysis,
        "opportunity_linkage": opportunity_linkage,
        "strengths": [],
        "recommendations": recommendations,
        "improvements": recommendations,
        "summary": f"로드맵 완성도 {completeness_score*100:.0f}%"
    }

