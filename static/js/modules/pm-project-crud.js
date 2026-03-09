/**
 * Project Manager - 프로젝트 CRUD 모듈
 * 프로젝트 생성, 읽기, 수정, 삭제 관리
 */

const PMProjectCrud = {
    // API Base URL
    API_BASE: '/api/v1',

    // 현재 선택된 프로젝트 ID
    currentProjectId: null,

    // 프로젝트 목록 캐시
    projectsCache: [],

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
            
            // 전체 프로젝트 수 업데이트
            const totalProjectsEl = document.getElementById('totalProjects');
            if (totalProjectsEl) {
                totalProjectsEl.textContent = this.projectsCache.length;
            }
            
            // 현재 프로젝트가 있으면 대시보드 업데이트
            if (this.currentProjectId) {
                const currentProject = this.projectsCache.find(p => 
                    this.getProjectId(p) === this.currentProjectId
                );
                if (currentProject) {
                    this.updateDashboard(currentProject);
                }
            }
            
            return this.projectsCache;
        } catch (error) {
            console.error('프로젝트 목록 로드 오류:', error);
            PMNotification.showNotification('프로젝트 목록을 불러오는데 실패했습니다.', 'error');
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
            option.textContent = `${projectName} (${PMUtils.formatDate(project.updated_at || project.created_at)})`;
            if (projectId === this.currentProjectId) {
                option.selected = true;
            }
            selector.appendChild(option);
        });

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
                    <td><small>${PMUtils.formatDate(project.updated_at || project.created_at)}</small></td>
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
        let total = 14;

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

    /**
     * 새 프로젝트 생성
     */
    async createProject(projectData) {
        try {
            PMNotification.showLoading('프로젝트를 생성하고 있습니다...');

            // framework API를 사용하여 프로젝트 생성 (프로젝트 목록과 동일한 저장소 사용)
            const response = await fetch(`${this.API_BASE}/framework/projects`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(projectData)
            });

            if (!response.ok) {
                const errorText = await response.text();
                let errorMessage = '프로젝트 생성 실패';
                try {
                    const errorData = JSON.parse(errorText);
                    errorMessage = errorData.detail || errorData.message || errorMessage;
                } catch (e) {
                    errorMessage = `${errorMessage} (${response.status}: ${errorText})`;
                }
                console.error('프로젝트 생성 API 오류:', {
                    status: response.status,
                    statusText: response.statusText,
                    error: errorMessage
                });
                throw new Error(errorMessage);
            }

            const data = await response.json();
            console.log('[PMProjectCrud] 프로젝트 생성 성공:', data);
            
            this.currentProjectId = data.project_id;
            localStorage.setItem('lastProjectId', data.project_id);

            // 프로젝트 목록 새로고침 (약간의 지연을 두어 서버 저장 완료 대기)
            await new Promise(resolve => setTimeout(resolve, 500));
            await this.loadProjectList();
            
            PMNotification.hideLoading();
            PMNotification.showNotification('프로젝트가 성공적으로 생성되었습니다.', 'success');

            return data;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('프로젝트 생성 오류:', error);
            const errorMsg = error.message || '프로젝트 생성에 실패했습니다.';
            PMNotification.showNotification(errorMsg, 'error');
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
            PMNotification.showLoading('프로젝트를 불러오는 중입니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}/summary`);
            if (!response.ok) {
                if (response.status === 404) {
                    localStorage.removeItem('lastProjectId');
                }
                throw new Error('프로젝트 로드 실패');
            }

            const data = await response.json();
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
            // ProjectManager 모듈도 업데이트
            if (typeof ProjectManager !== 'undefined') {
                ProjectManager.currentProjectId = projectId;
            }

            // 프로젝트 선택기 업데이트
            const selector = document.getElementById('projectSelector');
            if (selector) selector.value = projectId;

            // 현재 프로젝트 표시 업데이트
            this.updateCurrentProjectDisplay(project);

            // 대시보드 업데이트
            this.updateDashboard(project);

            // 대시보드 페이지가 보이는 경우에만 차트 업데이트
            const dashboardPage = document.getElementById('page-dashboard');
            if (dashboardPage && !dashboardPage.classList.contains('hidden')) {
                // 성숙도 차트 업데이트
                setTimeout(() => {
                    if (typeof updateMaturityChartFromProject === 'function') {
                        updateMaturityChartFromProject(project);
                    }
                }, 100);
                
                // Use Case 차트 업데이트
                setTimeout(() => {
                    if (typeof updateUseCaseChartFromProject === 'function') {
                        updateUseCaseChartFromProject(project);
                    }
                }, 150);
            }

            PMNotification.hideLoading();

            const projectName = project.company_profile?.name || project.project_name || projectId;
            PMNotification.showNotification(`프로젝트 "${projectName}"를 불러왔습니다.`, 'success');

            this.renderProjectTable();

            return project;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('프로젝트 로드 오류:', error);
            PMNotification.showNotification('프로젝트를 불러오는데 실패했습니다.', 'error');
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
            PMNotification.showLoading('프로젝트를 삭제하고 있습니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}`, {
                method: 'DELETE'
            });

            if (!response.ok) throw new Error('프로젝트 삭제 실패');

            if (this.currentProjectId === projectId) {
                this.currentProjectId = null;
                localStorage.removeItem('lastProjectId');
            }

            await this.loadProjectList();
            PMNotification.hideLoading();
            PMNotification.showNotification('프로젝트가 삭제되었습니다.', 'success');
        } catch (error) {
            PMNotification.hideLoading();
            console.error('프로젝트 삭제 오류:', error);
            PMNotification.showNotification('프로젝트 삭제에 실패했습니다.', 'error');
        }
    },

    /**
     * 대시보드 업데이트
     */
    updateDashboard(project) {
        // AI 성숙도 레벨 업데이트
        const maturityLevelEl = document.getElementById('maturityLevel');
        if (maturityLevelEl) {
            if (project.stage1_maturity?.overall_level) {
                maturityLevelEl.textContent = project.stage1_maturity.overall_level;
            } else if (project.methodology_detailed_maturity?.scores?.overall) {
                const overallScore = project.methodology_detailed_maturity.scores.overall;
                const level = Math.round(overallScore);
                maturityLevelEl.textContent = level;
            } else {
                maturityLevelEl.textContent = '-';
            }
        }

        // 예상 ROI 업데이트
        const expectedROIEl = document.getElementById('expectedROI');
        if (expectedROIEl && project.scenario_analysis?.scenario_details?.roi_estimate) {
            const roiText = project.scenario_analysis.scenario_details.roi_estimate;
            // "25-40%" 형식에서 숫자 추출
            const roiMatch = roiText.match(/(\d+)/);
            if (roiMatch) {
                expectedROIEl.textContent = roiMatch[1];
            } else {
                expectedROIEl.textContent = '-';
            }
        } else if (expectedROIEl) {
            expectedROIEl.textContent = '-';
        }

        // 전체 프로젝트 수 업데이트
        const totalProjectsEl = document.getElementById('totalProjects');
        if (totalProjectsEl && this.projectsCache) {
            totalProjectsEl.textContent = this.projectsCache.length;
        }

        // 리스크 레벨 업데이트
        const riskLevelEl = document.getElementById('riskLevel');
        if (riskLevelEl && project.scenario_analysis?.scenario_details?.risk_level) {
            riskLevelEl.textContent = project.scenario_analysis.scenario_details.risk_level;
        } else if (riskLevelEl) {
            riskLevelEl.textContent = '-';
        }
    },

    /**
     * 프로젝트 복제
     */
    async duplicateProject(projectId) {
        try {
            PMNotification.showLoading('프로젝트를 복제하고 있습니다...');

            const response = await fetch(`${this.API_BASE}/framework/projects/${projectId}/duplicate`, {
                method: 'POST'
            });

            if (!response.ok) throw new Error('프로젝트 복제 실패');

            const data = await response.json();
            await this.loadProjectList();
            PMNotification.hideLoading();
            PMNotification.showNotification('프로젝트가 복제되었습니다.', 'success');

            return data;
        } catch (error) {
            PMNotification.hideLoading();
            console.error('프로젝트 복제 오류:', error);
            PMNotification.showNotification('프로젝트 복제에 실패했습니다.', 'error');
        }
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMProjectCrud;
} else {
    window.PMProjectCrud = PMProjectCrud;
}

