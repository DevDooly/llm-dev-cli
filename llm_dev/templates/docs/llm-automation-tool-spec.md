# 🛠️ LLM 개발 표준 자동화 도구 기획 및 아키텍처 설계서 (LLM Scaffolder & Doctor Spec)

> **"LLM 프로젝트 초기 스캐폴딩(Init)부터 개발 진행 중 4대 사전 인프라 및 표준 규칙 준수 여부를 지속 점검(Doctor)하는 거버넌스 자동화 도구"**

---

## 1. 기획 배경 및 필요성 (Why Needed?)

`llm-development`에 정의된 4대 선행 인프라(ELF 로깅, Docker 샌드박스, 인증/토큰 제어, 보안 가드레일)와 코딩 룰셋은 프로젝트 품질과 안정성을 위해 필수적입니다.  
그러나 새로운 LLM 프로젝트를 시작할 때마다:
1. 문서를 일일이 복사하고 디렉토리 구조를 수동으로 만드는 번거로움이 발생합니다.
2. 개발이 진행되면서 규칙(구조화 JSON 로깅, 시크릿 격리, 샌드박스 격리 등)이 실제로 잘 지켜지고 있는지 자동으로 검증하기 어렵습니다.

따라서 **프로젝트를 표준 스펙으로 초기화(Init)하고, 지속적으로 규칙 준수 여부를 진단(Doctor)하는 자동화 도구**가 필요합니다.

---

## 2. 도구의 3대 핵심 기능 (Core Capabilities)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                   LLM 개발 표준 자동화 도구 (가칭: llm-dev)                   │
├──────────────────────────┬──────────────────────────┬───────────────────────┤
│ 🚀 1. Init (스캐폴딩)    │ 🔍 2. Doctor (룰 검증)   │ 📊 3. Tracker (진척도)│
├──────────────────────────┼──────────────────────────┼───────────────────────┤
│ • 표준 폴더 및 문서 복사 │ • 4대 인프라 구축 여부   │ • Day 0 -> Day 5      │
│ • Docker/ELF 로깅 템플릿 │ • 시크릿 하드코딩 검사   │   라이프사이클 단계별 │
│ • AI 룰셋(.cursorrules 등)│ • PII/구조화 로깅 정적분석│   체크리스트 상태 추적 │
│ • 백엔드(FastAPI/Spring) │ • API 응답 포맷 준수 검사│ • 종합 점수(Score) 산출│
└──────────────────────────┴──────────────────────────┴───────────────────────┘
```

---

## 3. 구현 형태별 비교 및 추천 아키텍처

| 구현 형태 | 개발 난이도 | 개발자 사용 편의성 | 확장성 (CI/CD, Git Hook) | 총평 및 추천 여부 |
| :--- | :---: | :---: | :---: | :--- |
| **단순 Shell/파이썬 스크립트** (`init.sh`, `check.py`) | 낮음 | 보통 | 보통 | 빠르고 단순하지만, 인터랙티브 옵션(스택 선택 등)이나 유지보수에 한계가 있음 |
| **CLI 도구 (Python / Node.js CLI)** | 보통 | **최상** (터미널에서 즉시 사용) | **최상** (Git Pre-commit, GitHub Actions 연동 가능) | 🏆 **가장 추천 (개발자 워크플로우에 최적)** |
| **웹 전용 애플리케이션 (Next.js/React 대시보드)** | 높음 | 보통 (브라우저 열어야 함) | 낮음 | 시각적으로 보기는 좋으나, 프로젝트 init 시점에 매번 웹 서버를 띄워야 하는 오버헤드 |
| **하이브리드 (CLI + 경량 웹 대시보드 내장)** | 보통~약간 높음 | **최상** | **최상** | **CLI 중심으로 작동하되, 필요 시 `llm-dev view`로 웹 브라우저에서 체크리스트 확인** |

> 💡 **최종 추천:** **Python 기반 하이브리드 CLI 도구 (`llm-dev`)**  
> 터미널 친화적이며 `pip` 또는 단일 실행 스크립트로 동작하고, Git Pre-commit 훅 및 CI/CD 파이프라인에 즉시 통합 가능합니다.

---

## 4. `llm-dev` CLI 상세 명령어 및 동작 시나리오

### 4.1 프로젝트 초기화 (`llm-dev init`)
새로운 프로젝트 디렉토리에서 표준 지식베이스와 템플릿을 자동으로 스캐폴딩합니다.

```bash
$ llm-dev init --name customer-rag-bot --stack fastapi --logging efk

[✔] 표준 지식베이스 문서 주입 완료 (docs/llm-development/)
[✔] AI 코딩 어시스턴트 룰셋 생성 완료 (.cursorrules, .agents/rules)
[✔] Docker 및 EFK 로깅 인프라 생성 완료 (docker-compose.llm-dev.yml)
[✔] 보안 및 PII 마스킹 모듈 생성 완료 (src/core/security/pii.py)
[✔] 표준 JSON 에러 핸들러 생성 완료 (src/core/exceptions.py)

🚀 프로젝트 초기화가 완료되었습니다! Day 0 기반 구축 체크리스트를 확인하세요.
```

---

### 4.2 프로젝트 규칙 및 보안 검증 (`llm-dev doctor`)
개발 진행 중 프로젝트의 소스코드와 환경설정을 정적 분석하여 표준 규칙을 검증합니다.

```bash
$ llm-dev doctor

