"""
공통 헬퍼 함수
"""
from typing import Dict, Any


def calc_avg_score(data: Dict[str, Any]) -> float:
    """딕셔너리의 숫자 값 평균 계산"""
    values = [v for v in data.values() if isinstance(v, (int, float))]
    return sum(values) / len(values) if values else 0

