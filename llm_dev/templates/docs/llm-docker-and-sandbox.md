# 🐳 LLM Docker 컨테이너화 & Agent Sandbox 격리 가이드 (LLM Docker & Sandbox)

> **"로컬부터 운영까지 재현 가능한 개발 환경 표준화 및 LLM Agent 코드 실행을 위한 안전한 Docker Sandbox 격리 인프라 구축 가이드"**

---

## 1. 개요 및 필요성 (Why Docker & Sandbox First?)

LLM 개발에서 Docker는 단순 배포 도구를 넘어 **환경 재현성**과 **보안 격리**의 핵심 인프라입니다:

1. **복잡한 의존성 표준화:** Python 버전, PyTorch/CUDA, C++ 라이브러리(tiktoken, llama.cpp), Vector DB(Qdrant, Chroma, PGvector) 등 파편화된 환경을 `docker-compose` 단 한 줄로 일관되게 기동합니다.
2. **LLM Agent 코드 실행 격리 (CRITICAL):** Function Calling이나 Auto-Agent가 생성한 파이썬 스크립트나 쉘 명령을 호스트 머신에서 직접 실행하는 것은 **시스템 파괴 및 보안 탈취의 직접적인 통로**가 됩니다. 반드시 **네트워크가 차단되고 자원이 제한된 임시 Docker 샌드박스(Sandbox)** 안에서 격리 실행해야 합니다.

---

## 2. LLM 서비스 프로덕션 Dockerfile 표준 (Best Practices)

### 2.1 Python / FastAPI LLM 백엔드 Dockerfile (`Dockerfile.fastapi`)
- **특징:** Multi-stage 빌드, 가상환경 캐싱, Non-root 사용자 적용, 경량 슬림 이미지(`python:3.11-slim`).

```dockerfile
# -------------------------------------------------------------
# Stage 1: Build & Dependency Resolution
# -------------------------------------------------------------
FROM python:3.11-slim AS builder

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=on

# 빌드 필수 시스템 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 가상환경 생성 및 의존성 설치
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# -------------------------------------------------------------
# Stage 2: Production Runtime
# -------------------------------------------------------------
FROM python:3.11-slim AS runner

WORKDIR /app

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    APP_ENV=production

# 보안: Non-root 유저 생성
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/bash -m appuser

# 빌더 스테이지에서 의존성 복사
COPY --from=builder /opt/venv /opt/venv

# 애플리케이션 소스 복사 및 권한 부여
COPY --chown=appuser:appgroup . .

# Non-root 유저로 전환
USER appuser

EXPOSE 8000

# 헬스체크 정의
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
```

---

### 2.2 Java 21 / Spring Boot 3 LLM 백엔드 Dockerfile (`Dockerfile.springboot`)
- **특징:** Java 21 런타임 분리, 계층형 레이어 추출(Layer Tools), 가상 스레드 최적화.

```dockerfile
# -------------------------------------------------------------
# Stage 1: Build
# -------------------------------------------------------------
FROM eclipse-temurin:21-jdk-alpine AS builder

WORKDIR /workspace/app

COPY gradlew .
COPY gradle gradle
COPY build.gradle settings.gradle ./
RUN chmod +x ./gradlew && ./gradlew dependencies --no-daemon

COPY src src
RUN ./gradlew bootJar --no-daemon -x test

# Spring Boot 계층형 JAR 추출
RUN java -Djarmode=layertools -jar build/libs/*.jar extract --destination extracted

# -------------------------------------------------------------
# Stage 2: Runtime
# -------------------------------------------------------------
FROM eclipse-temurin:21-jre-alpine AS runner

WORKDIR /application

# 보안: Non-root 사용자 생성
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# 계층별 레이어 복사 (Docker 빌드 캐시 극대화)
COPY --from=builder /workspace/app/extracted/dependencies/ ./
COPY --from=builder /workspace/app/extracted/spring-boot-loader/ ./
COPY --from=builder /workspace/app/extracted/snapshot-dependencies/ ./
COPY --from=builder /workspace/app/extracted/application/ ./

USER appuser

EXPOSE 8080

ENV JAVA_OPTS="-XX:+UseG1GC -XX:MaxRAMPercentage=75.0"

ENTRYPOINT ["sh", "-c", "java $JAVA_OPTS org.springframework.boot.loader.launch.JarLauncher"]
```

