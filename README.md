# 🤖 LLM Development CLI & Governance Hub (`llm-dev`)

> **LLM(대형 언어 모델) 프로젝트 표준 스캐폴딩(Init), 4대 사전 인프라 진단(Doctor) 및 라이프사이클 거버넌스 자동화 도구**

---

## 📌 주요 기능 (Key Features)

- 🚀 **`llm-dev init`**: 신규 프로젝트에 4대 인프라 가이드라인 문서, AI 코딩 룰셋(`.cursorrules`, `AGENTS.md`), Docker/EFK 로깅 스택, PII 마스커 모듈을 한 번에 스캐폴딩
- 🔍 **`llm-dev doctor`**: 소스코드 및 환경을 정적 분석하여 API Key 하드코딩 여부, JSON 구조화 로깅, Docker 샌드박스 격리, Rate Limiter, API 응답 포맷 준수 여부 실시간 진단
- 📊 **`llm-dev status`**: 마크다운 체크리스트를 기반으로 Day 0 ~ Day 5 단계별 프로젝트 진척도를 터미널 프로그레스 바 형태로 집계
- 🌐 **`llm-dev view`**: Glassmorphism 다크 테마 기반의 로컬 경량 웹 대시보드 제공 (실시간 진단 및 문서 진척도 시각화)

---

## 🛠️ 설치 방법 (Installation)

### 1) 로컬 개발 모드 설치
```bash
cd /home/rudy/dev/repository/devdooly/llm-dev-cli
pip install -e .
```

설치 후 터미널 어디서든 `llm-dev` 명령어를 바로 실행할 수 있습니다.

---

## 🚀 사용 가이드 (Usage Guide)

### 0. 대화형 콘솔 UI 모드 (Interactive TUI) - 💡 추천!
별도의 인자나 서브커맨드 없이 `llm-dev`만 단독 실행하면, **방향키(↑/↓)로 메뉴를 선택하고 입력을 진행하는 대화형 TUI 콘솔**이 실행됩니다.

```bash
llm-dev
```

```text
╭────────────────── Interactive Mode ───────────────────╮
│ 🤖 LLM Development CLI & Governance Hub (v0.1.0)      │
│ Day 0 사전 인프라 스캐폴딩 • 룰셋 정적 진단 • 대시보드 │
│ 방향키(↑/↓)로 메뉴를 이동하고 [Enter] 키로 선택하세요. │
╰───────────────────────────────────────────────────────╯

? 실행할 작업을 선택하세요: (Use arrow keys)
 ❯ 🚀  1. 신규 LLM 프로젝트 초기화 (Init)
   🔍  2. 거버넌스 & 보안 진단 (Doctor)
   📊  3. 라이프사이클 체크리스트 진척도 (Status)
   🌐  4. 로컬 실시간 웹 대시보드 실행 (View)
   ❌  0. 종료 (Exit)
```

---

### 1. 신규 LLM 프로젝트 초기화 (`init`)
프로젝트 성격(표준 풀스택, 경량 PoC, 외부 원격 Elasticsearch 연동 등)에 따라 유연하게 초기화할 수 있습니다.

```bash
# 🌟 [기본] 표준 전체 스캐폴딩 (FastAPI + 전체 로컬 EFK + Vector DB + 룰셋)
llm-dev init --name my-rag-service --dir ./my-rag-service --stack fastapi

# 🪶 [경량 PoC] 가볍게 빠른 시작 (무거운 Docker/ELK 제외, 핵심 가이드+룰셋+코드만 생성)
llm-dev init --name quick-poc --dir ./quick-poc --preset minimal

# 🌐 [원격 ES 연동] 기존 사내 Elasticsearch 클러스터 연동 (로컬 ES 컨테이너 제외)
llm-dev init --name enterprise-ai --dir ./enterprise-ai --docker-mode remote_es --es-host 192.168.0.28 --es-port 9200

# ⚡ [Vector DB 전용] Qdrant & Redis만 구동 (ELK 제외)
llm-dev init --name vector-service --dir ./vector-service --docker-mode vector_only

# ☕ Spring Boot 3 백엔드 스택으로 초기화
llm-dev init --name spring-ai --dir ./spring-ai --stack spring
```


### 2. 프로젝트 거버넌스 및 보안 진단 (`doctor`)
프로젝트 폴더 내에서 표준 준수 여부를 검사합니다.
```bash
cd my-rag-service
llm-dev doctor
```

### 3. 마크다운 체크리스트 진행률 확인 (`status`)
```bash
llm-dev status
```

### 4. 로컬 웹 대시보드 실행 (`view`)
FastAPI 기반의 거버넌스 & 진단 실시간 웹 뷰어를 실행합니다.

```bash
# 기본 실행 (로컬 루프백 127.0.0.1:8899)
llm-dev view

# 포트 지정 및 외부/원격 접속 허용 (--host 0.0.0.0)
llm-dev view --port 8082 --host 0.0.0.0

# 특정 프로젝트 디렉토리를 지정하여 실행
llm-dev view --dir ./my-rag-service --port 8082 --host 0.0.0.0
```

> 💡 **외부/내부망 접속 팁**:
> 기본값은 `127.0.0.1`로 바인딩되므로, 다른 PC나 외부 브라우저에서 접속하려면 반드시 `--host 0.0.0.0` 옵션을 지정해야 합니다.
> 방화벽(UFW 등)에서 해당 포트가 열려 있는지 확인하세요. (`sudo ufw allow 8082/tcp`)


---

## 📂 프로젝트 구조

```text
llm-dev-cli/
├── pyproject.toml
├── setup.py
├── requirements.txt
├── README.md
├── llm_dev/
│   ├── main.py              # CLI 엔트리포인트
│   ├── config.py            # 경로 및 상수
│   ├── commands/            # CLI 서브커맨드 (init, doctor, status, view)
│   ├── checkers/            # 정적 분석 및 룰 검사기 모음
│   ├── web/                 # FastAPI + HTML/CSS/JS 대시보드
│   └── templates/           # 내장 표준 문서, 룰셋, Docker, 보일러플레이트
```

---

## 🔗 GitHub 원격 저장소 연동 가이드

GitHub에서 새 저장소(`DevDooly/llm-dev-cli`)를 생성한 후 아래 명령어로 원격 저장소에 연결하고 푸시할 수 있습니다.

```bash
cd /home/rudy/dev/repository/devdooly/llm-dev-cli

# 원격 저장소 등록 (SSH 기준)
git remote add origin git@github.com:DevDooly/llm-dev-cli.git

# 메인 브랜치 푸시
git branch -M main
git push -u origin main
```
