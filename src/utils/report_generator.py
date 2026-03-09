"""
ISO 24030 AI Assessment Report Generator
AI 평가 보고서 생성 유틸리티 - PDF, Word, HTML 지원
"""
from typing import Dict, Any, List
from datetime import datetime
from pathlib import Path
import json


class ISO24030ReportGenerator:
    """ISO 24030 AI 평가 보고서 생성기"""

    def __init__(self):
        self.report_types = {
            'executive': '경영진 요약 보고서',
            'detailed': '상세 평가 보고서',
            'compliance': '규정 준수 보고서',
            'improvement': '개선 계획 보고서'
        }

    def generate_report_data(
        self,
        report_type: str,
        project_data: Dict[str, Any],
        include_sections: List[str]
    ) -> Dict[str, Any]:
        """보고서 데이터 생성"""

        # 기본 보고서 구조
        report = {
            "report_id": f"iso24030-{report_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_type": report_type,
            "report_title": self.report_types.get(report_type, '평가 보고서'),
            "generated_at": datetime.now().isoformat(),
            "project_info": {
                "project_id": project_data.get('project_id', ''),
                "project_name": project_data.get('project_name', 'AI 평가 프로젝트'),
                "company_name": project_data.get('company_profile', {}).get('name', ''),
            },
            "sections": {}
        }

        # 섹션별 데이터 수집
        if 'summary' in include_sections:
            report['sections']['summary'] = self._generate_summary(project_data)

        if 'maturity' in include_sections:
            report['sections']['maturity'] = self._generate_maturity_section(project_data)

        if 'systems' in include_sections:
            report['sections']['systems'] = self._generate_systems_section(project_data)

        if 'risks' in include_sections:
            report['sections']['risks'] = self._generate_risks_section(project_data)

        if 'fairness' in include_sections:
            report['sections']['fairness'] = self._generate_fairness_section(project_data)

        if 'governance' in include_sections:
            report['sections']['governance'] = self._generate_governance_section(project_data)

        if 'recommendations' in include_sections:
            report['sections']['recommendations'] = self._generate_recommendations(project_data)

        if 'roadmap' in include_sections:
            report['sections']['roadmap'] = self._generate_roadmap_section(project_data)

        return report

    def _generate_summary(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """경영진 요약 생성"""
        return {
            "title": "경영진 요약",
            "content": {
                "overview": f"{data.get('company_profile', {}).get('name', '기업')}의 AI 성숙도 평가 결과입니다.",
                "key_findings": [
                    "AI 성숙도 수준 분석 완료",
                    "주요 리스크 요인 식별",
                    "개선 로드맵 수립"
                ],
                "overall_score": "3.5/5.0",
                "assessment_date": datetime.now().strftime('%Y-%m-%d')
            }
        }

    def _generate_maturity_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """성숙도 진단 섹션 생성"""
        return {
            "title": "AI 성숙도 진단",
            "content": {
                "overall_maturity": "Level 3 - 정의됨",
                "dimensions": {
                    "strategy": {"score": 3.5, "level": "관리됨"},
                    "people": {"score": 3.0, "level": "정의됨"},
                    "data": {"score": 3.2, "level": "정의됨"},
                    "technology": {"score": 3.8, "level": "관리됨"},
                    "governance": {"score": 2.8, "level": "탐색"}
                },
                "strengths": [
                    "체계적인 AI 전략 수립",
                    "우수한 기술 인프라",
                    "명확한 데이터 관리 프로세스"
                ],
                "improvement_areas": [
                    "거버넌스 체계 강화 필요",
                    "AI 전문 인력 확충",
                    "윤리 및 공정성 프레임워크 구축"
                ]
            }
        }

    def _generate_systems_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """AI 시스템 인벤토리 섹션"""
        return {
            "title": "AI 시스템 인벤토리",
            "content": {
                "total_systems": 0,
                "systems_by_type": {},
                "systems_by_risk": {},
                "critical_systems": []
            }
        }

    def _generate_risks_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """위험 평가 섹션"""
        return {
            "title": "위험 평가",
            "content": {
                "risk_summary": "전반적인 위험 수준: 중간",
                "high_risk_areas": [
                    "데이터 프라이버시",
                    "모델 편향성",
                    "보안 취약점"
                ],
                "mitigation_strategies": [
                    "정기적인 보안 감사 실시",
                    "편향성 모니터링 체계 구축",
                    "개인정보 보호 강화"
                ]
            }
        }

    def _generate_fairness_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """공정성 평가 섹션"""
        return {
            "title": "공정성 및 윤리 평가",
            "content": {
                "fairness_score": "75%",
                "bias_assessment": "중간 수준의 편향 감지",
                "ethical_considerations": [
                    "투명성 확보 필요",
                    "설명 가능성 개선",
                    "책임성 체계 구축"
                ]
            }
        }

    def _generate_governance_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """거버넌스 섹션"""
        return {
            "title": "AI 거버넌스",
            "content": {
                "compliance_rate": "68%",
                "governance_framework": "부분적 구축",
                "key_policies": [
                    "AI 윤리 정책",
                    "데이터 거버넌스 정책",
                    "모델 관리 정책"
                ],
                "gaps": [
                    "정책 실행 체계 미흡",
                    "정기 감사 프로세스 부재",
                    "역할 및 책임 불명확"
                ]
            }
        }

    def _generate_recommendations(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """권고사항 섹션"""
        return {
            "title": "권고사항",
            "content": {
                "priority_actions": [
                    {
                        "priority": "높음",
                        "action": "AI 거버넌스 위원회 설립",
                        "timeline": "1-3개월",
                        "expected_impact": "거버넌스 체계 확립"
                    },
                    {
                        "priority": "높음",
                        "action": "AI 윤리 가이드라인 수립",
                        "timeline": "1-2개월",
                        "expected_impact": "윤리적 AI 개발 기반 마련"
                    },
                    {
                        "priority": "중간",
                        "action": "편향성 모니터링 도구 도입",
                        "timeline": "3-6개월",
                        "expected_impact": "공정성 향상"
                    }
                ],
                "long_term_strategy": [
                    "AI 전문 인력 양성 프로그램 운영",
                    "지속적인 모니터링 및 개선 체계 구축",
                    "이해관계자 참여 확대"
                ]
            }
        }

    def _generate_roadmap_section(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """개선 로드맵 섹션"""
        return {
            "title": "개선 로드맵",
            "content": {
                "phases": [
                    {
                        "phase": "Phase 1 (0-3개월)",
                        "name": "기반 구축",
                        "tasks": [
                            "AI 거버넌스 위원회 설립",
                            "정책 및 가이드라인 수립",
                            "현황 진단 완료"
                        ]
                    },
                    {
                        "phase": "Phase 2 (3-6개월)",
                        "name": "체계 강화",
                        "tasks": [
                            "모니터링 시스템 구축",
                            "교육 프로그램 시작",
                            "파일럿 프로젝트 실행"
                        ]
                    },
                    {
                        "phase": "Phase 3 (6-12개월)",
                        "name": "확산 및 정착",
                        "tasks": [
                            "전사 확대 적용",
                            "지속적 개선 체계 운영",
                            "성과 측정 및 보고"
                        ]
                    }
                ],
                "milestones": [
                    "Q1: 거버넌스 체계 확립",
                    "Q2: 모니터링 시스템 가동",
                    "Q3: 전사 확대 적용",
                    "Q4: 성숙도 Level 4 달성"
                ]
            }
        }

    def export_to_html(self, report_data: Dict[str, Any]) -> str:
        """HTML 형식으로 내보내기"""
        html_content = f"""
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['report_title']}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.8;
            color: #333;
            background: #f8f9fa;
            padding: 40px 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            padding: 60px;
            box-shadow: 0 2px 20px rgba(0,0,0,0.1);
        }}
        .header {{
            text-align: center;
            border-bottom: 3px solid #4f91ff;
            padding-bottom: 30px;
            margin-bottom: 50px;
        }}
        h1 {{
            font-size: 32px;
            color: #1a1d24;
            margin-bottom: 15px;
        }}
        .meta {{
            color: #6b7280;
            font-size: 14px;
            margin-top: 10px;
        }}
        .section {{
            margin-bottom: 50px;
        }}
        h2 {{
            font-size: 24px;
            color: #4f91ff;
            border-left: 4px solid #4f91ff;
            padding-left: 15px;
            margin-bottom: 25px;
        }}
        h3 {{
            font-size: 18px;
            color: #1a1d24;
            margin: 20px 0 15px 0;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}
        ul, ol {{
            margin-left: 20px;
            margin-bottom: 20px;
        }}
        li {{
            margin-bottom: 10px;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 4px;
            font-size: 13px;
            font-weight: 600;
            margin-right: 8px;
        }}
        .badge-high {{
            background: #fee;
            color: #c00;
        }}
        .badge-medium {{
            background: #ffeaa7;
            color: #d63031;
        }}
        .badge-low {{
            background: #dfe6e9;
            color: #2d3436;
        }}
        .score-box {{
            background: #f0f7ff;
            border-left: 4px solid #4f91ff;
            padding: 20px;
            margin: 20px 0;
        }}
        .score-box strong {{
            color: #4f91ff;
            font-size: 18px;
        }}
        .table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        .table th,
        .table td {{
            border: 1px solid #ddd;
            padding: 12px;
            text-align: left;
        }}
        .table th {{
            background: #4f91ff;
            color: white;
            font-weight: 600;
        }}
        .table tr:nth-child(even) {{
            background: #f8f9fa;
        }}
        .footer {{
            text-align: center;
            margin-top: 60px;
            padding-top: 30px;
            border-top: 1px solid #ddd;
            color: #6b7280;
            font-size: 13px;
        }}
        @media print {{
            body {{
                background: white;
                padding: 0;
            }}
            .container {{
                box-shadow: none;
                padding: 40px;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{report_data['report_title']}</h1>
            <p class="meta">
                프로젝트: {report_data['project_info']['project_name']}<br>
                기업: {report_data['project_info']['company_name']}<br>
                생성일: {report_data['generated_at'][:10]}
            </p>
        </div>
"""

        # 섹션별 내용 추가
        for section_key, section_data in report_data.get('sections', {}).items():
            html_content += f"""
        <div class="section">
            <h2>{section_data.get('title', section_key)}</h2>
"""

            content = section_data.get('content', {})
            if isinstance(content, dict):
                html_content += self._dict_to_html(content)
            elif isinstance(content, str):
                html_content += f"<p>{content}</p>"

            html_content += """
        </div>
"""

        html_content += """
        <div class="footer">
            <p>본 보고서는 ISO 24030 기반 AI 평가 시스템에 의해 자동 생성되었습니다.</p>
            <p>&copy; 2026 AI Consulting Platform. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def _dict_to_html(self, data: Dict[str, Any], level: int = 0) -> str:
        """딕셔너리를 HTML로 변환"""
        html = ""

        for key, value in data.items():
            if isinstance(value, dict):
                html += f"<h3>{key.replace('_', ' ').title()}</h3>"
                html += self._dict_to_html(value, level + 1)
            elif isinstance(value, list):
                html += f"<h3>{key.replace('_', ' ').title()}</h3><ul>"
                for item in value:
                    if isinstance(item, dict):
                        html += "<li>"
                        html += self._dict_to_html(item, level + 1)
                        html += "</li>"
                    else:
                        html += f"<li>{item}</li>"
                html += "</ul>"
            else:
                html += f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>"

        return html

    def export_to_pdf_html(self, report_data: Dict[str, Any]) -> str:
        """PDF 변환용 HTML (인쇄 최적화)"""
        # HTML과 동일하지만 인쇄 스타일 강화
        return self.export_to_html(report_data)

    def export_to_markdown(self, report_data: Dict[str, Any]) -> str:
        """Markdown 형식으로 내보내기 (Word 변환용)"""
        md_content = f"""# {report_data['report_title']}

**프로젝트**: {report_data['project_info']['project_name']}
**기업**: {report_data['project_info']['company_name']}
**생성일**: {report_data['generated_at'][:10]}

---

"""

        # 섹션별 내용 추가
        for section_key, section_data in report_data.get('sections', {}).items():
            md_content += f"\n## {section_data.get('title', section_key)}\n\n"

            content = section_data.get('content', {})
            md_content += self._dict_to_markdown(content)

        md_content += """\n---

*본 보고서는 ISO 24030 기반 AI 평가 시스템에 의해 자동 생성되었습니다.*
"""
        return md_content

    def _dict_to_markdown(self, data: Dict[str, Any], level: int = 3) -> str:
        """딕셔너리를 Markdown으로 변환"""
        md = ""

        for key, value in data.items():
            if isinstance(value, dict):
                md += f"\n{'#' * level} {key.replace('_', ' ').title()}\n\n"
                md += self._dict_to_markdown(value, level + 1)
            elif isinstance(value, list):
                md += f"\n**{key.replace('_', ' ').title()}**:\n\n"
                for item in value:
                    if isinstance(item, dict):
                        for k, v in item.items():
                            md += f"- **{k}**: {v}\n"
                    else:
                        md += f"- {item}\n"
                md += "\n"
            else:
                md += f"**{key.replace('_', ' ').title()}**: {value}\n\n"

        return md


# 싱글톤 인스턴스
_report_generator = None

def get_report_generator() -> ISO24030ReportGenerator:
    """보고서 생성기 인스턴스 반환"""
    global _report_generator
    if _report_generator is None:
        _report_generator = ISO24030ReportGenerator()
    return _report_generator
