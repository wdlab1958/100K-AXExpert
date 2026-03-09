"""
Stage 1: 기회 발굴 관련 로직
"""
from fastapi import HTTPException
from datetime import datetime
from typing import Dict, Any, List, Optional, Union
import json
import re

from ..common.database import get_project, update_project
from .models import OpportunityInput, OpportunityListInput


async def save_opportunities(project_id: str, opportunity: Union[OpportunityInput, OpportunityListInput]):
    """AI 기회 발굴 저장 (단일 기회 또는 전체 목록)"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    # Batch Save (Save All)
    if isinstance(opportunity, OpportunityListInput):
        new_opportunities = []
        for index, opp in enumerate(opportunity.opportunities):
            new_opp = {
                "id": f"OPP-{project_id[:4]}-{index+1:03d}",
                "name": opp.name,
                "description": opp.description,
                "business_area": opp.business_area,
                "priority_quadrant": opp.priority_quadrant,
                "expected_impact": opp.expected_impact,
                "implementation_difficulty": opp.implementation_difficulty,
                "estimated_timeline": opp.estimated_timeline,
                "required_resources": opp.required_resources,
                "data_availability": opp.data_availability,
                "urgency": opp.urgency,
                "strategic_alignment": opp.strategic_alignment,
                "created_at": datetime.now().isoformat()
            }
            new_opportunities.append(new_opp)

        update_project(project_id, {"stage1_opportunities": new_opportunities})

        return {
            "status": "success",
            "message": f"{len(new_opportunities)}개의 AI 기회가 저장되었습니다.",
            "opportunities": new_opportunities
        }

    # Single Save (Append)
    existing_opportunities = project.get("stage1_opportunities", [])

    new_opp = {
        "id": f"OPP-{project_id[:4]}-{len(existing_opportunities)+1:03d}",
        "name": opportunity.name,
        "description": opportunity.description,
        "business_area": opportunity.business_area,
        "priority_quadrant": opportunity.priority_quadrant,
        "expected_impact": opportunity.expected_impact,
        "implementation_difficulty": opportunity.implementation_difficulty,
        "estimated_timeline": opportunity.estimated_timeline,
        "required_resources": opportunity.required_resources,
        "data_availability": opportunity.data_availability,
        "urgency": opportunity.urgency,
        "strategic_alignment": opportunity.strategic_alignment,
        "created_at": datetime.now().isoformat()
    }

    existing_opportunities.append(new_opp)
    update_project(project_id, {"stage1_opportunities": existing_opportunities})

    return {
        "status": "success",
        "message": "AI 기회가 저장되었습니다.",
        "opportunity": new_opp
    }


async def get_opportunities(project_id: str):
    """AI 기회 발굴 조회"""
    project = get_project(project_id)
    if not project:
        return {"status": "success", "opportunities": []}

    return {
        "status": "success",
        "opportunities": project.get("stage1_opportunities", [])
    }


async def analyze_opportunities_with_ai(project_id: str, opportunities_data: Optional[Dict[str, Any]] = None):
    """AI 기반 기회 발굴 분석"""
    project = get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="프로젝트를 찾을 수 없습니다.")

    try:
        # 요청 본문에서 기회 데이터를 가져오거나, 저장된 프로젝트 데이터에서 가져옴
        if opportunities_data and opportunities_data.get("opportunities"):
            opportunities = opportunities_data["opportunities"]
        else:
            opportunities = project.get("stage1_opportunities", [])

        if not opportunities:
            raise HTTPException(status_code=400, detail="분석할 기회 데이터가 없습니다. 먼저 기회를 저장해주세요.")

        # 기업 프로필
        company_profile = project.get("company_profile", {})

        # 에이전트 오케스트레이터 가져오기
        from src.agents.agent_orchestrator import get_orchestrator
        orchestrator = get_orchestrator()
        strategy_agent = orchestrator.agents.get("strategy")

        # AI 분석 수행
        analysis_result = await _perform_ai_opportunity_analysis(
            strategy_agent,
            opportunities,
            company_profile
        )

        # 분석 결과 저장
        analysis_data = {
            "analysis_date": datetime.now().isoformat(),
            "opportunities_count": len(opportunities),
            "analysis_result": analysis_result
        }

        update_project(project_id, {
            "stage1_opportunities_analysis": analysis_data
        })

        return {
            "status": "success",
            "message": "AI 기회 발굴 분석이 완료되었습니다.",
            "analysis": analysis_result
        }
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"AI 분석 중 오류 발생: {str(e)}")


async def _perform_ai_opportunity_analysis(
    strategy_agent,
    opportunities: List[Dict[str, Any]],
    company_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """AI 에이전트를 사용한 기회 발굴 분석"""
    try:
        # ── 1. 기본 우선순위 점수 계산 ──
        scored_opportunities = []
        for opp in opportunities:
            scored_opp = dict(opp)
            scored_opp["priority_score"] = _calculate_priority_score(opp)
            scored_opp["recommendation"] = _generate_opportunity_recommendation(opp)
            scored_opportunities.append(scored_opp)

        scored_opportunities.sort(key=lambda x: x["priority_score"], reverse=True)
        priority_opportunities = [o for o in scored_opportunities if o["priority_score"] >= 7]
        priority_matrix = _generate_priority_matrix(scored_opportunities)

        # ── 2. LLM 분석 시도 ──
        llm_analysis = None
        try:
            from src.core.llm_provider import LLMProvider
            llm = LLMProvider(temperature=0.3)
            prompt = _build_opportunity_analysis_prompt(opportunities, company_profile)
            llm_response = await llm.generate(prompt)
            if llm_response:
                llm_analysis = _parse_llm_opportunity_response(llm_response)
        except Exception as _llm_err:
            import logging
            logging.getLogger(__name__).warning(f"LLM 분석 실패 (기본 분석으로 대체): {_llm_err}")

        # ── 3. 결과 조합 ──
        if llm_analysis:
            recommendations = llm_analysis.get("recommendations", [])
            summary = llm_analysis.get("executive_summary",
                f"총 {len(opportunities)}개의 기회를 분석하였습니다.")
            synergy_notes = llm_analysis.get("synergy_notes", "")
            risk_notes = llm_analysis.get("risk_notes", "")
        else:
            # 기본 권장사항
            recommendations = []
            if priority_opportunities:
                recommendations.append(
                    f"식별된 {len(priority_opportunities)}개의 고우선순위 기회를 우선적으로 추진하시기 바랍니다."
                )
            qw = priority_matrix.get("quick_win", [])
            st = priority_matrix.get("strategic", [])
            if qw:
                names = ", ".join(o["name"] for o in qw[:3])
                recommendations.append(
                    f"Quick Win 과제({names} 등)부터 착수하여 조기 성과를 확보하고 조직의 AI 추진 동력을 확보하시기 바랍니다."
                )
            if st:
                recommendations.append(
                    "전략적 가치가 높은 과제는 중장기 로드맵에 반영하여 체계적으로 추진하시기 바랍니다."
                )
            recommendations.append(
                "데이터 가용성이 낮은 과제는 데이터 수집 인프라 구축을 선행 과제로 설정하시기 바랍니다."
            )
            summary = (
                f"총 {len(opportunities)}개의 AI 도입 기회를 분석한 결과, "
                f"{len(priority_opportunities)}개의 고우선순위 과제와 "
                f"{len(priority_matrix.get('quick_win', []))}개의 Quick Win 과제가 식별되었습니다."
            )
            synergy_notes = ""
            risk_notes = ""

        return {
            "total_opportunities": len(opportunities),
            "analyzed_opportunities": scored_opportunities,
            "priority_opportunities": priority_opportunities[:5],
            "recommendations": recommendations,
            "summary": summary,
            "synergy_notes": synergy_notes,
            "risk_notes": risk_notes,
            "priority_matrix": priority_matrix,
            "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    except Exception:
        return await _perform_basic_opportunity_analysis(opportunities, company_profile)


def _build_opportunity_analysis_prompt(
    opportunities: List[Dict[str, Any]],
    company_profile: Dict[str, Any]
) -> str:
    """LLM 프롬프트 생성"""
    opp_text = "\n".join(
        _build_opportunity_prompt_text(opp) for opp in opportunities
    )

    industry = (company_profile.get("industry") or
                company_profile.get("업종") or "미상")
    size = (company_profile.get("size") or
            company_profile.get("규모") or "미상")
    name = (company_profile.get("company_name") or
            company_profile.get("name") or "")

    company_str = f"업종: {industry}"
    if size != "미상":
        company_str += f", 규모: {size}"
    if name:
        company_str += f", 기업명: {name}"

    return f"""당신은 AI 전략 컨설팅 전문가입니다. 아래 기업의 AI 도입 기회 목록을 분석하여 경영진 보고서 수준의 한국어 분석 결과를 JSON으로만 작성하십시오.

