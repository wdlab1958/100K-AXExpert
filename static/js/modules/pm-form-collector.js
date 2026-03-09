/**
 * Project Manager - 폼 데이터 수집 모듈
 * 각 Stage의 폼 데이터를 수집하는 함수들
 */

const PMFormCollector = {
    /**
     * 성숙도 진단 데이터 수집
     */
    collectMaturityData() {
        return {
            strategy: {
                ai_vision_clarity: PMUtils.getInputValue('maturity_strategy_vision', 'number') || 3,
                ai_investment_management: PMUtils.getInputValue('maturity_strategy_investment', 'number') || 3,
                usecase_portfolio_management: PMUtils.getInputValue('maturity_strategy_portfolio', 'number') || 3,
                ai_roi_measurement: PMUtils.getInputValue('maturity_strategy_roi', 'number') || 3
            },
            organization: {
                ai_organization_structure: PMUtils.getInputValue('maturity_org_structure', 'number') || 3,
                ai_talent_capability: PMUtils.getInputValue('maturity_org_talent', 'number') || 3,
                ai_training_program: PMUtils.getInputValue('maturity_org_training', 'number') || 3,
                ai_change_culture: PMUtils.getInputValue('maturity_org_culture', 'number') || 3
            },
            data_technology: {
                data_infrastructure: PMUtils.getInputValue('maturity_tech_infra', 'number') || 3,
                data_quality_governance: PMUtils.getInputValue('maturity_tech_quality', 'number') || 3,
                mlops_platform: PMUtils.getInputValue('maturity_tech_mlops', 'number') || 3,
                cloud_scalability: PMUtils.getInputValue('maturity_tech_cloud', 'number') || 3
            },
            process: {
                ai_development_methodology: PMUtils.getInputValue('maturity_proc_methodology', 'number') || 3,
                model_validation_process: PMUtils.getInputValue('maturity_proc_validation', 'number') || 3,
                ai_ethics_risk_management: PMUtils.getInputValue('maturity_proc_ethics', 'number') || 3,
                ai_monitoring_operation: PMUtils.getInputValue('maturity_proc_monitoring', 'number') || 3
            },
            notes: PMUtils.getInputValue('maturity_notes', 'string') || ''
        };
    },

    /**
     * 기회 발굴 데이터 수집
     */
    collectOpportunitiesData() {
        const opportunities = [];
        const items = document.querySelectorAll('.opportunity-item');

        items.forEach((item, index) => {
            const oppId = index + 1;
            opportunities.push({
                name: PMUtils.getInputValue(`opp-name-${oppId}`, 'string') || '',
                description: PMUtils.getInputValue(`opp-desc-${oppId}`, 'string') || '',
                business_area: item.querySelector('select')?.value || '', // Area selector might be tricky if not ID'd clearly. Assuming populator didn't add area ID?
                // Wait, populator didn't add 'opp-area-${oppId}' to the card HTML! 
                // Looking at populator HTML: inputs are opp-name, opp-roi, opp-complexity, opp-desc.
                // It does NOT have area, impact, timeline, resources.
                // The display card is a SUMMARY.

                // Keep existing (even if broken for now) but fix IDs for what exists 
                // and add new fields.

                roi_potential: PMUtils.getInputValue(`opp-roi-${oppId}`, 'string') || 'high',
                complexity: PMUtils.getInputValue(`opp-complexity-${oppId}`, 'string') || 'medium',

                // New Fields
                data_availability: PMUtils.getInputValue(`opp-data-${oppId}`, 'number') || 3,
                urgency: PMUtils.getInputValue(`opp-urgency-${oppId}`, 'number') || 3,
                strategic_alignment: PMUtils.getInputValue(`opp-strategic-${oppId}`, 'number') || 3
            });
        });

        return { opportunities };
    },

    /**
     * 로드맵 데이터 수집
     */
    collectRoadmapData() {
        return {
            vision: PMUtils.getInputValue('roadmap_vision', 'string') || '',
            goals: PMUtils.collectListItems('roadmap_goals'),
            kpis: PMUtils.collectListItems('roadmap_kpis'),
            phases: this.collectPhases()
        };
    },

    /**
     * 요건 정의 데이터 수집
     */
    collectRequirementsData() {
        // 성공 기준 수집
        const successCriteria = [];
        const criteriaInputs = document.querySelectorAll('#successCriteria input[type="text"]');
        criteriaInputs.forEach(input => {
            if (input.value.trim()) {
                successCriteria.push(input.value.trim());
            }
        });

        const businessReq = PMUtils.getInputValue('req_objective', 'string') || '';
        const constraintsStr = PMUtils.getInputValue('req_integration', 'string') || '';
        const dataReq = PMUtils.getInputValue('req_input', 'string') || '';

        // 백엔드 모델에 맞게 데이터 구조 변환
        // business_requirements: Dict[str, Any] - Dict 타입이어야 함
        const businessRequirements = businessReq ? { description: businessReq } : {};

        // data_requirements: Dict[str, Any] - Dict 타입이어야 함
        const dataRequirements = dataReq ? { description: dataReq } : {};

        // constraints: List[str] - 배열이어야 함
        const constraints = constraintsStr ? [constraintsStr] : [];

        // success_criteria: List[str] - 배열이어야 함
        const finalSuccessCriteria = successCriteria.length > 0 ? successCriteria : (businessReq ? [businessReq] : []);

        return {
            use_case_name: PMUtils.getInputValue('req_usecase', 'string') || '',
            business_requirements: businessRequirements,
            functional_requirements: {
                input_data: PMUtils.getInputValue('req_input', 'string') || '',
                output_format: PMUtils.getInputValue('req_output', 'string') || ''
            },
            non_functional_requirements: {
                accuracy: parseInt(PMUtils.getInputValue('req_accuracy', 'number')) || 95,
                latency: parseInt(PMUtils.getInputValue('req_latency', 'number')) || 100,
                throughput: parseInt(PMUtils.getInputValue('req_throughput', 'number')) || 10
            },
            data_requirements: dataRequirements,
            constraints: constraints,
            success_criteria: finalSuccessCriteria
        };
    },

    /**
     * 아키텍처 데이터 수집
     */
    collectArchitectureData() {
        // 실제 HTML 필드 ID에 맞게 수정
        // integration_points는 List[str]이어야 함 (필드가 없으면 빈 배열)
        const integrationStr = PMUtils.getInputValue('arch_integration', 'string') || '';
        const integrationPoints = integrationStr ? [integrationStr] : [];

        // 데이터 아키텍처 (실제 HTML 필드 ID 사용)
        const dataArchitecture = {
            storage: PMUtils.getInputValue('arch_storage', 'string') || '',
            pipeline: PMUtils.getInputValue('arch_pipeline', 'string') || ''
        };

        // ML 아키텍처 (실제 HTML 필드 ID 사용)
        const mlArchitecture = {
            training_platform: PMUtils.getInputValue('arch_training', 'string') || '',
            serving_method: PMUtils.getInputValue('arch_serving', 'string') || ''
        };

        // 기술 스택 (실제 HTML 필드 ID 사용)
        const techStack = {
            ml_framework: PMUtils.getInputValue('tech_ml', 'string') || '',
            mlops_platform: PMUtils.getInputValue('tech_mlops', 'string') || '',
            container: PMUtils.getInputValue('tech_container', 'string') || '',
            monitoring: PMUtils.getInputValue('tech_monitor', 'string') || ''
        };

        const result = {
            data_architecture: dataArchitecture,
            ml_architecture: mlArchitecture,
            tech_stack: techStack,
            integration_points: integrationPoints
        };

        // 디버깅용 로그
        console.log('[Architecture] Collected data:', JSON.stringify(result, null, 2));

        return result;
    },

    /**
     * 거버넌스 데이터 수집
     */
    collectGovernanceData() {
        return {
            privacy: {
                anonymization: PMUtils.getCheckboxValue('gov_anonymization'),
                consent_management: PMUtils.getCheckboxValue('gov_consent'),
                retention_policy: PMUtils.getCheckboxValue('gov_retention')
            },
            ethics: {
                bias_detection: PMUtils.getCheckboxValue('gov_bias_test'),
                fairness_evaluation: PMUtils.getCheckboxValue('gov_fairness'),
                diverse_data: PMUtils.getCheckboxValue('gov_diverse'),
                xai_level: PMUtils.getInputValue('gov_xai_level'),
                decision_logging: PMUtils.getCheckboxValue('gov_decision_log')
            },
            compliance: {
                gdpr: PMUtils.getCheckboxValue('reg_gdpr'),
                pipa: PMUtils.getCheckboxValue('reg_pipa'),
                iso27001: PMUtils.getCheckboxValue('reg_iso'),
                eu_ai_act: PMUtils.getCheckboxValue('reg_aiact'),
                model_versioning: PMUtils.getCheckboxValue('gov_model_version'),
                data_lineage: PMUtils.getCheckboxValue('gov_data_lineage'),
                audit_log: PMUtils.getCheckboxValue('gov_audit_log')
            },
            notes: PMUtils.getInputValue('gov_notes', 'string') || '' // If exists in other part of HTML or used as fallback
        };
    },

    /**
     * PoC 데이터 수집
     */
    collectPocData() {
        return {
            poc_name: PMUtils.getInputValue('poc_name', 'string') || '',
            objectives: PMUtils.getInputValue('poc_objectives', 'string') || '',
            scope: PMUtils.getInputValue('poc_scope', 'string') || '',
            success_metrics: PMUtils.getInputValue('poc_metrics', 'string') || '',
            timeline: PMUtils.getInputValue('poc_timeline', 'string') || '',
            resources: PMUtils.getInputValue('poc_resources', 'string') || '',
            risks: PMUtils.getInputValue('poc_risks', 'string') || ''
        };
    },

    /**
     * 플랫폼 데이터 수집
     */
    collectPlatformData() {
        return {
            components: {
                data_pipeline: PMUtils.getInputValue('platform_pipeline', 'string') || '',
                feature_store: PMUtils.getInputValue('platform_feature', 'string') || '',
                model_registry: PMUtils.getInputValue('platform_registry', 'string') || '',
                serving_infra: PMUtils.getInputValue('platform_serving', 'string') || '',
                monitoring: PMUtils.getInputValue('platform_monitoring', 'string') || ''
            },
            infrastructure: PMUtils.getInputValue('platform_infra', 'string') || '',
            security_config: PMUtils.getInputValue('platform_security', 'string') || '',
            scalability_plan: PMUtils.getInputValue('platform_scalability', 'string') || ''
        };
    },

    /**
     * 통합 데이터 수집
     */
    collectIntegrationData() {
        return {
            target_systems: PMUtils.getInputValue('integration_systems', 'string') || '',
            api_specifications: PMUtils.getInputValue('integration_api', 'string') || '',
            data_flow: PMUtils.getInputValue('integration_dataflow', 'string') || '',
            testing_plan: PMUtils.getInputValue('integration_testing', 'string') || ''
        };
    },

    /**
     * 파일럿 데이터 수집
     */
    collectPilotData() {
        return {
            pilot_name: PMUtils.getInputValue('pilot_name', 'string') || '',
            target_department: PMUtils.getInputValue('pilot_department', 'string') || '',
            pilot_scope: PMUtils.getInputValue('pilot_scope', 'string') || '',
            duration: PMUtils.getInputValue('pilot_duration', 'string') || '',
            success_criteria: PMUtils.getInputValue('pilot_success', 'string') || '',
            support_plan: PMUtils.getInputValue('pilot_support', 'string') || ''
        };
    },

    /**
     * 변화 관리 데이터 수집
     */
    collectChangeManagementData() {
        return {
            awareness: {
                communication_plan: PMUtils.getInputValue('change_comm', 'string') || '',
                stakeholder_engagement: PMUtils.getInputValue('change_stakeholder', 'string') || '',
                benefit_messaging: PMUtils.getInputValue('change_benefit', 'string') || ''
            },
            capability: {
                training_program: PMUtils.getInputValue('change_training', 'string') || '',
                skill_development: PMUtils.getInputValue('change_skill', 'string') || '',
                certification: PMUtils.getInputValue('change_cert', 'string') || ''
            },
            engagement: {
                champion_program: PMUtils.getInputValue('change_champion', 'string') || '',
                feedback_mechanism: PMUtils.getInputValue('change_feedback', 'string') || '',
                incentive_program: PMUtils.getInputValue('change_incentive', 'string') || ''
            },
            success_sharing: {
                success_metrics: PMUtils.getInputValue('change_metrics', 'string') || '',
                sharing_platform: PMUtils.getInputValue('change_platform', 'string') || '',
                recognition_program: PMUtils.getInputValue('change_recognition', 'string') || ''
            },
            notes: PMUtils.getInputValue('change_notes', 'string') || ''
        };
    },

    /**
     * 확산 데이터 수집
     */
    collectScaleData() {
        return {
            rollout_phases: this.collectRolloutPhases(),
            target_coverage: PMUtils.getInputValue('scale_coverage', 'string') || '',
            timeline: PMUtils.getInputValue('scale_timeline', 'string') || '',
            resource_plan: PMUtils.getInputValue('scale_resources', 'string') || '',
            risk_mitigation: PMUtils.getInputValue('scale_risks', 'string') || ''
        };
    },

    /**
     * 모니터링 데이터 수집
     */
    collectMonitoringData() {
        return {
            metrics: {
                technical_metrics: PMUtils.getInputValue('monitor_tech_metrics', 'string') || '',
                business_metrics: PMUtils.getInputValue('monitor_biz_metrics', 'string') || '',
                model_metrics: PMUtils.getInputValue('monitor_model_metrics', 'string') || ''
            },
            alert_thresholds: PMUtils.getInputValue('monitor_thresholds', 'string') || '',
            dashboard_config: PMUtils.getInputValue('monitor_dashboard', 'string') || '',
            reporting_frequency: PMUtils.getInputValue('monitor_frequency', 'string') || ''
        };
    },

    /**
     * 개선 데이터 수집
     */
    collectImprovementData() {
        return {
            improvement_cycle: PMUtils.getInputValue('improve_cycle', 'string') || '',
            feedback_sources: PMUtils.getInputValue('improve_feedback', 'string') || '',
            prioritization_criteria: PMUtils.getInputValue('improve_priority', 'string') || '',
            experiment_framework: PMUtils.getInputValue('improve_experiment', 'string') || '',
            success_metrics: PMUtils.getInputValue('improve_metrics', 'string') || ''
        };
    },

    /**
     * 거버넌스 검토 데이터 수집
     */
    collectGovernanceReviewData() {
        return {
            review_frequency: PMUtils.getInputValue('govreview_frequency', 'string') || '',
            review_scope: PMUtils.getInputValue('govreview_scope', 'string') || '',
            audit_checklist: PMUtils.getInputValue('govreview_checklist', 'string') || '',
            compliance_updates: PMUtils.getInputValue('govreview_compliance', 'string') || '',
            policy_revisions: PMUtils.getInputValue('govreview_policy', 'string') || ''
        };
    },

    /**
     * Phase 수집
     */
    collectPhases() {
        const phases = [];
        document.querySelectorAll('.phase-item').forEach((item, index) => {
            phases.push({
                phase_name: PMUtils.getInputValue(`phase_name_${index}`, 'string'),
                duration: PMUtils.getInputValue(`phase_duration_${index}`, 'string'),
                key_tasks: PMUtils.getInputValue(`phase_tasks_${index}`, 'string'),
                expected_investment: PMUtils.getInputValue(`phase_investment_${index}`, 'string'),
                expected_outcome: PMUtils.getInputValue(`phase_outcome_${index}`, 'string')
            });
        });
        return phases;
    },

    /**
     * Rollout Phase 수집
     */
    collectRolloutPhases() {
        const phases = [];
        document.querySelectorAll('.rollout-phase-item').forEach((item, index) => {
            phases.push({
                phase_name: PMUtils.getInputValue(`rollout_name_${index}`, 'string'),
                target_scope: PMUtils.getInputValue(`rollout_scope_${index}`, 'string'),
                timeline: PMUtils.getInputValue(`rollout_timeline_${index}`, 'string'),
                resources: PMUtils.getInputValue(`rollout_resources_${index}`, 'string')
            });
        });
        return phases;
    }
};

// 모듈 내보내기
if (typeof module !== 'undefined' && module.exports) {
    module.exports = PMFormCollector;
} else {
    window.PMFormCollector = PMFormCollector;
}

