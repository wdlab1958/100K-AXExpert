"""
Enhanced ISO 24030 AI Assessment Report Generator
고품질 AI 평가 보고서 생성 유틸리티 - AI 기반 콘텐츠 생성 지원
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import json


class EnhancedReportGenerator:
    """향상된 ISO 24030 AI 평가 보고서 생성기 - 실제 컨설팅 보고서 품질"""

    def __init__(self, llm_provider=None):
        # 하이브리드 LLM Provider 사용
        if llm_provider is None:
            from src.core.hybrid_llm_provider import get_hybrid_llm_provider
            self.llm_provider = get_hybrid_llm_provider()
        else:
            self.llm_provider = llm_provider

        self.report_types = {
            'executive': '경영진 요약 보고서',
            'detailed': 'AI 인프라 도입 컨설팅 종합 보고서',
            'compliance': '규정 준수 보고서',
            'improvement': '개선 계획 보고서'
        }

    async def generate_comprehensive_report(
        self,
        report_type: str,
        project_data: Dict[str, Any],
        include_sections: List[str]
    ) -> Dict[str, Any]:
        """종합 보고서 생성 (AI 기반)"""

        company_name = project_data.get('company_profile', {}).get('name', '귀사')
        project_name = project_data.get('project_name', 'AI 평가 프로젝트')

        # 기본 보고서 구조
        report = {
            "report_id": f"iso24030-{report_type}-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "report_type": report_type,
            "report_title": self.report_types.get(report_type, '평가 보고서'),
            "generated_at": datetime.now().isoformat(),
            "project_info": {
                "project_id": project_data.get('project_id', ''),
                "project_name": project_name,
                "company_name": company_name,
                "report_date": datetime.now().strftime('%Y년 %m월'),
                "consultant": "100K-AX Expert Platform"
            },
            "sections": {}
        }

        # 섹션별 생성
        if report_type == 'detailed' or report_type == 'executive':
            report['sections'] = await self._generate_detailed_sections(project_data, include_sections)
        elif report_type == 'compliance':
            report['sections'] = await self._generate_compliance_sections(project_data, include_sections)
        elif report_type == 'improvement':
            report['sections'] = await self._generate_improvement_sections(project_data, include_sections)

        return report

    async def _generate_detailed_sections(self, data: Dict[str, Any], include: List[str]) -> Dict[str, Any]:
        """상세 보고서 섹션 생성 (하이브리드 LLM 활용)"""
        sections = {}

        company_name = data.get('company_profile', {}).get('name', '귀사')
        industry = data.get('company_profile', {}).get('industry', 'IT 서비스')

        context = {
            'company_name': company_name,
            'industry': industry,
            'project_name': data.get('project_name', 'AI 전환 프로젝트')
        }

        # 1. 경영진 요약
        if 'summary' in include:
            # AI로 상세 내용 생성
            overview_content = await self._generate_ai_content(
                "1.1 보고서 개요",
                f"{company_name}의 AI 인프라 도입을 위한 종합 컨설팅 보고서의 배경, 목적, 범위를 상세히 설명하세요. {industry} 분야의 특성을 반영하여 작성하세요.",
                context
            )

            recommendations_content = await self._generate_ai_content(
                "1.2 핵심 권고사항",
                f"{company_name}의 AI 도입을 통한 전략적 가치와 구체적인 권고사항을 상세히 설명하세요. 기술 역량 강화, 업무 효율성, 시장 경쟁력 등을 포함하세요.",
                context
            )

            sections['executive_summary'] = {
                "title": "1. 경영진 요약 (Executive Summary)",
                "subsections": {
                    "overview": {
                        "title": "1.1 보고서 개요",
                        "content": self._clean_special_chars(overview_content)
                    },
                    "recommendations": {
                        "title": "1.2 핵심 권고사항",
                        "content": self._clean_special_chars(recommendations_content)
                    }
                }
            }

        # 2. 현황 분석 및 진단
        if 'maturity' in include:
            sections['current_state'] = {
                "title": "2. 현황 분석 및 진단 (As-Is Analysis)",
                "subsections": {
                    "organization": {
                        "title": "2.1 조직 현황",
                        "content": f"""{company_name}는 {industry} 분야에서 사업을 수행하고 있는 조직이다. 현재 조직 내 AI 관련 인프라 및 역량 현황을 진단한 결과, 다음과 같은 특징이 확인되었다.

