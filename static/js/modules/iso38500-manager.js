/**
 * ISO 38500 IT Governance Manager (모듈화 버전)
 * ISO/IEC 38500 IT 거버넌스 표준 기반 관리 모듈
 */

const ISO38500Manager = {
    // 저장된 데이터
    data: {
        edmCycle: { evaluate: [], direct: [], monitor: [] },
        principles: {},
        maturity: { strategy: 3, structure: 3, policy: 3, risk: 3, performance: 3, compliance: 3 },
        portfolio: []
    },

    // =========================================================================
    // 초기화
    // =========================================================================

    init() {
        this.loadFromStorage();
        this.bindEvents();
    },

    loadFromStorage() {
        const savedData = localStorage.getItem('iso38500Data');
        if (savedData) {
            try {
                this.data = JSON.parse(savedData);
            } catch (e) {
                console.error('ISO38500 데이터 로드 오류:', e);
            }
        }
    },

    saveToStorage() {
        localStorage.setItem('iso38500Data', JSON.stringify(this.data));
    },

    bindEvents() {
        document.querySelectorAll('.edm-check').forEach(cb => {
            cb.addEventListener('change', () => this.updateEDMProgress());
        });

        document.querySelectorAll('.principle-check').forEach(cb => {
            cb.addEventListener('change', () => this.updatePrincipleScore(cb.dataset.principle));
        });

        document.querySelectorAll('.maturity-select').forEach(select => {
            select.addEventListener('change', () => this.updateMaturityDisplay());
        });
    },

    // =========================================================================
    // 헬퍼 함수
    // =========================================================================

    _updateElement(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    },

    _setElementStyle(id, property, value) {
        const el = document.getElementById(id);
        if (el) el.style[property] = value;
    },

    showNotification(message, type = 'info') {
        if (typeof PMNotification !== 'undefined') {
            PMNotification.showNotification(message, type);
        } else {
            alert(message);
        }
    },

    // =========================================================================
    // IT 거버넌스 대시보드
    // =========================================================================

    loadDashboard() {
        this.loadFromStorage();
        this.updateDashboardStats();
        this.updatePrinciplesBars();
    },

    updateDashboardStats() {
        const { evaluate, direct, monitor } = this.data.edmCycle;

        this._updateElement('edm-evaluate-score', evaluate.length);
        this._updateElement('edm-direct-score', direct.length);
        this._updateElement('edm-monitor-score', monitor.length);

        this._setElementStyle('edm-evaluate-progress', 'width', `${(evaluate.length / 6) * 100}%`);
        this._setElementStyle('edm-direct-progress', 'width', `${(direct.length / 6) * 100}%`);
        this._setElementStyle('edm-monitor-progress', 'width', `${(monitor.length / 6) * 100}%`);
    },

    updatePrinciplesBars() {
        for (let i = 1; i <= 6; i++) {
            const principleData = this.data.principles[i] || [];
            const score = Math.round((principleData.filter(p => p).length / 6) * 100);

            this._updateElement(`principle-${i}-score`, `${score}%`);
            this._setElementStyle(`principle-${i}-bar`, 'width', `${score}%`);
        }
    },

    // =========================================================================
    // EDM 사이클 관리
    // =========================================================================

    loadEDMCycle() {
        this.loadFromStorage();
        this.restoreEDMCheckboxes();
    },

    restoreEDMCheckboxes() {
        ['evaluate', 'direct', 'monitor'].forEach(phase => {
            this.data.edmCycle[phase].forEach(id => {
                const el = document.getElementById(id);
                if (el) el.checked = true;
            });
        });
        this.updateEDMProgress();
    },

    updateEDMProgress() {
        const phases = { evaluate: [], direct: [], monitor: [] };

        document.querySelectorAll('.edm-check').forEach(cb => {
            if (cb.checked) {
                const phase = cb.dataset.phase;
                if (phases[phase]) phases[phase].push(cb.id);
            }
        });

        this.data.edmCycle = phases;
    },

    calculateEDMProgress() {
        this.updateEDMProgress();

        const { evaluate, direct, monitor } = this.data.edmCycle;
        const evalPercent = Math.round((evaluate.length / 6) * 100);
        const directPercent = Math.round((direct.length / 6) * 100);
        const monitorPercent = Math.round((monitor.length / 6) * 100);
        const totalPercent = Math.round((evalPercent + directPercent + monitorPercent) / 3);

        alert(`EDM 사이클 진행률:\n\n평가 (Evaluate): ${evalPercent}%\n지휘 (Direct): ${directPercent}%\n모니터링 (Monitor): ${monitorPercent}%\n\n전체 진행률: ${totalPercent}%`);
    },

    saveEDMCycle() {
        this.updateEDMProgress();
        this.saveToStorage();
        this.showNotification('EDM 사이클 활동이 저장되었습니다.', 'success');
    },

    // =========================================================================
    // 6대 원칙 체크리스트
    // =========================================================================

    loadPrinciples() {
        this.loadFromStorage();
        this.restorePrincipleCheckboxes();
    },

    restorePrincipleCheckboxes() {
        for (let i = 1; i <= 6; i++) {
            const principleData = this.data.principles[i] || [];
            for (let j = 1; j <= 6; j++) {
                const el = document.getElementById(`p${i}-${j}`);
                if (el && principleData[j - 1]) el.checked = true;
            }
            this.updatePrincipleScore(i);
        }
    },

    updatePrincipleScore(principleNum) {
        const checkboxes = document.querySelectorAll(`[data-principle="${principleNum}"]`);
        const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
        const score = Math.round((checked / checkboxes.length) * 100);

        this._updateElement(`principle${principleNum}-badge`, `${score}%`);

        if (!this.data.principles[principleNum]) {
            this.data.principles[principleNum] = [];
        }
        this.data.principles[principleNum] = Array.from(checkboxes).map(cb => cb.checked);
    },

    calculatePrinciplesScore() {
        let totalScore = 0;
        const principleNames = ['책임', '전략', '획득', '성과', '적합성', '인간 행동'];

        let message = '6대 원칙 준수율:\n\n';
        for (let i = 1; i <= 6; i++) {
            const checkboxes = document.querySelectorAll(`[data-principle="${i}"]`);
            const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
            const score = Math.round((checked / checkboxes.length) * 100);
            totalScore += score;
            message += `${i}. ${principleNames[i-1]}: ${score}%\n`;
        }

        message += `\n전체 평균 준수율: ${Math.round(totalScore / 6)}%`;
        alert(message);
    },

    savePrinciples() {
        for (let i = 1; i <= 6; i++) {
            const checkboxes = document.querySelectorAll(`[data-principle="${i}"]`);
            this.data.principles[i] = Array.from(checkboxes).map(cb => cb.checked);
        }
        this.saveToStorage();
        this.showNotification('6대 원칙 체크리스트가 저장되었습니다.', 'success');
    },

    // =========================================================================
    // RACI 매트릭스
    // =========================================================================

    loadRACIMatrix() {
        // 정적 데이터이므로 특별한 로딩 불필요
    },

    // =========================================================================
    // AI 포트폴리오 관리
    // =========================================================================

    loadPortfolio() {
        this.loadFromStorage();
        this.updatePortfolioDisplay();
    },

    updatePortfolioDisplay() {
        const p = this.data.portfolio || {
            total: 25, active: 18, completed: 7, investment: 50,
            core: 15, adjacent: 7, transform: 3,
            roi: 85, success: 75, value: 90, satisfaction: 4.2
        };

        const updates = [
            ['portfolio-total', p.total || 0],
            ['portfolio-active', p.active || 0],
            ['portfolio-completed', p.completed || 0],
            ['portfolio-investment', (p.investment || 0) + '억'],
            ['portfolio-core', (p.core || 0) + '건'],
            ['portfolio-adjacent', (p.adjacent || 0) + '건'],
            ['portfolio-transform', (p.transform || 0) + '건']
        ];

        updates.forEach(([id, val]) => this._updateElement(id, val));

        // KPI 업데이트
        const kpis = [
            ['kpi-roi', p.roi || 0, 150],
            ['kpi-success', p.success || 0, 80],
            ['kpi-value', p.value || 0, 90],
            ['kpi-satisfaction', (p.satisfaction || 0) + '/5.0', 4, true]
        ];

        kpis.forEach(([id, val, max, isSatisfaction]) => {
            this._updateElement(id, isSatisfaction ? val : val + '%');
            const barPercent = isSatisfaction 
                ? ((parseFloat(val) / max) * 100) 
                : Math.min((val / max) * 100, 100);
            this._setElementStyle(`${id}-bar`, 'width', barPercent + '%');
        });
    },

    // =========================================================================
    // 경영진 대시보드
    // =========================================================================

    loadExecutiveDashboard() {
        this.loadFromStorage();
        this.renderExecutiveCharts();
    },

    renderExecutiveCharts() {
        if (typeof Chart === 'undefined') return;

        // 프로젝트 상태 차트
        const projectCtx = document.getElementById('execProjectChart');
        if (projectCtx) {
            new Chart(projectCtx.getContext('2d'), {
                type: 'doughnut',
                data: {
                    labels: ['기획', '개발', '파일럿', '운영', '종료'],
                    datasets: [{
                        data: [5, 8, 3, 7, 2],
                        backgroundColor: ['#6f42c1', '#0d6efd', '#0dcaf0', '#198754', '#6c757d']
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } }
                }
            });
        }

        // 분기별 성과 차트
        const performanceCtx = document.getElementById('execPerformanceChart');
        if (performanceCtx) {
            new Chart(performanceCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [
                        { label: 'ROI 실현율', data: [65, 75, 80, 85], borderColor: '#198754', tension: 0.3 },
                        { label: '프로젝트 성공률', data: [70, 72, 75, 75], borderColor: '#0d6efd', tension: 0.3 }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { position: 'bottom' } },
                    scales: { y: { beginAtZero: true, max: 100 } }
                }
            });
        }
    },

    // =========================================================================
    // 거버넌스 성숙도 평가
    // =========================================================================

    loadMaturity() {
        this.loadFromStorage();
        this.restoreMaturitySelections();
        this.updateMaturityDisplay();
    },

    restoreMaturitySelections() {
        document.querySelectorAll('.maturity-select').forEach(select => {
            const area = select.dataset.area;
            if (this.data.maturity[area]) {
                select.value = this.data.maturity[area];
            }
        });
    },

    updateMaturityDisplay() {
        let total = 0, count = 0;

        document.querySelectorAll('.maturity-select').forEach(select => {
            const area = select.dataset.area;
            const value = parseInt(select.value);
            this.data.maturity[area] = value;
            total += value;
            count++;
        });

        const avgLevel = Math.round(total / count);
        const levelNames = {
            1: '초기 (Initial)', 2: '반복 (Repeatable)', 3: '정의 (Defined)',
            4: '관리 (Managed)', 5: '최적화 (Optimized)'
        };
        const levelDescs = {
            1: '비공식적 거버넌스, 개인 의존적',
            2: '기본 프로세스 존재, 일부 문서화',
            3: '표준화된 프로세스, 조직 전체 적용',
            4: '정량적 관리, 데이터 기반 의사결정',
            5: '지속적 개선, 산업 선도적 실무'
        };

        this._updateElement('maturity-current-level', avgLevel);
        this._updateElement('maturity-current-name', levelNames[avgLevel]);
        this._updateElement('maturity-current-desc', levelDescs[avgLevel]);
    },

    calculateMaturityLevel() {
        this.updateMaturityDisplay();

        const areas = ['전략적 정렬', '거버넌스 구조', '정책 및 표준', '리스크 관리', '성과 관리', '준수 관리'];
        const keys = ['strategy', 'structure', 'policy', 'risk', 'performance', 'compliance'];

        let message = '영역별 성숙도:\n\n';
        let total = 0;

        keys.forEach((key, i) => {
            const level = this.data.maturity[key];
            total += level;
            message += `${areas[i]}: Level ${level}\n`;
        });

        message += `\n전체 평균: Level ${(total / keys.length).toFixed(1)}`;
        alert(message);
    },

    saveMaturityAssessment() {
        this.updateMaturityDisplay();
        this.saveToStorage();
        this.showNotification('거버넌스 성숙도 평가가 저장되었습니다.', 'success');
    }
};

// DOM 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    ISO38500Manager.init();
});

// 전역 노출
window.ISO38500Manager = ISO38500Manager;

