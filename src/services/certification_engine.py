"""
100K-AX Expert Platform - Certification Engine
Phase 2: AX 전문가 인증 등급 자동 산정
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

import logging
from src.models.training import (
    CertificationLevel, TrainingProgress, TrainingProgressSummary, GrowthPoint
)
from datetime import datetime

logger = logging.getLogger("certification")


class CertificationEngine:
    """AX 전문가 등급 자동 산정 엔진"""

    LEVELS = {
        CertificationLevel.BEGINNER: {
            "min_tasks": 5,
            "min_roi_tasks": 0,
            "min_conversion": 0.0,
            "external_consulting": False,
            "label": "AX 개념 이해, 기본 도구 활용",
        },
        CertificationLevel.PRACTITIONER: {
            "min_tasks": 20,
            "min_roi_tasks": 10,
            "min_conversion": 0.0,
            "external_consulting": False,
            "label": "독립적 AX 과제 수행 가능",
        },
        CertificationLevel.SPECIALIST: {
            "min_tasks": 50,
            "min_roi_tasks": 25,
            "min_conversion": 0.30,
            "external_consulting": False,
            "label": "부서 내 AX 리더 역할",
        },
        CertificationLevel.EXPERT: {
            "min_tasks": 100,
            "min_roi_tasks": 50,
            "min_conversion": 0.50,
            "external_consulting": False,
            "label": "기업 전사 AX 전략 수립 가능",
        },
        CertificationLevel.MASTER: {
            "min_tasks": 100,
            "min_roi_tasks": 50,
            "min_conversion": 0.50,
            "external_consulting": True,
            "label": "산업 도메인 AX 전문가",
        },
    }

    # 등급 순서
    LEVEL_ORDER = [
        CertificationLevel.BEGINNER,
        CertificationLevel.PRACTITIONER,
        CertificationLevel.SPECIALIST,
        CertificationLevel.EXPERT,
        CertificationLevel.MASTER,
    ]

    def evaluate(self, progress: TrainingProgress) -> CertificationLevel:
        """실무자의 현재 자격 등급 산정"""
        current_level = CertificationLevel.BEGINNER

        for level in self.LEVEL_ORDER:
            req = self.LEVELS[level]
            if (
                progress.total_tasks_completed >= req["min_tasks"]
                and progress.roi_achieved_tasks >= req["min_roi_tasks"]
                and progress.dept_conversion_rate >= req["min_conversion"]
            ):
                if level == CertificationLevel.MASTER:
                    if progress.external_consulting:
                        current_level = level
                else:
                    current_level = level

        return current_level

    def get_next_level_gap(self, progress: TrainingProgress) -> dict:
        """다음 등급까지 필요한 요건 갭 분석"""
        current = self.evaluate(progress)
        current_idx = self.LEVEL_ORDER.index(current)

        if current_idx >= len(self.LEVEL_ORDER) - 1:
            return {"status": "max_level", "message": "최고 등급 AX Master에 도달했습니다."}

        next_level = self.LEVEL_ORDER[current_idx + 1]
        req = self.LEVELS[next_level]

        gap = {
            "next_level": next_level.value,
            "tasks_needed": max(0, req["min_tasks"] - progress.total_tasks_completed),
            "roi_tasks_needed": max(0, req["min_roi_tasks"] - progress.roi_achieved_tasks),
            "conversion_needed": max(0.0, req["min_conversion"] - progress.dept_conversion_rate),
            "external_consulting_needed": req["external_consulting"] and not progress.external_consulting,
        }
        gap["completion_pct"] = self._calculate_completion(progress, req)
        return gap

    def _calculate_completion(self, progress: TrainingProgress, req: dict) -> float:
        """다음 등급 달성률 계산"""
        metrics = []
        if req["min_tasks"] > 0:
            metrics.append(min(1.0, progress.total_tasks_completed / req["min_tasks"]))
        if req["min_roi_tasks"] > 0:
            metrics.append(min(1.0, progress.roi_achieved_tasks / req["min_roi_tasks"]))
        if req["min_conversion"] > 0:
            metrics.append(min(1.0, progress.dept_conversion_rate / req["min_conversion"]))
        return round(sum(metrics) / len(metrics) * 100, 1) if metrics else 100.0

    def generate_summary(self, progress: TrainingProgress) -> TrainingProgressSummary:
        """학습 진도 요약 생성"""
        level = self.evaluate(progress)
        gap = self.get_next_level_gap(progress)
        skill = progress.skill_radar
        skill_score = round(
            (skill.ax_discovery + skill.roi_analysis + skill.risk_assessment
             + skill.implementation + skill.change_management + skill.report_generation) / 6, 1
        )

        return TrainingProgressSummary(
            user_id=progress.user_id,
            user_name=progress.user_name,
            current_level=level.value,
            total_tasks=progress.total_tasks_completed,
            roi_tasks=progress.roi_achieved_tasks,
            conversion_rate=progress.dept_conversion_rate,
            skill_score=skill_score,
            next_level=gap.get("next_level", "MAX"),
            next_level_gap=gap,
        )

    def update_skills_from_task(self, progress: TrainingProgress, task_type: str) -> TrainingProgress:
        """과제 완료 시 역량 점수 자동 업데이트"""
        increment = 2.0
        radar = progress.skill_radar

        skill_map = {
            "discovery": "ax_discovery",
            "roi": "roi_analysis",
            "risk": "risk_assessment",
            "implementation": "implementation",
            "change": "change_management",
            "report": "report_generation",
        }

        field = skill_map.get(task_type, "ax_discovery")
        current = getattr(radar, field)
        setattr(radar, field, min(100.0, current + increment))

        # 모든 역량에 소폭 증가
        for f in skill_map.values():
            if f != field:
                cur = getattr(radar, f)
                setattr(radar, f, min(100.0, cur + 0.5))

        progress.skill_radar = radar
        return progress

    def award_badges(self, progress: TrainingProgress) -> list[str]:
        """배지 자동 부여"""
        new_badges = []

        badge_rules = [
            ("first_task", "첫 AX 과제 완료", lambda p: p.total_tasks_completed >= 1),
            ("roi_achiever", "첫 ROI 달성", lambda p: p.roi_achieved_tasks >= 1),
            ("ten_tasks", "10건 과제 달성", lambda p: p.total_tasks_completed >= 10),
            ("fifty_tasks", "50건 과제 달성", lambda p: p.total_tasks_completed >= 50),
            ("century", "100건 과제 달성", lambda p: p.total_tasks_completed >= 100),
            ("roi_master", "ROI 50건 달성", lambda p: p.roi_achieved_tasks >= 50),
            ("converter", "전환율 30% 달성", lambda p: p.dept_conversion_rate >= 0.3),
            ("domain_expert", "AX Expert 달성", lambda p: self.evaluate(p) == CertificationLevel.EXPERT),
            ("grand_master", "AX Master 달성", lambda p: self.evaluate(p) == CertificationLevel.MASTER),
        ]

        for badge_id, badge_name, condition in badge_rules:
            if badge_id not in progress.badges and condition(progress):
                new_badges.append(badge_id)
                progress.badges.append(badge_id)
                logger.info(f"배지 부여: {progress.user_id} → {badge_name}")

        return new_badges


# 싱글톤
_engine: CertificationEngine | None = None


def get_certification_engine() -> CertificationEngine:
    global _engine
    if _engine is None:
        _engine = CertificationEngine()
    return _engine
