"""
AI Consulting Assistant Platform - Consulting Process Logger
컨설팅 프로세스 전용 로깅 시스템
터미널 실시간 출력 및 파일 로그 저장
"""
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Optional
from config.settings import settings


class ConsultingLogger:
    """컨설팅 프로세스 전용 로거"""
    
    _instance: Optional['ConsultingLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """로거 초기화"""
        if self._logger is not None:
            return
        
        # 로거 생성
        self._logger = logging.getLogger('consulting_process')
        self._logger.setLevel(logging.DEBUG)
        self._logger.handlers.clear()  # 기존 핸들러 제거
        
        # 로그 포맷 설정
        detailed_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        simple_format = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # 콘솔 핸들러 (터미널 실시간 출력)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_format)
        self._logger.addHandler(console_handler)
        
        # 파일 핸들러 (상세 로그 저장)
        log_dir = settings.DATA_DIR / "consulting_logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        
        log_file = log_dir / f"consulting_{datetime.now().strftime('%Y%m%d')}.log"
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(detailed_format)
        self._logger.addHandler(file_handler)
    
    def info(self, message: str, project_id: Optional[str] = None):
        """정보 로그"""
        if project_id:
            message = f"[프로젝트: {project_id}] {message}"
        self._logger.info(message)
    
    def debug(self, message: str, project_id: Optional[str] = None):
        """디버그 로그"""
        if project_id:
            message = f"[프로젝트: {project_id}] {message}"
        self._logger.debug(message)
    
    def warning(self, message: str, project_id: Optional[str] = None):
        """경고 로그"""
        if project_id:
            message = f"[프로젝트: {project_id}] {message}"
        self._logger.warning(message)
    
    def error(self, message: str, project_id: Optional[str] = None, exc_info=False):
        """에러 로그"""
        if project_id:
            message = f"[프로젝트: {project_id}] {message}"
        self._logger.error(message, exc_info=exc_info)
    
    def stage_start(self, stage_name: str, project_id: Optional[str] = None):
        """단계 시작 로그"""
        separator = "=" * 70
        self.info("")
        self.info(separator)
        self.info(f"🚀 단계 시작: {stage_name}", project_id)
        self.info(separator)
    
    def stage_complete(self, stage_name: str, project_id: Optional[str] = None):
        """단계 완료 로그"""
        self.info(f"✅ 단계 완료: {stage_name}", project_id)
        self.info("")
    
    def agent_start(self, agent_name: str, task: str, project_id: Optional[str] = None):
        """에이전트 시작 로그"""
        self.info(f"🤖 [{agent_name}] 작업 시작: {task}", project_id)
    
    def agent_complete(self, agent_name: str, task: str, project_id: Optional[str] = None, result: Optional[dict] = None):
        """에이전트 완료 로그"""
        self.info(f"✅ [{agent_name}] 작업 완료: {task}", project_id)
        if result:
            self.debug(f"   결과 요약: {self._summarize_result(result)}", project_id)
    
    def agent_error(self, agent_name: str, task: str, error: Exception, project_id: Optional[str] = None):
        """에이전트 에러 로그"""
        self.error(f"❌ [{agent_name}] 작업 실패: {task} - {str(error)}", project_id, exc_info=True)
    
    def progress(self, message: str, project_id: Optional[str] = None):
        """진행 상황 로그"""
        self.info(f"📊 {message}", project_id)
    
    def _summarize_result(self, result: dict) -> str:
        """결과 요약"""
        if isinstance(result, dict):
            keys = list(result.keys())[:3]  # 처음 3개 키만 표시
            return f"키: {', '.join(keys)}"
        return str(result)[:100]  # 처음 100자만


def get_consulting_logger() -> ConsultingLogger:
    """ConsultingLogger 싱글톤 인스턴스 반환"""
    return ConsultingLogger()

