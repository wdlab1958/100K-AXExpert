/**
 * 100K-AX Expert Platform - Project Manager (모듈화 버전)
 * 모든 모듈을 통합하는 메인 파일
 * 
 * 의존성:
 * - pm-utils.js
 * - pm-notification.js
 * - pm-project-crud.js
 * - pm-stage-config.js
 * - pm-form-collector.js
 * - pm-form-populator.js
 * - pm-localstorage.js
 * - pm-scenario-report.js
 * - pm-aims.js
 * - pm-ml-framework.js
 */

const ProjectManager = {
    // API Base URL
    API_BASE: '/api/v1',

    // 현재 선택된 프로젝트 ID (PMProjectCrud에서 관리)
    get currentProjectId() {
        return PMProjectCrud.currentProjectId;
    },
    set currentProjectId(value) {
        PMProjectCrud.currentProjectId = value;
    },

    // 프로젝트 목록 캐시
    get projectsCache() {
        return PMProjectCrud.projectsCache;
    },

    // 워크플로우 상태
    get workflowStatus() {
        return PMStageConfig.workflowStatus;
    },

    // 자동 저장 타이머
    _saveTimeout: null,

    /**
     * 초기화
     */
    async init() {
        console.log('ProjectManager (Modular) initializing...');

        // 프로젝트 목록 로드
        await PMProjectCrud.loadProjectList();

        // 이벤트 바인딩
        this.bindEvents();

        // 마지막 프로젝트 복원
        this.restoreLastProject();

        // 자동 저장 초기화
        this.initAutoSave();

        // localStorage 자동 저장 시스템 초기화
        PMLocalStorage.init();

        // localStorage에서 데이터 복원
        PMLocalStorage.restoreFromLocalStorage();

        console.log('ProjectManager (Modular) initialized successfully');
    },

    /**
     * 이벤트 바인딩
     */
    bindEvents() {
        // 프로젝트 선택 드롭다운 변경
        const projectSelect = document.getElementById('projectSelector');
        if (projectSelect) {
            projectSelect.addEventListener('change', async (e) => {
                if (e.target.value) {
                    const project = await this.loadProject(e.target.value);
                    // 대시보드 업데이트
                    if (project && typeof PMProjectCrud !== 'undefined' && PMProjectCrud.updateDashboard) {
                        PMProjectCrud.updateDashboard(project);
                    }
                } else {
                    // 프로젝트 선택 해제 시 대시보드 초기화
                    const maturityLevelEl = document.getElementById('maturityLevel');
                    if (maturityLevelEl) maturityLevelEl.textContent = '-';
                    const expectedROIEl = document.getElementById('expectedROI');
                    if (expectedROIEl) expectedROIEl.textContent = '-';
                }
            });
        }

        // 폼 자동 저장
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

        const projectExists = this.projectsCache.find(p =>
            p.project_id === lastProjectId || p.id === lastProjectId
        );

        if (projectExists) {
            this.loadProject(lastProjectId);
        } else {
            localStorage.removeItem('lastProjectId');
        }
    },

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
     * 디바운스 저장
     */
    debouncedSave(stage) {
        if (this.saveTimeouts[stage]) {
            clearTimeout(this.saveTimeouts[stage]);
        }

        this.saveTimeouts[stage] = setTimeout(() => {
            console.log(`[AutoSave] Triggering save for ${stage}`);
            this.saveStageData(stage, null, true); // silent=true
        }, 1500);
    },

    // =========================================================================
    // 프로젝트 관리 (PMProjectCrud 위임)
    // =========================================================================

    async loadProjectList() {
        return PMProjectCrud.loadProjectList();
    },

    renderProjectList() {
        return PMProjectCrud.renderProjectList();
    },

    renderProjectTable() {
        return PMProjectCrud.renderProjectTable();
    },

    async createProject(projectData) {
        return PMProjectCrud.createProject(projectData);
    },

    async loadProject(projectId) {
        const project = await PMProjectCrud.loadProject(projectId);
        if (project) {
            // 워크플로우 상태 업데이트
            PMStageConfig.updateWorkflowStatus(project);
            // 모든 단계 데이터 로드
            await PMStageConfig.loadAllStageData(project);
        }
        return project;
    },

    async deleteProject(projectId) {
        return PMProjectCrud.deleteProject(projectId);
    },

    async duplicateProject(projectId) {
        return PMProjectCrud.duplicateProject(projectId);
    },

    getProjectName(project) {
        return PMProjectCrud.getProjectName(project);
    },

    getProjectId(project) {
        return PMProjectCrud.getProjectId(project);
    },

    calculateProgress(project) {
        return PMProjectCrud.calculateProgress(project);
    },

    // =========================================================================
    // Stage 데이터 관리 (PMStageConfig 위임)
    // =========================================================================

    async saveStageData(stage, data = null, silent = false) {
        return PMStageConfig.saveStageData(stage, data, this.currentProjectId, silent);
    },

    async loadStageData(stage) {
        return PMStageConfig.loadStageData(stage, this.currentProjectId);
    },

    getStageConfig(stage) {
        return PMStageConfig.getStageConfig(stage);
    },

    updateWorkflowStatus(project) {
        return PMStageConfig.updateWorkflowStatus(project);
    },

    renderWorkflowProgress() {
        return PMStageConfig.renderWorkflowProgress();
    },

    renderCompletionOverview() {
        return PMStageConfig.renderCompletionOverview();
    },

    // =========================================================================
    // 시나리오 및 보고서 (PMScenarioReport 위임)
    // =========================================================================

    async generateScenarios(scenarioOrParams = 'balanced') {
        return PMScenarioReport.generateScenarios(scenarioOrParams, this.currentProjectId);
    },

    async generateReport(options = {}) {
        return PMScenarioReport.generateReport(options, this.currentProjectId);
    },

    async runFullAnalysis() {
        const result = await PMScenarioReport.runFullAnalysis(this.currentProjectId);
        if (result) {
            await this.loadProject(this.currentProjectId);
        }
        return result;
    },

    // =========================================================================
    // 알림 (PMNotification 위임)
    // =========================================================================

    showLoading(message) {
        return PMNotification.showLoading(message);
    },

    hideLoading() {
        return PMNotification.hideLoading();
    },

    showNotification(message, type = 'info') {
        return PMNotification.showNotification(message, type);
    },

    // =========================================================================
    // 유틸리티 (PMUtils 위임)
    // =========================================================================

    getInputValue(id, type = 'string') {
        return PMUtils.getInputValue(id, type);
    },

    setInputValue(id, value) {
        return PMUtils.setInputValue(id, value);
    },

    setCheckboxValue(id, value) {
        return PMUtils.setCheckboxValue(id, value);
    },

    formatDate(dateString) {
        return PMUtils.formatDate(dateString);
    },

    escapeHtml(text) {
        return PMUtils.escapeHtml(text);
    },

    // =========================================================================
    // LocalStorage (PMLocalStorage 위임)
    // =========================================================================

    saveAllFieldsToLocalStorage() {
        return PMLocalStorage.saveAllFieldsToLocalStorage();
    },

    restoreFromLocalStorage() {
        return PMLocalStorage.restoreFromLocalStorage();
    },

    manualSaveToLocalStorage() {
        return PMLocalStorage.manualSaveToLocalStorage();
    },

    exportLocalStorageData() {
        return PMLocalStorage.exportLocalStorageData();
    },

    importLocalStorageData(file) {
        return PMLocalStorage.importLocalStorageData(file);
    },

    // =========================================================================
    // ISO 42001 AIMS (PMAims 위임)
    // =========================================================================

    saveAimsChecklist() {
        return PMAims.saveAimsChecklist();
    },

    loadAimsChecklist() {
        return PMAims.loadAimsChecklist();
    },

    exportAimsChecklist() {
        return PMAims.exportAimsChecklist();
    },

    saveRiskRegister() {
        return PMAims.saveRiskRegister();
    },

    loadRiskRegister() {
        return PMAims.loadRiskRegister();
    },

    addNewRisk() {
        return PMAims.addNewRisk();
    },

    editRisk(riskId) {
        return PMAims.editRisk(riskId);
    },

    deleteRisk(riskId) {
        return PMAims.deleteRisk(riskId);
    },

    saveImpactAssessment() {
        return PMAims.saveImpactAssessment();
    },

    loadImpactAssessment() {
        return PMAims.loadImpactAssessment();
    },

    exportImpactAssessment() {
        return PMAims.exportImpactAssessment();
    },

    saveModelCard() {
        return PMAims.saveModelCard();
    },

    loadModelCard() {
        return PMAims.loadModelCard();
    },

    exportModelCard() {
        return PMAims.exportModelCard();
    },

    saveDataSheet() {
        return PMAims.saveDataSheet();
    },

    loadDataSheet() {
        return PMAims.loadDataSheet();
    },

    exportDataSheet() {
        return PMAims.exportDataSheet();
    },

    saveAudit() {
        return PMAims.saveAudit();
    },

    loadAudit() {
        return PMAims.loadAudit();
    },

    exportAudit() {
        return PMAims.exportAudit();
    },

    updateAimsDashboardStats() {
        return PMAims.updateAimsDashboardStats();
    },

    loadAllAimsData() {
        return PMAims.loadAllAimsData();
    },

    // =========================================================================
    // ISO 23053 ML Framework (PMMlFramework 위임)
    // =========================================================================

    saveMlChecklist() {
        return PMMlFramework.saveMlChecklist();
    },

    loadMlChecklist() {
        return PMMlFramework.loadMlChecklist();
    },

    exportMlChecklist() {
        return PMMlFramework.exportMlChecklist();
    },

    updateMlDashboardStats() {
        return PMMlFramework.updateMlDashboardStats();
    },

    loadAllMlData() {
        return PMMlFramework.loadAllMlData();
    },

    // =========================================================================
    // 폼 데이터 수집 (PMFormCollector 위임)
    // =========================================================================

    collectMaturityData() {
        return PMFormCollector.collectMaturityData();
    },

    collectOpportunitiesData() {
        return PMFormCollector.collectOpportunitiesData();
    },

    collectRoadmapData() {
        return PMFormCollector.collectRoadmapData();
    },

    // =========================================================================
    // 폼 데이터 채우기 (PMFormPopulator 위임)
    // =========================================================================

    populateMaturityForm(data) {
        return PMFormPopulator.populateMaturityForm(data);
    },

    populateOpportunitiesForm(data) {
        return PMFormPopulator.populateOpportunitiesForm(data);
    },

    populateRoadmapForm(data) {
        return PMFormPopulator.populateRoadmapForm(data);
    },

    populateCompanyProfileForm(data) {
        return PMFormPopulator.populateCompanyProfileForm(data);
    },

    // =========================================================================
    // 현재 페이지/스테이지 저장
    // =========================================================================

    async saveCurrentStage() {
        if (!this.currentProjectId) {
            this.showNotification('먼저 프로젝트를 선택해주세요.', 'warning');
            return;
        }

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

        this.showNotification('저장할 데이터가 없습니다.', 'info');
    }
};