**진단 결과 요약**

• **AI 성숙도 수준**: 현재 조직은 AI 도입 초기 단계에 있으며, 체계적인 AI 전략 수립이 필요한 시점이다.

• **인프라 현황**: 기본적인 IT 인프라는 구축되어 있으나, AI 특화 인프라(GPU 서버, 클라우드 AI 서비스 등)는 미비한 상태이다.

• **인력 역량**: 일부 구성원이 AI/ML에 대한 기초 지식을 보유하고 있으나, 실무 적용 경험이 부족한 상태이다.

• **데이터 자산**: 업무 과정에서 생성되는 데이터가 축적되고 있으나, 체계적인 관리 및 활용 체계는 미흡한 상황이다."""
                    },
                    "insights": {
                        "title": "2.2 시사점",
                        "content": """상기 진단 결과를 종합하면, 다음과 같은 시사점을 도출할 수 있다.

• **단계적 접근 필요**: AI 도입은 단계적으로 접근하되, 명확한 로드맵을 수립하여 체계적으로 추진해야 한다.

• **교육 및 역량 강화**: 조직 구성원의 AI 역량 강화를 위한 체계적인 교육 프로그램이 필요하다.

• **파일럿 프로젝트**: 소규모 파일럿 프로젝트를 통해 성공 경험을 축적하고, 이를 바탕으로 전사 확대를 추진하는 것이 효과적이다.

• **거버넌스 체계**: AI 윤리, 보안, 규정 준수 등을 포함한 AI 거버넌스 체계를 조기에 구축해야 한다."""
                    }
                }
            }

        # 3. AI 도입 목표 및 전략
        if 'recommendations' in include:
            sections['strategy'] = {
                "title": "3. AI 도입 목표 및 전략 (To-Be Strategy)",
                "subsections": {
                    "objectives": {
                        "title": "3.1 전략적 목표",
                        "content": """AI 도입의 궁극적 목적은 기술 역량을 강화하고 시장 경쟁력을 향상시키는 데 있다. 이를 달성하기 위한 구체적인 전략 목표는 다음과 같이 설정하였다.

**전략 목표 체계**

• **AI 인프라 구축**: 안정적이고 확장 가능한 AI 운영 환경을 마련한다. 하드웨어, 소프트웨어, 네트워크 등 기반 시스템을 체계적으로 구성하여 AI 서비스의 안정적 운영을 보장한다.

• **데이터 분석 및 가치 추출**: 조직 내 축적된 데이터를 분석하여 의미 있는 인사이트를 도출한다. 업무에 특화된 데이터 분석 체계를 수립하여 서비스 품질 향상에 기여한다.

• **AI 기술력 강화**: 조직 구성원의 AI 역량을 체계적으로 개발한다. 교육 프로그램 운영, 외부 전문가 협력 등을 통해 지속적인 기술력 향상을 도모한다.

• **AI 윤리 및 거버넌스**: 책임감 있는 AI 활용을 위한 윤리 지침과 거버넌스 체계를 확립한다."""
                    },
                    "approach": {
                        "title": "3.2 추진 전략",
                        "content": """상기 목표를 달성하기 위해 다음과 같은 추진 전략을 제안한다.

• **단계적 접근**: 소규모 파일럿 프로젝트로 시작하여 성공 경험을 축적한 후 점진적으로 확대 적용한다.

