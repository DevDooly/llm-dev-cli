# LLM 기반 프로젝트 개발 가이드라인 & AI 룰셋 (LLM Development Guidelines)

이 문서는 **LLM(대형 언어 모델)을 활용한 소프트웨어 개발 프로젝트**의 전반적인 프로세스, 프롬프트/컨텍스트 엔지니어링 베스트 프랙티스, 보안 및 품질 관리 지침, 그리고 AI 코딩 어시스턴트(Gemini, Cursor, Copilot 등)에게 적용할 프로젝트 코딩 룰셋을 정의합니다.

---

## 1. 개요 (Overview)

### 1.1 본 문서의 목적
- **LLM 프로젝트 성공률 제고:** 단순 코드 생성을 넘어 아키텍처 설계, RAG/Agent 구축, 프롬프트 엔지니어링, 평가/모니터링 체계를 표준화합니다.
- **AI Pair Programming 최적화:** AI 어시스턴트가 프로젝트 맥락을 정확히 이해하고 모던 스펙 및 표준 아키텍처에 맞춰 일관성 있는 코드를 작성하도록 강제합니다.
- **보안 및 환각(Hallucination) 예방:** 하드코딩, 보안 정보 유출, 존재하지 않는 API 호출 등의 위험을 사전에 차단합니다.

---

## 2. LLM 프로젝트 추진 라이프사이클 (LLM Project Lifecycle)

```
[Phase 0: Day 0 기반 구축] ➔ [Phase 1: 문제 정의 & 기술 선택] ➔ [Phase 2: 프롬프트 & 컨텍스트] ➔ [Phase 3: AI 협업 구현] ➔ [Phase 4: 평가 & 보안 가드] ➔ [Phase 5: LLMOps 관제]
```

### Phase 0: 사전 필수 기반 환경 구축 (Day 0 Foundation - Pre-requisite)
> **🚨 CRITICAL:** 실제 LLM API 연동 및 비즈니스 코드 개발 전, 아래 4대 인프라를 최우선으로 선행 구축해야 합니다.

1. **Docker 컨테이너화 & 샌드박스 격리 ([`llm-docker-and-sandbox.md`](./llm-docker-and-sandbox.md)):**
   - 백엔드, Vector DB, 로컬 모델(Ollama)을 `docker-compose`로 단일 기동하는 환경 구성.
   - Agent 코드 실행을 위한 네트워크 차단(`network_mode: none`) 및 일회성 Docker Sandbox 격리망 구축.
2. **보안 & 시크릿 거버넌스 ([`llm-auth-and-security.md`](./llm-auth-and-security.md)):**
   - API Key/비밀번호 하드코딩 금지 및 Secret Manager 주입 체계.
   - PII(주민번호, 이메일, 전화번호) 실시간 자동 마스킹 및 Prompt Injection 1차 방어선 구축.
3. **인증, 인가 & 트래픽/비용 제어 ([`llm-auth-and-security.md`](./llm-auth-and-security.md)):**
   - JWT / API Key 인증 및 Redis 기반 Token Bucket Rate Limiter (RPM & TPM & 월간 예산 제어).
   - RAG 문서 수준 접근 제어 (Document-level RBAC 메타데이터 필터링).
4. **ELF/EFK 중앙 집중식 로그 모니터링 ([`llm-logging-and-observability.md`](./llm-logging-and-observability.md)):**
   - TraceID, 사용자ID, 프롬프트, 응답, 토큰 사용량, 지연시간, 추정 비용을 포함한 구조화 JSON 로깅.
   - Fluent Bit ➔ Elasticsearch ➔ Kibana 대시보드 및 이상 징후 알림(Telegram/Slack) 가동.

---

### Phase 1: 문제 정의 및 기술 아키텍처 선택 (Problem & Architecture Selection)
LLM 프로젝트 시작 시 적합한 기술 방식을 선택해야 비용과 복잡도를 크게 줄일 수 있습니다.