// DOM 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    ProjectManager.init();
});

// 전역 함수로 노출
window.ProjectManager = ProjectManager;

// ISO 42001 AIMS 전역 함수
window.saveAimsChecklist = () => PMAims.saveAimsChecklist();
window.exportAimsChecklist = () => PMAims.exportAimsChecklist();
window.saveRiskRegister = () => PMAims.saveRiskRegister();
window.addNewRisk = () => PMAims.addNewRisk();
window.editRisk = (id) => PMAims.editRisk(id);
window.deleteRisk = (id) => PMAims.deleteRisk(id);
window.saveImpactAssessment = () => PMAims.saveImpactAssessment();
window.loadImpactAssessment = () => PMAims.loadImpactAssessment();
window.exportImpactAssessment = () => PMAims.exportImpactAssessment();
window.saveModelCard = () => PMAims.saveModelCard();
window.loadModelCard = () => PMAims.loadModelCard();
window.exportModelCard = () => PMAims.exportModelCard();
window.saveDataSheet = () => PMAims.saveDataSheet();
window.loadDataSheet = () => PMAims.loadDataSheet();
window.exportDataSheet = () => PMAims.exportDataSheet();
window.saveAudit = () => PMAims.saveAudit();
window.loadAudit = () => PMAims.loadAudit();
window.exportAudit = () => PMAims.exportAudit();

// ISO 23053 ML Framework 전역 함수
window.saveMlChecklist = () => PMMlFramework.saveMlChecklist();
window.exportMlChecklist = () => PMMlFramework.exportMlChecklist();
window.loadMlChecklist = () => PMMlFramework.loadMlChecklist();

