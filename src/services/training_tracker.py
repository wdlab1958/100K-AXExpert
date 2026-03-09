"""
100K-AX Expert Platform - Training Progress Tracker
Phase 2: 실무자별 AX 역량 성장 추적 서비스
"""
import sys
sys.path.append('/home/ubuntu-02/ai_project/100K-Expert')

import json
import uuid
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.models.training import (
    TrainingProgress, AXTask, TaskStatus, GrowthPoint,
    SkillRadar, DepartmentAXStatus, EnterpriseAXDashboard,
    CertificationLevel, AXTaskCreate
)
from src.services.certification_engine import get_certification_engine

logger = logging.getLogger("training_tracker")

DATA_DIR = Path("/home/ubuntu-02/ai_project/100K-Expert/data/training")
DATA_DIR.mkdir(parents=True, exist_ok=True)


class TrainingTracker:
    """AX 전문가 양성 추적 서비스"""

    def __init__(self):
        self.engine = get_certification_engine()
        self._users: dict[str, TrainingProgress] = {}
        self._load_data()

    # ============================================================
    # 데이터 영속성
    # ============================================================
    def _load_data(self):
        """저장된 학습 데이터 로드"""
        data_file = DATA_DIR / "training_data.json"
        if data_file.exists():
            try:
                raw = json.loads(data_file.read_text(encoding="utf-8"))
                for uid, data in raw.items():
                    self._users[uid] = TrainingProgress(**data)
                logger.info(f"학습 데이터 로드: {len(self._users)}명")
            except Exception as e:
                logger.error(f"학습 데이터 로드 실패: {e}")

    def _save_data(self):
        """학습 데이터 저장"""
        data_file = DATA_DIR / "training_data.json"
        try:
            raw = {uid: prog.model_dump() for uid, prog in self._users.items()}
            data_file.write_text(json.dumps(raw, ensure_ascii=False, indent=2, default=str), encoding="utf-8")
        except Exception as e:
            logger.error(f"학습 데이터 저장 실패: {e}")

    # ============================================================
    # 사용자 관리
    # ============================================================
    def register_user(self, user_id: str, user_name: str, company_id: str,
                      company_name: str, department: str, domain: str = "manufacturing") -> TrainingProgress:
        """신규 실무자 등록"""
        if user_id in self._users:
            return self._users[user_id]

        progress = TrainingProgress(
            user_id=user_id,
            user_name=user_name,
            company_id=company_id,
            company_name=company_name,
            department=department,
            domain=domain,
        )
        # 초기 성장 기록
        progress.growth_history.append(GrowthPoint(
            date=datetime.now().strftime("%Y-%m-%d"),
            level=CertificationLevel.BEGINNER.value,
            total_tasks=0, roi_tasks=0, skill_score=0.0,
            event="학습자 등록"
        ))
        self._users[user_id] = progress
        self._save_data()
        logger.info(f"실무자 등록: {user_name} ({department})")
        return progress

    def get_user(self, user_id: str) -> Optional[TrainingProgress]:
        """실무자 정보 조회"""
        return self._users.get(user_id)

    def list_users(self, company_id: str = "", department: str = "") -> list[TrainingProgress]:
        """실무자 목록 조회"""
        users = list(self._users.values())
        if company_id:
            users = [u for u in users if u.company_id == company_id]
        if department:
            users = [u for u in users if u.department == department]
        return users

    # ============================================================
    # AX 과제 관리
    # ============================================================
    def add_task(self, user_id: str, task_data: AXTaskCreate) -> Optional[AXTask]:
        """AX 과제 추가"""
        user = self._users.get(user_id)
        if not user:
            return None

        task = AXTask(
            task_id=str(uuid.uuid4())[:8],
            title=task_data.title,
            department=task_data.department,
            description=task_data.description,
            domain=task_data.domain,
            complexity=task_data.complexity,
            roi_potential=task_data.roi_potential,
            investment_cost=task_data.investment_cost,
            status=TaskStatus.DISCOVERED,
        )
        user.tasks.append(task)
        user.last_activity = datetime.now().isoformat()
        self._save_data()
        return task

    def start_task(self, user_id: str, task_id: str) -> Optional[AXTask]:
        """AX 과제 시작"""
        user = self._users.get(user_id)
        if not user:
            return None

        for task in user.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.IN_PROGRESS
                task.started_at = datetime.now().isoformat()
                user.last_activity = datetime.now().isoformat()
                self._save_data()
                return task
        return None

    def complete_task(self, user_id: str, task_id: str,
                      roi_achieved: float = 0.0, dx_level_after: int = 0) -> Optional[dict]:
        """AX 과제 완료 처리"""
        user = self._users.get(user_id)
        if not user:
            return None

        for task in user.tasks:
            if task.task_id == task_id:
                task.status = TaskStatus.COMPLETED
                task.completed_at = datetime.now().isoformat()
                task.dx_level_after = dx_level_after
                task.roi_achieved = roi_achieved

                if roi_achieved > 0:
                    task.status = TaskStatus.ROI_ACHIEVED
                    user.roi_achieved_tasks += 1

                user.total_tasks_completed += 1
                user.last_activity = datetime.now().isoformat()

                # 역량 업데이트
                task_type = self._classify_task_type(task.title)
                self.engine.update_skills_from_task(user, task_type)

                # 인증 등급 재평가
                old_level = user.current_level
                new_level = self.engine.evaluate(user)
                user.current_level = new_level

                # 배지 부여
                new_badges = self.engine.award_badges(user)

                # 성장 기록
                skill = user.skill_radar
                avg_skill = round(
                    (skill.ax_discovery + skill.roi_analysis + skill.risk_assessment
                     + skill.implementation + skill.change_management + skill.report_generation) / 6, 1
                )
                user.growth_history.append(GrowthPoint(
                    date=datetime.now().strftime("%Y-%m-%d"),
                    level=new_level.value,
                    total_tasks=user.total_tasks_completed,
                    roi_tasks=user.roi_achieved_tasks,
                    skill_score=avg_skill,
                    event=f"과제 완료: {task.title}"
                ))

                self._save_data()

                result = {
                    "task": task.model_dump(),
                    "level_changed": old_level != new_level,
                    "old_level": old_level.value if isinstance(old_level, CertificationLevel) else old_level,
                    "new_level": new_level.value,
                    "new_badges": new_badges,
                    "total_tasks": user.total_tasks_completed,
                    "roi_tasks": user.roi_achieved_tasks,
                    "next_level_gap": self.engine.get_next_level_gap(user),
                }
                logger.info(f"과제 완료: {user.user_name} - {task.title} (Level: {new_level.value})")
                return result
        return None

    def _classify_task_type(self, title: str) -> str:
        """과제 제목으로 유형 분류"""
        keywords = {
            "discovery": ["발굴", "분석", "진단", "탐색"],
            "roi": ["ROI", "비용", "절감", "투자", "매출"],
            "risk": ["리스크", "위험", "보안", "안전"],
            "implementation": ["구현", "구축", "개발", "설치", "도입"],
            "change": ["변화", "교육", "조직", "관리"],
            "report": ["보고서", "리포트", "문서", "보고"],
        }
        for task_type, kws in keywords.items():
            if any(kw in title for kw in kws):
                return task_type
        return "discovery"

    # ============================================================
    # 부서 / 기업 대시보드
    # ============================================================
    def get_department_status(self, company_id: str, department: str) -> DepartmentAXStatus:
        """부서별 AX 전환 현황"""
        users = [u for u in self._users.values()
                 if u.company_id == company_id and u.department == department]

        status = DepartmentAXStatus(department=department, company_id=company_id)
        status.total_tasks = sum(len(u.tasks) for u in users)
        status.completed_tasks = sum(u.total_tasks_completed for u in users)
        status.total_roi_saving = sum(
            t.annual_saving for u in users for t in u.tasks if t.status == TaskStatus.ROI_ACHIEVED
        )
        if status.total_tasks > 0:
            status.conversion_rate = round(status.completed_tasks / status.total_tasks, 3)

        for u in users:
            level_key = u.current_level.value.split()[-1].lower() if isinstance(u.current_level, CertificationLevel) else "beginner"
            if level_key in status.experts_count:
                status.experts_count[level_key] += 1

        return status

    def get_enterprise_dashboard(self, company_id: str, company_name: str = "") -> EnterpriseAXDashboard:
        """기업 전체 AX 성과 대시보드"""
        users = [u for u in self._users.values() if u.company_id == company_id]
        departments = set(u.department for u in users)

        dashboard = EnterpriseAXDashboard(
            company_id=company_id,
            company_name=company_name or (users[0].company_name if users else ""),
            total_employees_trained=len(users),
            total_departments=len(departments),
            total_tasks_completed=sum(u.total_tasks_completed for u in users),
            total_roi_achieved=sum(
                t.annual_saving for u in users for t in u.tasks if t.status == TaskStatus.ROI_ACHIEVED
            ),
        )

        if users:
            dashboard.avg_conversion_rate = round(
                sum(u.dept_conversion_rate for u in users) / len(users), 3
            )

        for u in users:
            level_key = u.current_level.value.split()[-1].lower() if isinstance(u.current_level, CertificationLevel) else "beginner"
            if level_key in dashboard.certification_distribution:
                dashboard.certification_distribution[level_key] += 1

        for dept in sorted(departments):
            ds = self.get_department_status(company_id, dept)
            dashboard.department_statuses.append(ds)

        # Top ROI 과제
        all_roi_tasks = [
            t for u in users for t in u.tasks
            if t.status == TaskStatus.ROI_ACHIEVED
        ]
        all_roi_tasks.sort(key=lambda x: x.annual_saving, reverse=True)
        dashboard.top_roi_tasks = all_roi_tasks[:10]

        return dashboard

    # ============================================================
    # 통계
    # ============================================================
    def get_platform_stats(self) -> dict:
        """플랫폼 전체 통계"""
        users = list(self._users.values())
        companies = set(u.company_id for u in users if u.company_id)

        total_tasks = sum(u.total_tasks_completed for u in users)
        total_roi_tasks = sum(u.roi_achieved_tasks for u in users)

        level_dist = {}
        for level in CertificationLevel:
            level_dist[level.value] = sum(1 for u in users if u.current_level == level)

        return {
            "total_users": len(users),
            "total_companies": len(companies),
            "total_tasks_completed": total_tasks,
            "total_roi_tasks": total_roi_tasks,
            "certification_distribution": level_dist,
            "goal_progress": {
                "target": 100000,
                "current": len(users),
                "percentage": round(len(users) / 100000 * 100, 4),
            },
        }


# 싱글톤
_tracker: TrainingTracker | None = None


def get_training_tracker() -> TrainingTracker:
    global _tracker
    if _tracker is None:
        _tracker = TrainingTracker()
    return _tracker
