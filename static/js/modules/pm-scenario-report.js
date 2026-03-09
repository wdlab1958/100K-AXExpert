/**
 * Project Manager - 시나리오 및 보고서 모듈
 * 시나리오 분석 및 보고서 생성 관리
 */

const PMScenarioReport = {
    // API Base URL
    API_BASE: '/api/v1',

    /**
     * 시나리오 분석 실행
     */
    async generateScenarios(scenarioOrParams = 'balanced', currentProjectId) {
        if (!currentProjectId) {
            PMNotification.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        let selectedScenario = 'balanced';
        let analysisParameters = {};

        if (typeof scenarioOrParams === 'string') {
            selectedScenario = scenarioOrParams;
        } else if (typeof scenarioOrParams === 'object' && scenarioOrParams !== null) {
            const riskMap = { 'low': 'conservative', 'medium': 'balanced', 'high': 'aggressive' };
            selectedScenario = riskMap[scenarioOrParams.risk_appetite] || 'balanced';
            analysisParameters = scenarioOrParams;
        }

        try {
            PMNotification.showLoading('시나리오 분석을 수행하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${currentProjectId}/scenarios/analyze`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        scenarios: [],
                        selected_scenario: selectedScenario,
                        analysis_parameters: analysisParameters
                    })
                }
            );

            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                const errorMessage = errorData.detail 
                    ? (Array.isArray(errorData.detail) 
                        ? errorData.detail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join(', ')
                        : JSON.stringify(errorData.detail))
                    : `시나리오 분석 실패 (${response.status})`;
                throw new Error(errorMessage);
            }

            const data = await response.json();
            PMNotification.hideLoading();
            PMNotification.showNotification('시나리오 분석이 완료되었습니다.', 'success');

            this.displayScenarioResults(data.analysis, currentProjectId);

            return data;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('시나리오 분석 오류:', error);
            PMNotification.showNotification('시나리오 분석에 실패했습니다.', 'error');
            return null;
        }
    },

    /**
     * 시나리오 결과 표시
     */
    displayScenarioResults(analysis, currentProjectId) {
        const modal = document.getElementById('scenarioResultModal');
        const content = document.getElementById('scenarioResultContent');

        if (!modal || !content) {
            console.log('Scenario Results:', analysis);
            return;
        }

        const scenarios = analysis.all_scenarios || {};
        const selected = analysis.selected_scenario;

        content.innerHTML = `
            <div class="scenario-summary mb-4">
                <h5 class="mb-3">프로젝트 진행률</h5>
                <div class="progress mb-2" style="height: 20px;">
                    <div class="progress-bar bg-primary" style="width: ${analysis.overall_completion}%">
                        ${analysis.overall_completion}%
                    </div>
                </div>
                <div class="row g-2 mt-3">
                    ${Object.entries(analysis.stage_completion || {}).map(([stage, percent]) => `
                        <div class="col-4">
                            <div class="text-center p-2 bg-light rounded">
                                <div class="small text-dark fw-bold">${stage.toUpperCase()}</div>
                                <div class="fw-bold text-dark fs-5">${percent}%</div>
                            </div>
                        </div>
                    `).join('')}
                </div>
            </div>

            <h5 class="mb-3">시나리오 비교</h5>
            <div class="row g-3">
                ${Object.entries(scenarios).map(([key, scenario]) => `
                    <div class="col-md-4">
                        <div class="card h-100 ${key === selected ? 'border-primary' : ''}">
                            <div class="card-header ${key === selected ? 'bg-primary text-white' : ''}">
                                <strong>${scenario.name}</strong>
                                ${key === selected ? '<span class="badge bg-light text-primary ms-2">선택됨</span>' : ''}
                            </div>
                            <div class="card-body">
                                <p><strong>예상 ROI:</strong> ${scenario.roi_estimate}</p>
                                <p><strong>기간:</strong> ${scenario.timeline}</p>
                                <p><strong>리스크:</strong>
                                    <span class="badge ${scenario.risk_level === '높음' ? 'bg-danger' : scenario.risk_level === '중간' ? 'bg-warning' : 'bg-success'}">
                                        ${scenario.risk_level}
                                    </span>
                                </p>
                                <p class="mb-0"><strong>특징:</strong></p>
                                <ul class="small mb-0">
                                    ${scenario.key_features.map(f => `<li>${f}</li>`).join('')}
                                </ul>
                            </div>
                            <div class="card-footer">
                                <button class="btn btn-sm ${key === selected ? 'btn-primary' : 'btn-outline-primary'} w-100"
                                        onclick="ProjectManager.generateScenarios('${key}')">
                                    ${key === selected ? '현재 선택' : '이 시나리오 선택'}
                                </button>
                            </div>
                        </div>
                    </div>
                `).join('')}
            </div>

            <div class="mt-4">
                <h5>권고사항</h5>
                <ul class="list-group">
                    ${(analysis.recommendations || []).map(rec => `
                        <li class="list-group-item">
                            <i class="bi bi-lightbulb text-warning me-2"></i>${rec}
                        </li>
                    `).join('')}
                </ul>
            </div>
        `;

        // 기존 모달 인스턴스가 있으면 제거
        const existingModal = bootstrap.Modal.getInstance(modal);
        if (existingModal) {
            existingModal.dispose();
        }

        // 모달 닫힘 이벤트 리스너 추가 (한 번만)
        const handleModalHidden = () => {
            // backdrop 강제 제거
            setTimeout(() => {
                const backdrops = document.querySelectorAll('.modal-backdrop');
                backdrops.forEach(backdrop => {
                    backdrop.remove();
                });
                
                // body 스타일 복원
                document.body.classList.remove('modal-open');
                document.body.style.overflow = '';
                document.body.style.paddingRight = '';
                
                console.log('[Scenario Modal] Cleaned up backdrop and body styles');
            }, 100);
        };

        // 기존 이벤트 리스너 제거 후 새로 추가
        modal.removeEventListener('hidden.bs.modal', handleModalHidden);
        modal.addEventListener('hidden.bs.modal', handleModalHidden, { once: true });

        // 모달 표시
        const bsModal = new bootstrap.Modal(modal, {
            backdrop: true,
            keyboard: true,
            focus: true
        });
        
        bsModal.show();
        
        // 모달이 완전히 표시된 후에도 backdrop 확인
        modal.addEventListener('shown.bs.modal', () => {
            console.log('[Scenario Modal] Modal shown');
        }, { once: true });
    },

    /**
     * 최종 보고서 생성
     */
    async generateReport(options = {}, currentProjectId) {
        if (!currentProjectId) {
            PMNotification.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        try {
            PMNotification.showLoading('보고서를 생성하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${currentProjectId}/report/generate`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        report_type: options.type || 'full',
                        include_sections: options.sections || [
                            'executive_summary', 'current_state', 'gap_analysis',
                            'recommendations', 'roadmap', 'investment', 'risks'
                        ],
                        format: options.format || 'html'
                    })
                }
            );

            if (!response.ok) throw new Error('보고서 생성 실패');

            const data = await response.json();
            PMNotification.hideLoading();
            PMNotification.showNotification('보고서가 생성되었습니다.', 'success');

            this.displayReportResults(data.report, currentProjectId);

            return data;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('보고서 생성 오류:', error);
            PMNotification.showNotification('보고서 생성에 실패했습니다.', 'error');
            return null;
        }
    },

    /**
     * 보고서 결과 표시
     */
    displayReportResults(report, currentProjectId) {
        const modal = document.getElementById('reportResultModal');
        const content = document.getElementById('reportResultContent');

        if (!modal || !content) {
            console.log('Report:', report);
            return;
        }

        const sections = report.sections || {};

        content.innerHTML = `
            <div class="report-header mb-4 text-center">
                <h4 class="text-primary">AI 전환 전략 컨설팅 보고서</h4>
                <p class="text-muted">
                    ${report.project_info?.project_name || '프로젝트'} |
                    생성일: ${report.generated_at?.substring(0, 10) || '-'}
                </p>
            </div>

            ${Object.entries(sections).map(([key, section]) => `
                <div class="report-section mb-4">
                    <h5 class="border-bottom pb-2">
                        <i class="bi bi-bookmark-fill text-primary me-2"></i>${section.title}
                    </h5>
                    <div class="section-content">
                        ${this.formatReportContent(section.content)}
                    </div>
                </div>
            `).join('')}

            <div class="text-center mt-4">
                <a href="${this.API_BASE}/framework/projects/${currentProjectId}/report/download"
                   target="_blank" class="btn btn-primary">
                    <i class="bi bi-download me-2"></i>HTML로 다운로드
                </a>
            </div>
        `;

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    },

    /**
     * 보고서 콘텐츠 포맷팅
     */
    formatReportContent(content) {
        if (!content) return '<p class="text-muted">내용 없음</p>';

        if (typeof content === 'string') {
            return `<p>${content}</p>`;
        }

        if (Array.isArray(content)) {
            return `<ul class="list-unstyled">${content.map(item => {
                if (typeof item === 'object') {
                    return `<li class="mb-2">${JSON.stringify(item, null, 2)}</li>`;
                }
                return `<li><i class="bi bi-check2 text-success me-2"></i>${item}</li>`;
            }).join('')}</ul>`;
        }

        if (typeof content === 'object') {
            return `<div class="row g-3">${Object.entries(content).map(([k, v]) => `
                <div class="col-md-6">
                    <div class="p-3 bg-light rounded">
                        <strong class="text-primary">${k.replace(/_/g, ' ').toUpperCase()}</strong>
                        <div class="mt-1">${typeof v === 'object' ? JSON.stringify(v, null, 2) : v || '-'}</div>
                    </div>
                </div>
            `).join('')}</div>`;
        }

        return `<p>${content}</p>`;
    },

    /**
     * 전체 워크플로우 실행 (분석)
     */
    async runFullAnalysis(currentProjectId) {
        if (!currentProjectId) {
            PMNotification.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        if (!confirm('전체 AI 분석을 실행하시겠습니까? 이 작업은 시간이 걸릴 수 있습니다.')) {
            return null;
        }

        try {
            PMNotification.showLoading('AI 에이전트가 전체 분석을 수행하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/projects/${currentProjectId}/run-full-consultation?auto_approve=false`,
                { method: 'POST' }
            );

            if (!response.ok) {
                // 상세한 오류 메시지 추출
                let errorMessage = '분석 실행 실패';
                try {
                    const errorData = await response.json();
                    if (errorData.detail) {
                        errorMessage = typeof errorData.detail === 'string' 
                            ? errorData.detail 
                            : JSON.stringify(errorData.detail);
                    } else if (errorData.message) {
                        errorMessage = errorData.message;
                    }
                } catch (e) {
                    errorMessage = `HTTP ${response.status}: ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const data = await response.json();
            PMNotification.hideLoading();

            // 프로젝트 데이터 다시 로드 (분석 결과 반영)
            if (typeof PMProjectCrud !== 'undefined' && PMProjectCrud.loadProject) {
                await PMProjectCrud.loadProject(currentProjectId);
            } else if (typeof ProjectManager !== 'undefined' && ProjectManager.loadProject) {
                await ProjectManager.loadProject(currentProjectId);
            }

            PMNotification.showNotification('AI 분석이 완료되었습니다.', 'success');
            return data;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('전체 분석 오류:', error);
            const errorMessage = error.message || 'AI 분석에 실패했습니다.';
            PMNotification.showNotification(`AI 분석 실패: ${errorMessage}`, 'error');
            return null;
        }
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMScenarioReport;
} else {
    window.PMScenarioReport = PMScenarioReport;
}

