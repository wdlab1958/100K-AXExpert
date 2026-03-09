/**
 * 100K-AX Expert Platform - Project Manager Module
 * 프로젝트 데이터 저장/불러오기 및 워크플로우 관리
 */

const ProjectManager = {
    // API Base URL
    API_BASE: '/api/v1',

    // 현재 선택된 프로젝트 ID
    currentProjectId: null,

    // 프로젝트 목록 캐시
    projectsCache: [],

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

    // =========================================================================
    // localStorage 자동 저장 시스템
    // =========================================================================

    // localStorage 키 접두사
    STORAGE_PREFIX: 'ai_consulting_',

    // 자동 저장 간격 (ms)
    AUTO_SAVE_INTERVAL: 3000,

    // 마지막 저장 시간
    _lastSaveTime: null,

    // 저장 대기 타이머
    _localSaveTimeout: null,

    // 저장 상태 표시 요소
    _saveStatusElement: null,

    /**
     * 초기화
     */
    async init() {
        console.log('ProjectManager initializing...');
        await this.loadProjectList();
        this.bindEvents();
        this.restoreLastProject();
        this.initAutoSave();

        // localStorage 자동 저장 시스템 초기화
        this.initLocalStorageAutoSave();

        // 페이지 로드 시 localStorage에서 데이터 복원
        this.restoreFromLocalStorage();

        // 저장 상태 표시 UI 생성
        this.createSaveStatusIndicator();
    },

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 프로젝트 선택 드롭다운 변경
        const projectSelect = document.getElementById('projectSelector');
        if (projectSelect) {
            projectSelect.addEventListener('change', (e) => {
                if (e.target.value) {
                    this.loadProject(e.target.value);
                }
            });
        }

        // 폼 자동 저장 (입력 변경 시)
        document.querySelectorAll('input, select, textarea').forEach(el => {
            el.addEventListener('change', () => {
                if (this.currentProjectId && el.closest('.auto-save-form')) {
                    this.debouncedSave(el.closest('.auto-save-form').dataset.stage);
                }
            });
        });
    },

    /**
     * 마지막 작업 프로젝트 복원
     */
    restoreLastProject() {
        const lastProjectId = localStorage.getItem('lastProjectId');
        if (!lastProjectId) return;

        // projectsCache에서 프로젝트 찾기 (project_id 또는 id 필드 확인)
        const projectExists = this.projectsCache.find(p =>
            p.project_id === lastProjectId || p.id === lastProjectId
        );

        if (projectExists) {
            this.loadProject(lastProjectId);
        } else {
            // 캐시에 없으면 localStorage에서 제거
            localStorage.removeItem('lastProjectId');
        }
    },

    /**
     * 자동 저장 초기화
     */
    /**
     * 자동 저장 초기화
     */
    initAutoSave() {
        this.saveTimeouts = {};

        // Delegate input events for auto-saving (Continuous saving)
        document.body.addEventListener('input', (e) => {
            const target = e.target;
            if (!target.matches('input, textarea, select')) return;

            // Allow manual opt-out
            if (target.hasAttribute('data-no-autosave')) return;

            // Find closest container
            const container = target.closest('[data-save-key]');
            if (!container) return;

            const stageKey = container.getAttribute('data-save-key');
            if (!stageKey) return;

            this.debouncedSave(stageKey);
        });
    },

    /**
     * 디바운스 저장 (1.5초 딜레이)
     */
    debouncedSave(stage) {
        if (this.saveTimeouts[stage]) {
            clearTimeout(this.saveTimeouts[stage]);
        }

        // Show saving indicator (optional)
        // console.log(`[AutoSave] Scheduled for ${stage}`);

        this.saveTimeouts[stage] = setTimeout(() => {
            console.log(`[AutoSave] Triggering save for ${stage}`);
            this.saveStageData(stage, null, true); // silent=true
        }, 1500);
    },

    // =========================================================================
    // 프로젝트 목록 관리
    // =========================================================================

    /**
     * 프로젝트 목록 로드
     */
    async loadProjectList() {
        try {
            const response = await fetch(`${this.API_BASE}/framework/projects`);
            if (!response.ok) throw new Error('프로젝트 목록 로드 실패');

            const data = await response.json();
            this.projectsCache = data.projects || [];
            this.renderProjectList();
            return this.projectsCache;
        } catch (error) {
            console.error('프로젝트 목록 로드 오류:', error);
            this.showNotification('프로젝트 목록을 불러오는데 실패했습니다.', 'error');
            return [];
        }
    },

    /**
     * 프로젝트 이름 추출 헬퍼
     */
    getProjectName(project) {
        return project.company_profile?.name || project.project_name || project.project_id || 'Unknown';
    },

    /**
     * 프로젝트 ID 추출 헬퍼
     */
    getProjectId(project) {
        return project.project_id || project.id;
    },

    /**
     * 프로젝트 산업 추출 헬퍼
     */
    getProjectIndustry(project) {
        return project.company_profile?.industry || project.industry || '-';
    },

    /**
     * 프로젝트 목록 렌더링
     */
    renderProjectList() {
        const selector = document.getElementById('projectSelector');
        if (!selector) return;

        selector.innerHTML = '<option value="">-- 프로젝트 선택 --</option>';

        this.projectsCache.forEach(project => {
            const projectId = this.getProjectId(project);
            const projectName = this.getProjectName(project);
            const option = document.createElement('option');
            option.value = projectId;
            option.textContent = `${projectName} (${this.formatDate(project.updated_at || project.created_at)})`;
            if (projectId === this.currentProjectId) {
                option.selected = true;
            }
            selector.appendChild(option);
        });

        // 프로젝트 목록 테이블도 업데이트
        this.renderProjectTable();
    },

    /**
     * 프로젝트 테이블 렌더링
     */
    renderProjectTable() {
        const tableBody = document.getElementById('projectListTable');
        if (!tableBody) return;

        if (this.projectsCache.length === 0) {
            tableBody.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center text-muted py-4">
                        <i class="bi bi-folder2-open fs-1 d-block mb-2"></i>
                        프로젝트가 없습니다. 새 프로젝트를 생성해주세요.
                    </td>
                </tr>
            `;
            return;
        }

        tableBody.innerHTML = this.projectsCache.map(project => {
            const projectId = this.getProjectId(project);
            const projectName = this.getProjectName(project);
            const projectIndustry = this.getProjectIndustry(project);
            const progress = this.calculateProgress(project);
            const statusBadge = this.getStatusBadge(progress);

            return `
                <tr class="${projectId === this.currentProjectId ? 'table-active' : ''}"
                    onclick="ProjectManager.loadProject('${projectId}')" style="cursor: pointer;">
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <div class="project-icon">
                                <i class="bi bi-briefcase-fill text-primary"></i>
                            </div>
                            <div>
                                <div class="fw-semibold">${projectName}</div>
                                <small class="text-muted">${projectId}</small>
                            </div>
                        </div>
                    </td>
                    <td><span class="badge badge-primary">${projectIndustry}</span></td>
                    <td>
                        <div class="progress" style="height: 6px; width: 100px;">
                            <div class="progress-bar bg-primary" style="width: ${progress}%"></div>
                        </div>
                        <small class="text-muted">${progress}%</small>
                    </td>
                    <td>${statusBadge}</td>
                    <td><small>${this.formatDate(project.updated_at || project.created_at)}</small></td>
                    <td>
                        <div class="btn-group btn-group-sm">
                            <button class="btn btn-outline-primary" onclick="event.stopPropagation(); ProjectManager.loadProject('${projectId}')">
                                <i class="bi bi-folder-symlink"></i>
                            </button>
                            <button class="btn btn-outline-secondary" onclick="event.stopPropagation(); ProjectManager.duplicateProject('${projectId}')">
                                <i class="bi bi-copy"></i>
                            </button>
                            <button class="btn btn-outline-danger" onclick="event.stopPropagation(); ProjectManager.deleteProject('${projectId}')">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    </td>
                </tr>
            `;
        }).join('');
    },

    /**
     * 진행률 계산
     */
    calculateProgress(project) {
        let completed = 0;
        let total = 14; // 전체 단계 수

        if (project.stage1_maturity) completed++;
        if (project.stage1_opportunities) completed++;
        if (project.stage1_roadmap) completed++;
        if (project.stage2_requirements) completed++;
        if (project.stage2_architecture) completed++;
        if (project.stage2_governance) completed++;
        if (project.stage3_poc) completed++;
        if (project.stage3_platform) completed++;
        if (project.stage3_integration) completed++;
        if (project.stage4_pilot) completed++;
        if (project.stage4_change_management) completed++;
        if (project.stage4_scale) completed++;
        if (project.stage5_monitoring) completed++;
        if (project.stage5_improvement) completed++;

        return Math.round((completed / total) * 100);
    },

    /**
     * 상태 배지 생성
     */
    getStatusBadge(progress) {
        if (progress === 0) return '<span class="badge badge-secondary">시작 전</span>';
        if (progress < 30) return '<span class="badge badge-warning">진행 중</span>';
        if (progress < 70) return '<span class="badge badge-primary">중반 진행</span>';
        if (progress < 100) return '<span class="badge badge-accent">마무리 중</span>';
        return '<span class="badge badge-success">완료</span>';
    },

    // =========================================================================
    // 프로젝트 CRUD
    // =========================================================================

    /**
     * 새 프로젝트 생성
     */
    async createProject(projectData) {
        try {
            this.showLoading('프로젝트를 생성하고 있습니다...');

            const response = await fetch(`${this.API_BASE}/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData)
            });

            if (!response.ok) throw new Error('프로젝트 생성 실패');

            const data = await response.json();
            this.currentProjectId = data.project_id;
            localStorage.setItem('lastProjectId', data.project_id);

            await this.loadProjectList();
            this.hideLoading();
            this.showNotification('프로젝트가 성공적으로 생성되었습니다.', 'success');

            return data;
        } catch (error) {
            this.hideLoading();
            console.error('프로젝트 생성 오류:', error);
            this.showNotification('프로젝트 생성에 실패했습니다.', 'error');
            throw error;
        }
    },

    /**
     * 프로젝트 불러오기
     */
    async loadProject(projectId) {
        if (!projectId) {
            console.warn('프로젝트 ID가 없습니다.');
            return null;
        }

        try {
            this.showLoading('프로젝트를 불러오는 중입니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}/summary`);
            if (!response.ok) {
                // 프로젝트가 없으면 localStorage에서 제거
                if (response.status === 404) {
                    localStorage.removeItem('lastProjectId');
                }
                throw new Error('프로젝트 로드 실패');
            }

            const data = await response.json();

            // API 응답에서 project_data 사용
            const project = data.project_data;
            if (!project) {
                throw new Error('프로젝트 데이터가 없습니다.');
            }

            this.currentProjectId = projectId;
            localStorage.setItem('lastProjectId', projectId);

            // 전역 변수도 업데이트 (다른 모듈에서 사용)
            if (typeof window !== 'undefined') {
                window.currentProjectId = projectId;
            }
            // PMProjectCrud 모듈도 업데이트
            if (typeof PMProjectCrud !== 'undefined') {
                PMProjectCrud.currentProjectId = projectId;
            }

            // 프로젝트 선택기 업데이트
            const selector = document.getElementById('projectSelector');
            if (selector) selector.value = projectId;

            // 현재 프로젝트 표시 업데이트
            this.updateCurrentProjectDisplay(project);

            // 워크플로우 상태 업데이트
            this.updateWorkflowStatus(project);

            // 각 단계 데이터 로드
            await this.loadAllStageData(project);

            this.hideLoading();

            // 프로젝트 이름 가져오기 (company_profile.name 또는 project_name 사용)
            const projectName = project.company_profile?.name || project.project_name || projectId;
            this.showNotification(`프로젝트 "${projectName}"를 불러왔습니다.`, 'success');

            // 프로젝트 테이블 업데이트 (선택 표시)
            this.renderProjectTable();

            return project;
        } catch (error) {
            this.hideLoading();
            console.error('프로젝트 로드 오류:', error);
            this.showNotification('프로젝트를 불러오는데 실패했습니다.', 'error');
            return null;
        }
    },

    /**
     * 현재 프로젝트 표시 업데이트
     */
    updateCurrentProjectDisplay(project) {
        if (!project) return;

        const projectName = project.company_profile?.name || project.project_name || project.project_id || 'Unknown';

        const display = document.getElementById('currentProjectDisplay');
        if (display) {
            display.innerHTML = `
                <div class="d-flex align-items-center gap-2">
                    <i class="bi bi-briefcase-fill text-primary"></i>
                    <span class="fw-semibold">${projectName}</span>
                    <span class="badge badge-primary">${this.calculateProgress(project)}% 완료</span>
                </div>
            `;
        }

        // 헤더의 프로젝트 정보도 업데이트
        const headerProject = document.getElementById('headerProjectInfo');
        if (headerProject) {
            headerProject.textContent = projectName;
        }
    },

    /**
     * 프로젝트 삭제
     */
    async deleteProject(projectId) {
        if (!confirm(`프로젝트 "${projectId}"를 삭제하시겠습니까? 이 작업은 되돌릴 수 없습니다.`)) {
            return;
        }

        try {
            this.showLoading('프로젝트를 삭제하고 있습니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('프로젝트 삭제 실패');

            if (this.currentProjectId === projectId) {
                this.currentProjectId = null;
                localStorage.removeItem('lastProjectId');
            }

            await this.loadProjectList();
            this.hideLoading();
            this.showNotification('프로젝트가 삭제되었습니다.', 'success');
        } catch (error) {
            this.hideLoading();
            console.error('프로젝트 삭제 오류:', error);
            this.showNotification('프로젝트 삭제에 실패했습니다.', 'error');
        }
    },

    /**
     * 프로젝트 복제
     */
    async duplicateProject(projectId) {
        try {
            this.showLoading('프로젝트를 복제하고 있습니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}/duplicate`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('프로젝트 복제 실패');

            const data = await response.json();
            await this.loadProjectList();
            this.hideLoading();
            this.showNotification('프로젝트가 복제되었습니다.', 'success');

            return data;
        } catch (error) {
            this.hideLoading();
            console.error('프로젝트 복제 오류:', error);
            this.showNotification('프로젝트 복제에 실패했습니다.', 'error');
        }
    },

    // =========================================================================
    // Stage별 데이터 저장/불러오기
    // =========================================================================

    /**
     * 모든 단계 데이터 로드
     */
    async loadAllStageData(project) {
        // Stage 1
        if (project.stage1_maturity) this.populateMaturityForm(project.stage1_maturity);
        if (project.stage1_opportunities) this.populateOpportunitiesForm(project.stage1_opportunities);
        if (project.stage1_roadmap) this.populateRoadmapForm(project.stage1_roadmap);

        // Stage 2
        if (project.stage2_requirements) this.populateRequirementsForm(project.stage2_requirements);
        if (project.stage2_architecture) this.populateArchitectureForm(project.stage2_architecture);
        if (project.stage2_governance) this.populateGovernanceForm(project.stage2_governance);

        // Stage 3
        if (project.stage3_poc) this.populatePocForm(project.stage3_poc);
        if (project.stage3_platform) this.populatePlatformForm(project.stage3_platform);
        if (project.stage3_integration) this.populateIntegrationForm(project.stage3_integration);

        // Stage 4
        if (project.stage4_pilot) this.populatePilotForm(project.stage4_pilot);
        if (project.stage4_change_management) this.populateChangeManagementForm(project.stage4_change_management);
        if (project.stage4_scale) this.populateScaleForm(project.stage4_scale);

        // Stage 5
        if (project.stage5_monitoring) this.populateMonitoringForm(project.stage5_monitoring);
        if (project.stage5_improvement) this.populateImprovementForm(project.stage5_improvement);
        if (project.stage5_governance_review) this.populateGovernanceReviewForm(project.stage5_governance_review);

        // 기업 프로필
        if (project.company_profile) this.populateCompanyProfileForm(project.company_profile);
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
     * 추가 분석 현황 업데이트
     */
    renderCompletionOverview() {
        // MLOps 상태
        const mlopsCard = document.getElementById('mlopsStatus');
        if (mlopsCard) {
            const status = mlopsCard.querySelector('.status');
            if (status) {
                if (this.workflowStatus.mlops) {
                    status.textContent = '완료';
                    status.className = 'status text-success';
                } else {
                    status.textContent = '미완료';
                    status.className = 'status text-muted';
                }
            }
        }

        // 인력 구성 상태
        const personnelCard = document.getElementById('personnelStatus');
        if (personnelCard) {
            const status = personnelCard.querySelector('.status');
            if (status) {
                if (this.workflowStatus.personnel) {
                    status.textContent = '완료';
                    status.className = 'status text-success';
                } else {
                    status.textContent = '미완료';
                    status.className = 'status text-muted';
                }
            }
        }

        // 시나리오 상태
        const scenarioCard = document.getElementById('scenarioStatus');
        if (scenarioCard) {
            const status = scenarioCard.querySelector('.status');
            if (status) {
                if (this.workflowStatus.scenarios) {
                    status.textContent = '생성됨';
                    status.className = 'status text-success';
                } else {
                    status.textContent = '미생성';
                    status.className = 'status text-muted';
                }
            }
        }

        // 보고서 상태
        const reportCard = document.getElementById('reportStatus');
        if (reportCard) {
            const status = reportCard.querySelector('.status');
            if (status) {
                if (this.workflowStatus.report) {
                    status.textContent = '생성됨';
                    status.className = 'status text-success';
                } else {
                    status.textContent = '미생성';
                    status.className = 'status text-muted';
                }
            }
        }
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
     * Stage 데이터 저장 (범용)
     */
    async saveStageData(stage, data = null, silent = false) {
        if (!this.currentProjectId) {
            if (!silent) this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return false;
        }

        const stageConfig = this.getStageConfig(stage);
        if (!stageConfig) {
            console.error('Unknown stage:', stage);
            return false;
        }

        try {
            // 데이터가 제공되지 않으면 폼에서 수집
            if (!data) {
                data = stageConfig.collectData();
            }

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${this.currentProjectId}/${stageConfig.endpoint}`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(data)
                }
            );

            if (!response.ok) throw new Error(`${stageConfig.name} 저장 실패`);

            const result = await response.json();

            // 워크플로우 상태 업데이트
            this.updateStageStatus(stage, true);

            if (!silent) {
                this.showNotification(`${stageConfig.name} 데이터가 저장되었습니다.`, 'success');
            } else {
                console.log(`[AutoSave] ${stageConfig.name} 데이터가 자동으로 저장되었습니다.`);
            }
            return result;
        } catch (error) {
            console.error(`${stage} 저장 오류:`, error);
            if (!silent) {
                this.showNotification(`${stageConfig.name} 저장에 실패했습니다.`, 'error');
            }
            return false;
        }
    },

    /**
     * Stage 데이터 불러오기 (범용)
     */
    async loadStageData(stage) {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        const stageConfig = this.getStageConfig(stage);
        if (!stageConfig) {
            console.error('Unknown stage:', stage);
            return null;
        }

        try {
            const response = await fetch(
                `${this.API_BASE}/framework/projects/${this.currentProjectId}/${stageConfig.endpoint}`
            );

            if (!response.ok) throw new Error(`${stageConfig.name} 로드 실패`);

            const data = await response.json();

            // 폼에 데이터 채우기
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
     * Stage 설정 가져오기
     */
    getStageConfig(stage) {
        const configs = {
            // Stage 1
            'stage1-maturity': {
                name: 'AI 성숙도 진단',
                endpoint: 'stage1/maturity-assessment',
                collectData: () => this.collectMaturityData(),
                populateForm: (data) => this.populateMaturityForm(data)
            },
            'stage1-opportunities': {
                name: 'AI 기회 발굴',
                endpoint: 'stage1/opportunities',
                collectData: () => this.collectOpportunitiesData(),
                populateForm: (data) => this.populateOpportunitiesForm(data)
            },
            'stage1-roadmap': {
                name: 'AI 로드맵',
                endpoint: 'stage1/roadmap',
                collectData: () => this.collectRoadmapData(),
                populateForm: (data) => this.populateRoadmapForm(data)
            },
            // Stage 2
            'stage2-requirements': {
                name: '상세 요건 정의',
                endpoint: 'stage2/requirements',
                collectData: () => this.collectRequirementsData(),
                populateForm: (data) => this.populateRequirementsForm(data)
            },
            'stage2-architecture': {
                name: '아키텍처 설계',
                endpoint: 'stage2/architecture',
                collectData: () => this.collectArchitectureData(),
                populateForm: (data) => this.populateArchitectureForm(data)
            },
            'stage2-governance': {
                name: '거버넌스 체계',
                endpoint: 'stage2/governance',
                collectData: () => this.collectGovernanceData(),
                populateForm: (data) => this.populateGovernanceForm(data)
            },
            // Stage 3
            'stage3-poc': {
                name: 'PoC 계획',
                endpoint: 'stage3/poc',
                collectData: () => this.collectPocData(),
                populateForm: (data) => this.populatePocForm(data)
            },
            'stage3-platform': {
                name: '플랫폼 구축',
                endpoint: 'stage3/platform',
                collectData: () => this.collectPlatformData(),
                populateForm: (data) => this.populatePlatformForm(data)
            },
            'stage3-integration': {
                name: '시스템 통합',
                endpoint: 'stage3/integration',
                collectData: () => this.collectIntegrationData(),
                populateForm: (data) => this.populateIntegrationForm(data)
            },
            // Stage 4
            'stage4-pilot': {
                name: '파일럿 계획',
                endpoint: 'stage4/pilot',
                collectData: () => this.collectPilotData(),
                populateForm: (data) => this.populatePilotForm(data)
            },
            'stage4-change': {
                name: '변화 관리',
                endpoint: 'stage4/change-management',
                collectData: () => this.collectChangeManagementData(),
                populateForm: (data) => this.populateChangeManagementForm(data)
            },
            'stage4-scale': {
                name: '확산 계획',
                endpoint: 'stage4/scale',
                collectData: () => this.collectScaleData(),
                populateForm: (data) => this.populateScaleForm(data)
            },
            // Stage 5
            'stage5-monitoring': {
                name: '모니터링 설정',
                endpoint: 'stage5/monitoring',
                collectData: () => this.collectMonitoringData(),
                populateForm: (data) => this.populateMonitoringForm(data)
            },
            'stage5-improvement': {
                name: '개선 계획',
                endpoint: 'stage5/improvement',
                collectData: () => this.collectImprovementData(),
                populateForm: (data) => this.populateImprovementForm(data)
            },
            'stage5-governance-review': {
                name: '거버넌스 검토',
                endpoint: 'stage5/governance-review',
                collectData: () => this.collectGovernanceReviewData(),
                populateForm: (data) => this.populateGovernanceReviewForm(data)
            }
        };

        return configs[stage];
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
                // camelCase 변환
                const key = subStage.replace(/-([a-z])/g, (g) => g[1].toUpperCase());
                this.workflowStatus[stageNum][key] = completed;
                this.renderWorkflowProgress();
            }
        }
    },

    // =========================================================================
    // 폼 데이터 수집 함수들
    // =========================================================================

    collectMaturityData() {
        return {
            strategy: {
                ai_vision_clarity: this.getInputValue('maturity_strategy_vision', 'number') || 3,
                ai_investment_management: this.getInputValue('maturity_strategy_investment', 'number') || 3,
                usecase_portfolio_management: this.getInputValue('maturity_strategy_portfolio', 'number') || 3,
                ai_roi_measurement: this.getInputValue('maturity_strategy_roi', 'number') || 3
            },
            organization: {
                ai_organization_structure: this.getInputValue('maturity_org_structure', 'number') || 3,
                ai_talent_capability: this.getInputValue('maturity_org_talent', 'number') || 3,
                ai_training_program: this.getInputValue('maturity_org_training', 'number') || 3,
                ai_change_culture: this.getInputValue('maturity_org_culture', 'number') || 3
            },
            data_technology: {
                data_infrastructure: this.getInputValue('maturity_tech_infra', 'number') || 3,
                data_quality_governance: this.getInputValue('maturity_tech_quality', 'number') || 3,
                mlops_platform: this.getInputValue('maturity_tech_mlops', 'number') || 3,
                cloud_scalability: this.getInputValue('maturity_tech_cloud', 'number') || 3
            },
            process: {
                ai_development_methodology: this.getInputValue('maturity_proc_methodology', 'number') || 3,
                model_validation_process: this.getInputValue('maturity_proc_validation', 'number') || 3,
                ai_ethics_risk_management: this.getInputValue('maturity_proc_ethics', 'number') || 3,
                ai_monitoring_operation: this.getInputValue('maturity_proc_monitoring', 'number') || 3
            },
            notes: this.getInputValue('maturity_notes', 'string') || ''
        };
    },

    collectOpportunitiesData() {
        const opportunities = [];
        const items = document.querySelectorAll('.opportunity-item');

        items.forEach((item, index) => {
            opportunities.push({
                name: this.getInputValue(`opp_name_${index}`, 'string') || '',
                description: this.getInputValue(`opp_desc_${index}`, 'string') || '',
                business_area: this.getInputValue(`opp_area_${index}`, 'string') || '',
                priority_quadrant: this.getInputValue(`opp_priority_${index}`, 'string') || 'fill_in',
                expected_impact: this.getInputValue(`opp_impact_${index}`, 'string') || '',
                implementation_difficulty: this.getInputValue(`opp_difficulty_${index}`, 'string') || 'medium',
                estimated_timeline: this.getInputValue(`opp_timeline_${index}`, 'string') || '',
                required_resources: this.getInputValue(`opp_resources_${index}`, 'string') || ''
            });
        });

        return { opportunities };
    },

    collectRoadmapData() {
        return {
            vision: this.getInputValue('roadmap_vision', 'string') || '',
            goals: this.collectListItems('roadmap_goals'),
            kpis: this.collectListItems('roadmap_kpis'),
            phases: this.collectPhases()
        };
    },

    collectRequirementsData() {
        return {
            use_case_name: this.getInputValue('req_usecase_name', 'string') || '',
            business_requirements: this.getInputValue('req_business', 'string') || '',
            functional_requirements: this.getInputValue('req_functional', 'string') || '',
            non_functional_requirements: this.getInputValue('req_nonfunctional', 'string') || '',
            data_requirements: this.getInputValue('req_data', 'string') || '',
            constraints: this.getInputValue('req_constraints', 'string') || '',
            success_criteria: this.getInputValue('req_success', 'string') || ''
        };
    },

    collectArchitectureData() {
        return {
            data_architecture: {
                data_sources: this.getInputValue('arch_data_sources', 'string') || '',
                etl_approach: this.getInputValue('arch_etl', 'string') || '',
                storage_type: this.getInputValue('arch_storage', 'string') || '',
                processing_method: this.getInputValue('arch_processing', 'string') || ''
            },
            ml_architecture: {
                model_type: this.getInputValue('arch_model_type', 'string') || '',
                training_approach: this.getInputValue('arch_training', 'string') || '',
                deployment_method: this.getInputValue('arch_deployment', 'string') || '',
                inference_endpoint: this.getInputValue('arch_inference', 'string') || ''
            },
            tech_stack: {
                infrastructure: this.getInputValue('arch_infra', 'string') || '',
                data_layer: this.getInputValue('arch_data_layer', 'string') || '',
                ml_layer: this.getInputValue('arch_ml_layer', 'string') || '',
                serving_layer: this.getInputValue('arch_serving', 'string') || '',
                monitoring: this.getInputValue('arch_monitoring', 'string') || ''
            },
            integration_points: this.getInputValue('arch_integration', 'string') || ''
        };
    },

    collectGovernanceData() {
        return {
            privacy: {
                data_protection: this.getInputValue('gov_privacy_protection', 'string') || '',
                minimization: this.getInputValue('gov_privacy_minimization', 'string') || '',
                retention_policy: this.getInputValue('gov_privacy_retention', 'string') || '',
                consent_management: this.getInputValue('gov_privacy_consent', 'string') || ''
            },
            ethics: {
                bias_detection: this.getInputValue('gov_ethics_bias', 'string') || '',
                fairness_evaluation: this.getInputValue('gov_ethics_fairness', 'string') || '',
                transparency: this.getInputValue('gov_ethics_transparency', 'string') || '',
                accountability: this.getInputValue('gov_ethics_accountability', 'string') || ''
            },
            compliance: {
                gdpr_compliance: this.getInputValue('gov_compliance_gdpr', 'string') || '',
                industry_regulations: this.getInputValue('gov_compliance_industry', 'string') || '',
                audit_framework: this.getInputValue('gov_compliance_audit', 'string') || '',
                documentation: this.getInputValue('gov_compliance_docs', 'string') || ''
            },
            notes: this.getInputValue('gov_notes', 'string') || ''
        };
    },

    collectPocData() {
        return {
            poc_name: this.getInputValue('poc_name', 'string') || '',
            objectives: this.getInputValue('poc_objectives', 'string') || '',
            scope: this.getInputValue('poc_scope', 'string') || '',
            success_metrics: this.getInputValue('poc_metrics', 'string') || '',
            timeline: this.getInputValue('poc_timeline', 'string') || '',
            resources: this.getInputValue('poc_resources', 'string') || '',
            risks: this.getInputValue('poc_risks', 'string') || ''
        };
    },

    collectPlatformData() {
        return {
            components: {
                data_pipeline: this.getInputValue('platform_pipeline', 'string') || '',
                feature_store: this.getInputValue('platform_feature', 'string') || '',
                model_registry: this.getInputValue('platform_registry', 'string') || '',
                serving_infra: this.getInputValue('platform_serving', 'string') || '',
                monitoring: this.getInputValue('platform_monitoring', 'string') || ''
            },
            infrastructure: this.getInputValue('platform_infra', 'string') || '',
            security_config: this.getInputValue('platform_security', 'string') || '',
            scalability_plan: this.getInputValue('platform_scalability', 'string') || ''
        };
    },

    collectIntegrationData() {
        return {
            target_systems: this.getInputValue('integration_systems', 'string') || '',
            api_specifications: this.getInputValue('integration_api', 'string') || '',
            data_flow: this.getInputValue('integration_dataflow', 'string') || '',
            testing_plan: this.getInputValue('integration_testing', 'string') || ''
        };
    },

    collectPilotData() {
        return {
            pilot_name: this.getInputValue('pilot_name', 'string') || '',
            target_department: this.getInputValue('pilot_department', 'string') || '',
            pilot_scope: this.getInputValue('pilot_scope', 'string') || '',
            duration: this.getInputValue('pilot_duration', 'string') || '',
            success_criteria: this.getInputValue('pilot_success', 'string') || '',
            support_plan: this.getInputValue('pilot_support', 'string') || ''
        };
    },

    collectChangeManagementData() {
        return {
            awareness: {
                communication_plan: this.getInputValue('change_comm', 'string') || '',
                stakeholder_engagement: this.getInputValue('change_stakeholder', 'string') || '',
                benefit_messaging: this.getInputValue('change_benefit', 'string') || ''
            },
            capability: {
                training_program: this.getInputValue('change_training', 'string') || '',
                skill_development: this.getInputValue('change_skill', 'string') || '',
                certification: this.getInputValue('change_cert', 'string') || ''
            },
            engagement: {
                champion_program: this.getInputValue('change_champion', 'string') || '',
                feedback_mechanism: this.getInputValue('change_feedback', 'string') || '',
                incentive_program: this.getInputValue('change_incentive', 'string') || ''
            },
            success_sharing: {
                success_metrics: this.getInputValue('change_metrics', 'string') || '',
                sharing_platform: this.getInputValue('change_platform', 'string') || '',
                recognition_program: this.getInputValue('change_recognition', 'string') || ''
            },
            notes: this.getInputValue('change_notes', 'string') || ''
        };
    },

    collectScaleData() {
        return {
            rollout_phases: this.collectRolloutPhases(),
            target_coverage: this.getInputValue('scale_coverage', 'string') || '',
            timeline: this.getInputValue('scale_timeline', 'string') || '',
            resource_plan: this.getInputValue('scale_resources', 'string') || '',
            risk_mitigation: this.getInputValue('scale_risks', 'string') || ''
        };
    },

    collectMonitoringData() {
        return {
            metrics: {
                technical_metrics: this.getInputValue('monitor_tech_metrics', 'string') || '',
                business_metrics: this.getInputValue('monitor_biz_metrics', 'string') || '',
                model_metrics: this.getInputValue('monitor_model_metrics', 'string') || ''
            },
            alert_thresholds: this.getInputValue('monitor_thresholds', 'string') || '',
            dashboard_config: this.getInputValue('monitor_dashboard', 'string') || '',
            reporting_frequency: this.getInputValue('monitor_frequency', 'string') || ''
        };
    },

    collectImprovementData() {
        return {
            improvement_cycle: this.getInputValue('improve_cycle', 'string') || '',
            feedback_sources: this.getInputValue('improve_feedback', 'string') || '',
            prioritization_criteria: this.getInputValue('improve_priority', 'string') || '',
            experiment_framework: this.getInputValue('improve_experiment', 'string') || '',
            success_metrics: this.getInputValue('improve_metrics', 'string') || ''
        };
    },

    collectGovernanceReviewData() {
        return {
            review_frequency: this.getInputValue('govreview_frequency', 'string') || '',
            review_scope: this.getInputValue('govreview_scope', 'string') || '',
            audit_checklist: this.getInputValue('govreview_checklist', 'string') || '',
            compliance_updates: this.getInputValue('govreview_compliance', 'string') || '',
            policy_revisions: this.getInputValue('govreview_policy', 'string') || ''
        };
    },

    // =========================================================================
    // 폼 데이터 채우기 함수들
    // =========================================================================

    populateMaturityForm(data) {
        if (!data) return;

        // 데이터 구조 확인: scores.strategy.items 형식 또는 strategy 형식 둘 다 지원
        const getItems = (category) => {
            if (data.scores && data.scores[category]) {
                return data.scores[category].items || data.scores[category];
            }
            return data[category] || {};
        };

        // Strategy (전략 및 비전) - HTML ID: s1_vision, s1_investment, s1_portfolio, s1_roi
        const strategy = getItems('strategy');
        this.setInputValue('s1_vision', strategy.ai_vision_clarity);
        this.setInputValue('s1_investment', strategy.ai_investment_management);
        this.setInputValue('s1_portfolio', strategy.usecase_portfolio_management);
        this.setInputValue('s1_roi', strategy.ai_roi_measurement);

        // Organization (조직 및 역량) - HTML ID: s1_org, s1_talent, s1_training, s1_culture
        const organization = getItems('organization');
        this.setInputValue('s1_org', organization.ai_organization_structure);
        this.setInputValue('s1_talent', organization.ai_talent_capability);
        this.setInputValue('s1_training', organization.ai_training_program);
        this.setInputValue('s1_culture', organization.ai_change_culture);

        // Data & Technology (데이터 및 기술) - HTML ID: s1_infra, s1_quality, s1_mlops, s1_cloud
        const dataTech = getItems('data_technology');
        this.setInputValue('s1_infra', dataTech.data_infrastructure);
        this.setInputValue('s1_quality', dataTech.data_quality_governance);
        this.setInputValue('s1_mlops', dataTech.mlops_platform);
        this.setInputValue('s1_cloud', dataTech.cloud_scalability);

        // Process (프로세스 및 거버넌스) - HTML ID: s1_method, s1_validation, s1_ethics, s1_monitoring
        const process = getItems('process');
        this.setInputValue('s1_method', process.ai_development_methodology);
        this.setInputValue('s1_validation', process.model_validation_process);
        this.setInputValue('s1_ethics', process.ai_ethics_risk_management);
        this.setInputValue('s1_monitoring', process.ai_monitoring_operation);

        this.setInputValue('s1_notes', data.notes);

        // AI 분석 결과가 있으면 표시
        if (data.analysis_result) {
            this.displayMaturityAnalysisResult(data.analysis_result);
        }
    },

    /**
     * 성숙도 분석 결과 표시
     */
    displayMaturityAnalysisResult(result) {
        const resultContainer = document.getElementById('maturityAnalysisResult');
        if (resultContainer && result) {
            resultContainer.innerHTML = `
                <div class="card mt-3">
                    <div class="card-header bg-info text-white">
                        <i class="bi bi-robot me-2"></i>AI 분석 결과
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="white-space: pre-wrap;">${typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
                    </div>
                </div>
            `;
            resultContainer.style.display = 'block';
        }
    },

    populateOpportunitiesForm(data) {
        // 기회 발굴 폼에 데이터 채우기 - 동적 리스트
        if (!data) return;

        // 데이터가 배열인 경우와 객체인 경우 모두 처리
        let opportunities = Array.isArray(data) ? data : (data.opportunities || []);
        if (opportunities.length === 0) return;

        const container = document.getElementById('opportunityList');
        if (!container) return;

        // 기존 항목 제거
        container.innerHTML = '';

        // 전역 opportunityCounter 리셋
        if (typeof window.opportunityCounter !== 'undefined') {
            window.opportunityCounter = 0;
        }

        // 각 기회 항목 추가
        opportunities.forEach((opp, index) => {
            const oppId = index + 1;
            if (typeof window.opportunityCounter !== 'undefined') {
                window.opportunityCounter = oppId;
            }

            // 저장된 데이터 형식에 따른 필드 매핑
            const oppName = opp.name || '';
            const oppDesc = opp.description || '';
            // implementation_difficulty를 complexity로 매핑
            const difficulty = opp.implementation_difficulty || opp.complexity || 'medium';
            const complexityMap = { '낮음': 'low', '중': 'medium', '중간': 'medium', '높음': 'high' };
            const oppComplexity = complexityMap[difficulty] || difficulty;
            // priority_quadrant을 roi_potential로 매핑
            const quadrant = opp.priority_quadrant || opp.roi_potential || 'high';
            const roiMap = { 'quick_win': 'high', 'strategic': 'high', 'fill_in': 'medium', 'thankless': 'low' };
            const oppRoi = roiMap[quadrant] || quadrant;

            const opportunityHtml = `
                <div class="card mb-3 opportunity-item" id="opportunity-${oppId}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h6 class="card-title mb-0">기회 #${oppId}</h6>
                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeOpportunity(${oppId})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">기회/과제명</label>
                                <input type="text" class="form-control" id="opp-name-${oppId}" placeholder="AI 도입 기회명" value="${this.escapeHtml(oppName)}">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">ROI 잠재력</label>
                                <select class="form-select" id="opp-roi-${oppId}">
                                    <option value="low" ${oppRoi === 'low' ? 'selected' : ''}>낮음</option>
                                    <option value="medium" ${oppRoi === 'medium' ? 'selected' : ''}>중간</option>
                                    <option value="high" ${oppRoi === 'high' ? 'selected' : ''}>높음</option>
                                    <option value="very_high" ${oppRoi === 'very_high' ? 'selected' : ''}>매우 높음</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">구현 복잡도</label>
                                <select class="form-select" id="opp-complexity-${oppId}">
                                    <option value="low" ${oppComplexity === 'low' ? 'selected' : ''}>낮음</option>
                                    <option value="medium" ${oppComplexity === 'medium' ? 'selected' : ''}>중간</option>
                                    <option value="high" ${oppComplexity === 'high' ? 'selected' : ''}>높음</option>
                                </select>
                            </div>
                            <div class="col-12">
                                <label class="form-label">설명</label>
                                <textarea class="form-control" id="opp-desc-${oppId}" rows="2" placeholder="기회/과제에 대한 설명">${this.escapeHtml(oppDesc)}</textarea>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', opportunityHtml);
        });

        // AI 분석 결과가 있으면 표시
        if (data.analysis_result) {
            this.displayOpportunityAnalysisResult(data.analysis_result);
        }
    },

    /**
     * 기회 발굴 분석 결과 표시
     */
    displayOpportunityAnalysisResult(result) {
        const resultContainer = document.getElementById('opportunityAnalysisResult');
        if (resultContainer && result) {
            resultContainer.innerHTML = `
                <div class="card mt-3">
                    <div class="card-header bg-success text-white">
                        <i class="bi bi-robot me-2"></i>AI 분석 결과
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="white-space: pre-wrap;">${typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
                    </div>
                </div>
            `;
            resultContainer.style.display = 'block';
        }
    },

    /**
     * HTML 이스케이프 유틸리티
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    populateRoadmapForm(data) {
        if (!data) return;

        // 비전 - rm_vision 또는 roadmap_vision
        this.setInputValue('rm_vision', data.vision);
        this.setInputValue('roadmap_vision', data.vision);

        // 전략적 목표 (strategicGoals) - 저장된 형식: {id, name, target, timeline}
        if (data.goals && Array.isArray(data.goals)) {
            const goalsContainer = document.getElementById('strategicGoals');
            if (goalsContainer) {
                goalsContainer.innerHTML = '';
                data.goals.forEach(goal => {
                    // goal이 객체이면 name을 사용, 문자열이면 그대로 사용
                    const goalText = typeof goal === 'object'
                        ? `${goal.name || ''} - ${goal.target || ''}`
                        : goal;
                    const html = `
                        <div class="input-group mb-2">
                            <input type="text" class="form-control" placeholder="전략적 목표" value="${this.escapeHtml(goalText)}">
                            <button class="btn btn-outline-danger" type="button" onclick="removeGoal(this)"><i class="bi bi-x"></i></button>
                        </div>
                    `;
                    goalsContainer.insertAdjacentHTML('beforeend', html);
                });
            }
        }

        // KPI 목록 (kpiList) - 저장된 형식: {id, name, current, target, unit}
        if (data.kpis && Array.isArray(data.kpis)) {
            const kpiContainer = document.getElementById('kpiList');
            if (kpiContainer) {
                kpiContainer.innerHTML = '';
                data.kpis.forEach(kpi => {
                    const html = `
                        <div class="row g-2 mb-2 kpi-item">
                            <div class="col-md-4">
                                <input type="text" class="form-control" placeholder="KPI 명" value="${this.escapeHtml(kpi.name || kpi.metric || '')}">
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" placeholder="현재값" value="${this.escapeHtml(kpi.current || kpi.current_value || '')}">
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" placeholder="목표값" value="${this.escapeHtml(kpi.target || kpi.target_value || '')}">
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-outline-danger w-100" type="button" onclick="removeKpi(this)"><i class="bi bi-x"></i></button>
                            </div>
                        </div>
                    `;
                    kpiContainer.insertAdjacentHTML('beforeend', html);
                });
            }
        }

        // 단계별 로드맵 - 저장된 형식: [{id, name, activities[], budget}]
        if (data.phases && Array.isArray(data.phases)) {
            // 기존 phases 배열을 3단계로 분류
            data.phases.forEach((phase, index) => {
                let containerId = 'quickWins';
                if (index === 1) containerId = 'strategicItems';
                if (index >= 2) containerId = 'transformationalItems';

                const items = phase.activities || [];
                this.populateRoadmapPhase(containerId, items);
            });
        } else if (data.phases && typeof data.phases === 'object') {
            // 객체 형태인 경우 (quick_win, strategic, transformational)
            if (data.phases.quick_win || data.phases.quickWins) {
                this.populateRoadmapPhase('quickWins', data.phases.quick_win || data.phases.quickWins);
            }
            if (data.phases.strategic || data.phases.strategicItems) {
                this.populateRoadmapPhase('strategicItems', data.phases.strategic || data.phases.strategicItems);
            }
            if (data.phases.transformational || data.phases.transformationalItems) {
                this.populateRoadmapPhase('transformationalItems', data.phases.transformational || data.phases.transformationalItems);
            }
        }

        // AI 분석 결과가 있으면 표시
        if (data.analysis_result) {
            this.displayRoadmapAnalysisResult(data.analysis_result);
        }
    },

    /**
     * 로드맵 단계별 항목 채우기
     */
    populateRoadmapPhase(containerId, items) {
        if (!items || !Array.isArray(items)) return;

        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        items.forEach(item => {
            const itemName = typeof item === 'string' ? item : (item.name || item.task || '');
            const html = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control form-control-sm" placeholder="과제명" value="${this.escapeHtml(itemName)}">
                    <button class="btn btn-outline-danger btn-sm" type="button" onclick="removeItem(this)"><i class="bi bi-x"></i></button>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    },

    /**
     * 로드맵 분석 결과 표시
     */
    displayRoadmapAnalysisResult(result) {
        const resultContainer = document.getElementById('roadmapAnalysisResult');
        if (resultContainer && result) {
            resultContainer.innerHTML = `
                <div class="card mt-3">
                    <div class="card-header bg-primary text-white">
                        <i class="bi bi-robot me-2"></i>AI 분석 결과
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="white-space: pre-wrap;">${typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
                    </div>
                </div>
            `;
            resultContainer.style.display = 'block';
        }
    },

    populateRequirementsForm(data) {
        if (!data) return;

        // Stage 2 요건 정의 - HTML의 실제 ID 사용
        this.setInputValue('req_usecase', data.use_case || data.use_case_name);
        this.setInputValue('req_objective', data.objective || data.business_requirements);
        this.setInputValue('req_input', data.input_data || data.data_requirements);
        this.setInputValue('req_output', data.output_format);
        this.setInputValue('req_accuracy', data.accuracy || data.target_accuracy);
        this.setInputValue('req_latency', data.latency || data.target_latency);
        this.setInputValue('req_throughput', data.throughput || data.target_throughput);
        this.setInputValue('req_integration', data.integration_systems || data.constraints);
        this.setInputValue('req_security', data.security_requirements || data.success_criteria);

        // 성공 기준 (successCriteria) 동적 리스트
        if (data.success_criteria && Array.isArray(data.success_criteria)) {
            const container = document.getElementById('successCriteria');
            if (container) {
                container.innerHTML = '';
                data.success_criteria.forEach(criteria => {
                    const html = `
                        <div class="input-group mb-2">
                            <input type="text" class="form-control" placeholder="예: 정확도 95% 이상" value="${this.escapeHtml(criteria)}">
                            <button class="btn btn-outline-danger" type="button" onclick="removeItem(this)"><i class="bi bi-x"></i></button>
                        </div>
                    `;
                    container.insertAdjacentHTML('beforeend', html);
                });
            }
        }
    },

    populateArchitectureForm(data) {
        if (!data) return;

        // 데이터 아키텍처 - HTML의 실제 ID 사용
        this.setInputValue('arch_storage', data.data_storage || (data.data_architecture && data.data_architecture.storage_type));
        this.setInputValue('arch_pipeline', data.data_pipeline || (data.data_architecture && data.data_architecture.etl_approach));

        // ML 아키텍처
        this.setInputValue('arch_training', data.training_approach || (data.ml_architecture && data.ml_architecture.training_approach));
        this.setInputValue('arch_serving', data.serving_method || (data.ml_architecture && data.ml_architecture.deployment_method));
    },

    populateGovernanceForm(data) {
        if (!data) return;

        // 데이터 프라이버시 - 체크박스
        if (data.privacy || data.data_privacy) {
            const privacy = data.privacy || data.data_privacy;
            this.setCheckboxValue('gov_anonymization', privacy.anonymization);
            this.setCheckboxValue('gov_consent', privacy.consent || privacy.consent_management);
            this.setCheckboxValue('gov_retention', privacy.retention || privacy.retention_policy);
        }

        // 공정성 - 체크박스
        if (data.fairness || data.ethics) {
            const fairness = data.fairness || data.ethics;
            this.setCheckboxValue('gov_bias_test', fairness.bias_test || fairness.bias_detection);
            this.setCheckboxValue('gov_fairness', fairness.fairness_check || fairness.fairness_evaluation);
            this.setCheckboxValue('gov_diverse', fairness.diverse_data);
        }

        // 설명가능성
        if (data.explainability) {
            this.setInputValue('gov_xai_level', data.explainability.xai_level);
            this.setCheckboxValue('gov_decision_log', data.explainability.decision_logging);
        }

        // 추적가능성
        if (data.traceability) {
            this.setCheckboxValue('gov_model_version', data.traceability.model_versioning);
            this.setCheckboxValue('gov_data_lineage', data.traceability.data_lineage);
            this.setCheckboxValue('gov_audit_log', data.traceability.audit_log);
        }

        this.setInputValue('gov_notes', data.notes);
    },

    populatePocForm(data) {
        if (!data) return;

        // PoC 정보 - HTML의 실제 ID 사용
        this.setInputValue('poc_usecase', data.poc_usecase || data.poc_name);
        this.setInputValue('poc_duration', data.duration || data.poc_duration);
        this.setInputValue('poc_scope', data.scope);

        // 단계별 기간
        if (data.phases) {
            this.setInputValue('poc_w1', data.phases.data_preparation || data.phases.w1);
            this.setInputValue('poc_w2', data.phases.model_development || data.phases.w2);
            this.setInputValue('poc_w3', data.phases.testing || data.phases.w3);
            this.setInputValue('poc_w4', data.phases.evaluation || data.phases.w4);
        }

        // 리소스
        if (data.resources) {
            this.setInputValue('poc_ds', data.resources.data_scientist || data.resources.ds);
            this.setInputValue('poc_mle', data.resources.ml_engineer || data.resources.mle);
            this.setInputValue('poc_domain', data.resources.domain_expert || data.resources.domain);
        }
    },

    populatePlatformForm(data) {
        if (!data) return;

        // MLOps 플랫폼 컴포넌트
        if (data.components) {
            this.setInputValue('platform_pipeline', data.components.data_pipeline);
            this.setInputValue('platform_feature', data.components.feature_store);
            this.setInputValue('platform_registry', data.components.model_registry);
            this.setInputValue('platform_serving', data.components.serving_infra);
            this.setInputValue('platform_monitoring', data.components.monitoring);
        }

        this.setInputValue('platform_infra', data.infrastructure);
        this.setInputValue('platform_security', data.security_config);
        this.setInputValue('platform_scalability', data.scalability_plan);
    },

    populateIntegrationForm(data) {
        if (!data) return;
        this.setInputValue('integration_systems', data.target_systems);
        this.setInputValue('integration_api', data.api_specifications);
        this.setInputValue('integration_dataflow', data.data_flow);
        this.setInputValue('integration_testing', data.testing_plan);
    },

    populatePilotForm(data) {
        if (!data) return;

        // 파일럿 정보 - HTML의 실제 ID 사용
        this.setInputValue('pilot_dept', data.pilot_dept || data.target_department);
        this.setInputValue('pilot_duration', data.pilot_duration || data.duration);
        this.setInputValue('pilot_training', data.training_plan);
        this.setInputValue('pilot_support', data.support_plan);

        // 파일럿 체크리스트
        if (data.checklist) {
            this.setCheckboxValue('pilot_baseline', data.checklist.baseline);
            this.setCheckboxValue('pilot_feedback', data.checklist.feedback);
            this.setCheckboxValue('pilot_metrics', data.checklist.metrics);
            this.setCheckboxValue('pilot_issues', data.checklist.issues);
        }
    },

    populateChangeManagementForm(data) {
        if (!data) return;

        // 변화관리 체크리스트
        if (data.awareness) {
            this.setCheckboxValue('change_exec', data.awareness.executive_sponsorship);
            this.setCheckboxValue('change_comm', data.awareness.communication);
            this.setCheckboxValue('change_benefit', data.awareness.benefit_messaging);
        }

        if (data.training) {
            this.setCheckboxValue('change_basic', data.training.basic_training);
            this.setCheckboxValue('change_advanced', data.training.advanced_training);
            this.setCheckboxValue('change_cert', data.training.certification);
        }

        if (data.support) {
            this.setCheckboxValue('change_helpdesk', data.support.helpdesk);
            this.setCheckboxValue('change_champion', data.support.champion);
            this.setCheckboxValue('change_feedback', data.support.feedback);
        }

        this.setInputValue('change_notes', data.notes);
    },

    populateScaleForm(data) {
        if (!data) return;

        // 확산 계획 - HTML의 실제 ID 사용
        this.setInputValue('scale_infra', data.infra_expansion || data.infrastructure);
        this.setInputValue('scale_optimize', data.optimization || data.model_optimization);
    },

    populateMonitoringForm(data) {
        if (!data) return;

        // 모니터링 메트릭 - 체크박스 형태일 수 있음
        if (data.metrics) {
            this.setCheckboxValue('monitor_latency', data.metrics.latency);
            this.setCheckboxValue('monitor_throughput', data.metrics.throughput);
            this.setCheckboxValue('monitor_accuracy', data.metrics.accuracy);
            this.setCheckboxValue('monitor_drift', data.metrics.drift);
        }

        // 비즈니스 메트릭
        if (data.business_metrics) {
            this.setCheckboxValue('monitor_cost', data.business_metrics.cost_saving);
            this.setCheckboxValue('monitor_productivity', data.business_metrics.productivity);
            this.setCheckboxValue('monitor_quality', data.business_metrics.quality);
        }

        this.setInputValue('monitor_thresholds', data.alert_thresholds);
        this.setInputValue('monitor_dashboard', data.dashboard_config);
        this.setInputValue('monitor_frequency', data.reporting_frequency);
    },

    populateImprovementForm(data) {
        if (!data) return;

        // 지속적 개선 - HTML의 실제 ID 사용
        this.setInputValue('improve_retrain', data.retrain_cycle || data.improvement_cycle);
        this.setInputValue('improve_threshold', data.retrain_threshold || data.threshold);
        this.setInputValue('improve_doc', data.documentation || data.feedback_sources);
    },

    populateGovernanceReviewForm(data) {
        if (!data) return;

        // 거버넌스 검토 - HTML의 실제 ID 사용
        this.setInputValue('gov_audit_cycle', data.audit_cycle || data.review_frequency);
        this.setInputValue('gov_ethics_committee', data.ethics_committee || data.review_scope);
        this.setInputValue('gov_incident', data.incident_response || data.audit_checklist);
    },

    populateCompanyProfileForm(data) {
        if (!data) return;

        this.setInputValue('companyName', data.name);
        this.setInputValue('industry', data.industry);
        this.setInputValue('companySize', data.company_size);

        if (data.it_infrastructure) {
            this.setCheckboxValue('hasCloud', data.it_infrastructure.has_cloud);
            this.setCheckboxValue('hasDataWarehouse', data.it_infrastructure.has_data_warehouse);
            this.setCheckboxValue('gpuAvailable', data.it_infrastructure.gpu_available);
        }

        if (data.data_assets) {
            this.setInputValue('dataVolume', data.data_assets.data_volume_tb);
            this.setInputValue('dataQuality', data.data_assets.data_quality_score);
            this.setCheckboxValue('hasDataGovernance', data.data_assets.has_data_governance);
        }

        if (data.human_resources) {
            this.setInputValue('totalEmployees', data.human_resources.total_employees);
            this.setInputValue('dataScientists', data.human_resources.data_scientist_count);
            this.setInputValue('mlEngineers', data.human_resources.ml_engineer_count);
            this.setInputValue('aiProjects', data.human_resources.ai_experience_projects);
        }

        if (data.financial_resources) {
            this.setInputValue('annualRevenue', data.financial_resources.annual_revenue_billion);
            this.setInputValue('aiBudget', data.financial_resources.ai_investment_budget);
        }

        if (data.organizational_readiness) {
            this.setInputValue('executiveSupport', data.organizational_readiness.executive_support);
            this.setInputValue('changeManagement', data.organizational_readiness.change_management_capability);
            this.setInputValue('innovationCulture', data.organizational_readiness.innovation_culture);
        }
    },

    // =========================================================================
    // 시나리오 및 보고서
    // =========================================================================

    /**
     * 시나리오 분석 실행
     * @param {string|object} scenarioOrParams - 시나리오 타입 문자열 또는 파라미터 객체
     */
    async generateScenarios(scenarioOrParams = 'balanced') {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        // 파라미터가 객체인 경우와 문자열인 경우 처리
        let selectedScenario = 'balanced';
        let analysisParameters = {};

        if (typeof scenarioOrParams === 'string') {
            selectedScenario = scenarioOrParams;
        } else if (typeof scenarioOrParams === 'object' && scenarioOrParams !== null) {
            // 객체에서 시나리오 타입 추출 (risk_appetite를 기준으로 매핑)
            const riskMap = { 'low': 'conservative', 'medium': 'balanced', 'high': 'aggressive' };
            selectedScenario = riskMap[scenarioOrParams.risk_appetite] || 'balanced';
            analysisParameters = scenarioOrParams;
        }

        try {
            this.showLoading('시나리오 분석을 수행하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${this.currentProjectId}/scenarios/analyze`,
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
            this.hideLoading();
            this.showNotification('시나리오 분석이 완료되었습니다.', 'success');

            // 결과 표시
            this.displayScenarioResults(data.analysis);

            return data;
        } catch (error) {
            this.hideLoading();
            console.error('시나리오 분석 오류:', error);
            this.showNotification('시나리오 분석에 실패했습니다.', 'error');
            return null;
        }
    },

    /**
     * 시나리오 결과 표시
     */
    displayScenarioResults(analysis) {
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

        // Bootstrap 모달 열기
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    },

    /**
     * 최종 보고서 생성
     */
    async generateReport(options = {}) {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        try {
            this.showLoading('보고서를 생성하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/framework/projects/${this.currentProjectId}/report/generate`,
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
            this.hideLoading();
            this.showNotification('보고서가 생성되었습니다.', 'success');

            // 보고서 결과 표시
            this.displayReportResults(data.report);

            return data;
        } catch (error) {
            this.hideLoading();
            console.error('보고서 생성 오류:', error);
            this.showNotification('보고서 생성에 실패했습니다.', 'error');
            return null;
        }
    },

    /**
     * 보고서 결과 표시
     */
    displayReportResults(report) {
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
                <a href="${this.API_BASE}/framework/projects/${this.currentProjectId}/report/download"
                   target="_blank" class="btn btn-primary">
                    <i class="bi bi-download me-2"></i>HTML로 다운로드
                </a>
            </div>
        `;

        // Bootstrap 모달 열기
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
    async runFullAnalysis() {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return null;
        }

        if (!confirm('전체 AI 분석을 실행하시겠습니까? 이 작업은 시간이 걸릴 수 있습니다.')) {
            return null;
        }

        try {
            this.showLoading('AI 에이전트가 전체 분석을 수행하고 있습니다...');

            const response = await fetch(
                `${this.API_BASE}/projects/${this.currentProjectId}/run-full-consultation?auto_approve=false`,
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
            this.hideLoading();

            // 프로젝트 데이터 다시 로드
            await this.loadProject(this.currentProjectId);

            this.showNotification('AI 분석이 완료되었습니다.', 'success');
            return data;
        } catch (error) {
            this.hideLoading();
            console.error('전체 분석 오류:', error);
            const errorMessage = error.message || 'AI 분석에 실패했습니다.';
            this.showNotification(`AI 분석 실패: ${errorMessage}`, 'error');
            return null;
        }
    },

    /**
     * 현재 페이지/스테이지 저장
     */
    async saveCurrentStage() {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return;
        }

        // 현재 활성화된 탭/메뉴 확인
        const activeMenu = document.querySelector('.sidebar-menu a.active, .nav-link.active[data-bs-toggle="tab"]');
        let stageName = '현재 페이지';

        // Stage 저장 함수 호출 시도
        if (typeof saveStage1Data === 'function') {
            try {
                await saveStage1Data();
                return;
            } catch (e) { }
        }
        if (typeof saveStage2Data === 'function') {
            try {
                await saveStage2Data();
                return;
            } catch (e) { }
        }

        // 일반 저장 알림
        this.showNotification('저장할 데이터가 없습니다.', 'info');
    },

    // =========================================================================
    // 유틸리티 함수들
    // =========================================================================

    getInputValue(id, type = 'string') {
        const el = document.getElementById(id);
        if (!el) return type === 'number' ? 0 : '';

        if (type === 'number') {
            return parseFloat(el.value) || 0;
        } else if (type === 'boolean') {
            return el.checked || false;
        }
        return el.value || '';
    },

    setInputValue(id, value) {
        const el = document.getElementById(id);
        if (el && value !== undefined && value !== null) {
            el.value = value;

            // Range 슬라이더의 경우 표시 값도 업데이트
            const display = document.getElementById(id + 'Value');
            if (display) display.textContent = value;
        }
    },

    setCheckboxValue(id, value) {
        const el = document.getElementById(id);
        if (el) el.checked = !!value;
    },

    collectListItems(containerId) {
        const items = [];
        const container = document.getElementById(containerId);
        if (!container) return items;

        container.querySelectorAll('.list-item-input').forEach(input => {
            if (input.value.trim()) {
                items.push(input.value.trim());
            }
        });
        return items;
    },

    collectPhases() {
        const phases = [];
        document.querySelectorAll('.phase-item').forEach((item, index) => {
            phases.push({
                phase_name: this.getInputValue(`phase_name_${index}`, 'string'),
                duration: this.getInputValue(`phase_duration_${index}`, 'string'),
                key_tasks: this.getInputValue(`phase_tasks_${index}`, 'string'),
                expected_investment: this.getInputValue(`phase_investment_${index}`, 'string'),
                expected_outcome: this.getInputValue(`phase_outcome_${index}`, 'string')
            });
        });
        return phases;
    },

    collectRolloutPhases() {
        const phases = [];
        document.querySelectorAll('.rollout-phase-item').forEach((item, index) => {
            phases.push({
                phase_name: this.getInputValue(`rollout_name_${index}`, 'string'),
                target_scope: this.getInputValue(`rollout_scope_${index}`, 'string'),
                timeline: this.getInputValue(`rollout_timeline_${index}`, 'string'),
                resources: this.getInputValue(`rollout_resources_${index}`, 'string')
            });
        });
        return phases;
    },

    formatDate(dateString) {
        if (!dateString) return '-';
        try {
            const date = new Date(dateString);
            return date.toLocaleDateString('ko-KR', {
                year: 'numeric',
                month: '2-digit',
                day: '2-digit'
            });
        } catch {
            return dateString;
        }
    },

    showLoading(message = '처리 중입니다...') {
        const overlay = document.getElementById('loadingOverlay');
        const msgEl = document.getElementById('loadingMessage');
        if (msgEl) msgEl.textContent = message;
        if (overlay) overlay.classList.remove('hidden');
    },

    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('hidden');
    },

    showNotification(message, type = 'info') {
        // 토스트 알림 표시
        const container = document.getElementById('toastContainer') || this.createToastContainer();

        const toast = document.createElement('div');
        toast.className = `toast-notification toast-${type}`;
        toast.innerHTML = `
            <i class="bi ${this.getToastIcon(type)} me-2"></i>
            <span>${message}</span>
            <button class="toast-close" onclick="this.parentElement.remove()">
                <i class="bi bi-x"></i>
            </button>
        `;

        container.appendChild(toast);

        // 3초 후 자동 제거
        setTimeout(() => {
            if (toast.parentElement) {
                toast.classList.add('toast-fade-out');
                setTimeout(() => toast.remove(), 300);
            }
        }, 3000);
    },

    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    getToastIcon(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    },

    // =========================================================================
    // localStorage 자동 저장 시스템 구현
    // =========================================================================

    /**
     * localStorage 자동 저장 초기화
     */
    initLocalStorageAutoSave() {
        console.log('Initializing localStorage auto-save system...');

        // 모든 입력 필드에 변경 이벤트 리스너 추가
        this.bindLocalStorageEvents();

        // 주기적 자동 저장 (백업)
        setInterval(() => {
            this.saveAllFieldsToLocalStorage();
        }, this.AUTO_SAVE_INTERVAL);

        // 페이지 언로드 전 저장
        window.addEventListener('beforeunload', () => {
            this.saveAllFieldsToLocalStorage();
        });

        // 페이지 가시성 변경 시 저장 (탭 전환 시)
        document.addEventListener('visibilitychange', () => {
            if (document.visibilityState === 'hidden') {
                this.saveAllFieldsToLocalStorage();
            }
        });

        console.log('localStorage auto-save system initialized');
    },

    /**
     * 모든 입력 필드에 localStorage 저장 이벤트 바인딩
     */
    bindLocalStorageEvents() {
        // 입력 필드 선택자
        const inputSelectors = 'input:not([type="file"]):not([type="submit"]):not([type="button"]), select, textarea';

        // 기존 입력 필드에 이벤트 리스너 추가
        document.querySelectorAll(inputSelectors).forEach(el => {
            this.addLocalStorageListener(el);
        });

        // MutationObserver로 동적으로 추가되는 입력 필드 감시
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        // 추가된 노드가 입력 필드인 경우
                        if (node.matches && node.matches(inputSelectors)) {
                            this.addLocalStorageListener(node);
                        }
                        // 추가된 노드 내부의 입력 필드 검색
                        if (node.querySelectorAll) {
                            node.querySelectorAll(inputSelectors).forEach(el => {
                                this.addLocalStorageListener(el);
                            });
                        }
                    }
                });
            });
        });

        observer.observe(document.body, {
            childList: true,
            subtree: true
        });
    },

    /**
     * 개별 입력 필드에 localStorage 저장 리스너 추가
     */
    addLocalStorageListener(element) {
        // 이미 리스너가 추가된 경우 스킵
        if (element.dataset.localStorageEnabled) return;
        element.dataset.localStorageEnabled = 'true';

        const saveHandler = () => {
            this.debouncedLocalSave();
        };

        // 입력 이벤트에 따라 다른 이벤트 사용
        element.addEventListener('input', saveHandler);
        element.addEventListener('change', saveHandler);

        // 체크박스/라디오는 change 이벤트만
        if (element.type === 'checkbox' || element.type === 'radio') {
            element.removeEventListener('input', saveHandler);
        }
    },

    /**
     * 디바운스된 localStorage 저장
     */
    debouncedLocalSave() {
        if (this._localSaveTimeout) {
            clearTimeout(this._localSaveTimeout);
        }

        this.updateSaveStatus('saving');

        this._localSaveTimeout = setTimeout(() => {
            this.saveAllFieldsToLocalStorage();
        }, 500);
    },

    /**
     * 모든 입력 필드를 localStorage에 저장
     */
    saveAllFieldsToLocalStorage() {
        try {
            const formData = {};
            const timestamp = new Date().toISOString();

            // 모든 입력 필드 수집
            document.querySelectorAll('input:not([type="file"]):not([type="submit"]):not([type="button"]), select, textarea').forEach(el => {
                const id = el.id || el.name;
                if (!id) return;

                // 값 추출
                let value;
                if (el.type === 'checkbox') {
                    value = el.checked;
                } else if (el.type === 'radio') {
                    if (el.checked) {
                        value = el.value;
                    } else {
                        return; // 선택되지 않은 라디오는 스킵
                    }
                } else {
                    value = el.value;
                }

                formData[id] = {
                    value: value,
                    type: el.type || 'text',
                    tagName: el.tagName.toLowerCase()
                };
            });

            // 메타데이터 추가
            const storageData = {
                formData: formData,
                timestamp: timestamp,
                projectId: this.currentProjectId,
                url: window.location.pathname,
                fieldCount: Object.keys(formData).length
            };

            // localStorage에 저장
            const storageKey = this.STORAGE_PREFIX + 'form_data';
            localStorage.setItem(storageKey, JSON.stringify(storageData));

            // 마지막 저장 시간 업데이트
            this._lastSaveTime = timestamp;
            localStorage.setItem(this.STORAGE_PREFIX + 'last_save', timestamp);

            this.updateSaveStatus('saved');
            console.log(`[AutoSave] ${Object.keys(formData).length} fields saved at ${timestamp}`);

            return true;
        } catch (error) {
            console.error('[AutoSave] Error saving to localStorage:', error);
            this.updateSaveStatus('error');

            // localStorage 용량 초과 시 오래된 데이터 정리
            if (error.name === 'QuotaExceededError') {
                this.cleanupOldLocalStorageData();
            }
            return false;
        }
    },

    /**
     * localStorage에서 데이터 복원
     */
    restoreFromLocalStorage() {
        try {
            const storageKey = this.STORAGE_PREFIX + 'form_data';
            const savedData = localStorage.getItem(storageKey);

            if (!savedData) {
                console.log('[AutoRestore] No saved data found');
                return false;
            }

            const parsedData = JSON.parse(savedData);
            const formData = parsedData.formData;
            const savedTime = new Date(parsedData.timestamp);
            const now = new Date();

            // 24시간 이상 지난 데이터는 무시 (선택적)
            const hoursDiff = (now - savedTime) / (1000 * 60 * 60);
            if (hoursDiff > 24) {
                console.log('[AutoRestore] Saved data is older than 24 hours, skipping restore');
                return false;
            }

            let restoredCount = 0;
            let skippedCount = 0;

            // 각 필드에 값 복원
            Object.entries(formData).forEach(([id, data]) => {
                const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);

                if (!element) {
                    skippedCount++;
                    return;
                }

                // 이미 값이 있는 필드는 스킵 (서버에서 로드된 데이터 우선)
                const currentValue = element.type === 'checkbox' ? element.checked : element.value;
                if (currentValue && currentValue !== '' && currentValue !== false && currentValue !== '0') {
                    return;
                }

                // 값 복원
                if (element.type === 'checkbox') {
                    element.checked = data.value === true || data.value === 'true';
                } else if (element.type === 'radio') {
                    if (element.value === data.value) {
                        element.checked = true;
                    }
                } else {
                    element.value = data.value || '';
                }

                restoredCount++;

                // 슬라이더 표시 값 업데이트
                const display = document.getElementById(id + 'Value');
                if (display && element.type === 'range') {
                    display.textContent = element.value;
                }

                // change 이벤트 발생 (다른 리스너들이 반응하도록)
                element.dispatchEvent(new Event('change', { bubbles: true }));
            });

            console.log(`[AutoRestore] Restored ${restoredCount} fields, skipped ${skippedCount} (not found or already filled)`);

            // 복원 알림 표시
            if (restoredCount > 0) {
                this.showRestoreNotification(restoredCount, parsedData.timestamp);
            }

            return true;
        } catch (error) {
            console.error('[AutoRestore] Error restoring from localStorage:', error);
            return false;
        }
    },

    /**
     * 복원 알림 표시
     */
    showRestoreNotification(fieldCount, timestamp) {
        const savedTime = new Date(timestamp);
        const timeStr = savedTime.toLocaleString('ko-KR');

        // 알림 배너 생성
        const banner = document.createElement('div');
        banner.id = 'restoreNotificationBanner';
        banner.className = 'restore-notification-banner';
        banner.innerHTML = `
            <div class="restore-notification-content">
                <i class="bi bi-clock-history me-2"></i>
                <span><strong>${fieldCount}개</strong>의 입력 항목이 복원되었습니다 (${timeStr})</span>
                <div class="restore-notification-actions">
                    <button class="btn btn-sm btn-outline-light me-2" onclick="ProjectManager.keepRestoredData()">
                        <i class="bi bi-check-lg me-1"></i>유지
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="ProjectManager.clearRestoredData()">
                        <i class="bi bi-x-lg me-1"></i>초기화
                    </button>
                </div>
            </div>
        `;

        // 기존 배너 제거
        const existingBanner = document.getElementById('restoreNotificationBanner');
        if (existingBanner) {
            existingBanner.remove();
        }

        document.body.prepend(banner);

        // 10초 후 자동 숨김
        setTimeout(() => {
            if (banner.parentElement) {
                banner.classList.add('fade-out');
                setTimeout(() => banner.remove(), 300);
            }
        }, 10000);
    },

    /**
     * 복원된 데이터 유지
     */
    keepRestoredData() {
        const banner = document.getElementById('restoreNotificationBanner');
        if (banner) {
            banner.remove();
        }
        this.showNotification('복원된 데이터가 유지됩니다.', 'success');
    },

    /**
     * 복원된 데이터 초기화
     */
    clearRestoredData() {
        if (confirm('저장된 데이터를 모두 초기화하시겠습니까? 현재 입력된 내용이 모두 지워집니다.')) {
            // localStorage 데이터 삭제
            localStorage.removeItem(this.STORAGE_PREFIX + 'form_data');
            localStorage.removeItem(this.STORAGE_PREFIX + 'last_save');

            // 페이지 새로고침
            window.location.reload();
        }
    },

    /**
     * 저장 상태 표시 UI 생성
     */
    createSaveStatusIndicator() {
        // 저장 상태 표시 요소 생성
        const indicator = document.createElement('div');
        indicator.id = 'autoSaveIndicator';
        indicator.className = 'auto-save-indicator';
        indicator.innerHTML = `
            <span class="save-icon"></span>
            <span class="save-text">자동 저장 중...</span>
        `;

        document.body.appendChild(indicator);
        this._saveStatusElement = indicator;

        // 스타일 추가
        this.addAutoSaveStyles();

        // 초기 상태
        this.updateSaveStatus('idle');
    },

    /**
     * 저장 상태 업데이트
     */
    updateSaveStatus(status) {
        if (!this._saveStatusElement) return;

        const indicator = this._saveStatusElement;
        const icon = indicator.querySelector('.save-icon');
        const text = indicator.querySelector('.save-text');

        indicator.className = 'auto-save-indicator';

        switch (status) {
            case 'saving':
                indicator.classList.add('saving');
                icon.innerHTML = '<i class="bi bi-arrow-repeat spin"></i>';
                text.textContent = '저장 중...';
                indicator.style.opacity = '1';
                break;
            case 'saved':
                indicator.classList.add('saved');
                icon.innerHTML = '<i class="bi bi-check-circle-fill"></i>';
                const now = new Date();
                text.textContent = `저장됨 ${now.toLocaleTimeString('ko-KR')}`;
                indicator.style.opacity = '1';

                // 3초 후 페이드 아웃
                setTimeout(() => {
                    if (indicator.classList.contains('saved')) {
                        indicator.style.opacity = '0.5';
                    }
                }, 3000);
                break;
            case 'error':
                indicator.classList.add('error');
                icon.innerHTML = '<i class="bi bi-exclamation-circle-fill"></i>';
                text.textContent = '저장 실패';
                indicator.style.opacity = '1';
                break;
            default:
                indicator.style.opacity = '0.5';
                icon.innerHTML = '<i class="bi bi-cloud"></i>';
                text.textContent = '자동 저장 활성화';
        }
    },

    /**
     * 자동 저장 관련 스타일 추가
     */
    addAutoSaveStyles() {
        if (document.getElementById('autoSaveStyles')) return;

        const styles = document.createElement('style');
        styles.id = 'autoSaveStyles';
        styles.textContent = `
            .auto-save-indicator {
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 8px 16px;
                border-radius: 20px;
                font-size: 12px;
                display: flex;
                align-items: center;
                gap: 8px;
                z-index: 10000;
                transition: all 0.3s ease;
                box-shadow: 0 2px 8px rgba(0,0,0,0.2);
            }

            .auto-save-indicator.saving {
                background: rgba(59, 130, 246, 0.9);
            }

            .auto-save-indicator.saved {
                background: rgba(34, 197, 94, 0.9);
            }

            .auto-save-indicator.error {
                background: rgba(239, 68, 68, 0.9);
            }

            .auto-save-indicator .save-icon i {
                font-size: 14px;
            }

            .auto-save-indicator .spin {
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                from { transform: rotate(0deg); }
                to { transform: rotate(360deg); }
            }

            .restore-notification-banner {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: linear-gradient(135deg, #3b82f6, #8b5cf6);
                color: white;
                padding: 12px 20px;
                z-index: 10001;
                box-shadow: 0 2px 10px rgba(0,0,0,0.2);
                animation: slideDown 0.3s ease;
            }

            @keyframes slideDown {
                from {
                    transform: translateY(-100%);
                    opacity: 0;
                }
                to {
                    transform: translateY(0);
                    opacity: 1;
                }
            }

            .restore-notification-banner.fade-out {
                animation: slideUp 0.3s ease forwards;
            }

            @keyframes slideUp {
                from {
                    transform: translateY(0);
                    opacity: 1;
                }
                to {
                    transform: translateY(-100%);
                    opacity: 0;
                }
            }

            .restore-notification-content {
                display: flex;
                align-items: center;
                justify-content: center;
                flex-wrap: wrap;
                gap: 10px;
            }

            .restore-notification-actions {
                display: flex;
                gap: 8px;
            }

            @media (max-width: 768px) {
                .auto-save-indicator {
                    bottom: 70px;
                    left: 50%;
                    transform: translateX(-50%);
                    padding: 6px 12px;
                    font-size: 11px;
                }

                .restore-notification-banner {
                    padding: 10px 15px;
                    font-size: 13px;
                }

                .restore-notification-content {
                    flex-direction: column;
                    text-align: center;
                }
            }
        `;

        document.head.appendChild(styles);
    },

    /**
     * localStorage 용량 초과 시 오래된 데이터 정리
     */
    cleanupOldLocalStorageData() {
        console.log('[AutoSave] Cleaning up old localStorage data...');

        // ai_consulting_ 접두사가 있는 오래된 키 삭제
        const keysToRemove = [];
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            if (key && key.startsWith(this.STORAGE_PREFIX) && key !== this.STORAGE_PREFIX + 'form_data') {
                keysToRemove.push(key);
            }
        }

        keysToRemove.forEach(key => {
            localStorage.removeItem(key);
            console.log(`[AutoSave] Removed: ${key}`);
        });
    },

    /**
     * 특정 프로젝트의 데이터만 저장 (프로젝트별 분리 저장)
     */
    saveProjectDataToLocalStorage(projectId = null) {
        const pid = projectId || this.currentProjectId || 'default';
        const storageKey = this.STORAGE_PREFIX + 'project_' + pid;

        const formData = {};
        document.querySelectorAll('input:not([type="file"]):not([type="submit"]):not([type="button"]), select, textarea').forEach(el => {
            const id = el.id || el.name;
            if (!id) return;

            let value;
            if (el.type === 'checkbox') {
                value = el.checked;
            } else if (el.type === 'radio') {
                if (el.checked) {
                    value = el.value;
                } else {
                    return;
                }
            } else {
                value = el.value;
            }

            formData[id] = value;
        });

        const storageData = {
            formData: formData,
            timestamp: new Date().toISOString(),
            projectId: pid
        };

        localStorage.setItem(storageKey, JSON.stringify(storageData));
        console.log(`[AutoSave] Project ${pid} saved to localStorage`);
    },

    /**
     * 특정 프로젝트 데이터 복원
     */
    restoreProjectDataFromLocalStorage(projectId = null) {
        const pid = projectId || this.currentProjectId || 'default';
        const storageKey = this.STORAGE_PREFIX + 'project_' + pid;

        const savedData = localStorage.getItem(storageKey);
        if (!savedData) return false;

        try {
            const parsedData = JSON.parse(savedData);
            const formData = parsedData.formData;

            Object.entries(formData).forEach(([id, value]) => {
                const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
                if (!element) return;

                if (element.type === 'checkbox') {
                    element.checked = value === true || value === 'true';
                } else if (element.type === 'radio') {
                    if (element.value === value) {
                        element.checked = true;
                    }
                } else {
                    element.value = value || '';
                }
            });

            console.log(`[AutoRestore] Project ${pid} restored from localStorage`);
            return true;
        } catch (error) {
            console.error(`[AutoRestore] Error restoring project ${pid}:`, error);
            return false;
        }
    },

    /**
     * 수동 저장 버튼 핸들러
     */
    manualSaveToLocalStorage() {
        this.saveAllFieldsToLocalStorage();
        this.showNotification('모든 입력 데이터가 로컬에 저장되었습니다.', 'success');
    },

    /**
     * localStorage 데이터 내보내기 (백업)
     */
    exportLocalStorageData() {
        const storageKey = this.STORAGE_PREFIX + 'form_data';
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) {
            this.showNotification('저장된 데이터가 없습니다.', 'warning');
            return;
        }

        const blob = new Blob([savedData], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_consulting_backup_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        this.showNotification('데이터가 내보내기되었습니다.', 'success');
    },

    /**
     * localStorage 데이터 가져오기 (복원)
     */
    importLocalStorageData(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                const storageKey = this.STORAGE_PREFIX + 'form_data';
                localStorage.setItem(storageKey, JSON.stringify(data));
                this.restoreFromLocalStorage();
                this.showNotification('데이터가 가져오기되었습니다.', 'success');
            } catch (error) {
                this.showNotification('파일을 읽는 중 오류가 발생했습니다.', 'error');
            }
        };
        reader.readAsText(file);
    },

    // =========================================================================
    // ISO 42001 AIMS 관련 함수
    // =========================================================================

    /**
     * AIMS 데이터 저장 키 생성
     */
    getAimsStorageKey(type) {
        const pid = this.currentProjectId || 'default';
        return `${this.STORAGE_PREFIX}aims_${type}_${pid}`;
    },

    /**
     * AIMS 체크리스트 저장
     */
    saveAimsChecklist() {
        const checklistData = {
            phases: {}
        };

        // 모든 체크리스트 항목 수집
        document.querySelectorAll('#page-aims-checklist .form-check-input').forEach(checkbox => {
            const phaseCard = checkbox.closest('.card');
            const phaseTitle = phaseCard?.querySelector('.card-header')?.textContent?.trim() || 'unknown';

            if (!checklistData.phases[phaseTitle]) {
                checklistData.phases[phaseTitle] = [];
            }

            checklistData.phases[phaseTitle].push({
                id: checkbox.id,
                checked: checkbox.checked,
                label: checkbox.closest('.form-check')?.querySelector('label')?.textContent?.trim() || ''
            });
        });

        checklistData.timestamp = new Date().toISOString();

        const storageKey = this.getAimsStorageKey('checklist');
        localStorage.setItem(storageKey, JSON.stringify(checklistData));

        this.showNotification('AIMS 체크리스트가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return checklistData;
    },

    /**
     * AIMS 체크리스트 불러오기
     */
    loadAimsChecklist() {
        const storageKey = this.getAimsStorageKey('checklist');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const checklistData = JSON.parse(savedData);

            // 체크박스 상태 복원
            Object.values(checklistData.phases).flat().forEach(item => {
                const checkbox = document.getElementById(item.id);
                if (checkbox) {
                    checkbox.checked = item.checked;
                }
            });

            return checklistData;
        } catch (error) {
            console.error('AIMS 체크리스트 로드 오류:', error);
            return null;
        }
    },

    /**
     * AIMS 체크리스트 내보내기
     */
    exportAimsChecklist() {
        const data = this.saveAimsChecklist();
        this.downloadAsJson(data, 'aims_checklist');
    },

    /**
     * AI 위험 등록부 저장
     */
    saveRiskRegister() {
        const risks = [];

        document.querySelectorAll('#riskTableBody tr').forEach(row => {
            const cells = row.querySelectorAll('td');
            if (cells.length >= 7) {
                risks.push({
                    id: cells[0]?.textContent?.trim() || '',
                    category: cells[1]?.textContent?.trim() || '',
                    description: cells[2]?.textContent?.trim() || '',
                    probability: cells[3]?.textContent?.trim() || '',
                    impact: cells[4]?.textContent?.trim() || '',
                    level: cells[5]?.querySelector('.badge')?.textContent?.trim() || '',
                    mitigation: cells[6]?.textContent?.trim() || '',
                    status: cells[7]?.querySelector('.badge')?.textContent?.trim() || ''
                });
            }
        });

        const riskData = {
            risks: risks,
            timestamp: new Date().toISOString()
        };

        const storageKey = this.getAimsStorageKey('risk_register');
        localStorage.setItem(storageKey, JSON.stringify(riskData));

        this.showNotification('위험 등록부가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return riskData;
    },

    /**
     * AI 위험 등록부 불러오기
     */
    loadRiskRegister() {
        const storageKey = this.getAimsStorageKey('risk_register');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const riskData = JSON.parse(savedData);
            this.renderRiskTable(riskData.risks);
            return riskData;
        } catch (error) {
            console.error('위험 등록부 로드 오류:', error);
            return null;
        }
    },

    /**
     * 위험 테이블 렌더링
     */
    renderRiskTable(risks) {
        const tbody = document.getElementById('riskRegisterBody');
        if (!tbody || !risks) return;

        // 위험 점수 계산 함수
        const getProbScore = (prob) => {
            const scores = { '매우 높음': 5, '높음': 4, '중간': 3, '낮음': 2, '매우 낮음': 1 };
            return scores[prob] || 3;
        };
        const getImpactScore = (impact) => {
            const scores = { '매우 높음': 5, '높음': 4, '중간': 3, '낮음': 2, '매우 낮음': 1 };
            return scores[impact] || 3;
        };
        const getCategoryBadge = (cat) => {
            const badges = {
                '데이터': 'primary', '모델': 'danger', '운영': 'secondary',
                '보안': 'dark', '윤리': 'warning', '규제': 'info'
            };
            return badges[cat] || 'secondary';
        };
        const getStatusBadge = (status) => {
            const badges = { '식별됨': 'secondary', '진행중': 'info', '완료': 'success' };
            return badges[status] || 'secondary';
        };

        tbody.innerHTML = risks.map(risk => {
            const probScore = getProbScore(risk.probability);
            const impactScore = getImpactScore(risk.impact);
            const riskScore = probScore * impactScore;
            const scoreColor = riskScore >= 15 ? 'danger' : riskScore >= 8 ? 'warning' : 'success';
            const scoreText = riskScore >= 15 ? '높음' : riskScore >= 8 ? '중간' : '낮음';

            return `
            <tr>
                <td><code>${this.escapeHtml(risk.id)}</code></td>
                <td>${this.escapeHtml(risk.description)}</td>
                <td><span class="badge bg-${getCategoryBadge(risk.category)}">${this.escapeHtml(risk.category)}</span></td>
                <td>${probScore}</td>
                <td>${impactScore}</td>
                <td><span class="badge bg-${scoreColor}">${riskScore} ${scoreText}</span></td>
                <td>${this.escapeHtml(risk.mitigation)}</td>
                <td>-</td>
                <td><span class="badge bg-${getStatusBadge(risk.status)}">${this.escapeHtml(risk.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="editRisk('${risk.id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteRisk('${risk.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `}).join('');

        // 위험 카운트 업데이트
        this.updateRiskCounts(risks);
    },

    /**
     * 위험 카테고리별 카운트 업데이트
     */
    updateRiskCounts(risks) {
        if (!risks) return;

        const counts = {
            technical: risks.filter(r => r.category === '모델' || r.category === '데이터').length,
            ethical: risks.filter(r => r.category === '윤리').length,
            legal: risks.filter(r => r.category === '규제').length,
            operational: risks.filter(r => r.category === '운영').length,
            reputation: risks.filter(r => r.category === '보안').length,
            total: risks.length
        };

        const updateElement = (id, value) => {
            const el = document.getElementById(id);
            if (el) el.textContent = value;
        };

        updateElement('risk-count-technical', counts.technical);
        updateElement('risk-count-ethical', counts.ethical);
        updateElement('risk-count-legal', counts.legal);
        updateElement('risk-count-operational', counts.operational);
        updateElement('risk-count-reputation', counts.reputation);
        updateElement('risk-count-total', counts.total);
    },

    /**
     * 위험 수준 색상 반환
     */
    getRiskLevelColor(level) {
        const colors = {
            '매우 높음': 'danger',
            '높음': 'warning',
            '중간': 'info',
            '낮음': 'success',
            '매우 낮음': 'secondary'
        };
        return colors[level] || 'secondary';
    },

    /**
     * 새 위험 추가 모달 열기
     */
    addNewRisk() {
        // 모달이 있으면 열기, 없으면 생성
        let modal = document.getElementById('riskModal');
        if (!modal) {
            modal = this.createRiskModal();
            document.body.appendChild(modal);
        }

        // 폼 초기화
        document.getElementById('riskForm')?.reset();
        document.getElementById('riskModalTitle').textContent = '새 위험 추가';
        document.getElementById('riskId').value = 'R-' + String(Date.now()).slice(-4);

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    },

    /**
     * 위험 편집
     */
    editRisk(riskId) {
        const storageKey = this.getAimsStorageKey('risk_register');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return;

        const riskData = JSON.parse(savedData);
        const risk = riskData.risks.find(r => r.id === riskId);

        if (!risk) return;

        let modal = document.getElementById('riskModal');
        if (!modal) {
            modal = this.createRiskModal();
            document.body.appendChild(modal);
        }

        // 폼에 데이터 채우기
        document.getElementById('riskId').value = risk.id;
        document.getElementById('riskCategory').value = risk.category;
        document.getElementById('riskDescription').value = risk.description;
        document.getElementById('riskProbability').value = risk.probability;
        document.getElementById('riskImpact').value = risk.impact;
        document.getElementById('riskMitigation').value = risk.mitigation;
        document.getElementById('riskStatus').value = risk.status;
        document.getElementById('riskModalTitle').textContent = '위험 편집';

        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    },

    /**
     * 위험 삭제
     */
    deleteRisk(riskId) {
        if (!confirm('이 위험을 삭제하시겠습니까?')) return;

        const storageKey = this.getAimsStorageKey('risk_register');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return;

        const riskData = JSON.parse(savedData);
        riskData.risks = riskData.risks.filter(r => r.id !== riskId);

        localStorage.setItem(storageKey, JSON.stringify(riskData));
        this.renderRiskTable(riskData.risks);
        this.showNotification('위험이 삭제되었습니다.', 'success');
    },

    /**
     * 위험 모달 생성
     */
    createRiskModal() {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.id = 'riskModal';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title" id="riskModalTitle">새 위험 추가</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <form id="riskForm">
                            <div class="row g-3">
                                <div class="col-md-4">
                                    <label class="form-label">위험 ID</label>
                                    <input type="text" class="form-control" id="riskId" readonly>
                                </div>
                                <div class="col-md-8">
                                    <label class="form-label">카테고리</label>
                                    <select class="form-select" id="riskCategory">
                                        <option value="데이터">데이터</option>
                                        <option value="모델">모델</option>
                                        <option value="운영">운영</option>
                                        <option value="보안">보안</option>
                                        <option value="윤리">윤리</option>
                                        <option value="규제">규제</option>
                                    </select>
                                </div>
                                <div class="col-12">
                                    <label class="form-label">위험 설명</label>
                                    <textarea class="form-control" id="riskDescription" rows="2"></textarea>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">발생 확률</label>
                                    <select class="form-select" id="riskProbability">
                                        <option value="매우 높음">매우 높음</option>
                                        <option value="높음">높음</option>
                                        <option value="중간">중간</option>
                                        <option value="낮음">낮음</option>
                                        <option value="매우 낮음">매우 낮음</option>
                                    </select>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">영향도</label>
                                    <select class="form-select" id="riskImpact">
                                        <option value="매우 높음">매우 높음</option>
                                        <option value="높음">높음</option>
                                        <option value="중간">중간</option>
                                        <option value="낮음">낮음</option>
                                        <option value="매우 낮음">매우 낮음</option>
                                    </select>
                                </div>
                                <div class="col-12">
                                    <label class="form-label">완화 조치</label>
                                    <textarea class="form-control" id="riskMitigation" rows="2"></textarea>
                                </div>
                                <div class="col-md-6">
                                    <label class="form-label">상태</label>
                                    <select class="form-select" id="riskStatus">
                                        <option value="식별됨">식별됨</option>
                                        <option value="진행중">진행중</option>
                                        <option value="완료">완료</option>
                                    </select>
                                </div>
                            </div>
                        </form>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">취소</button>
                        <button type="button" class="btn btn-primary" onclick="ProjectManager.saveRiskFromModal()">저장</button>
                    </div>
                </div>
            </div>
        `;
        return modal;
    },

    /**
     * 모달에서 위험 저장
     */
    saveRiskFromModal() {
        const riskId = document.getElementById('riskId').value;
        const probability = document.getElementById('riskProbability').value;
        const impact = document.getElementById('riskImpact').value;

        // 위험 수준 계산
        const levelMatrix = {
            '매우 높음': { '매우 높음': '매우 높음', '높음': '매우 높음', '중간': '높음', '낮음': '중간', '매우 낮음': '낮음' },
            '높음': { '매우 높음': '매우 높음', '높음': '높음', '중간': '높음', '낮음': '중간', '매우 낮음': '낮음' },
            '중간': { '매우 높음': '높음', '높음': '높음', '중간': '중간', '낮음': '낮음', '매우 낮음': '낮음' },
            '낮음': { '매우 높음': '중간', '높음': '중간', '중간': '낮음', '낮음': '낮음', '매우 낮음': '매우 낮음' },
            '매우 낮음': { '매우 높음': '낮음', '높음': '낮음', '중간': '낮음', '낮음': '매우 낮음', '매우 낮음': '매우 낮음' }
        };

        const level = levelMatrix[probability]?.[impact] || '중간';

        const newRisk = {
            id: riskId,
            category: document.getElementById('riskCategory').value,
            description: document.getElementById('riskDescription').value,
            probability: probability,
            impact: impact,
            level: level,
            mitigation: document.getElementById('riskMitigation').value,
            status: document.getElementById('riskStatus').value
        };

        const storageKey = this.getAimsStorageKey('risk_register');
        let riskData = { risks: [], timestamp: new Date().toISOString() };

        const savedData = localStorage.getItem(storageKey);
        if (savedData) {
            riskData = JSON.parse(savedData);
        }

        // 기존 위험 업데이트 또는 새로 추가
        const existingIndex = riskData.risks.findIndex(r => r.id === riskId);
        if (existingIndex >= 0) {
            riskData.risks[existingIndex] = newRisk;
        } else {
            riskData.risks.push(newRisk);
        }

        riskData.timestamp = new Date().toISOString();
        localStorage.setItem(storageKey, JSON.stringify(riskData));

        this.renderRiskTable(riskData.risks);

        // 모달 닫기
        const modal = bootstrap.Modal.getInstance(document.getElementById('riskModal'));
        modal?.hide();

        this.showNotification('위험이 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
    },

    /**
     * AI 영향 평가 저장
     */
    saveImpactAssessment() {
        const formData = {};

        document.querySelectorAll('#page-ai-impact-assessment input, #page-ai-impact-assessment select, #page-ai-impact-assessment textarea').forEach(el => {
            if (el.id) {
                if (el.type === 'checkbox') {
                    formData[el.id] = el.checked;
                } else if (el.type === 'radio') {
                    if (el.checked) formData[el.name] = el.value;
                } else {
                    formData[el.id] = el.value;
                }
            }
        });

        const assessmentData = {
            formData: formData,
            timestamp: new Date().toISOString()
        };

        const storageKey = this.getAimsStorageKey('impact_assessment');
        localStorage.setItem(storageKey, JSON.stringify(assessmentData));

        this.showNotification('AI 영향 평가가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return assessmentData;
    },

    /**
     * AI 영향 평가 불러오기
     */
    loadImpactAssessment() {
        const storageKey = this.getAimsStorageKey('impact_assessment');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const assessmentData = JSON.parse(savedData);

            Object.entries(assessmentData.formData).forEach(([id, value]) => {
                const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
                if (!element) return;

                if (element.type === 'checkbox') {
                    element.checked = value;
                } else if (element.type === 'radio') {
                    if (element.value === value) element.checked = true;
                } else {
                    element.value = value || '';
                }
            });

            return assessmentData;
        } catch (error) {
            console.error('AI 영향 평가 로드 오류:', error);
            return null;
        }
    },

    /**
     * AI 영향 평가 내보내기
     */
    exportImpactAssessment() {
        const data = this.saveImpactAssessment();
        this.downloadAsJson(data, 'ai_impact_assessment');
    },

    /**
     * 모델 카드 저장
     */
    saveModelCard() {
        const formData = {};

        document.querySelectorAll('#page-model-card input, #page-model-card select, #page-model-card textarea').forEach(el => {
            if (el.id) {
                formData[el.id] = el.value;
            }
        });

        const modelCardData = {
            formData: formData,
            timestamp: new Date().toISOString()
        };

        const storageKey = this.getAimsStorageKey('model_card');
        localStorage.setItem(storageKey, JSON.stringify(modelCardData));

        this.showNotification('모델 카드가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return modelCardData;
    },

    /**
     * 모델 카드 불러오기
     */
    loadModelCard() {
        const storageKey = this.getAimsStorageKey('model_card');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const modelCardData = JSON.parse(savedData);

            Object.entries(modelCardData.formData).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.value = value || '';
            });

            return modelCardData;
        } catch (error) {
            console.error('모델 카드 로드 오류:', error);
            return null;
        }
    },

    /**
     * 모델 카드 내보내기
     */
    exportModelCard() {
        const data = this.saveModelCard();
        this.downloadAsJson(data, 'model_card');
    },

    /**
     * 데이터 시트 저장
     */
    saveDataSheet() {
        const formData = {};

        document.querySelectorAll('#page-data-sheet input, #page-data-sheet select, #page-data-sheet textarea').forEach(el => {
            if (el.id) {
                formData[el.id] = el.value;
            }
        });

        const dataSheetData = {
            formData: formData,
            timestamp: new Date().toISOString()
        };

        const storageKey = this.getAimsStorageKey('data_sheet');
        localStorage.setItem(storageKey, JSON.stringify(dataSheetData));

        this.showNotification('데이터 시트가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return dataSheetData;
    },

    /**
     * 데이터 시트 불러오기
     */
    loadDataSheet() {
        const storageKey = this.getAimsStorageKey('data_sheet');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const dataSheetData = JSON.parse(savedData);

            Object.entries(dataSheetData.formData).forEach(([id, value]) => {
                const element = document.getElementById(id);
                if (element) element.value = value || '';
            });

            return dataSheetData;
        } catch (error) {
            console.error('데이터 시트 로드 오류:', error);
            return null;
        }
    },

    /**
     * 데이터 시트 내보내기
     */
    exportDataSheet() {
        const data = this.saveDataSheet();
        this.downloadAsJson(data, 'data_sheet');
    },

    /**
     * 내부 감사 저장
     */
    saveAudit() {
        const auditData = {
            items: [],
            timestamp: new Date().toISOString()
        };

        document.querySelectorAll('#page-aims-audit .form-check-input').forEach(checkbox => {
            auditData.items.push({
                id: checkbox.id,
                checked: checkbox.checked,
                label: checkbox.closest('.form-check')?.querySelector('label')?.textContent?.trim() || ''
            });
        });

        // 감사 메모 저장
        const auditNotes = document.getElementById('auditNotes');
        if (auditNotes) {
            auditData.notes = auditNotes.value;
        }

        const storageKey = this.getAimsStorageKey('audit');
        localStorage.setItem(storageKey, JSON.stringify(auditData));

        this.showNotification('내부 감사 체크리스트가 저장되었습니다.', 'success');
        this.updateAimsDashboardStats();
        return auditData;
    },

    /**
     * 내부 감사 불러오기
     */
    loadAudit() {
        const storageKey = this.getAimsStorageKey('audit');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const auditData = JSON.parse(savedData);

            auditData.items.forEach(item => {
                const checkbox = document.getElementById(item.id);
                if (checkbox) checkbox.checked = item.checked;
            });

            const auditNotes = document.getElementById('auditNotes');
            if (auditNotes && auditData.notes) {
                auditNotes.value = auditData.notes;
            }

            return auditData;
        } catch (error) {
            console.error('내부 감사 로드 오류:', error);
            return null;
        }
    },

    /**
     * 내부 감사 내보내기
     */
    exportAudit() {
        const data = this.saveAudit();
        this.downloadAsJson(data, 'aims_audit');
    },

    /**
     * JSON 파일로 다운로드
     */
    downloadAsJson(data, filename) {
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${filename}_${new Date().toISOString().slice(0, 10)}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    /**
     * HTML 이스케이프
     */
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    /**
     * AIMS 대시보드 통계 업데이트
     */
    updateAimsDashboardStats() {
        // 체크리스트 완료 수 계산
        const checklistKey = this.getAimsStorageKey('checklist');
        const checklistData = localStorage.getItem(checklistKey);
        let completedChecklist = 0;
        let totalChecklist = 0;

        if (checklistData) {
            const data = JSON.parse(checklistData);
            const allItems = Object.values(data.phases).flat();
            totalChecklist = allItems.length;
            completedChecklist = allItems.filter(item => item.checked).length;
        }

        // 위험 현황 계산
        const riskKey = this.getAimsStorageKey('risk_register');
        const riskData = localStorage.getItem(riskKey);
        let riskCount = 0;

        if (riskData) {
            const data = JSON.parse(riskData);
            riskCount = data.risks.length;
        }

        // 문서화 완료 수 계산 (모델 카드 + 데이터 시트)
        let docCount = 0;
        const modelCardKey = this.getAimsStorageKey('model_card');
        const dataSheetKey = this.getAimsStorageKey('data_sheet');

        if (localStorage.getItem(modelCardKey)) {
            const modelData = JSON.parse(localStorage.getItem(modelCardKey));
            if (modelData.formData && Object.keys(modelData.formData).some(k => modelData.formData[k])) {
                docCount++;
            }
        }
        if (localStorage.getItem(dataSheetKey)) {
            const sheetData = JSON.parse(localStorage.getItem(dataSheetKey));
            if (sheetData.formData && Object.keys(sheetData.formData).some(k => sheetData.formData[k])) {
                docCount++;
            }
        }

        // 감사 완료 수 계산
        const auditKey = this.getAimsStorageKey('audit');
        const auditData = localStorage.getItem(auditKey);
        let auditCompleted = 0;

        if (auditData) {
            const data = JSON.parse(auditData);
            auditCompleted = data.items.filter(item => item.checked).length;
        }

        // 대시보드 UI 업데이트
        const completedElement = document.getElementById('aims-completed-count');
        if (completedElement) {
            completedElement.textContent = `${completedChecklist}/${totalChecklist || 20}`;
        }

        const riskElement = document.getElementById('aims-risk-count');
        if (riskElement) {
            riskElement.textContent = riskCount;
        }

        const docElement = document.getElementById('aims-doc-count');
        if (docElement) {
            docElement.textContent = docCount;
        }

        const auditElement = document.getElementById('aims-audit-count');
        if (auditElement) {
            auditElement.textContent = auditCompleted;
        }
    },

    /**
     * 모든 AIMS 데이터 로드 (페이지 전환 시)
     */
    loadAllAimsData() {
        this.loadAimsChecklist();
        this.loadRiskRegister();
        this.loadImpactAssessment();
        this.loadModelCard();
        this.loadDataSheet();
        this.loadAudit();
        this.updateAimsDashboardStats();
    },

    // ==========================================
    // ISO 23053 ML Framework 관련 함수
    // ==========================================

    /**
     * ISO 23053 ML 체크리스트 스토리지 키 생성
     */
    getMlStorageKey(type) {
        const projectId = this.currentProject?.id || 'default';
        return `ml_framework_${projectId}_${type}`;
    },

    /**
     * ML 프레임워크 체크리스트 저장
     */
    saveMlChecklist() {
        const checklistData = {
            categories: {}
        };

        // 모든 체크리스트 항목 수집
        document.querySelectorAll('#page-ml-framework-checklist .form-check-input').forEach(checkbox => {
            const categoryCard = checkbox.closest('.card');
            const categoryTitle = categoryCard?.querySelector('.card-header')?.textContent?.trim() || 'unknown';

            if (!checklistData.categories[categoryTitle]) {
                checklistData.categories[categoryTitle] = [];
            }

            checklistData.categories[categoryTitle].push({
                id: checkbox.id,
                checked: checkbox.checked,
                label: checkbox.closest('.form-check')?.querySelector('label')?.textContent?.trim() || ''
            });
        });

        checklistData.timestamp = new Date().toISOString();

        const storageKey = this.getMlStorageKey('checklist');
        localStorage.setItem(storageKey, JSON.stringify(checklistData));

        this.showNotification('ML 프레임워크 체크리스트가 저장되었습니다.', 'success');
        this.updateMlDashboardStats();
        return checklistData;
    },

    /**
     * ML 프레임워크 체크리스트 불러오기
     */
    loadMlChecklist() {
        const storageKey = this.getMlStorageKey('checklist');
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) return null;

        try {
            const checklistData = JSON.parse(savedData);

            // 체크박스 상태 복원
            Object.values(checklistData.categories).flat().forEach(item => {
                const checkbox = document.getElementById(item.id);
                if (checkbox) {
                    checkbox.checked = item.checked;
                }
            });

            return checklistData;
        } catch (error) {
            console.error('ML 체크리스트 로드 오류:', error);
            return null;
        }
    },

    /**
     * ML 프레임워크 체크리스트 내보내기
     */
    exportMlChecklist() {
        const data = this.saveMlChecklist();
        this.downloadAsJson(data, 'ml_framework_checklist');
    },

    /**
     * ML 대시보드 통계 업데이트
     */
    updateMlDashboardStats() {
        const storageKey = this.getMlStorageKey('checklist');
        const savedData = localStorage.getItem(storageKey);

        let totalChecklist = 0;
        let completedChecklist = 0;

        if (savedData) {
            try {
                const checklistData = JSON.parse(savedData);
                Object.values(checklistData.categories).flat().forEach(item => {
                    totalChecklist++;
                    if (item.checked) completedChecklist++;
                });
            } catch (error) {
                console.error('ML 통계 업데이트 오류:', error);
            }
        }

        // 카테고리별 진행률 계산 및 UI 업데이트
        const categoryStats = {};
        document.querySelectorAll('#page-ml-framework-checklist .card').forEach(card => {
            const header = card.querySelector('.card-header');
            const checkboxes = card.querySelectorAll('.form-check-input');
            if (header && checkboxes.length > 0) {
                const categoryName = header.textContent.trim();
                const total = checkboxes.length;
                const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
                categoryStats[categoryName] = { total, checked, percent: Math.round((checked / total) * 100) };
            }
        });

        // 대시보드 진행률 카드 업데이트
        const progressCards = document.querySelectorAll('#page-ml-framework-dashboard .progress');
        progressCards.forEach(progressBar => {
            const card = progressBar.closest('.card');
            const cardTitle = card?.querySelector('.card-title')?.textContent?.trim();

            Object.keys(categoryStats).forEach(catName => {
                if (cardTitle && catName.includes(cardTitle.replace(' Layer', '').replace(' 레이어', ''))) {
                    const bar = progressBar.querySelector('.progress-bar');
                    if (bar) {
                        bar.style.width = `${categoryStats[catName].percent}%`;
                        bar.setAttribute('aria-valuenow', categoryStats[catName].percent);
                    }
                    const percentText = card.querySelector('.text-muted');
                    if (percentText) {
                        percentText.textContent = `${categoryStats[catName].checked}/${categoryStats[catName].total} 완료`;
                    }
                }
            });
        });

        return { totalChecklist, completedChecklist, categoryStats };
    },

    /**
     * 모든 ML 프레임워크 데이터 로드
     */
    loadAllMlData() {
        this.loadMlChecklist();
        this.updateMlDashboardStats();
    }
};

// DOM 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    ProjectManager.init();
});

// 전역 함수로 노출 (HTML onclick에서 호출용)
window.ProjectManager = ProjectManager;

// ISO 42001 AIMS 전역 함수
window.saveAimsChecklist = () => ProjectManager.saveAimsChecklist();
window.exportAimsChecklist = () => ProjectManager.exportAimsChecklist();
window.saveRiskRegister = () => ProjectManager.saveRiskRegister();
window.addNewRisk = () => ProjectManager.addNewRisk();
window.editRisk = (id) => ProjectManager.editRisk(id);
window.deleteRisk = (id) => ProjectManager.deleteRisk(id);
window.saveImpactAssessment = () => ProjectManager.saveImpactAssessment();
window.exportImpactAssessment = () => ProjectManager.exportImpactAssessment();
window.saveModelCard = () => ProjectManager.saveModelCard();
window.exportModelCard = () => ProjectManager.exportModelCard();
window.saveDataSheet = () => ProjectManager.saveDataSheet();
window.exportDataSheet = () => ProjectManager.exportDataSheet();
window.saveAudit = () => ProjectManager.saveAudit();
window.exportAudit = () => ProjectManager.exportAudit();

// ISO 23053 ML Framework 전역 함수
window.saveMlChecklist = () => ProjectManager.saveMlChecklist();
window.exportMlChecklist = () => ProjectManager.exportMlChecklist();
window.loadMlChecklist = () => ProjectManager.loadMlChecklist();
