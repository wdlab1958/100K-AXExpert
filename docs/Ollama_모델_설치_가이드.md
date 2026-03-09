# Ollama 모델 설치 가이드
> Update: March 9, 2026 / Designer: Brian Lee / 100K AX Expert Team

## 문제 상황
브라우저 콘솔에서 다음 오류가 발생했습니다:
```
Ollama call failed with status code 404. Maybe your model is not found and you should pull the model with `ollama pull llama3.1:8b`.
```

## 해결 방법

### 방법 1: Ollama CLI 사용 (권장)
```bash
ollama pull llama3.1:8b
```

### 방법 2: Ollama API 사용
```bash
curl http://localhost:11434/api/pull -d '{"name": "llama3.1:8b"}'
```

### 방법 3: 대체 모델 사용
현재 설치된 모델을 사용하도록 설정을 변경할 수 있습니다:
- `llama3:latest` (이미 설치됨)
- `mistral`
- `gemma2`

## 현재 상태 확인

### 설치된 모델 확인
```bash
curl http://localhost:11434/api/tags | python3 -m json.tool
```

### 모델 테스트
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1:8b",
  "prompt": "안녕하세요",
  "stream": false
}'
```

## 설정 변경 (선택사항)

만약 다른 모델을 사용하고 싶다면 `config/settings.py`를 수정하세요:

```python
OLLAMA_MODEL: str = "llama3:latest"  # 또는 다른 모델
```

## 다운로드 진행 상황

현재 `llama3.1:8b` 모델이 다운로드 중입니다. 약 4.9GB 크기이므로 인터넷 속도에 따라 시간이 걸릴 수 있습니다.

다운로드가 완료되면 자동으로 사용 가능합니다.

## 참고사항

- Ollama 서버는 `http://localhost:11434`에서 실행 중입니다
- 모델 다운로드는 백그라운드에서 진행됩니다
- 다운로드 중에도 서버는 정상 작동하지만, LLM 기능은 모델 설치 후에만 사용 가능합니다

