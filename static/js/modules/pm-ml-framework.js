/**
 * Project Manager - ISO 23053 ML Framework 모듈
 * ML 프레임워크 관련 기능
 */

const PMMlFramework = {
    // localStorage 키 접두사
    STORAGE_PREFIX: 'ai_consulting_',

    /**
     * ISO 23053 ML 체크리스트 스토리지 키 생성
     */
    getMlStorageKey(type) {
        const projectId = PMProjectCrud.currentProjectId || 'default';
        return `ml_framework_${projectId}_${type}`;
    },

    /**
     * ML 프레임워크 체크리스트 저장
     */
    saveMlChecklist() {
        const checklistData = {
            categories: {}
        };

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

        PMNotification.showNotification('ML 프레임워크 체크리스트가 저장되었습니다.', 'success');
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
        PMUtils.downloadAsJson(data, 'ml_framework_checklist');
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

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMMlFramework;
} else {
    window.PMMlFramework = PMMlFramework;
}

