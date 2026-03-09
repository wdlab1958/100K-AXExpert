#!/bin/bash

# AI Consulting Assistant Platform - 실행 스크립트

echo "=============================================="
echo "  AI Consulting Assistant Platform"
echo "=============================================="

# 디렉토리 설정
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Python 환경 확인
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3이 설치되어 있지 않습니다."
    exit 1
fi

# 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo "[INFO] 가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 의존성 설치
echo "[INFO] 의존성을 설치합니다..."
pip install -q -r requirements.txt

# 필요한 디렉토리 생성
mkdir -p data reports static/css static/js

# Ollama 상태 확인
echo "[INFO] Ollama 상태를 확인합니다..."
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "[OK] Ollama가 실행 중입니다."
else
    echo "[WARNING] Ollama가 실행되고 있지 않습니다."
    echo "         'ollama serve' 명령으로 Ollama를 먼저 실행해주세요."
    echo "         LLM 기능 없이 데모 모드로 실행합니다."
fi

# 서버 실행
echo "[INFO] 서버를 시작합니다..."
echo "=============================================="
echo "  웹 브라우저에서 http://localhost:8001 접속"
echo "  API 문서: http://localhost:8001/docs"
echo "=============================================="

python3 main.py --host 0.0.0.0 --port 8001
