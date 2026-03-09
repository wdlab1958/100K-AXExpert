/**
 * Project Manager - LocalStorage 자동 저장 모듈
 * 입력 데이터의 자동 저장 및 복원 관리
 */

const PMLocalStorage = {
    // localStorage 키 접두사
    STORAGE_PREFIX: 'ai_consulting_',

    // 자동 저장 간격 (ms) - 10분(600초)마다 실행
    AUTO_SAVE_INTERVAL: 600000, // 10분 = 600초 = 600000ms

    // 마지막 저장 시간
    _lastSaveTime: null,

    // 저장 대기 타이머
    _localSaveTimeout: null,

    // 저장 상태 표시 요소
    _saveStatusElement: null,

    /**
     * localStorage 자동 저장 초기화
     */
    init() {
        console.log('Initializing localStorage auto-save system...');
        this.bindLocalStorageEvents();
        this.createSaveStatusIndicator();
        this.addAutoSaveStyles();

        // 주기적 자동 저장 (10분마다)
        setInterval(() => {
            this.saveAllFieldsToLocalStorage();
        }, this.AUTO_SAVE_INTERVAL);
        
        console.log(`AutoSave interval set to ${this.AUTO_SAVE_INTERVAL / 1000} seconds (${this.AUTO_SAVE_INTERVAL / 60000} minutes)`);

        // 페이지 언로드 전 저장
        window.addEventListener('beforeunload', () => {
            this.saveAllFieldsToLocalStorage();
        });

        // 페이지 가시성 변경 시 저장
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
        const inputSelectors = 'input:not([type="file"]):not([type="submit"]):not([type="button"]), select, textarea';

        document.querySelectorAll(inputSelectors).forEach(el => {
            this.addLocalStorageListener(el);
        });

        // MutationObserver로 동적으로 추가되는 입력 필드 감시
        const observer = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        if (node.matches && node.matches(inputSelectors)) {
                            this.addLocalStorageListener(node);
                        }
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
        if (element.dataset.localStorageEnabled) return;
        element.dataset.localStorageEnabled = 'true';

        const saveHandler = () => {
            this.debouncedLocalSave();
        };

        element.addEventListener('input', saveHandler);
        element.addEventListener('change', saveHandler);

        if (element.type === 'checkbox' || element.type === 'radio') {
            element.removeEventListener('input', saveHandler);
        }
    },

    /**
     * 디바운스된 localStorage 저장
     * 사용자 입력 후 2초 후에 저장 (즉시 저장은 하지 않음)
     */
    debouncedLocalSave() {
        if (this._localSaveTimeout) {
            clearTimeout(this._localSaveTimeout);
        }

        this.updateSaveStatus('saving');

        // 사용자 입력 후 2초 후에 저장 (너무 자주 저장하지 않도록)
        this._localSaveTimeout = setTimeout(() => {
            this.saveAllFieldsToLocalStorage();
        }, 2000);
    },

    /**
     * 모든 입력 필드를 localStorage에 저장
     */
    saveAllFieldsToLocalStorage() {
        try {
            const formData = {};
            const timestamp = new Date().toISOString();

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

                formData[id] = {
                    value: value,
                    type: el.type || 'text',
                    tagName: el.tagName.toLowerCase()
                };
            });

            const storageData = {
                formData: formData,
                timestamp: timestamp,
                projectId: PMProjectCrud.currentProjectId,
                url: window.location.pathname,
                fieldCount: Object.keys(formData).length
            };

            const storageKey = this.STORAGE_PREFIX + 'form_data';
            localStorage.setItem(storageKey, JSON.stringify(storageData));

            this._lastSaveTime = timestamp;
            localStorage.setItem(this.STORAGE_PREFIX + 'last_save', timestamp);

            this.updateSaveStatus('saved');
            console.log(`[AutoSave] ${Object.keys(formData).length} fields saved at ${timestamp}`);

            return true;
        } catch (error) {
            console.error('[AutoSave] Error saving to localStorage:', error);
            this.updateSaveStatus('error');

            if (error.name === 'QuotaExceededError') {
                this.cleanupOldLocalStorageData();
            }
            return false;
        }
    },

    /**
     * localStorage에서 데이터 복원
     * @param {Array<string>} excludeFields - 복원에서 제외할 필드 ID 배열
     */
    restoreFromLocalStorage(excludeFields = []) {
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

            const hoursDiff = (now - savedTime) / (1000 * 60 * 60);
            if (hoursDiff > 24) {
                console.log('[AutoRestore] Saved data is older than 24 hours, skipping restore');
                return false;
            }

            let restoredCount = 0;
            let skippedCount = 0;

            Object.entries(formData).forEach(([id, data]) => {
                // 제외할 필드는 건너뛰기
                if (excludeFields.includes(id)) {
                    skippedCount++;
                    return;
                }

                const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);

                if (!element) {
                    skippedCount++;
                    return;
                }

                const currentValue = element.type === 'checkbox' ? element.checked : element.value;
                if (currentValue && currentValue !== '' && currentValue !== false && currentValue !== '0') {
                    return;
                }

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

                const display = document.getElementById(id + 'Value');
                if (display && element.type === 'range') {
                    display.textContent = element.value;
                }

                element.dispatchEvent(new Event('change', { bubbles: true }));
            });

            console.log(`[AutoRestore] Restored ${restoredCount} fields, skipped ${skippedCount} (not found or already filled)`);

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
     * 특정 필드들을 강제로 복원 (기본값이 있어도 덮어쓰기)
     */
    restoreSpecificFields(fieldIds) {
        try {
            const storageKey = this.STORAGE_PREFIX + 'form_data';
            const savedData = localStorage.getItem(storageKey);

            if (!savedData) {
                console.log('[AutoRestore] No saved data found for specific fields');
                return false;
            }

            const parsedData = JSON.parse(savedData);
            const formData = parsedData.formData;

            let restoredCount = 0;

            fieldIds.forEach(id => {
                const data = formData[id];
                if (!data) {
                    return;
                }

                const element = document.getElementById(id) || document.querySelector(`[name="${id}"]`);
                if (!element) {
                    console.log(`[AutoRestore] Element not found for field: ${id}`);
                    return;
                }

                // 기본값이 있어도 강제로 복원
                let valueSet = false;
                if (element.type === 'checkbox') {
                    const newValue = data.value === true || data.value === 'true';
                    if (element.checked !== newValue) {
                        element.checked = newValue;
                        valueSet = true;
                    }
                } else if (element.type === 'radio') {
                    if (element.value === data.value) {
                        if (!element.checked) {
                            element.checked = true;
                            valueSet = true;
                        }
                    }
                } else if (element.tagName.toLowerCase() === 'select') {
                    // select 요소의 경우 저장된 값이 옵션에 존재하는지 확인
                    const savedValue = data.value || '';
                    if (savedValue && Array.from(element.options).some(opt => opt.value === savedValue)) {
                        if (element.value !== savedValue) {
                            element.value = savedValue;
                            valueSet = true;
                        }
                    } else if (savedValue) {
                        console.log(`[AutoRestore] Value "${savedValue}" not found in select options for field: ${id}`);
                    }
                } else {
                    // input, textarea 등
                    const savedValue = data.value || '';
                    if (element.value !== savedValue) {
                        element.value = savedValue;
                        valueSet = true;
                    }
                }

                if (valueSet) {
                    restoredCount++;

                    const display = document.getElementById(id + 'Value');
                    if (display && element.type === 'range') {
                        display.textContent = element.value;
                    }

                    // change 이벤트 발생
                    element.dispatchEvent(new Event('change', { bubbles: true }));
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                }
            });

            // hasCloud가 복원되면 클라우드 제공자 필드 표시/숨김 상태 업데이트
            if (fieldIds.includes('hasCloud') || fieldIds.includes('cloudProvider')) {
                if (typeof toggleCloudProvider === 'function') {
                    setTimeout(() => toggleCloudProvider(), 50);
                }
            }

            if (restoredCount > 0) {
                console.log(`[AutoRestore] Force restored ${restoredCount} specific fields: ${fieldIds.join(', ')}`);
            }

            return restoredCount > 0;
        } catch (error) {
            console.error('[AutoRestore] Error restoring specific fields:', error);
            return false;
        }
    },

    /**
     * 복원 알림 표시
     */
    showRestoreNotification(fieldCount, timestamp) {
        const savedTime = new Date(timestamp);
        const timeStr = savedTime.toLocaleString('ko-KR');

        const banner = document.createElement('div');
        banner.id = 'restoreNotificationBanner';
        banner.className = 'restore-notification-banner';
        banner.innerHTML = `
            <div class="restore-notification-content">
                <i class="bi bi-clock-history me-2"></i>
                <span><strong>${fieldCount}개</strong>의 입력 항목이 복원되었습니다 (${timeStr})</span>
                <div class="restore-notification-actions">
                    <button class="btn btn-sm btn-outline-light me-2" onclick="PMLocalStorage.keepRestoredData()">
                        <i class="bi bi-check-lg me-1"></i>유지
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="PMLocalStorage.clearRestoredData()">
                        <i class="bi bi-x-lg me-1"></i>초기화
                    </button>
                </div>
            </div>
        `;

        const existingBanner = document.getElementById('restoreNotificationBanner');
        if (existingBanner) {
            existingBanner.remove();
        }

        document.body.prepend(banner);

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
        PMNotification.showNotification('복원된 데이터가 유지됩니다.', 'success');
    },

    /**
     * 복원된 데이터 초기화
     */
    clearRestoredData() {
        if (confirm('저장된 데이터를 모두 초기화하시겠습니까? 현재 입력된 내용이 모두 지워집니다.')) {
            localStorage.removeItem(this.STORAGE_PREFIX + 'form_data');
            localStorage.removeItem(this.STORAGE_PREFIX + 'last_save');
            window.location.reload();
        }
    },

    /**
     * 저장 상태 표시 UI 생성
     */
    createSaveStatusIndicator() {
        const indicator = document.createElement('div');
        indicator.id = 'autoSaveIndicator';
        indicator.className = 'auto-save-indicator';
        indicator.innerHTML = `
            <span class="save-icon"></span>
            <span class="save-text">자동 저장 중...</span>
        `;

        document.body.appendChild(indicator);
        this._saveStatusElement = indicator;
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
                right: 20px;
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
                    right: 10px;
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
     * 수동 저장 버튼 핸들러
     */
    manualSaveToLocalStorage() {
        this.saveAllFieldsToLocalStorage();
        PMNotification.showNotification('모든 입력 데이터가 로컬에 저장되었습니다.', 'success');
    },

    /**
     * localStorage 데이터 내보내기
     */
    exportLocalStorageData() {
        const storageKey = this.STORAGE_PREFIX + 'form_data';
        const savedData = localStorage.getItem(storageKey);

        if (!savedData) {
            PMNotification.showNotification('저장된 데이터가 없습니다.', 'warning');
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

        PMNotification.showNotification('데이터가 내보내기되었습니다.', 'success');
    },

    /**
     * localStorage 데이터 가져오기
     */
    importLocalStorageData(file) {
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                const data = JSON.parse(e.target.result);
                const storageKey = this.STORAGE_PREFIX + 'form_data';
                localStorage.setItem(storageKey, JSON.stringify(data));
                this.restoreFromLocalStorage();
                PMNotification.showNotification('데이터가 가져오기되었습니다.', 'success');
            } catch (error) {
                PMNotification.showNotification('파일을 읽는 중 오류가 발생했습니다.', 'error');
            }
        };
        reader.readAsText(file);
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMLocalStorage;
} else {
    window.PMLocalStorage = PMLocalStorage;
}