🔍 LLM Development Compliance Check
----------------------------------------------------------------------
[✔] 1. Secret Governance: .env 환경변수 분리 완료 (하드코딩된 API Key 없음)
[✔] 2. Logging Standard : Logback/structlog JSON 구조화 로깅 적용됨
[✖] 3. Sandbox Isolation: Agent 코드 실행 격리 컨테이너 미구현 (경고)
     ↳ 권장 조치: llm-docker-and-sandbox.md의 SafeCodeSandbox 적용
[✔] 4. PII Masking      : 프롬프트 전송 전 PII 마스커 필터 호출 확인됨
[✖] 5. Rate Limiting    : Redis Token Bucket Rate Limiter 미적용 (경고)
     ↳ 권장 조치: llm-auth-and-security.md의 LlmRateLimiter 적용
[✔] 6. Response Format  : 표준 API 응답 포맷 ({success, data, error}) 준수
----------------------------------------------------------------------
📊 표준 준수율: 83% (5/6 항목 통과) | 최종 판정: PASS WITH WARNINGS
```

---

### 4.3 진척도 및 체크리스트 확인 (`llm-dev status`)
프로젝트 마크다운 문서 내의 체크박스(`- [x]`, `- [ ]`)를 실시간 파싱하여 6단계 라이프사이클별 진척도를 집계합니다.

```bash
$ llm-dev status

📌 [customer-rag-bot] LLM Development Lifecycle Progress
----------------------------------------------------------------------
Phase 0. Day 0 기반 인프라 구축 : [████████████████████] 100% (8/8) ✅
Phase 1. 문제 정의 & 기술 선택  : [████████████████████] 100% (3/3) ✅
Phase 2. 프롬프트 & 컨텍스트    : [██████████████░░░░░░]  70% (7/10) 🚧
Phase 3. AI 협업 코딩 & 구현    : [██████████░░░░░░░░░░]  50% (4/8)  🚧
Phase 4. 평가, 보안 & 가드레일  : [████░░░░░░░░░░░░░░░░]  20% (1/5)  📝
Phase 5. LLMOps & 관제         : [░░░░░░░░░░░░░░░░░░░░]   0% (0/4)  📝
----------------------------------------------------------------------
총 진척도: 57.8% (23/38 체크리스트 완료)
```

---

### 4.4 로컬 웹 뷰어 대시보드 (`llm-dev view` 또는 `dashboard`)
시각적 UI가 필요한 경우, 경량 로컬 웹 서버를 실행하여 웹 브라우저에서 대시보드를 확인합니다.

```bash
$ llm-dev view --port 8899
🚀 Local Dashboard running at http://localhost:8899 (Press Ctrl+C to stop)
```

---

## 5. 도구 디렉토리 구조 설계 (Project Layout)

`ai-playground/llm-development` 내에 다음과 같은 모듈형 패키지 구조로 구축할 수 있습니다.

```text
llm-development/
├── README.md                      # 지식베이스 마스터 허브
├── llm-foundation-setup.md        # Day 0 사전 필수 인프라 가이드
├── llm-logging-and-observability.md
├── llm-docker-and-sandbox.md
├── llm-auth-and-security.md
├── llm-guidelines.md
├── llm-roadmap.md
├── llm-automation-tool-spec.md    # [본 문서] 자동화 도구 기획 및 설계서
│
├── cli/                           # llm-dev CLI 구현 디렉토리
│   ├── pyproject.toml             # CLI 패키지 설정
│   ├── llm_dev/
│   │   ├── __init__.py
│   │   ├── main.py                # Typer / Click 기반 CLI 진입점
│   │   ├── commands/
│   │   │   ├── init.py            # init 명령어 (템플릿 복사 및 치환)
│   │   │   ├── doctor.py          # doctor 명령어 (정적 분석 및 룰 검증)
│   │   │   ├── status.py          # status 명령어 (체크리스트 파싱 및 집계)
│   │   │   └── view.py            # 로컬 웹 대시보드 서빙 (FastAPI/HTML)
│   │   ├── checkers/              # 정적 분석기 모음
│   │   │   ├── secret_checker.py  # API 키 하드코딩 탐지
│   │   │   ├── log_checker.py     # 구조화 로깅 적용 여부
│   │   │   └── schema_checker.py  # API 응답 포맷 준수 검사
│   │   └── templates/             # 스캐폴딩 대상 템플릿 모음
│   │       ├── docs/              # 표준 md 파일들
│   │       ├── rules/             # .cursorrules, .agents/rules
│   │       ├── docker/            # docker-compose.llm-dev.yml
│   │       └── boilerplates/      # fastapi / spring-boot 기본 코드
```

---

## 6. 단계별 개발 로드맵 (Execution Plan)

- **Phase 1 (MVP 스크립트):**
  - `llm_dev/commands/init.py`: 템플릿 복사 및 프로젝트명 치환 기능 구현
  - `llm_dev/commands/doctor.py`: 핵심 3대 검사(시크릿 하드코딩, docker-compose 존재 여부, 표준 JSON 응답 구조) 정적 검사기 구현
- **Phase 2 (체크리스트 파서 & CLI 패키징):**
  - 마크다운 체크리스트 자동 파싱 및 `llm-dev status` 시각화 CLI 배포
- **Phase 3 (Git Hook & 로컬 웹 뷰어):**
  - Git `pre-commit` 훅 연동 (`git commit` 시 `llm-dev doctor` 자동 실행)
  - `llm-dev view` 경량 웹 대시보드 뷰어 추가

---

*본 문서는 LLM 프로젝트 템플릿화 및 거버넌스 자동화 도구 개발의 기준 명세서로 사용됩니다.*