| 기술 방식 | 적용 적합 사례 | 장점 | 단점/고려사항 |
| :--- | :--- | :--- | :--- |
| **Prompt Engineering** | 일반적인 문맥 이해, 텍스트 요약, 코드 생성 | 구현이 가장 빠르고 비용이 저렴함 | 모델 지식 한계, 도메인 특화 지식 부족 |
| **RAG (Retrieval-Augmented Generation)** | 최신 문서/사내 데이터 기반 답변, 검증 가능한 출처 필요 시 | 최신성 유지 가능, 환각 감소, 데이터 업데이트 쉬움 | Chunking/Embedding/Search 최적화 필요 |
| **Fine-Tuning** | 특정 스타일/태그/출력 형식 고정, 소형 모델(SLM) 최적화 | 추론 속도 개선, 프롬프트 길이 줄임 | 데이터셋 구축 비용 높음, 최신 지식 업데이트 어려움 |
| **LLM Agent & Tool-Use** | 복잡한 다단계 의사결정, 외부 API 연동 및 자동화 | 자율적 문제 해결 및 실시간 외부 시스템 작동 | 환각 시 잘못된 액션 수행 위험, 루프/비용 제어 필수 |

---

### Phase 2: 프롬프트 & 컨텍스트 엔지니어링 (Prompt & Context Engineering)
1. **System Prompt 5대 요소 명시:**
   - **Role (역할):** "너는 10년 차 수석 백엔드 아키텍트이다."
   - **Task (작업):** "Spring Boot 기반 RESTful API를 설계하고 구현하라."
   - **Context (맥락):** "우리는 Java 21, Spring Boot 3.2, PostgreSQL을 사용 중이다."
   - **Constraints (제약):** "가상 스레드를 사용하고 Controller에는 비즈니스 로직을 넣지 마라."
   - **Output Format (출력 형식):** "JSON 형식 또는 지정된 코드 블록으로만 응답하라."
2. **Context Window 관리:**
   - 불필요한 전체 코드 전달을 지양하고, **관련 인터페이스, DTO, 도메인 모델 중심**으로 조각화(Chunking)하여 주입합니다.
   - Long Context 소모를 줄이기 위해 중요 가이드라인은 문서 상단/하단에 배치합니다.

---

### Phase 3: AI Pair Programming 워크플로우 (AI 코딩 어시스턴트 활용)
1. **역질문(Back-questioning) 유도:**
   - 불확실한 요구사항이나 모호한 설계에 대해 LLM이 임의로 추측하지 않고 **개발자에게 되물어보도록** 룰을 부여합니다.
2. **Small Step Iteration (작은 단위 개발):**
   - 한 번에 대규모 클래스나 여러 파일 생성을 요구하지 않고, `인터페이스 -> DTO -> Service -> Controller -> Unit Test` 순서로 단계를 분할하여 검증합니다.
3. **Diff 검증 필수:**
   - AI가 제시한 코드 변경점을 적용하기 전 기존 코드와의 혜택 및 의존성 파급 효과를 개발자가 직접 검토합니다.

---

### Phase 4: 평가, 보안 & 가드레일 (Evaluation, Security & Guardrails)
1. **환각 방지 및 코드 검증:**
   - 정적 분석 도구(SonarQube, SpotBugs 등) 및 단위 테스트 자동 실행을 연동합니다.
   - 존재하지 않는 라이브러리/메서드 호출(Hallucinated APIs) 여부를 컴파일 및 린트로 검증합니다.
2. **보안 지침 (OWASP Top 10 for LLM 대응):**
   - **Prompt Injection 방지:** 사용자 입력값을 프롬프트에 직접 결합하지 않고 구문 분리(Delimiter Escaping)를 적용합니다.
   - **Sensitive Info Leakage 방지:** API 키, DB 비밀번호, 개인정보(PII)가 프롬프트나 로그, 저장소에 노출되지 않도록 마스킹 처리합니다.
   - **Insecure Output Handling:** LLM이 생성한 코드가 SQL Injection, XSS, Command Injection 취약점을 포함하지 않는지 입력 검증/Sanitizing을 강제합니다.

---

### Phase 5: LLMOps 및 모니터링 (Observability & Ops)
- **Tracing & Logging:** LLM API 호출 Latency, Token consumption, Prompt/Completion 로그를 ELF(Elasticsearch+Fluent Bit+Kibana) 및 OpenInference로 추적합니다.
- **Cost Control:** 모델별 입력/출력 토큰 단가를 모니터링하고 파이프라인별 적절한 모델(예: 단순 분류는 Light 모델, 복잡 추론은 Heavy 모델)을 분기합니다.

---

## 3. AI 코딩 어시스턴트 프로젝트 규칙 (Project Coding Rules)

> 아래 룰셋은 AI 코딩 어시스턴트(Gemini, Cursor, Copilot 등)가 프로젝트 내에서 코드를 작성하거나 수정할 때 준수해야 하는 **시스템 프롬프트 지침**입니다.