• **현업 중심**: 실제 업무 프로세스와 연계된 Use Case를 우선 발굴하여 실질적인 효과를 조기에 확인한다.

• **인력 양성**: 외부 솔루션 도입과 병행하여 내부 AI 전문 인력을 육성함으로써 장기적인 기술 자립 기반을 마련한다.

• **협업 체계**: 내부 부서 간 협업과 외부 전문 파트너와의 협력을 통해 시너지를 창출한다."""
                    }
                }
            }

        # 4. 세부 이행 계획
        if 'roadmap' in include:
            sections['roadmap'] = {
                "title": "4. 세부 이행 계획 (Roadmap)",
                "content": """AI 인프라 도입을 위한 세부 이행 계획을 3개 단계로 구분하여 제시한다. 각 단계별 주요 활동과 예상 산출물은 다음과 같다.""",
                "subsections": {
                    "phase1": {
                        "title": "4.1 1단계: 기반 조성 (1~3개월)",
                        "content": """**목표**: AI 도입을 위한 기본 환경을 조성하고 추진 체계를 확립한다.

**주요 활동**:

• AI 도입 목표 및 전략의 검토와 확정

• AI 추진 조직 구성 및 역할 정의

• AI 인프라 구축 착수 (하드웨어, 클라우드 환경 등)

• 우선순위 Use Case 발굴 및 선정

• 데이터 현황 조사 및 품질 평가

**예상 산출물**: AI 도입 전략서, 추진 조직도, 인프라 구축 계획서, Use Case 목록"""
                    },
                    "phase2": {
                        "title": "4.2 2단계: 역량 구축 (4~6개월)",
                        "content": """**목표**: AI 활용 역량을 체계적으로 구축하고 파일럿 프로젝트를 수행한다.

**주요 활동**:

• 데이터 분석 및 가치 추출 방법론 설계

• AI 기술력 강화 교육 프로그램 운영

• 파일럿 프로젝트 수행 및 효과 검증

• AI 거버넌스 체계 수립

• MLOps 파이프라인 구축

**예상 산출물**: 교육 이수 현황, 파일럿 프로젝트 결과 보고서, AI 거버넌스 정책서, MLOps 프로세스 문서"""
                    },
                    "phase3": {
                        "title": "4.3 3단계: 본격 적용 (7~9개월)",
                        "content": """**목표**: 검증된 AI 솔루션을 본격적으로 업무에 적용하고 운영 체계를 안정화한다.

**주요 활동**:

• AI 도입 프로젝트 본격 실행

• AI 인프라 구축 완료 및 안정화

• 성과 측정 및 지속적 개선 체계 구축

• 확대 적용 계획 수립

• AI CoE(Center of Excellence) 운영

**예상 산출물**: AI 시스템 운영 현황, 성과 측정 리포트, 확대 적용 로드맵, AI CoE 운영 보고서"""
                    }
                }
            }

        # 5. 리스크 관리
        if 'risks' in include:
            sections['risk_management'] = {
                "title": "5. 리스크 관리 및 제언 (Risk Management)",
                "subsections": {
                    "risks": {
                        "title": "5.1 주요 리스크 요인",
                        "content": """AI 도입 과정에서 예상되는 주요 리스크 요인과 대응 방안을 다음과 같이 정리하였다.

**리스크 1: 기술적 복잡성**
- 내용: AI 기술의 높은 복잡도로 인한 구현 및 운영 어려움
- 대응: 전문 파트너 협력, 단계적 접근, 지속적인 교육

**리스크 2: 데이터 품질**
- 내용: 데이터 품질 미흡으로 인한 AI 모델 성능 저하
- 대응: 데이터 품질 관리 체계 구축, 데이터 거버넌스 강화

**리스크 3: 조직 저항**
- 내용: 구성원의 변화 거부감으로 인한 도입 지연
- 대응: 적극적인 커뮤니케이션, 성공 사례 공유, 인센티브 제공

