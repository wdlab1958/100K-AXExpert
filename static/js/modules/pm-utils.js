/**
 * Project Manager - 유틸리티 모듈
 * 공통 유틸리티 함수들
 */

const PMUtils = {
    /**
     * 입력 요소에서 값 가져오기
     */
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

    /**
     * 체크박스 값 가져오기
     */
    getCheckboxValue(id) {
        const el = document.getElementById(id);
        return el ? el.checked : false;
    },

    /**
     * 입력 요소에 값 설정하기
     */
    setInputValue(id, value) {
        const el = document.getElementById(id);
        if (el && value !== undefined && value !== null) {
            el.value = value;

            // Range 슬라이더의 경우 표시 값도 업데이트
            const display = document.getElementById(id + 'Value');
            if (display) display.textContent = value;
        }
    },

    /**
     * 체크박스 값 설정하기
     */
    setCheckboxValue(id, value) {
        const el = document.getElementById(id);
        if (el) el.checked = !!value;
    },

    /**
     * 리스트 항목 수집
     */
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

    /**
     * 날짜 포맷팅
     */
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
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMUtils;
} else {
    window.PMUtils = PMUtils;
}

