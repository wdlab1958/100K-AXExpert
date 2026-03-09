/**
 * Project Manager - 폼 데이터 채우기 모듈
 * 각 Stage의 폼에 데이터를 채우는 함수들
 */

const PMFormPopulator = {
    /**
     * 성숙도 폼에 데이터 채우기
     */
    populateMaturityForm(data) {
        if (!data) return;

        const getItems = (category) => {
            if (data.scores && data.scores[category]) {
                return data.scores[category].items || data.scores[category];
            }
            return data[category] || {};
        };

        // Strategy
        const strategy = getItems('strategy');
        PMUtils.setInputValue('s1_vision', strategy.ai_vision_clarity);
        PMUtils.setInputValue('s1_investment', strategy.ai_investment_management);
        PMUtils.setInputValue('s1_portfolio', strategy.usecase_portfolio_management);
        PMUtils.setInputValue('s1_roi', strategy.ai_roi_measurement);

        // Organization
        const organization = getItems('organization');
        PMUtils.setInputValue('s1_org', organization.ai_organization_structure);
        PMUtils.setInputValue('s1_talent', organization.ai_talent_capability);
        PMUtils.setInputValue('s1_training', organization.ai_training_program);
        PMUtils.setInputValue('s1_culture', organization.ai_change_culture);

        // Data & Technology
        const dataTech = getItems('data_technology');
        PMUtils.setInputValue('s1_infra', dataTech.data_infrastructure);
        PMUtils.setInputValue('s1_quality', dataTech.data_quality_governance);
        PMUtils.setInputValue('s1_mlops', dataTech.mlops_platform);
        PMUtils.setInputValue('s1_cloud', dataTech.cloud_scalability);

        // Process
        const process = getItems('process');
        PMUtils.setInputValue('s1_method', process.ai_development_methodology);
        PMUtils.setInputValue('s1_validation', process.model_validation_process);
        PMUtils.setInputValue('s1_ethics', process.ai_ethics_risk_management);
        PMUtils.setInputValue('s1_monitoring', process.ai_monitoring_operation);

        PMUtils.setInputValue('s1_notes', data.notes);

        if (data.analysis_result) {
            this.displayAnalysisResult('maturityAnalysisResult', data.analysis_result, 'info', 'AI 분석 결과');
        }
    },

    /**
     * 기회 발굴 폼에 데이터 채우기
     */
    populateOpportunitiesForm(data) {
        if (!data) return;

        let opportunities = Array.isArray(data) ? data : (data.opportunities || []);
        if (opportunities.length === 0) return;

        const container = document.getElementById('opportunityList');
        if (!container) return;

        container.innerHTML = '';

        if (typeof window.opportunityCounter !== 'undefined') {
            window.opportunityCounter = 0;
        }

        opportunities.forEach((opp, index) => {
            const oppId = index + 1;
            if (typeof window.opportunityCounter !== 'undefined') {
                window.opportunityCounter = oppId;
            }

            const oppName = opp.name || '';
            const oppDesc = opp.description || '';
            const difficulty = opp.implementation_difficulty || opp.complexity || 'medium';
            const complexityMap = { '낮음': 'low', '중': 'medium', '중간': 'medium', '높음': 'high' };
            const oppComplexity = complexityMap[difficulty] || difficulty;
            const quadrant = opp.priority_quadrant || opp.roi_potential || 'high';
            const roiMap = { 'quick_win': 'high', 'strategic': 'high', 'fill_in': 'medium', 'thankless': 'low' };
            const oppRoi = roiMap[quadrant] || quadrant;

            const opportunityHtml = `
                <div class="card mb-3 opportunity-item" id="opportunity-${oppId}">
                    <div class="card-body">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h6 class="card-title mb-0">기회 #${oppId}</h6>
                            <button type="button" class="btn btn-sm btn-outline-danger" onclick="removeOpportunity(${oppId})">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                        <div class="row g-3">
                            <div class="col-md-6">
                                <label class="form-label">기회/과제명</label>
                                <input type="text" class="form-control" id="opp-name-${oppId}" placeholder="AI 도입 기회명" value="${PMUtils.escapeHtml(oppName)}">
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">ROI 잠재력</label>
                                <select class="form-select" id="opp-roi-${oppId}">
                                    <option value="low" ${oppRoi === 'low' ? 'selected' : ''}>낮음</option>
                                    <option value="medium" ${oppRoi === 'medium' ? 'selected' : ''}>중간</option>
                                    <option value="high" ${oppRoi === 'high' ? 'selected' : ''}>높음</option>
                                    <option value="very_high" ${oppRoi === 'very_high' ? 'selected' : ''}>매우 높음</option>
                                </select>
                            </div>
                            <div class="col-md-3">
                                <label class="form-label">구현 복잡도</label>
                                <select class="form-select" id="opp-complexity-${oppId}">
                                    <option value="low" ${oppComplexity === 'low' ? 'selected' : ''}>낮음</option>
                                    <option value="medium" ${oppComplexity === 'medium' ? 'selected' : ''}>중간</option>
                                    <option value="high" ${oppComplexity === 'high' ? 'selected' : ''}>높음</option>
                                </select>
                            </div>
                            
                            <!-- 슬라이더 필드 -->
                            <div class="col-md-4">
                                <label class="form-label">데이터 가용성 (1-5)</label>
                                <input type="range" class="form-range" id="opp-data-${oppId}" min="1" max="5" value="${opp.data_availability || 3}"
                                    oninput="updateSliderDisplay('opp-data-${oppId}', 'opp-data-${oppId}-display')">
                                <small class="text-muted">현재: <span id="opp-data-${oppId}-display">${opp.data_availability || 3}</span></small>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">긴급도 (1-5)</label>
                                <input type="range" class="form-range" id="opp-urgency-${oppId}" min="1" max="5" value="${opp.urgency || 3}"
                                    oninput="updateSliderDisplay('opp-urgency-${oppId}', 'opp-urgency-${oppId}-display')">
                                <small class="text-muted">현재: <span id="opp-urgency-${oppId}-display">${opp.urgency || 3}</span></small>
                            </div>
                            <div class="col-md-4">
                                <label class="form-label">전략 정합성 (1-5)</label>
                                <input type="range" class="form-range" id="opp-strategic-${oppId}" min="1" max="5" value="${opp.strategic_alignment || 3}"
                                    oninput="updateSliderDisplay('opp-strategic-${oppId}', 'opp-strategic-${oppId}-display')">
                                <small class="text-muted">현재: <span id="opp-strategic-${oppId}-display">${opp.strategic_alignment || 3}</span></small>
                            </div>

                            <div class="col-12">
                                <label class="form-label">설명</label>
                                <textarea class="form-control" id="opp-desc-${oppId}" rows="2" placeholder="기회/과제에 대한 설명">${PMUtils.escapeHtml(oppDesc)}</textarea>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', opportunityHtml);
        });

        if (data.analysis_result) {
            this.displayAnalysisResult('opportunityAnalysisResult', data.analysis_result, 'success', 'AI 분석 결과');
        }
    },

    /**
     * 로드맵 폼에 데이터 채우기
     */
    populateRoadmapForm(data) {
        if (!data) return;

        PMUtils.setInputValue('rm_vision', data.vision);
        PMUtils.setInputValue('roadmap_vision', data.vision);

        if (data.goals && Array.isArray(data.goals)) {
            const goalsContainer = document.getElementById('strategicGoals');
            if (goalsContainer) {
                goalsContainer.innerHTML = '';
                data.goals.forEach(goal => {
                    const goalText = typeof goal === 'object'
                        ? `${goal.name || ''} - ${goal.target || ''}`
                        : goal;
                    const html = `
                        <div class="input-group mb-2">
                            <input type="text" class="form-control" placeholder="전략적 목표" value="${PMUtils.escapeHtml(goalText)}">
                            <button class="btn btn-outline-danger" type="button" onclick="removeGoal(this)"><i class="bi bi-x"></i></button>
                        </div>
                    `;
                    goalsContainer.insertAdjacentHTML('beforeend', html);
                });
            }
        }

        if (data.kpis && Array.isArray(data.kpis)) {
            const kpiContainer = document.getElementById('kpiList');
            if (kpiContainer) {
                kpiContainer.innerHTML = '';
                data.kpis.forEach(kpi => {
                    const html = `
                        <div class="row g-2 mb-2 kpi-item">
                            <div class="col-md-4">
                                <input type="text" class="form-control" placeholder="KPI 명" value="${PMUtils.escapeHtml(kpi.name || kpi.metric || '')}">
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" placeholder="현재값" value="${PMUtils.escapeHtml(kpi.current || kpi.current_value || '')}">
                            </div>
                            <div class="col-md-3">
                                <input type="text" class="form-control" placeholder="목표값" value="${PMUtils.escapeHtml(kpi.target || kpi.target_value || '')}">
                            </div>
                            <div class="col-md-2">
                                <button class="btn btn-outline-danger w-100" type="button" onclick="removeKpi(this)"><i class="bi bi-x"></i></button>
                            </div>
                        </div>
                    `;
                    kpiContainer.insertAdjacentHTML('beforeend', html);
                });
            }
        }

        if (data.phases && Array.isArray(data.phases)) {
            data.phases.forEach((phase, index) => {
                let containerId = 'quickWins';
                if (index === 1) containerId = 'strategicItems';
                if (index >= 2) containerId = 'transformationalItems';

                const items = phase.activities || [];
                this.populateRoadmapPhase(containerId, items);
            });
        } else if (data.phases && typeof data.phases === 'object') {
            if (data.phases.quick_win || data.phases.quickWins) {
                this.populateRoadmapPhase('quickWins', data.phases.quick_win || data.phases.quickWins);
            }
            if (data.phases.strategic || data.phases.strategicItems) {
                this.populateRoadmapPhase('strategicItems', data.phases.strategic || data.phases.strategicItems);
            }
            if (data.phases.transformational || data.phases.transformationalItems) {
                this.populateRoadmapPhase('transformationalItems', data.phases.transformational || data.phases.transformationalItems);
            }
        }

        if (data.analysis_result) {
            this.displayAnalysisResult('roadmapAnalysisResult', data.analysis_result, 'primary', 'AI 분석 결과');
        }
    },

    /**
     * 로드맵 단계별 항목 채우기
     */
    populateRoadmapPhase(containerId, items) {
        if (!items || !Array.isArray(items)) return;

        const container = document.getElementById(containerId);
        if (!container) return;

        container.innerHTML = '';
        items.forEach(item => {
            const itemName = typeof item === 'string' ? item : (item.name || item.task || '');
            const html = `
                <div class="input-group mb-2">
                    <input type="text" class="form-control form-control-sm" placeholder="과제명" value="${PMUtils.escapeHtml(itemName)}">
                    <button class="btn btn-outline-danger btn-sm" type="button" onclick="removeItem(this)"><i class="bi bi-x"></i></button>
                </div>
            `;
            container.insertAdjacentHTML('beforeend', html);
        });
    },

    /**
     * 요건 정의 폼에 데이터 채우기
     */
    populateRequirementsForm(data) {
        if (!data) return;

        PMUtils.setInputValue('req_usecase', data.use_case_name || data.use_case);

        // Handle business_requirements (Dict or String)
        const businessReq = data.business_requirements && typeof data.business_requirements === 'object'
            ? (data.business_requirements.description || '')
            : (data.business_requirements || data.objective || '');
        PMUtils.setInputValue('req_objective', businessReq);

        // Handle functional_requirements
        const funcReq = data.functional_requirements || {};
        const inputData = funcReq.input_data || (data.data_requirements && typeof data.data_requirements === 'object' ? data.data_requirements.description : '') || data.input_data || '';
        const outputFormat = funcReq.output_format || data.output_format || '';

        PMUtils.setInputValue('req_input', inputData);
        PMUtils.setInputValue('req_output', outputFormat);

        // Handle non_functional_requirements
        const nonFunc = data.non_functional_requirements || {};
        PMUtils.setInputValue('req_accuracy', nonFunc.accuracy || data.accuracy || 95);
        PMUtils.setInputValue('req_latency', nonFunc.latency || data.latency || 100);
        PMUtils.setInputValue('req_throughput', nonFunc.throughput || data.throughput || 10);

        // Handle constraints
        const constraints = Array.isArray(data.constraints) ? data.constraints.join(', ') : (data.constraints || '');
        PMUtils.setInputValue('req_integration', constraints || data.integration_systems);

        // Handle security_requirements (can be object or string)
        let securityReq = '';
        if (data.security_requirements) {
            if (typeof data.security_requirements === 'object' && !Array.isArray(data.security_requirements)) {
                securityReq = data.security_requirements.description || data.security_requirements.value || '';
            } else {
                securityReq = data.security_requirements;
            }
        }
        PMUtils.setInputValue('req_security', securityReq);

        // Populate Success Criteria List
        if (data.success_criteria && Array.isArray(data.success_criteria)) {
            const container = document.getElementById('successCriteria');
            if (container) {
                container.innerHTML = '';
                data.success_criteria.forEach(criteria => {
                    // criteria가 객체인 경우 description 또는 value 추출
                    let criteriaText = '';
                    if (typeof criteria === 'object' && criteria !== null) {
                        criteriaText = criteria.description || criteria.value || criteria.text || '';
                    } else {
                        criteriaText = String(criteria || '');
                    }
                    const html = `
                        <div class="input-group mb-2">
                            <input type="text" class="form-control" placeholder="예: 정확도 95% 이상" value="${PMUtils.escapeHtml(criteriaText)}">
                            <button class="btn btn-outline-danger" type="button" onclick="removeItem(this)"><i class="bi bi-x"></i></button>
                        </div>
                    `;
                    container.insertAdjacentHTML('beforeend', html);
                });
            }
        }
    },

    /**
     * 아키텍처 폼에 데이터 채우기
     */
    populateArchitectureForm(data) {
        if (!data) return;

        PMUtils.setInputValue('arch_storage', data.data_storage || (data.data_architecture && data.data_architecture.storage_type));
        PMUtils.setInputValue('arch_pipeline', data.data_pipeline || (data.data_architecture && data.data_architecture.etl_approach));
        PMUtils.setInputValue('arch_training', data.training_approach || (data.ml_architecture && data.ml_architecture.training_approach));
        PMUtils.setInputValue('arch_serving', data.serving_method || (data.ml_architecture && data.ml_architecture.deployment_method));
    },

    /**
     * 거버넌스 폼에 데이터 채우기
     */
    populateGovernanceForm(data) {
        if (!data) return;

        // Privacy
        const privacy = data.privacy || data.data_privacy || {};
        PMUtils.setCheckboxValue('gov_anonymization', privacy.anonymization);
        PMUtils.setCheckboxValue('gov_consent', privacy.consent || privacy.consent_management);
        PMUtils.setCheckboxValue('gov_retention', privacy.retention || privacy.retention_policy);

        // Ethics & Explainability
        const ethics = data.ethics || data.fairness || {};
        PMUtils.setCheckboxValue('gov_bias_test', ethics.bias_test || ethics.bias_detection);
        PMUtils.setCheckboxValue('gov_fairness', ethics.fairness_check || ethics.fairness_evaluation);
        PMUtils.setCheckboxValue('gov_diverse', ethics.diverse_data);

        // XAI fields might be in ethics (new collector) or explainability (legacy)
        const xaiData = data.explainability || ethics;
        PMUtils.setInputValue('gov_xai_level', xaiData.xai_level || 'basic');
        PMUtils.setCheckboxValue('gov_decision_log', xaiData.decision_logging || xaiData.decision_log);

        // Compliance & Audit
        const compliance = data.compliance || {};
        const traceability = data.traceability || compliance; // Logic overlap

        // Regulatory checkboxes
        PMUtils.setCheckboxValue('reg_gdpr', compliance.gdpr || compliance.gdpr_compliance);
        PMUtils.setCheckboxValue('reg_pipa', compliance.pipa);
        PMUtils.setCheckboxValue('reg_iso', compliance.iso27001 || compliance.iso);
        PMUtils.setCheckboxValue('reg_aiact', compliance.eu_ai_act || compliance.aiact);

        // Audit/Traceability checkboxes
        PMUtils.setCheckboxValue('gov_model_version', traceability.model_versioning || compliance.model_versioning);
        PMUtils.setCheckboxValue('gov_data_lineage', traceability.data_lineage || compliance.data_lineage);
        PMUtils.setCheckboxValue('gov_audit_log', traceability.audit_log || compliance.audit_log);

        PMUtils.setInputValue('gov_notes', data.notes);
    },

    /**
     * PoC 폼에 데이터 채우기
     */
    populatePocForm(data) {
        if (!data) return;

        PMUtils.setInputValue('poc_usecase', data.poc_usecase || data.poc_name);
        PMUtils.setInputValue('poc_duration', data.duration || data.poc_duration);
        PMUtils.setInputValue('poc_scope', data.scope);

        if (data.phases) {
            PMUtils.setInputValue('poc_w1', data.phases.data_preparation || data.phases.w1);
            PMUtils.setInputValue('poc_w2', data.phases.model_development || data.phases.w2);
            PMUtils.setInputValue('poc_w3', data.phases.testing || data.phases.w3);
            PMUtils.setInputValue('poc_w4', data.phases.evaluation || data.phases.w4);
        }

        if (data.resources) {
            PMUtils.setInputValue('poc_ds', data.resources.data_scientist || data.resources.ds);
            PMUtils.setInputValue('poc_mle', data.resources.ml_engineer || data.resources.mle);
            PMUtils.setInputValue('poc_domain', data.resources.domain_expert || data.resources.domain);
        }
    },

    /**
     * 플랫폼 폼에 데이터 채우기
     */
    populatePlatformForm(data) {
        if (!data) return;

        if (data.components) {
            PMUtils.setInputValue('platform_pipeline', data.components.data_pipeline);
            PMUtils.setInputValue('platform_feature', data.components.feature_store);
            PMUtils.setInputValue('platform_registry', data.components.model_registry);
            PMUtils.setInputValue('platform_serving', data.components.serving_infra);
            PMUtils.setInputValue('platform_monitoring', data.components.monitoring);
        }

        PMUtils.setInputValue('platform_infra', data.infrastructure);
        PMUtils.setInputValue('platform_security', data.security_config);
        PMUtils.setInputValue('platform_scalability', data.scalability_plan);
    },

    /**
     * 통합 폼에 데이터 채우기
     */
    populateIntegrationForm(data) {
        if (!data) return;
        PMUtils.setInputValue('integration_systems', data.target_systems);
        PMUtils.setInputValue('integration_api', data.api_specifications);
        PMUtils.setInputValue('integration_dataflow', data.data_flow);
        PMUtils.setInputValue('integration_testing', data.testing_plan);
    },

    /**
     * 파일럿 폼에 데이터 채우기
     */
    populatePilotForm(data) {
        if (!data) return;

        PMUtils.setInputValue('pilot_dept', data.pilot_dept || data.target_department);
        PMUtils.setInputValue('pilot_duration', data.pilot_duration || data.duration);
        PMUtils.setInputValue('pilot_training', data.training_plan);
        PMUtils.setInputValue('pilot_support', data.support_plan);

        if (data.checklist) {
            PMUtils.setCheckboxValue('pilot_baseline', data.checklist.baseline);
            PMUtils.setCheckboxValue('pilot_feedback', data.checklist.feedback);
            PMUtils.setCheckboxValue('pilot_metrics', data.checklist.metrics);
            PMUtils.setCheckboxValue('pilot_issues', data.checklist.issues);
        }
    },

    /**
     * 변화 관리 폼에 데이터 채우기
     */
    populateChangeManagementForm(data) {
        if (!data) return;

        if (data.awareness) {
            PMUtils.setCheckboxValue('change_exec', data.awareness.executive_sponsorship);
            PMUtils.setCheckboxValue('change_comm', data.awareness.communication);
            PMUtils.setCheckboxValue('change_benefit', data.awareness.benefit_messaging);
        }

        if (data.training) {
            PMUtils.setCheckboxValue('change_basic', data.training.basic_training);
            PMUtils.setCheckboxValue('change_advanced', data.training.advanced_training);
            PMUtils.setCheckboxValue('change_cert', data.training.certification);
        }

        if (data.support) {
            PMUtils.setCheckboxValue('change_helpdesk', data.support.helpdesk);
            PMUtils.setCheckboxValue('change_champion', data.support.champion);
            PMUtils.setCheckboxValue('change_feedback', data.support.feedback);
        }

        PMUtils.setInputValue('change_notes', data.notes);
    },

    /**
     * 확산 폼에 데이터 채우기
     */
    populateScaleForm(data) {
        if (!data) return;

        PMUtils.setInputValue('scale_infra', data.infra_expansion || data.infrastructure);
        PMUtils.setInputValue('scale_optimize', data.optimization || data.model_optimization);
    },

    /**
     * 모니터링 폼에 데이터 채우기
     */
    populateMonitoringForm(data) {
        if (!data) return;

        if (data.metrics) {
            PMUtils.setCheckboxValue('monitor_latency', data.metrics.latency);
            PMUtils.setCheckboxValue('monitor_throughput', data.metrics.throughput);
            PMUtils.setCheckboxValue('monitor_accuracy', data.metrics.accuracy);
            PMUtils.setCheckboxValue('monitor_drift', data.metrics.drift);
        }

        if (data.business_metrics) {
            PMUtils.setCheckboxValue('monitor_cost', data.business_metrics.cost_saving);
            PMUtils.setCheckboxValue('monitor_productivity', data.business_metrics.productivity);
            PMUtils.setCheckboxValue('monitor_quality', data.business_metrics.quality);
        }

        PMUtils.setInputValue('monitor_thresholds', data.alert_thresholds);
        PMUtils.setInputValue('monitor_dashboard', data.dashboard_config);
        PMUtils.setInputValue('monitor_frequency', data.reporting_frequency);
    },

    /**
     * 개선 폼에 데이터 채우기
     */
    populateImprovementForm(data) {
        if (!data) return;

        PMUtils.setInputValue('improve_retrain', data.retrain_cycle || data.improvement_cycle);
        PMUtils.setInputValue('improve_threshold', data.retrain_threshold || data.threshold);
        PMUtils.setInputValue('improve_doc', data.documentation || data.feedback_sources);
    },

    /**
     * 거버넌스 검토 폼에 데이터 채우기
     */
    populateGovernanceReviewForm(data) {
        if (!data) return;

        PMUtils.setInputValue('gov_audit_cycle', data.audit_cycle || data.review_frequency);
        PMUtils.setInputValue('gov_ethics_committee', data.ethics_committee || data.review_scope);
        PMUtils.setInputValue('gov_incident', data.incident_response || data.audit_checklist);
    },

    /**
     * 기업 프로필 폼에 데이터 채우기
     */
    populateCompanyProfileForm(data) {
        if (!data) return;

        PMUtils.setInputValue('companyName', data.name);
        PMUtils.setInputValue('industry', data.industry);
        PMUtils.setInputValue('companySize', data.company_size);

        if (data.it_infrastructure) {
            PMUtils.setCheckboxValue('hasCloud', data.it_infrastructure.has_cloud);
            PMUtils.setCheckboxValue('hasDataWarehouse', data.it_infrastructure.has_data_warehouse);
            PMUtils.setCheckboxValue('gpuAvailable', data.it_infrastructure.gpu_available);
        }

        if (data.data_assets) {
            PMUtils.setInputValue('dataVolume', data.data_assets.data_volume_tb);
            PMUtils.setInputValue('dataQuality', data.data_assets.data_quality_score);
            PMUtils.setCheckboxValue('hasDataGovernance', data.data_assets.has_data_governance);
        }

        if (data.human_resources) {
            PMUtils.setInputValue('totalEmployees', data.human_resources.total_employees);
            PMUtils.setInputValue('dataScientists', data.human_resources.data_scientist_count);
            PMUtils.setInputValue('mlEngineers', data.human_resources.ml_engineer_count);
            PMUtils.setInputValue('aiProjects', data.human_resources.ai_experience_projects);
        }

        if (data.financial_resources) {
            PMUtils.setInputValue('annualRevenue', data.financial_resources.annual_revenue_billion);
            PMUtils.setInputValue('aiBudget', data.financial_resources.ai_investment_budget);
        }

        if (data.organizational_readiness) {
            PMUtils.setInputValue('executiveSupport', data.organizational_readiness.executive_support);
            PMUtils.setInputValue('changeManagement', data.organizational_readiness.change_management_capability);
            PMUtils.setInputValue('innovationCulture', data.organizational_readiness.innovation_culture);
        }
    },

    /**
     * 분석 결과 표시
     */
    displayAnalysisResult(containerId, result, colorClass, title) {
        const resultContainer = document.getElementById(containerId);
        if (resultContainer && result) {
            resultContainer.innerHTML = `
                <div class="card mt-3">
                    <div class="card-header bg-${colorClass} text-white">
                        <i class="bi bi-robot me-2"></i>${title}
                    </div>
                    <div class="card-body">
                        <pre class="mb-0" style="white-space: pre-wrap;">${typeof result === 'string' ? result : JSON.stringify(result, null, 2)}</pre>
                    </div>
                </div>
            `;
            resultContainer.style.display = 'block';
        }
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMFormPopulator;
} else {
    window.PMFormPopulator = PMFormPopulator;
}