**리스크 4: 비용 초과**
- 내용: 예상보다 높은 도입 및 운영 비용 발생
- 대응: 단계별 예산 수립, 클라우드 활용, ROI 지속 모니터링

**리스크 5: 보안 및 프라이버시**
- 내용: AI 활용 과정에서의 보안 취약점 및 개인정보 침해
- 대응: 보안 정책 수립, 정기적인 보안 감사, 프라이버시 보호 체계 구축"""
                    },
                    "recommendations": {
                        "title": "5.2 제언",
                        "content": """본 컨설팅 결과를 바탕으로 다음과 같은 사항을 제언한다.

• **경영진의 적극적 지원**: AI 도입은 단순한 기술 도입이 아닌 조직 변화 관리의 관점에서 접근해야 하며, 이를 위해 경영진의 적극적인 관심과 지원이 필수적이다.

• **구체적 Use Case 발굴**: 업무 특성을 반영한 구체적인 AI 활용 사례를 발굴하여 실질적인 도입 효과를 조기에 확인할 필요가 있다.

• **전문 파트너 협력**: AI 도입 초기 단계에서는 전문 컨설팅 업체 또는 솔루션 벤더와의 협력을 통해 시행착오를 최소화하는 것이 효율적이다.

• **지속적인 모니터링**: AI 도입 효과를 정기적으로 측정하고 개선 방안을 도출하는 지속적인 모니터링 체계를 구축해야 한다.

• **윤리적 AI**: 책임감 있는 AI 활용을 위한 윤리 지침을 수립하고 준수하는 문화를 조성해야 한다."""
                    }
                }
            }

        # 6. 결론
        sections['conclusion'] = {
            "title": "6. 결론",
            "content": f"""본 보고서는 {company_name}의 AI 인프라 도입을 위한 종합적인 컨설팅 내용을 담고 있다. 현황 분석, AI 도입 목표 및 전략, 세부 이행 계획, 리스크 관리 등 AI 도입에 필요한 제반 사항을 체계적으로 정리하였다.

AI 기술은 빠르게 발전하고 있으며, 조직의 경쟁력 확보를 위해서는 적기에 AI를 도입하고 활용하는 것이 중요하다. 본 보고서에서 제시한 로드맵과 전략을 바탕으로, {company_name}가 성공적으로 AI를 도입하고 지속 가능한 AI 역량을 구축하기를 기대한다.

향후 AI 도입 과정에서 추가적인 지원이 필요할 경우, 100K-AX Expert 컨설팅 팀이 지속적으로 협력할 준비가 되어 있다.

**- 이상 -**"""
        }

        return sections

    async def _generate_ai_content(
        self,
        section_title: str,
        description: str,
        context: Dict[str, Any]
    ) -> str:
        """AI를 활용한 콘텐츠 생성"""
        try:
            if hasattr(self.llm_provider, 'generate_structured_content'):
                # 하이브리드 LLM Provider 사용
                content = await self.llm_provider.generate_structured_content(
                    section_title=section_title,
                    section_description=description,
                    context=context
                )
                return content
            else:
                # 기본 템플릿 사용
                return self._get_default_content(section_title, description, context)
        except Exception as e:
            print(f"AI 콘텐츠 생성 실패, 기본 템플릿 사용: {e}")
            return self._get_default_content(section_title, description, context)

    def _get_default_content(self, section_title: str, description: str, context: Dict[str, Any]) -> str:
        """기본 콘텐츠 템플릿"""
        company_name = context.get('company_name', '귀사')
        return f"""본 절에서는 {company_name}의 {description}에 대해 설명합니다.

