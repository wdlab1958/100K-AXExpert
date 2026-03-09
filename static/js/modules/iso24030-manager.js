/**
 * ISO 24030 AI Assessment Manager (모듈화 버전)
 * AI 시스템 및 역량 평가 관리 모듈
 */

const ISO24030Manager = {
    // API Base URL
    API_BASE: '/api/v1',

    // 현재 프로젝트 ID
    currentProjectId: null,

    // 현재 선택된 보고서 유형
    currentReportType: 'detailed',

    // 데이터 캐시
    data: {
        survey: {},
        inventory: [],
        riskAssessment: {},
        fairness: {},
        governance: {},
        roadmap: []
    },

    // =========================================================================
    // 초기화
    // =========================================================================

    init() {
        console.log('ISO24030Manager initializing...');
        this.bindEvents();
        this.loadFromLocalStorage();
    },

    bindEvents() {
        document.querySelectorAll('.maturity-survey-item').forEach(item => {
            item.addEventListener('change', () => this.updateSurveyProgress());
        });

        document.querySelectorAll('.gov-check').forEach(item => {
            item.addEventListener('change', () => this.updateGovernanceProgress());
        });

        document.querySelectorAll('.fairness-check').forEach(item => {
            item.addEventListener('change', () => this.updateFairnessProgress());
        });
    },

    // =========================================================================
    // 대시보드
    // =========================================================================

    loadDashboard() {
        this.loadFromLocalStorage();
        this.updateDashboardStats();
        this.initMaturityChart();
    },

    updateDashboardStats() {
        const maturityScore = this.calculateOverallMaturity();
        this._updateElement('iso24030-maturity-score', maturityScore.toFixed(1));

        const systemCount = this.data.inventory.length;
        this._updateElement('iso24030-system-count', systemCount);

        const highRiskCount = this.data.inventory.filter(s => s.riskLevel === 'high' || s.riskLevel === 'critical').length;
        this._updateElement('iso24030-high-risk', highRiskCount);

        const complianceRate = this.calculateGovernanceCompliance();
        this._updateElement('iso24030-compliance', complianceRate + '%');
    },

    _updateElement(id, value) {
        const el = document.getElementById(id);
        if (el) el.textContent = value;
    },

    initMaturityChart() {
        const ctx = document.getElementById('iso24030MaturityChart');
        if (!ctx || typeof Chart === 'undefined') return;

        const scores = this.getSurveyScoresByCategory();

        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['전략/리더십', '인력/역량', '데이터', '기술/인프라', '거버넌스'],
                datasets: [{
                    label: '현재 성숙도',
                    data: [scores.strategy, scores.people, scores.data, scores.tech, scores.governance],
                    backgroundColor: [
                        'rgba(79, 145, 255, 0.7)',
                        'rgba(16, 185, 129, 0.7)',
                        'rgba(6, 182, 212, 0.7)',
                        'rgba(245, 158, 11, 0.7)',
                        'rgba(107, 114, 128, 0.7)'
                    ],
                    borderWidth: 1
                }, {
                    label: '목표 성숙도',
                    data: [4, 4, 4, 4, 4],
                    backgroundColor: 'rgba(139, 92, 246, 0.3)',
                    type: 'line'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 5, ticks: { stepSize: 1 } } },
                plugins: { legend: { position: 'bottom' } }
            }
        });
    },

    // =========================================================================
    // 성숙도 진단 설문
    // =========================================================================

    loadSurvey() {
        this.loadFromLocalStorage();
        this.restoreSurveyAnswers();
        this.updateSurveyProgress();
    },

    restoreSurveyAnswers() {
        if (!this.data.survey) return;

        Object.keys(this.data.survey).forEach(key => {
            const radio = document.querySelector(`input[name="${key}"][value="${this.data.survey[key]}"]`);
            if (radio) radio.checked = true;
        });
    },

    updateSurveyProgress() {
        const totalQuestions = document.querySelectorAll('.maturity-survey-item').length / 5;
        const answeredQuestions = document.querySelectorAll('.maturity-survey-item:checked').length;
        const progress = Math.round((answeredQuestions / totalQuestions) * 100);

        this._updateElement('surveyProgress', progress + '%');
        const progressBar = document.getElementById('surveyProgressBar');
        if (progressBar) progressBar.style.width = progress + '%';
    },

    calculateSurveyResults() {
        const scores = this.getSurveyScoresByCategory();
        const overallScore = this.calculateOverallMaturity();

        this._updateElement('surveyOverallScore', overallScore.toFixed(1));

        const levelEl = document.getElementById('surveyMaturityLevel');
        if (levelEl) {
            const levels = [
                [1.5, 'Level 1: 초기'], [2.5, 'Level 2: 탐색'],
                [3.5, 'Level 3: 정의됨'], [4.5, 'Level 4: 관리됨'],
                [Infinity, 'Level 5: 최적화']
            ];
            levelEl.textContent = levels.find(([threshold]) => overallScore < threshold)[1];
        }

        const recEl = document.getElementById('surveyRecommendation');
        if (recEl) {
            const categories = Object.entries(scores).filter(([, v]) => v > 0);
            if (categories.length > 0) {
                const lowest = categories.sort((a, b) => a[1] - b[1])[0];
                const names = { strategy: '전략/리더십', people: '인력/역량', data: '데이터', tech: '기술/인프라', governance: '거버넌스' };
                recEl.textContent = names[lowest[0]] || '-';
            }
        }

        this.showNotification('설문 결과가 분석되었습니다.', 'success');
    },

    getSurveyScoresByCategory() {
        const scores = { strategy: 0, people: 0, data: 0, tech: 0, governance: 0 };
        const counts = { strategy: 0, people: 0, data: 0, tech: 0, governance: 0 };

        const categoryRanges = [
            ['strategy', 'q1_', 3], ['people', 'q2_', 2], ['data', 'q3_', 3],
            ['tech', 'q4_', 2], ['governance', 'q5_', 3]
        ];

        categoryRanges.forEach(([category, prefix, count]) => {
            for (let i = 1; i <= count; i++) {
                const checked = document.querySelector(`input[name="${prefix}${i}"]:checked`);
                if (checked) {
                    scores[category] += parseInt(checked.value);
                    counts[category]++;
                }
            }
        });

        Object.keys(scores).forEach(key => {
            scores[key] = counts[key] > 0 ? scores[key] / counts[key] : 0;
        });

        return scores;
    },

    calculateOverallMaturity() {
        const scores = this.getSurveyScoresByCategory();
        const values = Object.values(scores).filter(v => v > 0);
        return values.length > 0 ? values.reduce((a, b) => a + b, 0) / values.length : 0;
    },

    saveSurvey() {
        const survey = {};
        document.querySelectorAll('.maturity-survey-item:checked').forEach(item => {
            survey[item.name] = item.value;
        });

        this.data.survey = survey;
        this.saveToLocalStorage();
        this.showNotification('성숙도 진단 설문이 저장되었습니다.', 'success');
    },

    // =========================================================================
    // AI 시스템 인벤토리
    // =========================================================================

    loadInventory() {
        this.loadFromLocalStorage();
        this.renderInventoryTable();
        this.updateInventoryStats();
    },

    updateInventoryStats() {
        const total = this.data.inventory.length;
        const active = this.data.inventory.filter(s => s.status === 'active').length;
        const dev = this.data.inventory.filter(s => s.status === 'development').length;
        const highRisk = this.data.inventory.filter(s => s.riskLevel === 'high' || s.riskLevel === 'critical').length;

        this._updateElement('inventoryTotalSystems', total);
        this._updateElement('inventoryActiveSystems', active);
        this._updateElement('inventoryDevSystems', dev);
        this._updateElement('inventoryHighRiskSystems', highRisk);
    },

    renderInventoryTable() {
        const tbody = document.getElementById('aiSystemInventoryTable');
        if (!tbody) return;

        if (this.data.inventory.length === 0) {
            tbody.innerHTML = `<tr><td colspan="7" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>등록된 AI 시스템이 없습니다.
            </td></tr>`;
            return;
        }

        tbody.innerHTML = this.data.inventory.map((system, index) => `
            <tr>
                <td><strong>${system.name}</strong></td>
                <td><span class="badge bg-info">${system.type || 'ML'}</span></td>
                <td>${this._getBadge('risk', system.riskLevel)}</td>
                <td>${this._getBadge('status', system.status)}</td>
                <td>${system.owner || '-'}</td>
                <td>${system.lastAssessment || '-'}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <button class="btn btn-outline-primary" onclick="ISO24030Manager.editSystem(${index})">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-outline-danger" onclick="ISO24030Manager.deleteSystem(${index})">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
        `).join('');
    },

    _getBadge(type, value) {
        const badges = {
            risk:     { low: ['success', '낮음'], medium: ['warning', '중간'], high: ['danger', '높음'], critical: ['dark', '심각'] },
            status:   { development: ['info', '개발 중'], active: ['success', '운영 중'], retired: ['secondary', '폐기'],
                        pending: ['secondary', '대기'], 'in-progress': ['primary', '진행 중'], completed: ['success', '완료'] },
            category: { strategy: ['primary', '전략'], people: ['info', '인력'], data: ['warning', '데이터'],
                        tech: ['success', '기술'], governance: ['danger', '거버넌스'] },
            priority: { critical: ['dark', '심각'], high: ['danger', '높음'], medium: ['warning', '중간'], low: ['secondary', '낮음'] },
        };
        const map = badges[type];
        if (!map) return `<span class="badge bg-secondary">${value || '-'}</span>`;
        const [color, text] = map[value] || ['secondary', value || '-'];
        return `<span class="badge bg-${color}">${text}</span>`;
    },

    showAddSystemModal() {
        const name = prompt('AI 시스템 이름을 입력하세요:');
        if (!name) return;

        const system = {
            id: Date.now(),
            name,
            type: prompt('시스템 유형 (ML, DL, NLP, CV 등):', 'ML') || 'ML',
            owner: prompt('담당자 이름:') || '-',
            riskLevel: prompt('위험 등급 (low, medium, high, critical):', 'medium') || 'medium',
            status: prompt('상태 (development, active, retired):', 'development') || 'development',
            lastAssessment: new Date().toLocaleDateString('ko-KR'),
            createdAt: new Date().toISOString()
        };

        this.data.inventory.push(system);
        this.saveToLocalStorage();
        this.renderInventoryTable();
        this.updateInventoryStats();
        this.showNotification('AI 시스템이 등록되었습니다.', 'success');
    },

    deleteSystem(index) {
        if (!confirm('이 AI 시스템을 삭제하시겠습니까?')) return;

        this.data.inventory.splice(index, 1);
        this.saveToLocalStorage();
        this.renderInventoryTable();
        this.updateInventoryStats();
        this.showNotification('AI 시스템이 삭제되었습니다.', 'info');
    },

    // =========================================================================
    // 위험 평가 매트릭스
    // =========================================================================

    loadRiskMatrix() {
        this.loadFromLocalStorage();
        this.restoreRiskAssessment();
    },

    restoreRiskAssessment() {
        if (!this.data.riskAssessment) return;

        document.querySelectorAll('.risk-assessment-item').forEach(select => {
            const key = `${select.dataset.category}_${select.dataset.item}`;
            if (this.data.riskAssessment[key]) {
                select.value = this.data.riskAssessment[key];
            }
        });
    },

    selectRiskCell(impact, likelihood) {
        const level = this._getRiskLevel(impact * likelihood);
        alert(`위험 수준: ${level}\n영향도: ${impact}, 발생가능성: ${likelihood}`);
    },

    _getRiskLevel(score) {
        if (score >= 20) return 'Critical (심각)';
        if (score >= 12) return 'High (높음)';
        if (score >= 6) return 'Medium (중간)';
        return 'Low (낮음)';
    },

    calculateRiskScore() {
        let totalScore = 0, count = 0;

        document.querySelectorAll('.risk-assessment-item').forEach(select => {
            if (select.value) {
                totalScore += parseInt(select.value);
                count++;
            }
        });

        const avgScore = count > 0 ? (totalScore / count).toFixed(1) : 0;
        alert(`위험 평가 결과\n\n평균 위험 점수: ${avgScore}\n위험 수준: ${this._getRiskLevel(avgScore * 5)}`);
        this.showNotification('위험 점수가 계산되었습니다.', 'success');
    },

    saveRiskAssessment() {
        const assessment = {};
        document.querySelectorAll('.risk-assessment-item').forEach(select => {
            assessment[`${select.dataset.category}_${select.dataset.item}`] = select.value;
        });

        this.data.riskAssessment = assessment;
        this.saveToLocalStorage();
        this.showNotification('위험 평가가 저장되었습니다.', 'success');
    },

    // =========================================================================
    // 공정성 대시보드
    // =========================================================================

    loadFairnessDashboard() {
        this.loadFromLocalStorage();
        this.restoreFairnessChecklist();
        this.initFairnessTrendChart();
    },

    restoreFairnessChecklist() {
        if (!this.data.fairness?.checklist) return;
        this.data.fairness.checklist.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) checkbox.checked = true;
        });
    },

    initFairnessTrendChart() {
        const ctx = document.getElementById('fairnessTrendChart');
        if (!ctx || typeof Chart === 'undefined') return;

        new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['1월', '2월', '3월', '4월', '5월', '6월'],
                datasets: [{
                    label: '공정성 점수',
                    data: [65, 68, 72, 75, 78, 82],
                    borderColor: 'rgba(79, 145, 255, 1)',
                    backgroundColor: 'rgba(79, 145, 255, 0.1)',
                    fill: true,
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: { y: { beginAtZero: true, max: 100 } },
                plugins: { legend: { position: 'bottom' } }
            }
        });
    },

    showBiasDetail(biasType) {
        const details = {
            selection: '선택 편향: 훈련 데이터가 실제 인구를 대표하지 않을 때 발생합니다.',
            measurement: '측정 편향: 데이터 수집 과정에서 부정확한 측정이나 라벨링으로 발생합니다.',
            historical: '역사적 편향: 과거의 차별적 관행이 데이터에 반영되어 발생합니다.',
            algorithmic: '알고리즘 편향: 모델 구조나 훈련 과정에서 특정 그룹에 불리하게 작용합니다.',
            deployment: '배포 편향: 모델이 의도하지 않은 환경에서 사용될 때 발생합니다.'
        };
        alert(details[biasType] || '상세 정보를 찾을 수 없습니다.');
    },

    updateFairnessProgress() {
        const total = document.querySelectorAll('.fairness-check').length;
        const checked = document.querySelectorAll('.fairness-check:checked').length;
        this._updateElement('fairnessOverallScore', Math.round((checked / total) * 100) + '%');
    },

    saveFairnessAssessment() {
        const checklist = [];
        document.querySelectorAll('.fairness-check:checked').forEach(cb => checklist.push(cb.id));

        this.data.fairness = { checklist };
        this.saveToLocalStorage();
        this.showNotification('공정성 평가가 저장되었습니다.', 'success');
    },

    // =========================================================================
    // 거버넌스 체크리스트
    // =========================================================================

    loadGovernanceChecklist() {
        this.loadFromLocalStorage();
        this.restoreGovernanceChecklist();
        this.updateGovernanceProgress();
    },

    restoreGovernanceChecklist() {
        if (!this.data.governance?.checklist) return;
        this.data.governance.checklist.forEach(id => {
            const checkbox = document.getElementById(id);
            if (checkbox) checkbox.checked = true;
        });
    },

    calculateGovernanceCompliance() {
        const total = document.querySelectorAll('.gov-check').length;
        if (total === 0) return 0;
        return Math.round((document.querySelectorAll('.gov-check:checked').length / total) * 100);
    },

    updateGovernanceProgress() {
        const total = document.querySelectorAll('.gov-check').length;
        const checked = document.querySelectorAll('.gov-check:checked').length;
        const rate = total > 0 ? Math.round((checked / total) * 100) : 0;

        this._updateElement('govComplianceRate', rate + '%');
        this._updateElement('govCompletedItems', checked);
        this._updateElement('govPendingItems', total - checked);
    },

    saveGovernanceChecklist() {
        const checklist = [];
        document.querySelectorAll('.gov-check:checked').forEach(cb => checklist.push(cb.id));

        this.data.governance = { checklist };
        this.saveToLocalStorage();
        this.showNotification('거버넌스 체크리스트가 저장되었습니다.', 'success');
    },

    // =========================================================================
    // 보고서 / 로드맵
    // =========================================================================

    loadReportGenerator() {
        this.loadFromLocalStorage();
        const typeNames = { executive: '경영진 요약 보고서', detailed: '상세 평가 보고서', compliance: '규정 준수 보고서', improvement: '개선 계획 보고서' };
        const labelEl = document.getElementById('reportPreviewTypeLabel');
        if (labelEl) labelEl.textContent = typeNames[this.currentReportType] || '상세 평가 보고서';
        this.refreshReportPreview();
    },

    selectReportType(type) {
        this.currentReportType = type;
        document.querySelectorAll('.report-type-card').forEach(card => {
            card.classList.remove('active', 'border-primary', 'border-success', 'border-warning', 'border-info');
        });
        const colorMap = { executive: 'border-primary', detailed: 'border-success', compliance: 'border-warning', improvement: 'border-info' };
        if (event && event.currentTarget) {
            event.currentTarget.classList.add('active', colorMap[type] || 'border-primary');
        }
        const typeNames = { executive: '경영진 요약 보고서', detailed: '상세 평가 보고서', compliance: '규정 준수 보고서', improvement: '개선 계획 보고서' };
        const labelEl = document.getElementById('reportPreviewTypeLabel');
        if (labelEl) labelEl.textContent = typeNames[type] || '';
        this.refreshReportPreview();
    },

    _getCheckedItems() {
        const get = (id, def) => { const el = document.getElementById(id); return el ? el.checked : def; };
        return {
            maturity:        get('rpt-maturity', true),
            inventory:       get('rpt-inventory', true),
            risk:            get('rpt-risk', true),
            fairness:        get('rpt-fairness', true),
            governance:      get('rpt-governance', true),
            gap:             get('rpt-gap', false),
            recommendations: get('rpt-recommendations', true),
            roadmap:         get('rpt-roadmap', true),
            benchmark:       get('rpt-benchmark', false),
        };
    },

    _getScores() {
        const catScores = this.getSurveyScoresByCategory();
        const maturity  = this.calculateOverallMaturity();
        const govRate   = this.calculateGovernanceCompliance();

        const fairnessChecked = document.querySelectorAll('.fairness-check:checked').length;
        const fairnessTotal   = document.querySelectorAll('.fairness-check').length || 1;
        const fairness = Math.round((fairnessChecked / fairnessTotal) * 100);

        const riskItems = document.querySelectorAll('.risk-assessment-item');
        let riskSum = 0, riskCount = 0;
        riskItems.forEach(el => { if (el.value) { riskSum += parseInt(el.value); riskCount++; } });
        const riskAvg   = riskCount > 0 ? riskSum / riskCount : 2;
        const riskLabel = riskAvg >= 4 ? '심각' : riskAvg >= 3 ? '높음' : riskAvg >= 2 ? '중간' : '낮음';
        const riskColor = riskAvg >= 3 ? 'danger' : riskAvg >= 2 ? 'warning' : 'success';

        const maturityLevel = maturity < 1.5 ? 'Level 1: 초기' :
                              maturity < 2.5 ? 'Level 2: 탐색' :
                              maturity < 3.5 ? 'Level 3: 정의됨' :
                              maturity < 4.5 ? 'Level 4: 관리됨' : 'Level 5: 최적화';

        const systemTotal = this.data.inventory.length;
        const systemHigh  = this.data.inventory.filter(s => s.riskLevel === 'high' || s.riskLevel === 'critical').length;

        return { catScores, maturity, maturityLevel, govRate, fairness, riskAvg, riskLabel, riskColor, systemTotal, systemHigh };
    },

    refreshReportPreview() {
        try {
            const container = document.getElementById('reportPreviewContent');
            if (!container) return;

            const type = this.currentReportType || 'detailed';
            const items = this._getCheckedItems();
            const s     = this._getScores();
            const now   = new Date().toLocaleDateString('ko-KR');

            const typeConfig = {
                executive:   { title: '경영진 요약 보고서',  subtitle: '핵심 지표 및 전략적 권고사항 요약',          badge: 'primary', icon: 'bi-briefcase'      },
                detailed:    { title: '상세 평가 보고서',    subtitle: 'ISO 24030 기반 AI 시스템 영역별 상세 분석',   badge: 'success', icon: 'bi-file-text'       },
                compliance:  { title: '규정 준수 보고서',    subtitle: 'ISO/규제 준수 현황 및 미준수 항목 분석',      badge: 'warning', icon: 'bi-shield-check'    },
                improvement: { title: '개선 계획 보고서',    subtitle: '갭 분석 기반 우선순위 개선 로드맵',           badge: 'info',    icon: 'bi-graph-up-arrow'  },
            };
            const cfg = typeConfig[type] || typeConfig.detailed;

            let no = 1;
            const sec = (title, content) => `
                <div class="rpt-section mb-4">
                    <h5 class="rpt-section-title text-dark border-bottom pb-2 mb-3">
                        <span class="badge bg-${cfg.badge} me-2">${no++}</span>${title}
                    </h5>
                    ${content}
                </div>`;

            // ── 헤더 ──
            let html = `
            <div class="rpt-doc p-4 bg-white rounded border">
                <div class="text-center mb-4 pb-3 border-bottom">
                    <span class="badge bg-${cfg.badge} fs-6 px-3 py-2 mb-2 d-inline-block">
                        <i class="bi ${cfg.icon} me-2"></i>${cfg.title}
                    </span>
                    <h3 class="text-dark mt-2 mb-1">AI 평가 보고서</h3>
                    <p class="text-muted mb-1">${cfg.subtitle}</p>
                    <small class="text-muted">생성일: ${now} | 기준: ISO 24030</small>
                </div>`;

            // ── KPI 4개 ──
            html += `
                <div class="row g-3 mb-4">
                    <div class="col-6 col-md-3 text-center">
                        <div class="card bg-primary text-white border-0 shadow-sm">
                            <div class="card-body py-3">
                                <div class="fs-4 fw-bold">${s.maturity > 0 ? s.maturity.toFixed(1) : '-'}</div>
                                <small>AI 성숙도 점수</small>
                                <div class="mt-1 opacity-75 small">${s.maturityLevel}</div>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3 text-center">
                        <div class="card bg-success text-white border-0 shadow-sm">
                            <div class="card-body py-3">
                                <div class="fs-4 fw-bold">${s.govRate}%</div>
                                <small>거버넌스 준수율</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3 text-center">
                        <div class="card bg-${s.riskColor} border-0 shadow-sm">
                            <div class="card-body py-3">
                                <div class="fs-4 fw-bold ${s.riskColor === 'warning' ? 'text-dark' : 'text-white'}">${s.riskLabel}</div>
                                <small class="${s.riskColor === 'warning' ? 'text-dark' : 'text-white'}">위험 수준</small>
                            </div>
                        </div>
                    </div>
                    <div class="col-6 col-md-3 text-center">
                        <div class="card bg-info text-white border-0 shadow-sm">
                            <div class="card-body py-3">
                                <div class="fs-4 fw-bold">${s.fairness}%</div>
                                <small>공정성 준수율</small>
                            </div>
                        </div>
                    </div>
                </div>`;

            // ── 유형별 개요 ──
            if (type === 'executive') {
                html += sec('경영진 요약', `
                    <div class="alert alert-primary border-0">
                        <strong>종합 평가:</strong> 현재 AI 성숙도 수준은 <strong>${s.maturityLevel}</strong>이며,
                        거버넌스 준수율 <strong>${s.govRate}%</strong>, 위험 수준 <strong>${s.riskLabel}</strong>으로 진단되었습니다.
                    </div>
                    <p class="text-muted">경영진의 신속한 의사결정을 위해 핵심 지표와 우선 권고사항을 요약합니다.</p>`);
            } else if (type === 'detailed') {
                html += sec('평가 개요', `
                    <table class="table table-sm table-bordered text-dark">
                        <tbody>
                            <tr><th class="bg-light" style="width:35%">평가 기준</th><td>ISO/IEC 24030:2021 AI Use Cases</td></tr>
                            <tr><th class="bg-light">평가 범위</th><td>전략/리더십, 인력/역량, 데이터, 기술/인프라, 거버넌스</td></tr>
                            <tr><th class="bg-light">평가일</th><td>${now}</td></tr>
                            <tr><th class="bg-light">등록 AI 시스템</th><td>${s.systemTotal}개 (고위험 ${s.systemHigh}개)</td></tr>
                        </tbody>
                    </table>`);
            } else if (type === 'compliance') {
                html += sec('준수 현황 개요', `
                    <div class="row g-3 mb-3">
                        <div class="col-md-4 text-center"><div class="card bg-light border-0"><div class="card-body">
                            <div class="fs-3 fw-bold text-success">${s.govRate}%</div><small class="text-muted">ISO 24030 준수율</small>
                        </div></div></div>
                        <div class="col-md-4 text-center"><div class="card bg-light border-0"><div class="card-body">
                            <div class="fs-3 fw-bold text-${s.riskColor}">${s.riskLabel}</div><small class="text-muted">규제 위험 수준</small>
                        </div></div></div>
                        <div class="col-md-4 text-center"><div class="card bg-light border-0"><div class="card-body">
                            <div class="fs-3 fw-bold text-info">${s.fairness}%</div><small class="text-muted">공정성 준수율</small>
                        </div></div></div>
                    </div>
                    <p class="text-dark small">ISO 24030, EU AI Act, 국내 AI 가이드라인 등 주요 규제 요건에 대한 준수 현황을 분석합니다.</p>`);
            } else if (type === 'improvement') {
                html += sec('현황 및 목표', `
                    <div class="row g-3">
                        <div class="col-md-6">
                            <div class="card border-warning border-2">
                                <div class="card-body text-center">
                                    <div class="fs-3 fw-bold text-warning">${s.maturity > 0 ? s.maturity.toFixed(1) : '-'}</div>
                                    <small class="text-muted">현재 성숙도 (${s.maturityLevel})</small>
                                </div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="card border-success border-2">
                                <div class="card-body text-center">
                                    <div class="fs-3 fw-bold text-success">4.0</div>
                                    <small class="text-muted">목표 성숙도 (Level 4: 관리됨)</small>
                                </div>
                            </div>
                        </div>
                    </div>`);
            }

            // ── 성숙도 진단 결과 ──
            if (items.maturity) {
                const catNames = { strategy: '전략/리더십', people: '인력/역량', data: '데이터', tech: '기술/인프라', governance: '거버넌스' };
                const rows = Object.entries(s.catScores).map(([k, v]) => {
                    const pct = Math.round(v * 20);
                    const color = v >= 3.5 ? 'success' : v >= 2.5 ? 'primary' : v >= 1.5 ? 'warning' : 'danger';
                    return `<tr>
                        <td class="text-dark">${catNames[k]}</td>
                        <td class="fw-bold text-dark">${v > 0 ? v.toFixed(1) : '-'}</td>
                        <td style="min-width:120px">
                            <div class="progress" style="height:12px">
                                <div class="progress-bar bg-${color}" style="width:${pct}%"></div>
                            </div>
                        </td>
                        <td><span class="badge bg-${color}">${v >= 3.5 ? '우수' : v >= 2.5 ? '양호' : v >= 1.5 ? '개선필요' : '미흡'}</span></td>
                    </tr>`;
                }).join('');

                if (type === 'executive') {
                    html += sec('성숙도 현황', `
                        <p class="text-dark">전체 AI 성숙도:
                            <strong class="text-primary fs-5">${s.maturity > 0 ? s.maturity.toFixed(1) : '-'}/5.0</strong>
                            <span class="badge bg-primary ms-2">${s.maturityLevel}</span>
                        </p>
                        <div class="alert alert-${s.maturity >= 3 ? 'success' : s.maturity >= 2 ? 'warning' : 'danger'} border-0">
                            ${s.maturity >= 3 ? '✅ 전반적으로 양호한 수준이나 일부 영역 강화가 필요합니다.' :
                              s.maturity >= 2 ? '⚠️ 주요 영역에서 개선이 필요합니다.' :
                              '🔴 전반적인 AI 역량 강화가 시급합니다.'}
                        </div>`);
                } else {
                    html += sec('성숙도 진단 결과', `
                        <div class="mb-3">
                            <strong class="text-dark">종합 점수: </strong>
                            <span class="badge bg-primary fs-6">${s.maturity > 0 ? s.maturity.toFixed(1) : '-'} / 5.0</span>
                            <span class="badge bg-secondary ms-2">${s.maturityLevel}</span>
                        </div>
                        <table class="table table-hover table-sm text-dark">
                            <thead class="table-dark"><tr><th>평가 영역</th><th>점수</th><th>수준</th><th>등급</th></tr></thead>
                            <tbody>${rows}</tbody>
                        </table>
                        <p class="text-muted small mt-2">* 점수: 1(초기) ~ 5(최적화), ISO 24030 성숙도 모델 적용</p>`);
                }
            }

            // ── AI 시스템 인벤토리 ──
            if (items.inventory && type !== 'executive') {
                const invRows = this.data.inventory.length > 0
                    ? this.data.inventory.map(sys => `
                        <tr>
                            <td class="fw-semibold text-dark">${sys.name}</td>
                            <td><span class="badge bg-info">${sys.type || 'ML'}</span></td>
                            <td>${this._getBadge('risk', sys.riskLevel)}</td>
                            <td>${this._getBadge('status', sys.status)}</td>
                            <td class="text-muted">${sys.owner || '-'}</td>
                            <td class="text-muted">${sys.lastAssessment || '-'}</td>
                        </tr>`).join('')
                    : `<tr><td colspan="6" class="text-center text-muted py-3">등록된 AI 시스템이 없습니다.</td></tr>`;

                html += sec('AI 시스템 인벤토리', `
                    <div class="row g-2 mb-3">
                        <div class="col-4 text-center"><div class="card bg-light border-0"><div class="card-body py-2">
                            <div class="fw-bold fs-5 text-dark">${s.systemTotal}</div><small class="text-muted">전체</small>
                        </div></div></div>
                        <div class="col-4 text-center"><div class="card bg-light border-0"><div class="card-body py-2">
                            <div class="fw-bold fs-5 text-success">${this.data.inventory.filter(x=>x.status==='active').length}</div><small class="text-muted">운영 중</small>
                        </div></div></div>
                        <div class="col-4 text-center"><div class="card bg-light border-0"><div class="card-body py-2">
                            <div class="fw-bold fs-5 text-danger">${s.systemHigh}</div><small class="text-muted">고위험</small>
                        </div></div></div>
                    </div>
                    <div class="table-responsive">
                        <table class="table table-sm table-hover text-dark">
                            <thead class="table-dark"><tr><th>시스템명</th><th>유형</th><th>위험등급</th><th>상태</th><th>담당자</th><th>평가일</th></tr></thead>
                            <tbody>${invRows}</tbody>
                        </table>
                    </div>`);
            }

            // ── 위험 평가 결과 ──
            if (items.risk) {
                if (type === 'executive') {
                    html += sec('위험 현황', `
                        <div class="d-flex align-items-center gap-3 mb-3">
                            <span class="fs-2 fw-bold text-${s.riskColor}">${s.riskLabel}</span>
                            <span class="text-muted">종합 위험 수준</span>
                        </div>
                        <ul class="text-dark">
                            <li>고위험 AI 시스템 <strong>${s.systemHigh}개</strong> 식별</li>
                            <li>위험 완화 조치 즉시 필요 항목 검토 권고</li>
                        </ul>`);
                } else {
                    const riskCats = [
                        { name: '데이터 위험',  detail: '데이터 편향, 품질, 개인정보 침해',  lv: s.riskAvg },
                        { name: '모델 위험',   detail: '성능 저하, 과적합, 설명불가능성',    lv: s.riskAvg * 0.9 },
                        { name: '운영 위험',   detail: '시스템 장애, 보안 취약점, 의존성',   lv: s.riskAvg * 1.1 },
                        { name: '규제 위험',   detail: '법적 준수 미흡, 공정성 문제',        lv: s.riskAvg * 0.8 },
                    ];
                    const riskRows = riskCats.map(rc => {
                        const lv = Math.min(rc.lv, 5);
                        const col = lv >= 3 ? 'danger' : lv >= 2 ? 'warning' : 'success';
                        const lbl = lv >= 4 ? '심각' : lv >= 3 ? '높음' : lv >= 2 ? '중간' : '낮음';
                        return `<tr>
                            <td class="fw-semibold text-dark">${rc.name}</td>
                            <td class="text-muted small">${rc.detail}</td>
                            <td><span class="badge bg-${col}">${lbl}</span></td>
                            <td class="text-muted small">모니터링 ${lv >= 3 ? '강화' : '유지'}</td>
                        </tr>`;
                    }).join('');
                    html += sec('위험 평가 결과', `
                        <div class="alert alert-${s.riskColor === 'danger' ? 'danger' : s.riskColor === 'warning' ? 'warning' : 'success'} border-0 mb-3">
                            <strong>종합 위험 수준: ${s.riskLabel}</strong> (평균 점수: ${s.riskAvg.toFixed(1)}/5.0)
                        </div>
                        <table class="table table-sm table-hover text-dark">
                            <thead class="table-dark"><tr><th>위험 범주</th><th>세부 항목</th><th>수준</th><th>대응</th></tr></thead>
                            <tbody>${riskRows}</tbody>
                        </table>`);
                }
            }

            // ── 공정성 분석 ──
            if (items.fairness && type !== 'executive') {
                const fairColor = s.fairness >= 70 ? 'success' : s.fairness >= 50 ? 'warning' : 'danger';
                const fairItems = [
                    ['선택 편향 검토', s.fairness >= 60],
                    ['측정 편향 검토', s.fairness >= 50],
                    ['알고리즘 공정성 평가', s.fairness >= 70],
                    ['배포 편향 모니터링', s.fairness >= 80],
                    ['공정성 메트릭 정의', s.fairness >= 40],
                ];
                const fairRows = fairItems.map(([nm, ok]) => `
                    <tr>
                        <td class="text-dark">${nm}</td>
                        <td>${ok ? '<span class="badge bg-success">완료</span>' : '<span class="badge bg-warning">미완료</span>'}</td>
                        <td class="text-muted small">${ok ? '정기 검토 유지' : '즉시 조치 필요'}</td>
                    </tr>`).join('');
                html += sec('공정성 분석', `
                    <div class="mb-3">
                        <div class="d-flex justify-content-between mb-1">
                            <strong class="text-dark">공정성 준수율</strong>
                            <span class="badge bg-${fairColor} fs-6">${s.fairness}%</span>
                        </div>
                        <div class="progress" style="height:16px">
                            <div class="progress-bar bg-${fairColor}" style="width:${s.fairness}%">${s.fairness}%</div>
                        </div>
                    </div>
                    <table class="table table-sm table-hover text-dark">
                        <thead class="table-dark"><tr><th>점검 항목</th><th>상태</th><th>비고</th></tr></thead>
                        <tbody>${fairRows}</tbody>
                    </table>`);
            }

            // ── 거버넌스 준수 현황 ──
            if (items.governance) {
                const govColor = s.govRate >= 70 ? 'success' : s.govRate >= 50 ? 'warning' : 'danger';
                if (type === 'executive') {
                    html += sec('거버넌스 현황', `
                        <p class="text-dark">거버넌스 준수율 <strong class="text-${govColor} fs-5">${s.govRate}%</strong></p>
                        <div class="progress mb-2" style="height:20px">
                            <div class="progress-bar bg-${govColor}" style="width:${s.govRate}%">${s.govRate}%</div>
                        </div>
                        <p class="text-muted small">${s.govRate >= 70 ? '전반적 준수 양호. 미준수 항목 지속 모니터링 필요.' : '주요 거버넌스 항목 즉시 강화 필요.'}</p>`);
                } else if (type === 'compliance') {
                    const compItems = [
                        { domain: 'ISO 24030', item: 'AI 역량 평가 프레임워크',   req: '필수', ok: s.govRate >= 60 },
                        { domain: 'ISO 42001', item: 'AI 관리 시스템',           req: '필수', ok: s.govRate >= 70 },
                        { domain: 'EU AI Act', item: '고위험 AI 시스템 등록',    req: '필수', ok: s.systemHigh === 0 || s.govRate >= 65 },
                        { domain: 'GDPR',      item: '개인정보 처리 AI 거버넌스', req: '필수', ok: s.govRate >= 55 },
                        { domain: '국내 가이드라인', item: 'AI 윤리 원칙 적용', req: '권고', ok: s.fairness >= 60 },
                    ];
                    const compRows = compItems.map(ci => `
                        <tr>
                            <td><span class="badge bg-secondary">${ci.domain}</span></td>
                            <td class="text-dark">${ci.item}</td>
                            <td><span class="badge bg-${ci.req === '필수' ? 'danger' : 'secondary'}">${ci.req}</span></td>
                            <td>${ci.ok ? '<span class="badge bg-success">준수</span>' : '<span class="badge bg-danger">미준수</span>'}</td>
                            <td class="text-muted small">${ci.ok ? '정기 검토 유지' : '즉시 개선 필요'}</td>
                        </tr>`).join('');
                    html += sec('규제별 준수 현황', `
                        <table class="table table-sm table-hover text-dark">
                            <thead class="table-dark"><tr><th>규제 프레임워크</th><th>준수 항목</th><th>요구수준</th><th>상태</th><th>조치사항</th></tr></thead>
                            <tbody>${compRows}</tbody>
                        </table>
                        <div class="alert alert-${govColor} border-0 mt-3">
                            <strong>전체 거버넌스 준수율: ${s.govRate}%</strong> —
                            ${s.govRate >= 70 ? '대부분의 규제 요건을 준수하고 있습니다.' : '필수 규제 항목에 대한 즉각적인 조치가 필요합니다.'}
                        </div>`);
                } else {
                    const govAreas = [
                        { name: 'AI 전략 및 정책',  items: 'AI 정책 수립, 거버넌스 위원회', rate: Math.min(100, s.govRate + 10) },
                        { name: '책임 및 투명성',   items: '책임소재 명확화, 의사결정 문서화', rate: s.govRate },
                        { name: '데이터 거버넌스',  items: '데이터 품질, 개인정보 보호',      rate: Math.max(0, s.govRate - 5) },
                        { name: '리스크 관리',      items: '위험 식별, 모니터링, 대응',       rate: Math.max(0, s.govRate - 10) },
                        { name: '성과 모니터링',    items: 'KPI 정의, 보고 체계',             rate: Math.max(0, s.govRate - 15) },
                    ];
                    const govRows = govAreas.map(ga => {
                        const col = ga.rate >= 70 ? 'success' : ga.rate >= 50 ? 'warning' : 'danger';
                        return `<tr>
                            <td class="fw-semibold text-dark">${ga.name}</td>
                            <td class="text-muted small">${ga.items}</td>
                            <td style="min-width:160px">
                                <div class="d-flex align-items-center gap-2">
                                    <div class="progress flex-grow-1" style="height:10px">
                                        <div class="progress-bar bg-${col}" style="width:${ga.rate}%"></div>
                                    </div>
                                    <small class="text-dark">${ga.rate}%</small>
                                </div>
                            </td>
                            <td><span class="badge bg-${col}">${ga.rate >= 70 ? '양호' : ga.rate >= 50 ? '보통' : '미흡'}</span></td>
                        </tr>`;
                    }).join('');
                    html += sec('거버넌스 준수 현황', `
                        <table class="table table-sm table-hover text-dark">
                            <thead class="table-dark"><tr><th>거버넌스 영역</th><th>주요 항목</th><th>준수율</th><th>등급</th></tr></thead>
                            <tbody>${govRows}</tbody>
                        </table>`);
                }
            }

            // ── 갭 분석 ──
            if (items.gap && type !== 'executive') {
                const catNames = { strategy: '전략/리더십', people: '인력/역량', data: '데이터', tech: '기술/인프라', governance: '거버넌스' };
                const gapRows = Object.entries(s.catScores).map(([k, v]) => {
                    const gap = v > 0 ? (4.0 - v).toFixed(1) : '4.0';
                    const pc  = parseFloat(gap);
                    const col = pc >= 2 ? 'danger' : pc >= 1 ? 'warning' : 'success';
                    const pri = pc >= 2 ? '높음' : pc >= 1 ? '중간' : '낮음';
                    return `<tr>
                        <td class="text-dark">${catNames[k]}</td>
                        <td class="text-dark">${v > 0 ? v.toFixed(1) : '-'}</td>
                        <td class="text-dark">4.0</td>
                        <td><strong class="text-${col}">${pc > 0 ? '+' : ''}${gap}</strong></td>
                        <td><span class="badge bg-${col}">${pri}</span></td>
                    </tr>`;
                }).join('');
                html += sec('갭 분석', `
                    <p class="text-dark">현재 성숙도 대비 목표(4.0) 달성을 위한 영역별 갭 분석입니다.</p>
                    <table class="table table-sm table-hover text-dark">
                        <thead class="table-dark"><tr><th>영역</th><th>현재</th><th>목표</th><th>갭</th><th>우선순위</th></tr></thead>
                        <tbody>${gapRows}</tbody>
                    </table>`);
            }

            // ── 개선 권고사항 ──
            if (items.recommendations) {
                const recsMap = {
                    executive: [
                        { no:1, title:'고위험 AI 시스템 즉각 평가',   detail:'식별된 고위험 시스템 위험 완화 조치 즉시 수행', color:'danger',  priority:'긴급' },
                        { no:2, title:'거버넌스 위원회 구성',         detail:'최고경영진 참여 AI 거버넌스 위원회 설립',       color:'warning', priority:'높음' },
                        { no:3, title:'AI 성숙도 향상 투자',         detail:'취약 영역 중심 역량 강화 및 예산 확보',          color:'warning', priority:'높음' },
                    ],
                    detailed: [
                        { no:1, title:'데이터 거버넌스 강화',        detail:'데이터 품질 관리 체계 및 메타데이터 관리 구축',   color:'danger',    priority:'높음' },
                        { no:2, title:'AI 역량 교육 프로그램',       detail:'전사 AI 리터러시 향상 및 전문 인력 양성 로드맵', color:'warning',   priority:'높음' },
                        { no:3, title:'모델 모니터링 자동화',        detail:'모델 드리프트 탐지 및 자동 경보 시스템 도입',    color:'warning',   priority:'중간' },
                        { no:4, title:'AI 윤리 가이드라인 수립',     detail:'공정성·투명성·책임성 반영 내부 AI 윤리 정책',   color:'info',      priority:'중간' },
                        { no:5, title:'MLOps 파이프라인 구축',      detail:'모델 개발-배포-운영 자동화 CI/CD 파이프라인',    color:'secondary', priority:'낮음' },
                    ],
                    compliance: [
                        { no:1, title:'필수 규제 미준수 항목 즉시 조치', detail:'ISO 42001, EU AI Act 핵심 요건 시정 계획 수립', color:'danger',  priority:'긴급' },
                        { no:2, title:'규제 준수 모니터링 체계 구축',   detail:'분기별 규제 준수 감사 및 내부 통제 시스템 도입', color:'warning', priority:'높음' },
                        { no:3, title:'개인정보 처리 AI 심사',         detail:'GDPR/개인정보보호법 기준 개인정보 영향평가',     color:'warning', priority:'높음' },
                    ],
                    improvement: [
                        { no:1, title:'단기(0~3개월): 기반 구축',    detail:'거버넌스 정책 수립, 데이터 품질 기준 정의',      color:'danger',  priority:'긴급' },
                        { no:2, title:'중기(3~12개월): 체계화',      detail:'교육 프로그램 실행, MLOps 도입, 모니터링 자동화', color:'warning', priority:'높음' },
                        { no:3, title:'장기(12~24개월): 최적화',     detail:'성숙도 Level 4 달성, 지속적 개선 문화 정착',     color:'info',    priority:'중간' },
                    ],
                };
                const recs = recsMap[type] || recsMap.detailed;
                const recHtml = recs.map(r => `
                    <div class="d-flex gap-3 mb-3 p-3 border rounded">
                        <div class="flex-shrink-0">
                            <div class="badge bg-${r.color} rounded-circle d-flex align-items-center justify-content-center"
                                 style="width:32px;height:32px">${r.no}</div>
                        </div>
                        <div class="flex-grow-1">
                            <div class="d-flex justify-content-between align-items-start">
                                <strong class="text-dark">${r.title}</strong>
                                <span class="badge bg-${r.color} ms-2">${r.priority}</span>
                            </div>
                            <p class="text-muted small mb-0 mt-1">${r.detail}</p>
                        </div>
                    </div>`).join('');
                html += sec('개선 권고사항', recHtml);
            }

            // ── 개선 로드맵 ──
            if (items.roadmap) {
                const tasks = this.data.roadmap.length > 0 ? this.data.roadmap : [
                    { name: '데이터 거버넌스 기반 구축',  category:'data',       priority:'high',   status:'pending',     dueDate:'2026-06-30' },
                    { name: 'AI 윤리 가이드라인 수립',    category:'governance', priority:'high',   status:'in-progress', dueDate:'2026-05-31' },
                    { name: 'AI 역량 교육 프로그램 실행', category:'people',     priority:'medium', status:'pending',     dueDate:'2026-09-30' },
                    { name: '모델 모니터링 자동화',       category:'tech',       priority:'medium', status:'pending',     dueDate:'2026-12-31' },
                    { name: 'MLOps 파이프라인 구축',      category:'tech',       priority:'low',    status:'pending',     dueDate:'2027-03-31' },
                ];
                const taskRows = (type === 'executive' ? tasks.slice(0,3) : tasks).map((t,i) => `
                    <tr>
                        <td class="text-dark">${t.name || t.title}</td>
                        ${type !== 'executive' ? `<td>${this._getBadge('category', t.category)}</td>` : ''}
                        <td>${this._getBadge('priority', t.priority)}</td>
                        <td>${this._getBadge('status', t.status)}</td>
                        <td class="text-muted">${t.dueDate || '-'}</td>
                    </tr>`).join('');

                const taskCols = type === 'executive'
                    ? '<tr><th>과제명</th><th>우선순위</th><th>상태</th><th>완료 예정</th></tr>'
                    : '<tr><th>과제명</th><th>영역</th><th>우선순위</th><th>상태</th><th>완료 예정</th></tr>';

                if (type !== 'executive') {
                    const phases = [
                        { name:'1단계: 기반 구축', period:'2026 Q1~Q2', items:'거버넌스 정책, 데이터 표준, 위험 평가', color:'danger' },
                        { name:'2단계: 역량 강화', period:'2026 Q3~Q4', items:'교육 프로그램, 도구 도입, 프로세스 정비', color:'warning' },
                        { name:'3단계: 최적화',   period:'2027 Q1~Q2', items:'자동화, 성숙도 고도화, 지속 개선', color:'success' },
                    ];
                    const phaseHtml = phases.map(p => `
                        <div class="col-md-4">
                            <div class="card border-${p.color} border-2 h-100">
                                <div class="card-header bg-${p.color} text-white py-2">
                                    <strong>${p.name}</strong>
                                </div>
                                <div class="card-body">
                                    <div class="text-muted small mb-1">${p.period}</div>
                                    <p class="text-dark small mb-0">${p.items}</p>
                                </div>
                            </div>
                        </div>`).join('');
                    html += sec('개선 로드맵', `
                        <div class="row g-3 mb-4">${phaseHtml}</div>
                        <table class="table table-sm table-hover text-dark">
                            <thead class="table-dark">${taskCols}</thead>
                            <tbody>${taskRows}</tbody>
                        </table>`);
                } else {
                    html += sec('주요 개선 과제 Top 3', `
                        <table class="table table-sm text-dark">
                            <thead class="table-dark">${taskCols}</thead>
                            <tbody>${taskRows}</tbody>
                        </table>`);
                }
            }

            // ── 벤치마크 비교 ──
            if (items.benchmark && type !== 'executive') {
                const catNames = { strategy: '전략/리더십', people: '인력/역량', data: '데이터', tech: '기술/인프라', governance: '거버넌스' };
                const benchmarks = { strategy:{industry:3.2,leader:4.5}, people:{industry:2.9,leader:4.3},
                    data:{industry:3.0,leader:4.4}, tech:{industry:3.3,leader:4.6}, governance:{industry:2.8,leader:4.2} };
                const bmRows = Object.entries(s.catScores).map(([k, v]) => {
                    const b = benchmarks[k];
                    const diff = v > 0 ? (v - b.industry).toFixed(1) : '-';
                    const col = parseFloat(diff) >= 0 ? 'success' : 'danger';
                    return `<tr>
                        <td class="text-dark">${catNames[k]}</td>
                        <td class="fw-semibold text-dark">${v > 0 ? v.toFixed(1) : '-'}</td>
                        <td class="text-muted">${b.industry.toFixed(1)}</td>
                        <td class="text-muted">${b.leader.toFixed(1)}</td>
                        <td><span class="text-${col} fw-bold">${v > 0 ? (parseFloat(diff)>=0?'+':'') + diff : '-'}</span></td>
                    </tr>`;
                }).join('');
                html += sec('업종 벤치마크 비교', `
                    <p class="text-muted small mb-2">* 업종 평균 및 선도기업 기준은 추정치입니다.</p>
                    <table class="table table-sm table-hover text-dark">
                        <thead class="table-dark"><tr><th>영역</th><th>우리 기업</th><th>업종 평균</th><th>선도기업</th><th>업종 대비</th></tr></thead>
                        <tbody>${bmRows}</tbody>
                    </table>`);
            }

            // ── 결론 ──
            const conclusions = {
                executive:   '경영진의 신속한 의사결정과 자원 배분을 권고드립니다. AI 거버넌스 강화 및 취약 영역 우선 투자를 통해 경쟁 우위를 확보하시기 바랍니다.',
                detailed:    '영역별 상세 평가 결과를 기반으로 체계적인 AI 역량 강화 계획을 수립하고 이행하시기를 권고합니다. 정기적인 평가(연 1회 이상)를 통해 성숙도 변화를 추적하시기 바랍니다.',
                compliance:  '규제 미준수 항목에 대한 즉각적인 시정 조치를 취하고, 규정 준수 모니터링 체계를 상시 운영하시기 바랍니다. AI 관련 규제가 지속적으로 강화되고 있으므로 선제적 대응이 중요합니다.',
                improvement: '제시된 3단계 개선 로드맵에 따라 우선순위 높은 과제부터 순차적으로 이행하시기 바랍니다. 각 단계별 성과 측정 및 보고를 통해 개선 모멘텀을 유지하는 것이 중요합니다.',
            };
            html += sec('결론 및 향후 방향', `
                <div class="alert alert-light border text-dark">${conclusions[type] || ''}</div>
                <p class="text-muted small mb-0">본 보고서는 ISO 24030 기반 AI 평가 결과를 자동 생성한 것으로, 정식 활용 전 전문가 검토를 권장합니다.</p>`);

            html += '</div>'; // rpt-doc

            container.innerHTML = html;

            // 스크롤 상단으로
            container.scrollTop = 0;

        } catch (err) {
            console.error('[refreshReportPreview] 오류:', err);
            const container = document.getElementById('reportPreviewContent');
            if (container) container.innerHTML = `<div class="alert alert-danger m-3">
                <strong>보고서 생성 오류:</strong> ${err.message}
                <pre class="mt-2 small">${err.stack}</pre></div>`;
        }
    },

    generateReport() {
        this.refreshReportPreview();
        this.showNotification('보고서가 생성되었습니다.', 'success');
    },

    exportReport(format) {
        const content = document.getElementById('reportPreviewContent');
        if (!content || !content.innerHTML.trim()) {
            this.showNotification('보고서 미리보기가 없습니다. 먼저 보고서를 생성해주세요.', 'warning');
            return;
        }

        // "word" → "docx" 매핑 (HTML 템플릿 호환)
        const formatMap = { word: 'docx', pdf: 'pdf', html: 'html', docx: 'docx' };
        const apiFormat = formatMap[format] || format;
        const displayName = format === 'word' ? 'Word' : apiFormat.toUpperCase();

        const typeNames = { executive: '경영진 요약 보고서', detailed: '상세 평가 보고서', compliance: '규정 준수 보고서', improvement: '개선 계획 보고서' };
        const reportTitle = 'AI 평가 보고서 - ' + (typeNames[this.currentReportType] || '상세 평가 보고서');

        // 버튼 로딩 상태
        const btn = event && event.currentTarget ? event.currentTarget : null;
        const btnOrigHTML = btn ? btn.innerHTML : '';
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = `<span class="spinner-border spinner-border-sm me-1"></span>${displayName} 생성 중...`;
        }

        const restoreBtn = () => {
            if (btn) { btn.disabled = false; btn.innerHTML = btnOrigHTML; }
        };

        // HTML은 서버 경유 (html_content → prepare-download → download)
        // PDF/DOCX도 동일 플로우
        // blob: URL을 사용하지 않고 서버 URL을 <a download>로 직접 연결
        fetch(`${this.API_BASE}/reports/prepare-download`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                format: apiFormat,
                html_content: content.innerHTML,
                title: reportTitle
            })
        })
        .then(resp => {
            if (!resp.ok) return resp.json().then(e => { throw new Error(e.detail || '서버 오류'); });
            return resp.json();
        })
        .then(data => {
            if (!data.token) throw new Error('다운로드 토큰을 받지 못했습니다.');
            // 서버 URL을 <a download>로 직접 연결 — blob: URL을 만들지 않음
            const a = document.createElement('a');
            a.href = `${this.API_BASE}/reports/download/${data.token}`;
            a.download = '';  // 서버 Content-Disposition 파일명 사용
            a.style.display = 'none';
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            this.showNotification(`${displayName} 파일 다운로드를 시작합니다.`, 'success');
        })
        .catch(err => {
            console.error('보고서 내보내기 오류:', err);
            this.showNotification(`${displayName} 내보내기 실패: ${err.message}`, 'danger');
        })
        .finally(restoreBtn);
    },

    loadRoadmap() {
        this.loadFromLocalStorage();
        this.renderRoadmapTasks();
        this.updateRoadmapStats();
    },

    updateRoadmapStats() {
        const total = this.data.roadmap.length;
        const inProgress = this.data.roadmap.filter(t => t.status === 'in-progress').length;
        const completed = this.data.roadmap.filter(t => t.status === 'completed').length;

        this._updateElement('roadmapTotalTasks', total);
        this._updateElement('roadmapInProgress', inProgress);
        this._updateElement('roadmapCompleted', completed);
        this._updateElement('roadmapProgress', total > 0 ? Math.round((completed / total) * 100) + '%' : '0%');
    },

    renderRoadmapTasks() {
        const tbody = document.getElementById('roadmapTasksTable');
        if (!tbody) return;

        if (this.data.roadmap.length === 0) {
            tbody.innerHTML = `<tr><td colspan="8" class="text-center text-muted py-4">
                <i class="bi bi-inbox fs-1 d-block mb-2"></i>등록된 개선 과제가 없습니다.
            </td></tr>`;
            return;
        }

        const badges = {
            priority: { high: ['danger', '높음'], medium: ['warning', '중간'], low: ['success', '낮음'] },
            status: { pending: ['secondary', '대기'], 'in-progress': ['primary', '진행 중'], completed: ['success', '완료'] },
            category: { strategy: ['primary', '전략'], people: ['success', '인력'], data: ['info', '데이터'], tech: ['warning', '기술'], governance: ['secondary', '거버넌스'] }
        };

        tbody.innerHTML = this.data.roadmap.map((task, index) => {
            const getBadge = (type, val) => {
                const [color, text] = badges[type][val] || ['secondary', val || '기타'];
                return `<span class="badge bg-${color}">${text}</span>`;
            };

            return `
                <tr>
                    <td><input type="checkbox" class="form-check-input" ${task.status === 'completed' ? 'checked' : ''}
                        onchange="ISO24030Manager.toggleTaskStatus(${index})"></td>
                    <td>${task.name}</td>
                    <td>${getBadge('category', task.category)}</td>
                    <td>${getBadge('priority', task.priority)}</td>
                    <td><div class="progress" style="height: 6px; width: 80px;">
                        <div class="progress-bar" style="width: ${task.progress || 0}%"></div></div></td>
                    <td>${task.dueDate || '-'}</td>
                    <td>${getBadge('status', task.status)}</td>
                    <td><button class="btn btn-sm btn-outline-danger" onclick="ISO24030Manager.deleteTask(${index})">
                        <i class="bi bi-trash"></i></button></td>
                </tr>`;
        }).join('');
    },

    addRoadmapTask() {
        const name = document.getElementById('newTaskName')?.value;
        if (!name) {
            this.showNotification('과제명을 입력해주세요.', 'warning');
            return;
        }

        const task = {
            id: Date.now(),
            name,
            priority: document.getElementById('newTaskPriority')?.value || 'medium',
            category: document.getElementById('newTaskCategory')?.value || 'strategy',
            dueDate: document.getElementById('newTaskDueDate')?.value || '',
            status: 'pending',
            progress: 0,
            createdAt: new Date().toISOString()
        };

        this.data.roadmap.push(task);
        this.saveToLocalStorage();
        this.renderRoadmapTasks();
        this.updateRoadmapStats();

        document.getElementById('newTaskName').value = '';
        document.getElementById('newTaskDueDate').value = '';
        this.showNotification('개선 과제가 추가되었습니다.', 'success');
    },

    toggleTaskStatus(index) {
        const task = this.data.roadmap[index];
        task.status = task.status === 'completed' ? 'pending' : 'completed';
        task.progress = task.status === 'completed' ? 100 : 0;
        this.saveToLocalStorage();
        this.renderRoadmapTasks();
        this.updateRoadmapStats();
    },

    deleteTask(index) {
        if (!confirm('이 과제를 삭제하시겠습니까?')) return;
        this.data.roadmap.splice(index, 1);
        this.saveToLocalStorage();
        this.renderRoadmapTasks();
        this.updateRoadmapStats();
        this.showNotification('과제가 삭제되었습니다.', 'info');
    },

    saveRoadmap() {
        this.saveToLocalStorage();
        this.showNotification('로드맵이 저장되었습니다.', 'success');
    },

    // =========================================================================
    // 알림 / 스토리지
    // =========================================================================

    showNotification(message, type = 'info') {
        if (typeof PMNotification !== 'undefined') {
            PMNotification.showNotification(message, type);
        } else if (typeof ProjectManager !== 'undefined' && ProjectManager.showNotification) {
            ProjectManager.showNotification(message, type);
        } else {
            alert(message);
        }
    },

    saveToLocalStorage() {
        localStorage.setItem('iso24030_data', JSON.stringify(this.data));
    },

    loadFromLocalStorage() {
        const saved = localStorage.getItem('iso24030_data');
        if (saved) {
            try {
                this.data = JSON.parse(saved);
            } catch (e) {
                console.error('Failed to load ISO 24030 data:', e);
            }
        }
    }
};

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', () => {
    ISO24030Manager.init();
});

// 전역 노출
window.ISO24030Manager = ISO24030Manager;