---

## 3. 통합 로컬 개발 환경 구성 (`docker-compose.llm-dev.yml`)

LLM 백엔드, Vector DB(Qdrant), 로컬 모델 서버(Ollama), EFK 중앙 로깅 시스템이 한 번에 유기적으로 연동되는 마스터 Compose 파일입니다.

```yaml
version: '3.8'

networks:
  llm-network:
    name: llm-network
    driver: bridge

volumes:
  es_data:
  qdrant_data:
  ollama_models:

services:
  # 1. 중앙 로깅: Elasticsearch
  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.13.4
    container_name: dev-elasticsearch
    environment:
      - discovery.type=single-node
      - "ES_JAVA_OPTS=-Xms512m -Xmx512m"
      - xpack.security.enabled=false
    ports:
      - "9200:9200"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - llm-network

  # 2. 중앙 로깅: Fluent Bit 로그 수집기
  fluent-bit:
    image: fluent/fluent-bit:3.0.4
    container_name: dev-fluent-bit
    ports:
      - "24224:24224"
    volumes:
      - ./logging/fluent-bit.conf:/fluent-bit/etc/fluent-bit.conf:ro
    depends_on:
      - elasticsearch
    networks:
      - llm-network

  # 3. 중앙 로깅 대시보드: Kibana
  kibana:
    image: docker.elastic.co/kibana/kibana:8.13.4
    container_name: dev-kibana
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    ports:
      - "5601:5601"
    depends_on:
      - elasticsearch
    networks:
      - llm-network

  # 4. 고성능 Vector DB: Qdrant
  qdrant:
    image: qdrant/qdrant:v1.9.0
    container_name: dev-qdrant
    ports:
      - "6333:6333" # HTTP REST API
      - "6334:6334" # gRPC API
    volumes:
      - qdrant_data:/qdrant/storage
    networks:
      - llm-network

  # 5. 로컬 오픈소스 LLM & 임베딩 서버: Ollama
  ollama:
    image: ollama/ollama:latest
    container_name: dev-ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama
    networks:
      - llm-network
    # GPU가 있는 경우 deploy 블록 활성화
    # deploy:
    #   resources:
    #     reservations:
    #       devices:
    #         - driver: nvidia
    #           count: all
    #           capabilities: [gpu]

  # 6. 메인 LLM 백엔드 애플리케이션
  llm-backend:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: dev-llm-backend
    environment:
      - APP_ENV=development
      - QDRANT_URL=http://qdrant:6333
      - OLLAMA_BASE_URL=http://ollama:11434
      - ELASTICSEARCH_URL=http://elasticsearch:9200
      - GEMINI_API_KEY=${GEMINI_API_KEY}
    ports:
      - "8080:8080"
    depends_on:
      - qdrant
      - fluent-bit
    networks:
      - llm-network
```

---

## 4. LLM Agent 코드 실행을 위한 Docker Sandbox 격리 환경 (CRITICAL)

### 4.1 샌드박스 격리 5대 원칙 (Security Invariants)

LLM이 생성한 Python 스크립트나 터미널 명령을 실행할 때 반드시 준수해야 하는 격리 원칙입니다.

```
┌──────────────────────────────────────────────────────────────────┐
│                   Docker Sandbox 5대 보안 통제                  │
├──────────────────────────────────────────────────────────────────┤
│ 1. 🚫 Network None: 외부 인터넷 및 사내 내부망 접근 완전 차단   │
│ 2. ⏳ Ephemeral Container: 실행 후 즉시 컨테이너 자동 파기 (--rm)│
│ 3. 🔒 Read-Only Filesystem: 루트 FS 쓰기 금지 (임시 메모리만 허용)│
│ 4. 🛑 Resource Limit: CPU 최대 1코어, RAM 256MB 등 강제 제한   │
│ 5. ⏱️ Hard Timeout: 5~10초 초과 시 강제 kill (무한 루프 방지)   │
└──────────────────────────────────────────────────────────────────┘
```

