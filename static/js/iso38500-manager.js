/**
 * ISO 38500 IT Governance Manager
 * ISO/IEC 38500 IT 거버넌스 표준 기반 관리 모듈
 */

const ISO38500Manager = {
    // 저장된 데이터
    data: {
        edmCycle: {
            evaluate: [],
            direct: [],
            monitor: []
        },
        principles: {},
        maturity: {
            strategy: 3,
            structure: 3,
            policy: 3,
            risk: 3,
            performance: 3,
            compliance: 3
        },
        portfolio: []
    },

    // 초기화
    init: function() {
        this.loadFromStorage();
        this.bindEvents();
    },

    // 로컬 스토리지에서 데이터 로드
    loadFromStorage: function() {
        const savedData = localStorage.getItem('iso38500Data');
        if (savedData) {
            try {
                this.data = JSON.parse(savedData);
            } catch (e) {
                console.error('ISO38500 데이터 로드 오류:', e);
            }
        }
    },

    // 로컬 스토리지에 데이터 저장
    saveToStorage: function() {
        localStorage.setItem('iso38500Data', JSON.stringify(this.data));
    },

    // 이벤트 바인딩
    bindEvents: function() {
        // EDM 체크박스 이벤트
        document.querySelectorAll('.edm-check').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateEDMProgress();
            });
        });

        // 원칙 체크박스 이벤트
        document.querySelectorAll('.principle-check').forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updatePrincipleScore(checkbox.dataset.principle);
            });
        });

        // 성숙도 선택 이벤트
        document.querySelectorAll('.maturity-select').forEach(select => {
            select.addEventListener('change', () => {
                this.updateMaturityDisplay();
            });
        });
    },

    // =========================================
    // IT 거버넌스 대시보드
    // =========================================
    loadDashboard: function() {
        this.loadFromStorage();
        this.updateDashboardStats();
        this.updatePrinciplesBars();
    },

    updateDashboardStats: function() {
        // EDM 통계 업데이트
        const evaluateCount = this.data.edmCycle.evaluate.length;
        const directCount = this.data.edmCycle.direct.length;
        const monitorCount = this.data.edmCycle.monitor.length;

        document.getElementById('edm-evaluate-score').textContent = evaluateCount;
        document.getElementById('edm-direct-score').textContent = directCount;
        document.getElementById('edm-monitor-score').textContent = monitorCount;

        document.getElementById('edm-evaluate-progress').style.width = `${(evaluateCount / 6) * 100}%`;
        document.getElementById('edm-direct-progress').style.width = `${(directCount / 6) * 100}%`;
        document.getElementById('edm-monitor-progress').style.width = `${(monitorCount / 6) * 100}%`;
    },

    updatePrinciplesBars: function() {
        for (let i = 1; i <= 6; i++) {
            const principleData = this.data.principles[i] || [];
            const score = Math.round((principleData.filter(p => p).length / 6) * 100);
            
            const scoreEl = document.getElementById(`principle-${i}-score`);
            const barEl = document.getElementById(`principle-${i}-bar`);
            
            if (scoreEl) scoreEl.textContent = `${score}%`;
            if (barEl) barEl.style.width = `${score}%`;
        }
    },

    // =========================================
    // EDM 사이클 관리
    // =========================================
    loadEDMCycle: function() {
        this.loadFromStorage();
        this.restoreEDMCheckboxes();
    },

    restoreEDMCheckboxes: function() {
        // 저장된 체크 상태 복원
        this.data.edmCycle.evaluate.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.checked = true;
        });
        this.data.edmCycle.direct.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.checked = true;
        });
        this.data.edmCycle.monitor.forEach(id => {
            const el = document.getElementById(id);
            if (el) el.checked = true;
        });
        this.updateEDMProgress();
    },

    updateEDMProgress: function() {
        const evaluate = [];
        const direct = [];
        const monitor = [];

        document.querySelectorAll('.edm-check').forEach(checkbox => {
            if (checkbox.checked) {
                const phase = checkbox.dataset.phase;
                if (phase === 'evaluate') evaluate.push(checkbox.id);
                else if (phase === 'direct') direct.push(checkbox.id);
                else if (phase === 'monitor') monitor.push(checkbox.id);
            }
        });

        this.data.edmCycle = { evaluate, direct, monitor };
    },

    calculateEDMProgress: function() {
        this.updateEDMProgress();
        
        const evaluatePercent = (this.data.edmCycle.evaluate.length / 6) * 100;
        const directPercent = (this.data.edmCycle.direct.length / 6) * 100;
        const monitorPercent = (this.data.edmCycle.monitor.length / 6) * 100;
        const totalPercent = Math.round((evaluatePercent + directPercent + monitorPercent) / 3);

        alert(`EDM 사이클 진행률:
        
평가 (Evaluate): ${Math.round(evaluatePercent)}%
지휘 (Direct): ${Math.round(directPercent)}%
모니터링 (Monitor): ${Math.round(monitorPercent)}%

전체 진행률: ${totalPercent}%`);
    },

    saveEDMCycle: function() {
        this.updateEDMProgress();
        this.saveToStorage();
        alert('EDM 사이클 활동이 저장되었습니다.');
    },

    // =========================================
    // 6대 원칙 체크리스트
    // =========================================
    loadPrinciples: function() {
        this.loadFromStorage();
        this.restorePrincipleCheckboxes();
    },

    restorePrincipleCheckboxes: function() {
        for (let i = 1; i <= 6; i++) {
            const principleData = this.data.principles[i] || [];
            for (let j = 1; j <= 6; j++) {
                const el = document.getElementById(`p${i}-${j}`);
                if (el && principleData[j - 1]) {
                    el.checked = true;
                }
            }
            this.updatePrincipleScore(i);
        }
    },

    updatePrincipleScore: function(principleNum) {
        const checkboxes = document.querySelectorAll(`[data-principle="${principleNum}"]`);
        const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
        const score = Math.round((checked / checkboxes.length) * 100);
        
        const badge = document.getElementById(`principle${principleNum}-badge`);
        if (badge) badge.textContent = `${score}%`;

        // 데이터 업데이트
        if (!this.data.principles[principleNum]) {
            this.data.principles[principleNum] = [];
        }
        this.data.principles[principleNum] = Array.from(checkboxes).map(cb => cb.checked);
    },

    calculatePrinciplesScore: function() {
        let totalScore = 0;
        for (let i = 1; i <= 6; i++) {
            const checkboxes = document.querySelectorAll(`[data-principle="${i}"]`);
            const checked = Array.from(checkboxes).filter(cb => cb.checked).length;
            totalScore += (checked / checkboxes.length) * 100;
        }
        const avgScore = Math.round(totalScore / 6);

        alert(`6대 원칙 준수율:
        
1. 책임 (Responsibility): ${document.getElementById('principle1-badge').textContent}
2. 전략 (Strategy): ${document.getElementById('principle2-badge').textContent}
3. 획득 (Acquisition): ${document.getElementById('principle3-badge').textContent}
4. 성과 (Performance): ${document.getElementById('principle4-badge').textContent}
5. 적합성 (Conformance): ${document.getElementById('principle5-badge').textContent}
6. 인간 행동 (Human): ${document.getElementById('principle6-badge').textContent}

전체 평균 준수율: ${avgScore}%`);
    },

    savePrinciples: function() {
        for (let i = 1; i <= 6; i++) {
            const checkboxes = document.querySelectorAll(`[data-principle="${i}"]`);
            this.data.principles[i] = Array.from(checkboxes).map(cb => cb.checked);
        }
        this.saveToStorage();
        alert('6대 원칙 체크리스트가 저장되었습니다.');
    },

    // =========================================
    // RACI 매트릭스
    // =========================================
    loadRACIMatrix: function() {
        // RACI 매트릭스는 정적 데이터이므로 특별한 로딩 불필요
    },

    // =========================================
    // AI 포트폴리오 관리
    // =========================================
    loadPortfolio: function() {
        this.loadFromStorage();
        this.updatePortfolioDisplay();
    },

    updatePortfolioDisplay: function() {
        // 샘플 데이터 또는 저장된 데이터 표시
        const portfolioData = this.data.portfolio || {
            total: 25,
            active: 18,
            completed: 7,
            investment: 50,
            core: 15,
            adjacent: 7,
            transform: 3,
            roi: 85,
            success: 75,
            value: 90,
            satisfaction: 4.2
        };

        const el = (id) => document.getElementById(id);
        
        if (el('portfolio-total')) el('portfolio-total').textContent = portfolioData.total || 0;
        if (el('portfolio-active')) el('portfolio-active').textContent = portfolioData.active || 0;
        if (el('portfolio-completed')) el('portfolio-completed').textContent = portfolioData.completed || 0;
        if (el('portfolio-investment')) el('portfolio-investment').textContent = (portfolioData.investment || 0) + '억';
        if (el('portfolio-core')) el('portfolio-core').textContent = (portfolioData.core || 0) + '건';
        if (el('portfolio-adjacent')) el('portfolio-adjacent').textContent = (portfolioData.adjacent || 0) + '건';
        if (el('portfolio-transform')) el('portfolio-transform').textContent = (portfolioData.transform || 0) + '건';

        // KPI 업데이트
        if (el('kpi-roi')) {
            el('kpi-roi').textContent = (portfolioData.roi || 0) + '%';
            el('kpi-roi-bar').style.width = Math.min((portfolioData.roi / 150) * 100, 100) + '%';
        }
        if (el('kpi-success')) {
            el('kpi-success').textContent = (portfolioData.success || 0) + '%';
            el('kpi-success-bar').style.width = (portfolioData.success / 80) * 100 + '%';
        }
        if (el('kpi-value')) {
            el('kpi-value').textContent = (portfolioData.value || 0) + '%';
            el('kpi-value-bar').style.width = (portfolioData.value / 90) * 100 + '%';
        }
        if (el('kpi-satisfaction')) {
            el('kpi-satisfaction').textContent = (portfolioData.satisfaction || 0) + '/5.0';
            el('kpi-satisfaction-bar').style.width = ((portfolioData.satisfaction / 4) * 100) + '%';
        }
    },

    // =========================================
    // 경영진 대시보드
    // =========================================
    loadExecutiveDashboard: function() {
        this.loadFromStorage();
        this.renderExecutiveCharts();
    },

    renderExecutiveCharts: function() {
        // 프로젝트 상태 차트
        const projectCtx = document.getElementById('execProjectChart');
        if (projectCtx && typeof Chart !== 'undefined') {
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
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    }
                }
            });
        }

        // 분기별 성과 차트
        const performanceCtx = document.getElementById('execPerformanceChart');
        if (performanceCtx && typeof Chart !== 'undefined') {
            new Chart(performanceCtx.getContext('2d'), {
                type: 'line',
                data: {
                    labels: ['Q1', 'Q2', 'Q3', 'Q4'],
                    datasets: [{
                        label: 'ROI 실현율',
                        data: [65, 75, 80, 85],
                        borderColor: '#198754',
                        tension: 0.3
                    }, {
                        label: '프로젝트 성공률',
                        data: [70, 72, 75, 75],
                        borderColor: '#0d6efd',
                        tension: 0.3
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            position: 'bottom'
                        }
                    },
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
        }
    },

    // =========================================
    // 거버넌스 성숙도 평가
    // =========================================
    loadMaturity: function() {
        this.loadFromStorage();
        this.restoreMaturitySelections();
        this.updateMaturityDisplay();
    },

    restoreMaturitySelections: function() {
        document.querySelectorAll('.maturity-select').forEach(select => {
            const area = select.dataset.area;
            if (this.data.maturity[area]) {
                select.value = this.data.maturity[area];
            }
        });
    },

    updateMaturityDisplay: function() {
        let total = 0;
        let count = 0;
        
        document.querySelectorAll('.maturity-select').forEach(select => {
            const area = select.dataset.area;
            const value = parseInt(select.value);
            this.data.maturity[area] = value;
            total += value;
            count++;
        });

        const avgLevel = Math.round(total / count);
        const levelNames = {
            1: '초기 (Initial)',
            2: '반복 (Repeatable)',
            3: '정의 (Defined)',
            4: '관리 (Managed)',
            5: '최적화 (Optimized)'
        };
        const levelDescs = {
            1: '비공식적 거버넌스, 개인 의존적',
            2: '기본 프로세스 존재, 일부 문서화',
            3: '표준화된 프로세스, 조직 전체 적용',
            4: '정량적 관리, 데이터 기반 의사결정',
            5: '지속적 개선, 산업 선도적 실무'
        };

        const currentLevelEl = document.getElementById('maturity-current-level');
        const currentNameEl = document.getElementById('maturity-current-name');
        const currentDescEl = document.getElementById('maturity-current-desc');

        if (currentLevelEl) currentLevelEl.textContent = avgLevel;
        if (currentNameEl) currentNameEl.textContent = levelNames[avgLevel];
        if (currentDescEl) currentDescEl.textContent = levelDescs[avgLevel];
    },

    calculateMaturityLevel: function() {
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

        const avg = (total / keys.length).toFixed(1);
        message += `\n전체 평균: Level ${avg}`;

        alert(message);
    },

    saveMaturityAssessment: function() {
        this.updateMaturityDisplay();
        this.saveToStorage();
        alert('거버넌스 성숙도 평가가 저장되었습니다.');
    }
};

// DOM 로드 시 초기화
document.addEventListener('DOMContentLoaded', function() {
    ISO38500Manager.init();
});

