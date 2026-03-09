/**
 * Project Manager - ISO 42001 AIMS 모듈
 * AI 관리 시스템 (AIMS) 관련 기능
 */

const PMAims = {
    // localStorage 키 접두사
    STORAGE_PREFIX: 'ai_consulting_',

    /**
     * AIMS 데이터 저장 키 생성
     */
    getAimsStorageKey(type) {
        const pid = PMProjectCrud.currentProjectId || 'default';
        return `${this.STORAGE_PREFIX}aims_${type}_${pid}`;
    },

    /**
     * AIMS 체크리스트 저장
     */
    saveAimsChecklist() {
        const checklistData = {
            phases: {}
        };

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

        PMNotification.showNotification('AIMS 체크리스트가 저장되었습니다.', 'success');
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
        PMUtils.downloadAsJson(data, 'aims_checklist');
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

        PMNotification.showNotification('위험 등록부가 저장되었습니다.', 'success');
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
                <td><code>${PMUtils.escapeHtml(risk.id)}</code></td>
                <td>${PMUtils.escapeHtml(risk.description)}</td>
                <td><span class="badge bg-${getCategoryBadge(risk.category)}">${PMUtils.escapeHtml(risk.category)}</span></td>
                <td>${probScore}</td>
                <td>${impactScore}</td>
                <td><span class="badge bg-${scoreColor}">${riskScore} ${scoreText}</span></td>
                <td>${PMUtils.escapeHtml(risk.mitigation)}</td>
                <td>-</td>
                <td><span class="badge bg-${getStatusBadge(risk.status)}">${PMUtils.escapeHtml(risk.status)}</span></td>
                <td>
                    <button class="btn btn-sm btn-outline-primary" onclick="PMAims.editRisk('${risk.id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="PMAims.deleteRisk('${risk.id}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `}).join('');

        this.updateRiskCounts(risks);
    },

    /**
     * 위험 카운트 업데이트
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
     * 새 위험 추가 모달 열기
     */
    addNewRisk() {
        let modal = document.getElementById('riskModal');
        if (!modal) {
            modal = this.createRiskModal();
            document.body.appendChild(modal);
        }

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
        PMNotification.showNotification('위험이 삭제되었습니다.', 'success');
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
                        <button type="button" class="btn btn-primary" onclick="PMAims.saveRiskFromModal()">저장</button>
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

        const existingIndex = riskData.risks.findIndex(r => r.id === riskId);
        if (existingIndex >= 0) {
            riskData.risks[existingIndex] = newRisk;
        } else {
            riskData.risks.push(newRisk);
        }

        riskData.timestamp = new Date().toISOString();
        localStorage.setItem(storageKey, JSON.stringify(riskData));

        this.renderRiskTable(riskData.risks);

        const modal = bootstrap.Modal.getInstance(document.getElementById('riskModal'));
        modal?.hide();

        PMNotification.showNotification('위험이 저장되었습니다.', 'success');
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

        PMNotification.showNotification('AI 영향 평가가 저장되었습니다.', 'success');
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
        if (!data) return;
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `ai_impact_assessment_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
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

        PMNotification.showNotification('모델 카드가 저장되었습니다.', 'success');
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
                if (element) {
                    element.value = value || '';
                }
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
        if (!data) return;
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `model_card_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
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

        PMNotification.showNotification('데이터 시트가 저장되었습니다.', 'success');
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
                if (element) {
                    element.value = value || '';
                }
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
        if (!data) return;
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `data_sheet_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
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

        const auditNotes = document.getElementById('auditNotes');
        if (auditNotes) {
            auditData.notes = auditNotes.value;
        }

        const storageKey = this.getAimsStorageKey('audit');
        localStorage.setItem(storageKey, JSON.stringify(auditData));

        PMNotification.showNotification('내부 감사 체크리스트가 저장되었습니다.', 'success');
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
                if (checkbox) {
                    checkbox.checked = item.checked;
                }
            });

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
        if (!data) return;
        
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `aims_audit_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    },

    /**
     * AIMS 대시보드 통계 업데이트
     */
    updateAimsDashboardStats() {
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

        const riskKey = this.getAimsStorageKey('risk_register');
        const riskData = localStorage.getItem(riskKey);
        let riskCount = 0;

        if (riskData) {
            const data = JSON.parse(riskData);
            riskCount = data.risks.length;
        }

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

        const auditKey = this.getAimsStorageKey('audit');
        const auditData = localStorage.getItem(auditKey);
        let auditCompleted = 0;

        if (auditData) {
            const data = JSON.parse(auditData);
            auditCompleted = data.items.filter(item => item.checked).length;
        }

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
     * 모든 AIMS 데이터 로드
     */
    loadAllAimsData() {
        this.loadAimsChecklist();
        this.loadRiskRegister();
        this.loadImpactAssessment();
        this.loadModelCard();
        this.loadDataSheet();
        this.loadAudit();
        this.updateAimsDashboardStats();
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMAims;
} else {
    window.PMAims = PMAims;
}