[기업 정보]
{company_str}

[AI 도입 기회 목록 ({len(opportunities)}건)]
{opp_text}

아래 JSON 형식으로만 응답하십시오. JSON 외에는 어떠한 텍스트도 포함하지 마십시오:
{{
  "executive_summary": "본 보고서는... 로 시작하는 4~5문장의 종합 요약. 전문적 문어체(입니다/합니다)",
  "recommendations": [
    "권장사항 1: 구체적 실행 방안 (2문장, 문어체)",
    "권장사항 2: 구체적 실행 방안 (2문장, 문어체)",
    "권장사항 3: 구체적 실행 방안 (2문장, 문어체)",
    "권장사항 4: 구체적 실행 방안 (2문장, 문어체)",
    "권장사항 5: 구체적 실행 방안 (2문장, 문어체)"
  ],
  "synergy_notes": "기회들 간 시너지 및 연계 효과 분석. 3~4문장, 문어체.",
  "risk_notes": "주요 구현 리스크 및 선제적 고려사항. 3~4문장, 문어체."
}}"""


def _parse_llm_opportunity_response(llm_response: str) -> Optional[Dict[str, Any]]:
    """LLM 응답에서 JSON 파싱"""
    try:
        # 마크다운 코드 블록 제거
        cleaned = re.sub(r'```(?:json)?\s*', '', llm_response).strip()
        # JSON 블록 추출
        json_match = re.search(r'\{[\s\S]*\}', cleaned)
        if json_match:
            data = json.loads(json_match.group())
            # 필수 키 검증
            if "executive_summary" in data or "recommendations" in data:
                return data
    except Exception:
        pass
    return None


def _calculate_priority_score(opportunity: Dict[str, Any]) -> float:
    """기회 우선순위 점수 계산 (0~10점)"""
    score = 3.0

    # ── priority_quadrant 기반 기본 점수 ──
    quadrant_map = {
        "quick_win": 3.0, "quick-win": 3.0, "quickwin": 3.0,
        "strategic": 2.0,
        "fill_in": 1.0, "fill-in": 1.0, "fillin": 1.0,
        "reconsider": 0.0,
    }
    quadrant = str(opportunity.get("priority_quadrant", "")).lower().strip()
    score += quadrant_map.get(quadrant, 1.5)

    # ── ROI 잠재력 (roi_potential > expected_impact 순으로 확인) ──
    roi_val = (opportunity.get("roi_potential") or
               opportunity.get("expected_impact") or "")
    if roi_val:
        roi_map = {"low": 0, "medium": 1, "high": 2, "very_high": 3,
                   "낮음": 0, "중간": 1, "높음": 2, "매우 높음": 3}
        score += roi_map.get(str(roi_val).lower().strip(), 1)
    else:
        # strategic_alignment 기반 ROI 추정
        strategic = opportunity.get("strategic_alignment", 3)
        if isinstance(strategic, (int, float)):
            score += (strategic / 5.0) * 2.0

    # ── 구현 복잡도 (낮을수록 높은 점수) ──
    cpx_val = (opportunity.get("complexity") or
               opportunity.get("implementation_difficulty") or "")
    if cpx_val:
        cpx_map = {"low": 2, "medium": 1, "high": 0, "very_high": -1,
                   "낮음": 2, "중간": 1, "높음": 0, "매우 높음": -1}
        score += cpx_map.get(str(cpx_val).lower().strip(), 1)
    else:
        # data_availability가 높으면 복잡도 낮다고 추정
        data_avail = opportunity.get("data_availability", 3)
        if isinstance(data_avail, (int, float)):
            score += (data_avail / 5.0) * 1.5

    # ── 긴급도 (1~5) ──
    urgency = opportunity.get("urgency", 3)
    if isinstance(urgency, (int, float)):
        score += (urgency / 5.0) * 1.0

    return min(round(score, 1), 10.0)


def _generate_opportunity_recommendation(opportunity: Dict[str, Any]) -> str:
    """기회별 사분면 분류 (priority_quadrant 우선, ROI/복잡도 폴백)"""
    # priority_quadrant가 있으면 그대로 사용
    quadrant = str(opportunity.get("priority_quadrant", "")).lower().strip()
    quadrant_label = {
        "quick_win": "Quick Win: 즉시 착수하여 조기 성과 확보 권장",
        "quick-win": "Quick Win: 즉시 착수하여 조기 성과 확보 권장",
        "strategic": "Strategic: 중장기 전략 과제로 체계적 계획 수립 필요",
        "fill_in":   "Fill-in: 여유 자원 확보 시 추진 검토 권장",
        "fill-in":   "Fill-in: 여유 자원 확보 시 추진 검토 권장",
        "reconsider":"Reconsider: ROI 및 구현 가능성 재검토 필요",
    }
    if quadrant and quadrant in quadrant_label:
        return quadrant_label[quadrant]

    # ROI/복잡도 기반 폴백
    roi_val = str(opportunity.get("roi_potential") or
                  opportunity.get("expected_impact") or "").lower().strip()
    cpx_val = str(opportunity.get("complexity") or
                  opportunity.get("implementation_difficulty") or "").lower().strip()

    high_roi = roi_val in ["high", "very_high", "높음", "매우 높음"]
    low_cpx = cpx_val in ["low", "낮음"]
    med_cpx = cpx_val in ["medium", "중간"]

    if high_roi and low_cpx:
        return "Quick Win: 즉시 착수하여 조기 성과 확보 권장"
    elif high_roi:
        return "Strategic: 중장기 전략 과제로 체계적 계획 수립 필요"
    elif roi_val in ["medium", "중간"] and (low_cpx or med_cpx):
        return "Fill-in: 여유 자원 확보 시 추진 검토 권장"
    else:
        return "Reconsider: ROI 및 구현 가능성 재검토 필요"


def _generate_priority_matrix(analyzed_opportunities: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """우선순위 매트릭스 생성"""
    matrix = {"quick_win": [], "strategic": [], "fill_in": [], "reconsider": []}

    for opp in analyzed_opportunities:
        rec = opp.get("recommendation", "")
        if "Quick Win" in rec:
            matrix["quick_win"].append(opp)
        elif "Strategic" in rec:
            matrix["strategic"].append(opp)
        elif "Fill-in" in rec:
            matrix["fill_in"].append(opp)
        else:
            matrix["reconsider"].append(opp)

    return matrix


def _build_opportunity_prompt_text(opp: Dict[str, Any]) -> str:
    """프롬프트용 기회 항목 텍스트 생성"""
    parts = [f"[{opp.get('id', 'N/A')}] {opp.get('name', '')}"]
    if opp.get("description"):
        parts.append(f"  설명: {opp['description'][:150]}")

    attrs = []
    if opp.get("business_area"):
        attrs.append(f"영역: {opp['business_area']}")
    if opp.get("priority_quadrant"):
        qmap = {"quick_win": "Quick Win", "quick-win": "Quick Win",
                "strategic": "Strategic", "fill_in": "Fill-in",
                "fill-in": "Fill-in", "reconsider": "Reconsider"}
        q = qmap.get(opp["priority_quadrant"], opp["priority_quadrant"])
        attrs.append(f"사전분류: {q}")
    if opp.get("roi_potential") or opp.get("expected_impact"):
        attrs.append(f"ROI: {opp.get('roi_potential') or opp.get('expected_impact')}")
    if opp.get("complexity") or opp.get("implementation_difficulty"):
        attrs.append(f"복잡도: {opp.get('complexity') or opp.get('implementation_difficulty')}")
    for k, label in [("data_availability", "데이터가용성"), ("urgency", "긴급도"), ("strategic_alignment", "전략정합성")]:
        if opp.get(k) is not None:
            attrs.append(f"{label}: {opp[k]}/5")
    if attrs:
        parts.append(f"  속성: {', '.join(attrs)}")
    return "\n".join(parts)


async def _perform_basic_opportunity_analysis(
    opportunities: List[Dict[str, Any]],
    company_profile: Dict[str, Any]
) -> Dict[str, Any]:
    """기본 기회 발굴 분석 (LLM 없이)"""
    analyzed = []
    for opp in opportunities:
        scored = dict(opp)
        scored["priority_score"] = _calculate_priority_score(opp)
        scored["recommendation"] = _generate_opportunity_recommendation(opp)
        analyzed.append(scored)

    analyzed.sort(key=lambda x: x["priority_score"], reverse=True)
    priority_opps = [o for o in analyzed if o["priority_score"] >= 7]
    matrix = _generate_priority_matrix(analyzed)

    qw_names = ", ".join(o["name"] for o in matrix.get("quick_win", [])[:3])
    recs = []
    if priority_opps:
        recs.append(f"{len(priority_opps)}개의 고우선순위 기회를 우선 추진하시기 바랍니다.")
    if qw_names:
        recs.append(f"Quick Win 과제({qw_names})부터 착수하여 조기 성과를 확보하시기 바랍니다.")
    recs.append("전략적 가치가 높은 과제는 중장기 로드맵에 반영하여 체계적으로 추진하시기 바랍니다.")

    return {
        "total_opportunities": len(opportunities),
        "analyzed_opportunities": analyzed,
        "priority_opportunities": priority_opps[:5],
        "recommendations": recs,
        "summary": (
            f"총 {len(opportunities)}개의 AI 도입 기회를 분석한 결과, "
            f"{len(priority_opps)}개의 고우선순위 과제와 "
            f"{len(matrix.get('quick_win', []))}개의 Quick Win 과제가 식별되었습니다."
        ),
        "synergy_notes": "",
        "risk_notes": "",
        "priority_matrix": matrix,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
