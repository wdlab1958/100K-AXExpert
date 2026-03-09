/**
 * Project Manager - Stage 설정 모듈
 * Stage별 데이터 설정 및 워크플로우 관리
 */

const PMStageConfig = {
    // API Base URL
    API_BASE: '/api/v1',

    // 워크플로우 진행 상태
    workflowStatus: {
        stage1: { maturity: false, opportunities: false, roadmap: false },
        stage2: { requirements: false, architecture: false, governance: false },
        stage3: { poc: false, platform: false, integration: false },
        stage4: { pilot: false, changeManagement: false, scale: false },
        stage5: { monitoring: false, improvement: false, governanceReview: false },
        mlops: false,
        personnel: false,
        scenarios: false,
        report: false
    },

    /**
     * Stage 설정 가져오기
     */
    getStageConfig(stage) {
        const configs = {
            // Stage 1
            'stage1-maturity': {
                name: 'AI 성숙도 진단',
                endpoint: 'stage1/maturity-assessment',
                collectData: () => PMFormCollector.collectMaturityData(),
                populateForm: (data) => PMFormPopulator.populateMaturityForm(data)
            },
            'stage1-opportunities': {
                name: 'AI 기회 발굴',
                endpoint: 'stage1/opportunities',
                collectData: () => PMFormCollector.collectOpportunitiesData(),
                populateForm: (data) => PMFormPopulator.populateOpportunitiesForm(data)
            },
            'stage1-roadmap': {
                name: 'AI 로드맵',
                endpoint: 'stage1/roadmap',
                collectData: () => PMFormCollector.collectRoadmapData(),
                populateForm: (data) => PMFormPopulator.populateRoadmapForm(data)
            },
            // Stage 2
            'stage2-requirements': {
                name: '상세 요건 정의',
                endpoint: 'stage2/requirements',
                collectData: () => PMFormCollector.collectRequirementsData(),
                populateForm: (data) => PMFormPopulator.populateRequirementsForm(data)
            },
            'stage2-architecture': {
                name: '아키텍처 설계',
                endpoint: 'stage2/architecture',
                collectData: () => PMFormCollector.collectArchitectureData(),
                populateForm: (data) => PMFormPopulator.populateArchitectureForm(data)
            },
            'stage2-governance': {
                name: '거버넌스 체계',
                endpoint: 'stage2/governance',
                collectData: () => PMFormCollector.collectGovernanceData(),
                populateForm: (data) => PMFormPopulator.populateGovernanceForm(data)
            },
            // Stage 3
            'stage3-poc': {
                name: 'PoC 계획',
                endpoint: 'stage3/poc',
                collectData: () => PMFormCollector.collectPocData(),
                populateForm: (data) => PMFormPopulator.populatePocForm(data)
            },
            'stage3-platform': {
                name: '플랫폼 구축',
                endpoint: 'stage3/platform',
                collectData: () => PMFormCollector.collectPlatformData(),
                populateForm: (data) => PMFormPopulator.populatePlatformForm(data)
            },
            'stage3-integration': {
                name: '시스템 통합',
                endpoint: 'stage3/integration',
                collectData: () => PMFormCollector.collectIntegrationData(),
                populateForm: (data) => PMFormCollector.collectIntegrationData()
            },
            // Stage 4
            'stage4-pilot': {
                name: '파일럿 계획',
                endpoint: 'stage4/pilot',
                collectData: () => PMFormCollector.collectPilotData(),
                populateForm: (data) => PMFormPopulator.populatePilotForm(data)
            },
            'stage4-change': {
                name: '변화 관리',
                endpoint: 'stage4/change-management',
                collectData: () => PMFormCollector.collectChangeManagementData(),
                populateForm: (data) => PMFormPopulator.populateChangeManagementForm(data)
            },
            'stage4-scale': {
                name: '확산 계획',
                endpoint: 'stage4/scale',
                collectData: () => PMFormCollector.collectScaleData(),
                populateForm: (data) => PMFormPopulator.populateScaleForm(data)
            },
            // Stage 5
            'stage5-monitoring': {
                name: '모니터링 설정',
                endpoint: 'stage5/monitoring',
                collectData: () => PMFormCollector.collectMonitoringData(),
                populateForm: (data) => PMFormPopulator.populateMonitoringForm(data)
            },
            'stage5-improvement': {
                name: '개선 계획',
                endpoint: 'stage5/improvement',
                collectData: () => PMFormCollector.collectImprovementData(),
                populateForm: (data) => PMFormPopulator.populateImprovementForm(data)
            },
            'stage5-governance-review': {
                name: '거버넌스 검토',
                endpoint: 'stage5/governance-review',
                collectData: () => PMFormCollector.collectGovernanceReviewData(),
                populateForm: (data) => PMFormPopulator.populateGovernanceReviewForm(data)
            }
        };

        return configs[stage];
    },

    /**
     * Stage 데이터 저장 (범용)
     */
    async saveStageData(stage, data = null, currentProjectId, silent = false) {
        if (!currentProjectId) {
            if (!silent) PMNotification.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return false;
        }

        const stageConfig = this.getStageConfig(stage);
        if (!stageConfig) {
            console.error('Unknown stage:', stage);
            return false;
        }

        try {
            if (!data) {
                data = stageConfig.collectData();
            }

            // 데이터 검증
            if (!data) {
                throw new Error('수집된 데이터가 없습니다.');
            }

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${currentProjectId}/${stageConfig.endpoint}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }
            );

            if (!response.ok) {
                let errorMessage = `${stageConfig.name} 저장 실패`;
                try {
                    const errorData = await response.json();
                    // Pydantic validation errors 처리
                    if (errorData.detail && Array.isArray(errorData.detail)) {
                        const validationErrors = errorData.detail.map(err => {
                            const loc = err.loc ? err.loc.join('.') : '';
                            return `${loc}: ${err.msg || err.type || 'validation error'}`;
                        }).join(', ');
                        errorMessage += `: ${validationErrors}`;
                        console.error(`[${stage}] Validation errors:`, errorData.detail);
                        console.error(`[${stage}] Sent data:`, JSON.stringify(data, null, 2));
                    } else {
                        errorMessage += `: ${errorData.detail || errorData.message || response.statusText}`;
                    }
                } catch (e) {
                    errorMessage += `: ${response.status} ${response.statusText}`;
                }
                throw new Error(errorMessage);
            }

            const result = await response.json();
            this.updateStageStatus(stage, true);

            if (!silent) {
                PMNotification.showNotification(`${stageConfig.name} 데이터가 저장되었습니다.`, 'success');
            } else {
                console.log(`[AutoSave] ${stageConfig.name} Saved.`);
            }
            return result;
        } catch (error) {
            console.error(`${stage} 저장 오류:`, error);
            if (!silent) {
                const errorMsg = error.message || `${stageConfig.name} 저장에 실패했습니다.`;
                PMNotification.showNotification(errorMsg, 'error');
            }
            return false;
        }
    },

    /**
     * Stage 데이터 불러오기 (범용)
     */
    async loadStageData(stage, currentProjectId) {
        if (!currentProjectId) {
            PMNotification.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        const stageConfig = this.getStageConfig(stage);
        if (!stageConfig) {
            console.error('Unknown stage:', stage);
            return null;
        }

        try {
            const response = await fetch(
                `${this.API_BASE}/framework/projects/${currentProjectId}/${stageConfig.endpoint}`
            );

            if (!response.ok) throw new Error(`${stageConfig.name} 로드 실패`);

            const data = await response.json();

            if (stageConfig.populateForm && data.data) {
                stageConfig.populateForm(data.data);
            }

            return data;
        } catch (error) {
            console.error(`${stage} 로드 오류:`, error);
            return null;
        }
    },

    /**
     * Stage 상태 업데이트
     */
    updateStageStatus(stage, completed) {
        const parts = stage.split('-');
        if (parts.length >= 2) {
            const stageNum = parts[0];
            const subStage = parts.slice(1).join('');

            if (this.workflowStatus[stageNum]) {
                const key = subStage.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                this.workflowStatus[stageNum][key] = completed;
                this.renderWorkflowProgress();
            }
        }
    },

    /**
     * 워크플로우 상태 업데이트
     */
    updateWorkflowStatus(project) {
        this.workflowStatus = {
            stage1: {
                maturity: !!project.stage1_maturity,
                opportunities: !!project.stage1_opportunities,
                roadmap: !!project.stage1_roadmap
            },
            stage2: {
                requirements: !!project.stage2_requirements,
                architecture: !!project.stage2_architecture,
                governance: !!project.stage2_governance
            },
            stage3: {
                poc: !!project.stage3_poc,
                platform: !!project.stage3_platform,
                integration: !!project.stage3_integration
            },
            stage4: {
                pilot: !!project.stage4_pilot,
                changeManagement: !!project.stage4_change_management,
                scale: !!project.stage4_scale
            },
            stage5: {
                monitoring: !!project.stage5_monitoring,
                improvement: !!project.stage5_improvement,
                governanceReview: !!project.stage5_governance_review
            },
            mlops: !!project.mlops_standards,
            personnel: !!project.personnel_organization,
            scenarios: !!project.scenarios && project.scenarios.length > 0,
            report: !!project.reports && project.reports.length > 0
        };

        this.renderWorkflowProgress();
        this.renderCompletionOverview();
    },

    /**
     * 워크플로우 진행 상태 렌더링
     */
    renderWorkflowProgress() {
        const container = document.getElementById('workflowProgressContainer');
        if (!container) return;

        const stages = [
            { id: 'stage1', name: 'Stage 1: 전략 수립', items: this.workflowStatus.stage1 },
            { id: 'stage2', name: 'Stage 2: 설계 정의', items: this.workflowStatus.stage2 },
            { id: 'stage3', name: 'Stage 3: 솔루션 구축', items: this.workflowStatus.stage3 },
            { id: 'stage4', name: 'Stage 4: 파일럿/확산', items: this.workflowStatus.stage4 },
            { id: 'stage5', name: 'Stage 5: 운영/개선', items: this.workflowStatus.stage5 }
        ];

        container.innerHTML = stages.map(stage => {
            const completed = Object.values(stage.items).filter(v => v).length;
            const total = Object.values(stage.items).length;
            const percent = Math.round((completed / total) * 100);

            return `
                <div class="workflow-stage-item mb-3">
                    <div class="d-flex justify-content-between align-items-center mb-1">
                        <span class="fw-medium">${stage.name}</span>
                        <span class="badge ${percent === 100 ? 'badge-success' : 'badge-primary'}">${completed}/${total}</span>
                    </div>
                    <div class="progress" style="height: 4px;">
                        <div class="progress-bar ${percent === 100 ? 'bg-success' : 'bg-primary'}"
                             style="width: ${percent}%"></div>
                    </div>
                </div>
            `;
        }).join('');
    },

    /**
     * 추가 분석 현황 업데이트
     */
    renderCompletionOverview() {
        const statusMap = [
            { id: 'mlopsStatus', key: 'mlops', completedText: '완료', pendingText: '미완료' },
            { id: 'personnelStatus', key: 'personnel', completedText: '완료', pendingText: '미완료' },
            { id: 'scenarioStatus', key: 'scenarios', completedText: '생성됨', pendingText: '미생성' },
            { id: 'reportStatus', key: 'report', completedText: '생성됨', pendingText: '미생성' }
        ];

        statusMap.forEach(item => {
            const card = document.getElementById(item.id);
            if (card) {
                const status = card.querySelector('.status');
                if (status) {
                    if (this.workflowStatus[item.key]) {
                        status.textContent = item.completedText;
                        status.className = 'status text-success';
                    } else {
                        status.textContent = item.pendingText;
                        status.className = 'status text-muted';
                    }
                }
            }
        });
    },

    /**
     * 모든 단계 데이터 로드
     */
    async loadAllStageData(project) {
        // Stage 1
        if (project.stage1_maturity) PMFormPopulator.populateMaturityForm(project.stage1_maturity);
        if (project.stage1_opportunities) PMFormPopulator.populateOpportunitiesForm(project.stage1_opportunities);
        if (project.stage1_roadmap) PMFormPopulator.populateRoadmapForm(project.stage1_roadmap);

        // Stage 2
        if (project.stage2_requirements) PMFormPopulator.populateRequirementsForm(project.stage2_requirements);
        if (project.stage2_architecture) PMFormPopulator.populateArchitectureForm(project.stage2_architecture);
        if (project.stage2_governance) PMFormPopulator.populateGovernanceForm(project.stage2_governance);

        // Stage 3
        if (project.stage3_poc) PMFormPopulator.populatePocForm(project.stage3_poc);
        if (project.stage3_platform) PMFormPopulator.populatePlatformForm(project.stage3_platform);
        if (project.stage3_integration) PMFormPopulator.populateIntegrationForm(project.stage3_integration);

        // Stage 4
        if (project.stage4_pilot) PMFormPopulator.populatePilotForm(project.stage4_pilot);
        if (project.stage4_change_management) PMFormPopulator.populateChangeManagementForm(project.stage4_change_management);
        if (project.stage4_scale) PMFormPopulator.populateScaleForm(project.stage4_scale);

        // Stage 5
        if (project.stage5_monitoring) PMFormPopulator.populateMonitoringForm(project.stage5_monitoring);
        if (project.stage5_improvement) PMFormPopulator.populateImprovementForm(project.stage5_improvement);
        if (project.stage5_governance_review) PMFormPopulator.populateGovernanceReviewForm(project.stage5_governance_review);

        // 기업 프로필
        if (project.company_profile) PMFormPopulator.populateCompanyProfileForm(project.company_profile);
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMStageConfig;
} else {
    window.PMStageConfig = PMStageConfig;
}