상세한 내용은 프로젝트 진행 과정에서 추가로 보완될 예정입니다."""

    def _clean_special_chars(self, content: str) -> str:
        """특수문자 제거 및 정리"""
        if not content:
            return ""

        # '#', '*' 제거
        content = content.replace('#', '')
        content = content.replace('*', '')

        # 연속된 공백 정리
        import re
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()

    async def _generate_compliance_sections(self, data: Dict[str, Any], include: List[str]) -> Dict[str, Any]:
        """규정 준수 보고서 섹션"""
        # 규정 준수 관련 섹션 생성 (간략화)
        return {
            "governance": {
                "title": "AI 거버넌스 준수 현황",
                "content": "ISO 24030 및 관련 규정 준수 현황을 평가한 결과입니다."
            }
        }

    async def _generate_improvement_sections(self, data: Dict[str, Any], include: List[str]) -> Dict[str, Any]:
        """개선 계획 보고서 섹션"""
        # 개선 계획 관련 섹션 생성 (간략화)
        return {
            "improvement_plan": {
                "title": "AI 역량 개선 계획",
                "content": "식별된 개선 영역에 대한 구체적인 실행 계획입니다."
            }
        }

    def export_to_enhanced_html(self, report_data: Dict[str, Any]) -> str:
        """고품질 HTML 보고서 생성"""
        company_name = report_data['project_info'].get('company_name', '')
        project_name = report_data['project_info'].get('project_name', '')
        report_date = report_data['project_info'].get('report_date', '')
        consultant = report_data['project_info'].get('consultant', 'AI Consulting Team')

        html_content = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_data['report_title']}</title>
    <style>
        @page {{
            size: A4;
            margin: 2cm;
        }}
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif;
            line-height: 1.8;
            color: #1a1a1a;
            background: white;
            padding: 0;
        }}
        .container {{
            max-width: 210mm;
            margin: 0 auto;
            padding: 20mm;
            background: white;
        }}

        /* 표지 */
        .cover-page {{
            text-align: center;
            padding: 80px 40px;
            page-break-after: always;
            min-height: 297mm;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }}
        .cover-page h1 {{
            font-size: 42px;
            color: #1a365d;
            margin-bottom: 10px;
            font-weight: 700;
            letter-spacing: 2px;
        }}
        .cover-page h2 {{
            font-size: 38px;
            color: #2d3748;
            margin-bottom: 60px;
            font-weight: 600;
        }}
        .cover-page .company {{
            font-size: 24px;
            color: #4a5568;
            margin: 40px 0 20px 0;
            font-weight: 500;
        }}
        .cover-page .consultant {{
            font-size: 20px;
            color: #718096;
            margin-bottom: 40px;
        }}
        .cover-page .date {{
            font-size: 22px;
            color: #4a5568;
            margin-top: 60px;
            font-weight: 500;
        }}

        /* 목차 */
        .toc {{
            page-break-after: always;
            padding: 40px 0;
        }}
        .toc h2 {{
            font-size: 28px;
            color: #1a365d;
            margin-bottom: 30px;
            border-bottom: 3px solid #3182ce;
            padding-bottom: 15px;
        }}
        .toc-item {{
            padding: 12px 0;
            border-bottom: 1px dotted #cbd5e0;
        }}
        .toc-item a {{
            text-decoration: none;
            color: #2d3748;
            display: flex;
            justify-content: space-between;
        }}

        /* 본문 */
        .section {{
            margin-bottom: 50px;
            page-break-inside: avoid;
        }}
        h2 {{
            font-size: 26px;
            color: #1a365d;
            border-left: 5px solid #3182ce;
            padding-left: 20px;
            margin: 50px 0 30px 0;
            page-break-after: avoid;
        }}
        h3 {{
            font-size: 22px;
            color: #2c5282;
            margin: 35px 0 20px 0;
            page-break-after: avoid;
        }}
        h4 {{
            font-size: 18px;
            color: #2d3748;
            margin: 25px 0 15px 0;
            font-weight: 600;
        }}
        p {{
            margin-bottom: 15px;
            text-align: justify;
            line-height: 1.9;
        }}
        ul, ol {{
            margin: 15px 0 20px 30px;
        }}
        li {{
            margin-bottom: 12px;
            line-height: 1.8;
        }}

        /* 강조 */
        strong {{
            color: #1a365d;
            font-weight: 600;
        }}

        /* 박스 */
        .highlight-box {{
            background: #f7fafc;
            border-left: 4px solid #3182ce;
            padding: 25px;
            margin: 25px 0;
            page-break-inside: avoid;
        }}
        .highlight-box h4 {{
            color: #3182ce;
            margin-top: 0;
        }}

        /* 표 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            page-break-inside: avoid;
        }}
        th, td {{
            border: 1px solid #cbd5e0;
            padding: 14px;
            text-align: left;
        }}
        th {{
            background: #edf2f7;
            color: #2d3748;
            font-weight: 600;
        }}
        tr:nth-child(even) {{
            background: #f7fafc;
        }}

        /* 페이지 번호 */
        .page-number {{
            text-align: center;
            margin-top: 40px;
            color: #718096;
            font-size: 14px;
        }}

        /* 푸터 */
        .footer {{
            text-align: center;
            margin-top: 80px;
            padding-top: 30px;
            border-top: 2px solid #e2e8f0;
            color: #718096;
            font-size: 14px;
            page-break-before: avoid;
        }}

        /* 인쇄 최적화 */
        @media print {{
            body {{
                background: white;
            }}
            .container {{
                padding: 0;
                max-width: 100%;
            }}
            .section {{
                page-break-inside: avoid;
            }}
            h2, h3, h4 {{
                page-break-after: avoid;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- 표지 -->
        <div class="cover-page">
            <h1>{report_data['report_title'].split()[0]}</h1>
            <h2>{report_data['report_title'].split()[-1] if len(report_data['report_title'].split()) > 1 else ''}</h2>
            <div class="company">{company_name}</div>
            <div class="consultant">{consultant}</div>
            <div class="date">{report_date}</div>
        </div>
"""

        # 본문 섹션
        for section_key, section_data in report_data.get('sections', {}).items():
            html_content += self._section_to_html(section_data)

        html_content += """
        <div class="footer">
            <p>본 보고서는 ISO 24030 기반 AI 평가 시스템에 의해 생성되었습니다.</p>
            <p>&copy; 2026 AI Consulting Platform. All rights reserved.</p>
        </div>
    </div>
</body>
</html>
"""
        return html_content

    def _section_to_html(self, section_data: Dict[str, Any], level: int = 2) -> str:
        """섹션을 HTML로 변환"""
        html = f"""
        <div class="section">
            <h{level}>{section_data.get('title', '')}</h{level}>
"""

        # subsections가 있는 경우
        if 'subsections' in section_data:
            for sub_key, sub_data in section_data['subsections'].items():
                html += self._section_to_html(sub_data, level + 1)
        # content가 있는 경우
        elif 'content' in section_data:
            content = section_data['content']
            # 개행을 단락으로 변환
            paragraphs = content.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    # 리스트 항목 처리
                    if para.strip().startswith('•') or para.strip().startswith('-'):
                        items = para.split('\n')
                        html += '<ul>'
                        for item in items:
                            item = item.strip().lstrip('•-').strip()
                            if item:
                                # ** ** 강조 처리
                                item = item.replace('**', '<strong>').replace('**', '</strong>')
                                html += f'<li>{item}</li>'
                        html += '</ul>'
                    else:
                        # 일반 단락
                        para = para.replace('**', '<strong>').replace('**', '</strong>')
                        html += f'<p>{para}</p>'

        html += """
        </div>
"""
        return html


# 싱글톤 인스턴스
_enhanced_generator = None

def get_enhanced_report_generator(llm_provider=None):
    """향상된 보고서 생성기 인스턴스 반환"""
    global _enhanced_generator
    if _enhanced_generator is None:
        _enhanced_generator = EnhancedReportGenerator(llm_provider)
    return _enhanced_generator