---

### 4.2 Python 기반 안전한 Docker Sandbox 실행기 구현

`docker-py` 라이브러리를 사용하여 생성된 파이썬 코드를 완벽히 격리된 일회성 컨테이너에서 실행하는 레퍼런스 코드입니다.

```python
import docker
import os
import tempfile
from typing import Dict, Any

class SafeCodeSandbox:
    def __init__(self, image_name: str = "python:3.11-alpine"):
        self.client = docker.from_env()
        self.image_name = image_name

    def execute_python_code(self, code_snippet: str, timeout_sec: int = 5) -> Dict[str, Any]:
        """
        LLM이 생성한 파이썬 코드를 네트워크 차단 및 자원 제한 샌드박스에서 실행합니다.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            script_path = os.path.join(temp_dir, "script.py")
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(code_snippet)

            try:
                # 샌드박스 컨테이너 생성 및 실행
                container = self.client.containers.run(
                    image=self.image_name,
                    command=["python", "/sandbox/script.py"],
                    volumes={
                        temp_dir: {"bind": "/sandbox", "mode": "ro"} # Read-Only 마운트
                    },
                    network_mode="none",             # 1. 네트워크 완전 차단 (외부 API/데이터 탈취 방지)
                    mem_limit="256m",                 # 2. 메모리 제한 256MB (메모리 고갈 방지)
                    cpu_period=100000,
                    cpu_quota=50000,                  # 3. CPU 0.5 코어로 제한
                    read_only=True,                   # 4. 루트 파일시스템 읽기 전용
                    tmpfs={"/tmp": "size=16m,noexec"},# 5. 임시 공간 제한 및 실행 금지
                    user="10001:10001",               # 6. Non-root 사용자
                    detach=True,
                    stdout=True,
                    stderr=True,
                    remove=False
                )

                # 타임아웃 대기 (무한 루프 방어)
                try:
                    result = container.wait(timeout=timeout_sec)
                    exit_code = result.get("StatusCode", 1)
                    logs = container.logs().decode("utf-8")
                except Exception:
                    container.kill()
                    return {
                        "success": False,
                        "exit_code": -1,
                        "output": f"Execution timed out after {timeout_sec} seconds."
                    }
                finally:
                    container.remove(force=True)

                return {
                    "success": (exit_code == 0),
                    "exit_code": exit_code,
                    "output": logs
                }

            except Exception as e:
                return {
                    "success": False,
                    "exit_code": -1,
                    "output": f"Sandbox error: {str(e)}"
                }

# 사용 예시:
if __name__ == "__main__":
    sandbox = SafeCodeSandbox()
    test_code = """
import sys
# 샌드박스 계산 테스트
result = sum([i * i for i in range(1000)])
print(f"Calculated Result: {result}")
"""
    res = sandbox.execute_python_code(test_code)
    print("Execution Result:", res)
```

---

## 5. 컨테이너 보안 & 최적화 점검 목록

- [x] **도커 데몬 소켓 노출 금지:** `/var/run/docker.sock`을 일반 웹 애플리케이션 컨테이너에 직접 마운트하지 않습니다.
- [x] **Multi-stage 빌드로 이미지 경량화:** 빌드 툴(컴파일러, git 등)이 런타임 이미지에 남지 않도록 합니다.
- [x] **민감 정보 ARG/ENV 직접 포함 금지:** API Key나 Secret은 `docker build --secret` 또는 런타임 환경변수로만 전달합니다.
- [x] **Sandbox 자원 상한 강제:** CPU/Memory Limit 없이 사용자/Agent 코드를 절대 실행하지 않습니다.
