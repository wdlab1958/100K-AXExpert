"""
AI Consulting Assistant Platform - Report Generator Service
컨설팅 보고서 생성 서비스
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json

import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

from config.settings import settings, CONSULTING_FRAMEWORK


class ReportGenerator:
    """컨설팅 보고서 생성기"""

    def __init__(self):
        self.reports_dir = settings.REPORTS_DIR
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    def generate_executive_summary(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Executive Summary 생성"""
        company = project_data.get("company_profile", {})
        assessment = project_data.get("maturity_assessment", {})
        scenarios = project_data.get("scenarios", [])
        selected_scenario = project_data.get("selected_scenario")

        # 선택된 시나리오 찾기
        chosen_scenario = None
        if selected_scenario:
            for s in scenarios:
                if s.get("id") == selected_scenario:
                    chosen_scenario = s
                    break

        report = {
            "title": f"{company.get('name', '기업')} AI 전환 컨설팅 Executive Summary",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "sections": []
        }

        # 1. 프로젝트 개요
        report["sections"].append({
            "title": "1. 프로젝트 개요",
            "content": f"""
**기업명**: {company.get('name', 'N/A')}
**산업 분류**: {company.get('industry', 'N/A')}
**기업 규모**: {company.get('company_size', 'N/A')}

본 보고서는 {company.get('name', '해당 기업')}의 AI 인프라 도입 및 구축을 위한
전문 컨설팅 결과를 요약한 문서입니다.
            """.strip()
        })

        # 2. AI 성숙도 진단 결과
        if assessment:
            overall_level = assessment.get("overall_level", "N/A")
            scores = assessment.get("scores", {})

            maturity_content = f"""
**종합 성숙도 Level**: {overall_level}

| 영역 | 현재 Level | 점수 |
|------|-----------|------|
| 전략/비전 | {scores.get('strategy', {}).get('level', '-')} | {scores.get('strategy', {}).get('score', '-'):.1f} |
| 조직/역량 | {scores.get('organization', {}).get('level', '-')} | {scores.get('organization', {}).get('score', '-'):.1f} |
| 데이터/기술 | {scores.get('data_tech', {}).get('level', '-')} | {scores.get('data_tech', {}).get('score', '-'):.1f} |
| 프로세스 | {scores.get('process', {}).get('level', '-')} | {scores.get('process', {}).get('score', '-'):.1f} |

**주요 개선 권고사항**:
"""
            for rec in assessment.get("recommendations", [])[:5]:
                maturity_content += f"\n- {rec}"

            report["sections"].append({
                "title": "2. AI 성숙도 진단 결과",
                "content": maturity_content.strip()
            })

        # 3. 시나리오 분석
        if scenarios:
            scenario_content = "**분석된 시나리오**:\n\n"

            for s in scenarios:
                roi = s.get("roi_analysis", {}).get("metrics", {}).get("roi_percent", 0)
                risk = s.get("risk_assessment", {}).get("risk_level", "N/A")
                score = s.get("overall_score", 0)

                scenario_content += f"""
### {s.get('name', 'N/A')} ({s.get('type', 'N/A')})
- **투자 예산**: {s.get('parameters', {}).get('investment_budget', 0):.1f}억원
- **예상 ROI**: {roi:.1f}%
- **리스크 레벨**: {risk}
- **종합 점수**: {score:.1f}

"""

            if chosen_scenario:
                scenario_content += f"""
---
**선택된 시나리오**: {chosen_scenario.get('name')}

{chosen_scenario.get('description', '')}
"""

            report["sections"].append({
                "title": "3. 시나리오 분석",
                "content": scenario_content.strip()
            })

        # 4. 권고사항 및 Next Steps
        recommendations = project_data.get("recommendations", [])
        rec_content = "**핵심 권고사항**:\n\n"

        for i, rec in enumerate(recommendations[:10], 1):
            rec_content += f"{i}. {rec}\n"

        rec_content += """

**Next Steps**:
1. 선택된 시나리오에 대한 세부 실행 계획 수립
2. 필요 인력 및 예산 확보
3. 파일럿 프로젝트 대상 선정
4. 변화 관리 프로그램 준비
5. 정기 리뷰 체계 구축
"""

        report["sections"].append({
            "title": "4. 권고사항 및 Next Steps",
            "content": rec_content.strip()
        })

        return report

    def generate_full_report(
        self,
        project_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """전체 컨설팅 보고서 생성"""
        company = project_data.get("company_profile", {})

        report = {
            "title": f"{company.get('name', '기업')} AI 인프라 도입 컨설팅 종합 보고서",
            "generated_at": datetime.now().isoformat(),
            "version": "1.0",
            "chapters": []
        }

        # Chapter 1: 개요
        report["chapters"].append({
            "number": 1,
            "title": "개요",
            "sections": [
                {"title": "1.1 배경 및 목적", "content": self._generate_background(company)},
                {"title": "1.2 프로젝트 범위", "content": self._generate_scope(project_data)},
                {"title": "1.3 추진 경과", "content": self._generate_progress(project_data)}
            ]
        })

        # Chapter 2: 현황 분석
        assessment = project_data.get("maturity_assessment", {})
        report["chapters"].append({
            "number": 2,
            "title": "현황 분석",
            "sections": [
                {"title": "2.1 AI 성숙도 진단", "content": self._generate_maturity_detail(assessment)},
                {"title": "2.2 IT 인프라 분석", "content": self._generate_infra_analysis(company)},
                {"title": "2.3 조직 역량 분석", "content": self._generate_org_analysis(company)},
                {"title": "2.4 데이터 자산 분석", "content": self._generate_data_analysis(company)}
            ]
        })

        # Chapter 3: AI 전략 수립
        opportunities = project_data.get("opportunities", {})
        report["chapters"].append({
            "number": 3,
            "title": "AI 전략 수립",
            "sections": [
                {"title": "3.1 AI 비전", "content": self._generate_vision(company)},
                {"title": "3.2 핵심 Use Case", "content": self._generate_use_cases(opportunities)},
                {"title": "3.3 우선순위 결정", "content": self._generate_priorities(opportunities)}
            ]
        })

        # Chapter 4: 실행 계획
        scenarios = project_data.get("scenarios", [])
        report["chapters"].append({
            "number": 4,
            "title": "실행 계획",
            "sections": [
                {"title": "4.1 시나리오 분석", "content": self._generate_scenario_analysis(scenarios)},
                {"title": "4.2 로드맵", "content": self._generate_roadmap(project_data)},
                {"title": "4.3 투자 계획", "content": self._generate_investment_plan(scenarios)}
            ]
        })

        # Chapter 5: 기대 효과
        selected = project_data.get("selected_scenario")
        report["chapters"].append({
            "number": 5,
            "title": "기대 효과",
            "sections": [
                {"title": "5.1 정량적 효과", "content": self._generate_quantitative_benefits(scenarios, selected)},
                {"title": "5.2 정성적 효과", "content": self._generate_qualitative_benefits()},
                {"title": "5.3 ROI 분석", "content": self._generate_roi_analysis(scenarios, selected)}
            ]
        })

        # Chapter 6: 리스크 관리
        report["chapters"].append({
            "number": 6,
            "title": "리스크 관리",
            "sections": [
                {"title": "6.1 리스크 식별", "content": self._generate_risks(scenarios, selected)},
                {"title": "6.2 완화 전략", "content": self._generate_mitigation(scenarios, selected)}
            ]
        })

        return report

    def _generate_background(self, company: Dict) -> str:
        """배경 및 목적 생성"""
        return f"""
AI 기술은 산업 전반에 걸쳐 핵심 경쟁력으로 부상하고 있으며,
{company.get('industry', '해당 산업')} 분야에서도 AI 도입이 가속화되고 있습니다.

{company.get('name', '본 기업')}은 AI 기반 업무 환경으로의 전환을 통해
경쟁력을 강화하고 비즈니스 가치를 극대화하고자 본 컨설팅을 추진하였습니다.

**컨설팅 목적**:
1. 현재 AI 역량 수준 진단
2. AI 적용 가능 영역 발굴
3. 최적 AI 도입 전략 및 로드맵 수립
4. 투자 대비 효과(ROI) 분석
5. 리스크 평가 및 완화 전략 수립
        """.strip()

    def _generate_scope(self, project_data: Dict) -> str:
        """프로젝트 범위 생성"""
        return """
**컨설팅 범위**:

1. **진단 영역**
   - AI 성숙도 진단 (전략, 조직, 데이터/기술, 프로세스)
   - IT 인프라 현황 분석
   - 데이터 자산 평가

2. **전략 수립 영역**
   - AI 비전 및 목표 정의
   - Use Case 발굴 및 우선순위 결정
   - 기술 아키텍처 설계

3. **실행 계획 영역**
   - 시나리오별 투자/효과 분석
   - 실행 로드맵 수립
   - 변화 관리 계획
        """.strip()

    def _generate_progress(self, project_data: Dict) -> str:
        """추진 경과 생성"""
        return """
**추진 경과**:

| 단계 | 활동 | 상태 |
|------|------|------|
| 1단계 | AI 비전 및 전략 수립 | 완료 |
| 2단계 | Use Case 및 설계 정의 | 완료 |
| 3단계 | 시나리오 분석 | 완료 |
| 4단계 | 시나리오 검토 및 승인 | 완료 |
| 5단계 | 최종 보고서 작성 | 진행중 |
        """.strip()

    def _generate_maturity_detail(self, assessment: Dict) -> str:
        """성숙도 상세 분석 생성"""
        if not assessment:
            return "성숙도 진단 데이터가 없습니다."

        content = f"""
**종합 AI 성숙도**: Level {assessment.get('overall_level', 'N/A')}

**영역별 상세 분석**:
"""
        scores = assessment.get("scores", {})

        for dimension, data in scores.items():
            content += f"""
### {dimension.replace('_', ' ').title()}
- **Level**: {data.get('level', 'N/A')}
- **점수**: {data.get('score', 0):.2f}

세부 항목:
"""
            for item, score in data.get("items", {}).items():
                content += f"  - {item}: {score}/5\n"

        return content.strip()

    def _generate_infra_analysis(self, company: Dict) -> str:
        """IT 인프라 분석 생성"""
        infra = company.get("it_infrastructure", {})
        return f"""
**IT 인프라 현황**:

| 항목 | 현황 |
|------|------|
| 클라우드 환경 | {'보유' if infra.get('has_cloud') else '미보유'} |
| 클라우드 제공자 | {infra.get('cloud_provider', 'N/A')} |
| 데이터 웨어하우스 | {'보유' if infra.get('has_data_warehouse') else '미보유'} |
| 데이터 레이크 | {'보유' if infra.get('has_data_lake') else '미보유'} |
| GPU 서버 | {'보유' if infra.get('gpu_available') else '미보유'} |
| 레거시 시스템 수 | {infra.get('legacy_system_count', 0)}개 |
| 보안 수준 | {infra.get('security_level', 'N/A')} |
        """.strip()

    def _generate_org_analysis(self, company: Dict) -> str:
        """조직 역량 분석 생성"""
        hr = company.get("human_resources", {})
        org = company.get("organizational_readiness", {})

        return f"""
**인적 자원 현황**:

| 항목 | 인원/수치 |
|------|----------|
| 총 직원 수 | {hr.get('total_employees', 0)}명 |
| IT 인력 | {hr.get('it_staff_count', 0)}명 |
| 데이터 사이언티스트 | {hr.get('data_scientist_count', 0)}명 |
| ML 엔지니어 | {hr.get('ml_engineer_count', 0)}명 |
| AI 프로젝트 경험 | {hr.get('ai_experience_projects', 0)}건 |

**조직 준비도**:

| 항목 | 점수 (5점 만점) |
|------|-----------------|
| 경영진 지원도 | {org.get('executive_support', 0)} |
| 변화 관리 역량 | {org.get('change_management_capability', 0)} |
| 혁신 문화 | {org.get('innovation_culture', 0)} |
| 부서간 협업 | {org.get('cross_functional_collaboration', 0)} |
        """.strip()

    def _generate_data_analysis(self, company: Dict) -> str:
        """데이터 자산 분석 생성"""
        data = company.get("data_assets", {})
        return f"""
**데이터 자산 현황**:

| 항목 | 현황 |
|------|------|
| 데이터 총량 | {data.get('data_volume_tb', 0)} TB |
| 정형 데이터 비율 | {data.get('structured_ratio', 0) * 100:.0f}% |
| 데이터 품질 점수 | {data.get('data_quality_score', 0)}/5 |
| 데이터 거버넌스 | {'체계 수립' if data.get('has_data_governance') else '미수립'} |
| 히스토리 데이터 | {data.get('historical_data_years', 0)}년 |

**데이터 소스**: {', '.join(data.get('data_sources', [])) or '미정의'}
        """.strip()

    def _generate_vision(self, company: Dict) -> str:
        """AI 비전 생성"""
        return f"""
**{company.get('name', '기업')} AI 비전**:

"AI 기술을 활용하여 업무 효율성을 극대화하고,
데이터 기반의 의사결정 체계를 구축하여
{company.get('industry', '산업')} 분야의 선도 기업으로 도약한다."

**핵심 목표**:
1. AI 성숙도 Level 4 달성 (3년 내)
2. 핵심 업무 프로세스의 AI 자동화
3. 예측 분석 기반 의사결정 체계 구축
4. AI 거버넌스 및 윤리 체계 확립
        """.strip()

    def _generate_use_cases(self, opportunities: Dict) -> str:
        """Use Case 분석 생성"""
        if not opportunities:
            return "Use Case 분석 데이터가 없습니다."

        content = "**발굴된 AI Use Case**:\n\n"

        for uc in opportunities.get("opportunities", [])[:10]:
            content += f"""
### {uc.get('name', 'N/A')}
- **ROI 잠재력**: {uc.get('roi_potential', 'N/A')}
- **구현 복잡도**: {uc.get('complexity', 'N/A')}
- **적합도 점수**: {uc.get('fit_score', 0):.0f}/100

"""
        return content.strip()

    def _generate_priorities(self, opportunities: Dict) -> str:
        """우선순위 분석 생성"""
        if not opportunities:
            return "우선순위 분석 데이터가 없습니다."

        content = """
**가치-실행 용이성 매트릭스 분석 결과**:

| 분류 | Use Case | 권고 |
|------|----------|------|
"""
        for uc in opportunities.get("opportunities", [])[:5]:
            fit = uc.get("fit_score", 0)
            if fit >= 70:
                category = "Quick Win"
            elif fit >= 50:
                category = "Strategic"
            else:
                category = "Reconsider"

            content += f"| {category} | {uc.get('name')} | 우선 추진 권장 |\n"

        return content.strip()

    def _generate_scenario_analysis(self, scenarios: List[Dict]) -> str:
        """시나리오 분석 생성"""
        if not scenarios:
            return "시나리오 분석 데이터가 없습니다."

        content = "**시나리오 비교 분석**:\n\n"

        for s in scenarios:
            params = s.get("parameters", {})
            roi = s.get("roi_analysis", {}).get("metrics", {})
            risk = s.get("risk_assessment", {})

            content += f"""
### {s.get('name', 'N/A')}
**유형**: {s.get('type', 'N/A')}

| 항목 | 값 |
|------|-----|
| 투자 예산 | {params.get('investment_budget', 0):.1f}억원 |
| 추진 기간 | {params.get('timeline_months', 0)}개월 |
| 예상 ROI | {roi.get('roi_percent', 0):.1f}% |
| 투자 회수 기간 | {roi.get('payback_months', 0):.0f}개월 |
| 리스크 레벨 | {risk.get('risk_level', 'N/A')} |
| 종합 점수 | {s.get('overall_score', 0):.1f} |

{s.get('description', '')}

---
"""
        return content.strip()

    def _generate_roadmap(self, project_data: Dict) -> str:
        """로드맵 생성"""
        return """
**AI 도입 로드맵**:

### 단기 (0-6개월): Quick Win
- AI 성숙도 기반 개선 과제 착수
- Quick Win 과제 PoC 수행
- AI CoE(Center of Excellence) 조직 구성
- 데이터 품질 개선 프로그램 시작

### 중기 (6-18개월): 핵심 역량 구축
- MLOps 플랫폼 구축
- 핵심 Use Case 본격 개발
- AI 거버넌스 체계 운영
- 내부 AI 역량 강화 교육

### 장기 (18-36개월): 전사 확산
- AI 솔루션 전사 확산
- 비즈니스 모델 혁신
- AI 기반 의사결정 체계 정착
- 외부 파트너십 확대
        """.strip()

    def _generate_investment_plan(self, scenarios: List[Dict]) -> str:
        """투자 계획 생성"""
        if not scenarios:
            return "투자 계획 데이터가 없습니다."

        content = "**시나리오별 투자 계획**:\n\n"

        for s in scenarios:
            params = s.get("parameters", {})
            budget = params.get("investment_budget", 0)

            content += f"""
### {s.get('name')}
- **총 투자 예산**: {budget:.1f}억원
- **인프라 투자**: {budget * 0.4:.1f}억원 (40%)
- **소프트웨어/라이선스**: {budget * 0.2:.1f}억원 (20%)
- **인력/교육**: {budget * 0.3:.1f}억원 (30%)
- **기타**: {budget * 0.1:.1f}억원 (10%)

"""
        return content.strip()

    def _generate_quantitative_benefits(self, scenarios: List[Dict], selected: str) -> str:
        """정량적 효과 생성"""
        scenario = None
        for s in scenarios:
            if s.get("id") == selected:
                scenario = s
                break

        if not scenario:
            scenario = scenarios[0] if scenarios else {}

        roi = scenario.get("roi_analysis", {})
        metrics = roi.get("metrics", {})
        benefits = roi.get("benefits", {})

        return f"""
**예상 정량적 효과** (선택 시나리오 기준):

| 지표 | 값 |
|------|-----|
| 예상 ROI | {metrics.get('roi_percent', 0):.1f}% |
| 투자 회수 기간 | {metrics.get('payback_months', 0):.0f}개월 |
| NPV (3년) | {metrics.get('npv_3year', 0):,.0f}만원 |
| IRR | {metrics.get('irr', 0):.1f}% |

**연간 효과**:
- 총 연간 효과: {benefits.get('annual', 0):,.0f}만원
- 3년 누적 효과: {benefits.get('3year_total', 0):,.0f}만원
        """.strip()

    def _generate_qualitative_benefits(self) -> str:
        """정성적 효과 생성"""
        return """
**예상 정성적 효과**:

1. **업무 효율성 향상**
   - 반복 업무 자동화로 인한 업무 부담 경감
   - 의사결정 속도 향상

2. **데이터 기반 경영**
   - 정확한 예측 및 분석에 기반한 의사결정
   - 리스크 조기 감지 및 대응

3. **조직 역량 강화**
   - AI/데이터 활용 역량 내재화
   - 혁신 문화 정착

4. **고객 만족도 향상**
   - 서비스 품질 개선
   - 개인화된 고객 경험 제공

5. **경쟁력 강화**
   - 산업 내 디지털 리더십 확보
   - 새로운 비즈니스 기회 창출
        """.strip()

    def _generate_roi_analysis(self, scenarios: List[Dict], selected: str) -> str:
        """ROI 분석 생성"""
        scenario = None
        for s in scenarios:
            if s.get("id") == selected:
                scenario = s
                break

        if not scenario:
            scenario = scenarios[0] if scenarios else {}

        roi = scenario.get("roi_analysis", {})
        costs = roi.get("costs", {})
        benefits = roi.get("benefits", {})
        metrics = roi.get("metrics", {})

        return f"""
**ROI 상세 분석**:

### 비용 구조
| 항목 | 금액 (만원) |
|------|------------|
| 초기 투자 | {costs.get('initial_investment', 0):,.0f} |
| 연간 운영비 | {costs.get('annual_operation', 0):,.0f} |
| 연간 유지보수 | {costs.get('annual_maintenance', 0):,.0f} |
| 3년 총 비용 | {costs.get('total_3year', 0):,.0f} |

### 효과 구조
| 항목 | 금액 (만원) |
|------|------------|
| 연간 효과 | {benefits.get('annual', 0):,.0f} |
| 3년 총 효과 | {benefits.get('3year_total', 0):,.0f} |

### 투자 평가 지표
| 지표 | 값 | 평가 |
|------|-----|------|
| ROI | {metrics.get('roi_percent', 0):.1f}% | {'우수' if metrics.get('roi_percent', 0) > 30 else '양호'} |
| Payback | {metrics.get('payback_months', 0):.0f}개월 | {'우수' if metrics.get('payback_months', 0) < 24 else '양호'} |
| NPV | {metrics.get('npv_3year', 0):,.0f}만원 | {'양호' if metrics.get('npv_3year', 0) > 0 else '재검토'} |

### 권고
{roi.get('recommendation', '추가 분석 필요')}
        """.strip()

    def _generate_risks(self, scenarios: List[Dict], selected: str) -> str:
        """리스크 분석 생성"""
        scenario = None
        for s in scenarios:
            if s.get("id") == selected:
                scenario = s
                break

        if not scenario:
            scenario = scenarios[0] if scenarios else {}

        risk = scenario.get("risk_assessment", {})
        top_risks = risk.get("top_risks", [])

        content = f"""
**리스크 분석 결과**:

- **종합 리스크 점수**: {risk.get('total_risk_score', 0):.1f}
- **리스크 레벨**: {risk.get('risk_level', 'N/A')}

### 주요 리스크

| 리스크 | 범주 | 확률 | 영향 | 점수 |
|--------|------|------|------|------|
"""
        for r in top_risks[:5]:
            content += f"| {r.get('name')} | {r.get('category')} | {r.get('probability')}/5 | {r.get('impact')}/5 | {r.get('risk_score')} |\n"

        return content.strip()

    def _generate_mitigation(self, scenarios: List[Dict], selected: str) -> str:
        """완화 전략 생성"""
        scenario = None
        for s in scenarios:
            if s.get("id") == selected:
                scenario = s
                break

        if not scenario:
            scenario = scenarios[0] if scenarios else {}

        risk = scenario.get("risk_assessment", {})
        priorities = risk.get("mitigation_priorities", [])

        content = "**리스크 완화 전략**:\n\n"

        for i, strategy in enumerate(priorities[:5], 1):
            content += f"{i}. {strategy}\n"

        content += """

### 리스크 대응 체계

1. **예방 (Prevention)**
   - 정기 리스크 평가 및 모니터링
   - 표준 프로세스 준수
   - 교육 및 역량 강화

2. **대응 (Response)**
   - 이슈 발생 시 즉시 에스컬레이션
   - 비상 대응 계획 실행
   - Human-in-the-Loop 체계

3. **복구 (Recovery)**
   - 백업 시스템 운영
   - 장애 복구 절차
   - 학습 및 개선
        """

        return content.strip()

    def save_report(self, report: Dict[str, Any], filename: str) -> Path:
        """보고서 저장"""
        filepath = self.reports_dir / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        return filepath


# 싱글톤 인스턴스
_report_generator = None


def get_report_generator() -> ReportGenerator:
    """Report Generator 싱글톤 인스턴스 반환"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ReportGenerator()
    return _report_generator
