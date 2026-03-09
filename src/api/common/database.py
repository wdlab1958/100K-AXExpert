"""
데이터베이스 유틸리티 함수
프로젝트 데이터 로드/저장 관련 공통 함수
"""
import json
from typing import Optional, Dict
from datetime import datetime
from pathlib import Path

# 데이터 저장 경로 (현재 작업 디렉토리 기준)
BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROJECTS_FILE = DATA_DIR / "consulting_projects.json"


def load_projects() -> Dict:
    """프로젝트 데이터 로드"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    if PROJECTS_FILE.exists():
        with open(PROJECTS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"projects": {}}


def save_projects(data: Dict):
    """프로젝트 데이터 저장"""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(PROJECTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, default=str)


def get_project(project_id: str) -> Optional[Dict]:
    """프로젝트 조회"""
    data = load_projects()
    return data["projects"].get(project_id)


def update_project(project_id: str, updates: Dict):
    """프로젝트 업데이트"""
    data = load_projects()
    if project_id not in data["projects"]:
        data["projects"][project_id] = {"id": project_id, "created_at": datetime.now().isoformat()}
    data["projects"][project_id].update(updates)
    data["projects"][project_id]["updated_at"] = datetime.now().isoformat()
    save_projects(data)
    return data["projects"][project_id]

