/**
 * Project Manager - 알림 모듈
 * 토스트 알림 및 로딩 오버레이 관리
 */

const PMNotification = {
    /**
     * 로딩 오버레이 표시
     */
    showLoading(message = '처리 중입니다...') {
        const overlay = document.getElementById('loadingOverlay');
        const msgEl = document.getElementById('loadingMessage');
        if (msgEl) msgEl.textContent = message;
        if (overlay) overlay.classList.remove('hidden');
    },

    /**
     * 로딩 오버레이 숨기기
     */
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('hidden');
    },

    /**
     * 토스트 알림 표시
     */
    showNotification(message, type = 'info') {
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

    /**
     * 토스트 컨테이너 생성
     */
    createToastContainer() {
        const container = document.createElement('div');
        container.id = 'toastContainer';
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    },

    /**
     * 토스트 아이콘 가져오기
     */
    getToastIcon(type) {
        const icons = {
            success: 'bi-check-circle-fill',
            error: 'bi-exclamation-circle-fill',
            warning: 'bi-exclamation-triangle-fill',
            info: 'bi-info-circle-fill'
        };
        return icons[type] || icons.info;
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMNotification;
} else {
    window.PMNotification = PMNotification;
}