### 3.1. Project Overview
- **프로젝트명:** [프로젝트 이름을 입력하세요]
- **목적:** [프로젝트의 핵심 목표 및 제공하는 서비스 요약]
- **대상 사용자:** [서비스의 주요 타겟층]

### 3.2. Tech Stack & Modern Coding Standards

사용하지 않는 기술이나 레거시 방식/오래된 라이브러리를 제안하지 마세요.

- **Backend (Java / Spring Boot & Python / FastAPI):**
  - **Modern Java:** Java 21의 신규 기능(Record, Pattern Matching, Switch Expressions, Sealed Class 등) 및 Virtual Threads를 적극 활용하세요.
  - **Architecture:** `Controller` -> `Service` -> `Repository` / `Domain` 계층형 아키텍처를 엄격히 준수하세요.
  - **Logging & Observability:** `System.out.println` 또는 `print()` 사용을 엄격히 금지합니다. 구조화된 JSON 로깅(Logback JSON Encoder / structlog)을 사용하고, LLM 호출 시 반드시 MDC(TraceID, Token Usage, Latency)를 기록하세요.
  - **Container & Sandbox:** 생성된 코드를 실행할 때는 반드시 네트워크가 차단된 Docker 샌드박스를 통하도록 작성하세요.

- **Frontend:**
  - **Component Pattern:** [Vue 3 Composition API / React Functional Components + Hooks]를 기본으로 작성하세요.
  - **TypeScript:** 엄격한 타입 정의(Interface/Type)를 준수하고 `any` 사용을 금지합니다.

### 3.3. Error Handling & Response Schema
모든 API 응답은 아래의 일관된 JSON 구조를 유지해야 합니다.

**성공 응답 예시 (HTTP 200/201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "Sample Data"
  },
  "error": null
}
```

**실패 응답 예시 (HTTP 4xx/5xx):**
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_INPUT_VALUE",
    "message": "입력값 검증에 실패하였습니다.",
    "details": [
      {
        "field": "email",
        "reason": "올바른 이메일 형식이 아닙니다."
      }
    ]
  }
}
```

### 3.4. Git Commit & PR Conventions
Conventional Commits 규격 준수: `feat:`, `fix:`, `refactor:`, `docs:`, `style:`, `test:`, `chore:`

### 3.5. Strict Prohibitions (절대 금지 사항)
1. **외부 라이브러리 임의 추가 금지:** 사전 제안 및 승인 없이 의존성(Dependency)을 추가하지 마세요.
2. **보안 민감 정보 하드코딩 금지:** API Key, DB 비밀번호, JWT Secret 등은 절대로 코드에 하드코딩하지 말고 환경변수 또는 Secret Manager를 사용하세요.
3. **무권한/비격리 코드 실행 금지:** LLM/Agent가 생성한 파이썬 스크립트나 쉘 명령을 호스트 머신에서 직접 실행하지 말고 Docker Sandbox에서 실행하세요.
4. **로깅 없는 LLM API 호출 금지:** 비용 및 장애 추적을 위해 토큰 사용량과 TraceID 기록 없는 LLM 호출 코드를 작성하지 마세요.
5. **추측에 기반한 코드 작성 금지:** 요구사항이 불명확할 경우 개발자에게 역질문(Questions)을 통해 확인하세요.

---

## 4. 지식베이스 구축 가이드 목록 (Knowledge Base Index)

- [x] **00. [`llm-foundation-setup.md`](./llm-foundation-setup.md) (Day 0 사전 필수 기반 환경 구축 가이드)**
- [x] **01. [`llm-logging-and-observability.md`](./llm-logging-and-observability.md) (ELF/EFK 중앙 로그 모니터링 & LLMOps 가이드)**
- [x] **02. [`llm-docker-and-sandbox.md`](./llm-docker-and-sandbox.md) (Docker 컨테이너화 & Agent Sandbox 가이드)**
- [x] **03. [`llm-auth-and-security.md`](./llm-auth-and-security.md) (인증/인가, Rate Limit, RBAC & 보안 가드레일)**
- [ ] **04. `llm-architecture-design.md` (RAG 파이프라인 & Vector DB 설계서)**
- [ ] **05. `prompt-templates-catalog.md` (프롬프트 템플릿 카탈로그)**
- [ ] **06. `llm-eval-and-benchmarks.md` (RAGAS & LLM-as-a-Judge 평가 가이드)**
- [ ] **07. `llm-agent-and-tools.md` (LLM Agent & Function Calling 개발 지침)**

---

*본 문서는 프로젝트 진행 상황 및 LLM 기술 발전에 따라 지속적으로 업데이트됩니다.*
