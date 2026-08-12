# LLM 개발 지식베이스 구축 로드맵 (LLM Development Knowledge Base Roadmap)

이 문서는 **LLM(대형 언어 모델) 기반 프로젝트 수행에 필요한 지식 체계와 상세 문서 구축 로드맵**을 관리하는 마스터 파일입니다.  
본 로드맵에 따라 `llm-development` 폴더 하위에 각 주제별 문서들을 단계적으로 작성 및 고도화하고, 프로젝트 진행 과정에서 얻은 인사이트와 베스트 프랙티스를 지속적으로 추가하여 살을 붙여 나갑니다.

---

## 1. 지식베이스 관리 체계 및 운용 가이드

### 1.1 기본 원칙
- **선행 인프라 최우선 (Day 0 Foundation First):** 비즈니스 개발 및 프롬프트 작성 전, 로깅(ELF), Docker/Sandbox, 인증, 보안 가드레일을 1순위로 구축합니다.
- **단계별 구축 & 상호 연계:** 로드맵 문서 간의 참조 링크를 체계화하고 일관된 표준 JSON 규격 및 코딩 룰을 유지합니다.
- **실전 코드 중심:** 이론적 설명에 그치지 않고, Spring Boot/Java 21, Python/FastAPI, Docker, Elasticsearch/Fluent Bit 등 프로젝트에 직접 적용 가능한 설정과 예시 코드를 포함합니다.

---

## 2. 문서 구축 마스터 로드맵 (Master Document List)

| 번호 | 문서명 (파일명) | 주제 및 핵심 목적 | 진행 상태 |
| :---: | :--- | :--- | :---: |
| **00** | [`llm-foundation-setup.md`](./llm-foundation-setup.md) | **[Day 0]** LLM 개발 전 필수 사전 구축 4대 인프라 마스터 가이드 & 체크리스트 | ✅ 완료 |
| **01** | [`llm-logging-and-observability.md`](./llm-logging-and-observability.md) | **[Day 0]** ELF/EFK 중앙 로그 수집, 구조화 JSON 스키마, Kibana 대시보드 & 실시간 알림 | ✅ 완료 |
| **02** | [`llm-docker-and-sandbox.md`](./llm-docker-and-sandbox.md) | **[Day 0]** Docker Compose 로컬 통합 스택 및 Agent 코드 실행용 격리 Sandbox 구축 | ✅ 완료 |
| **03** | [`llm-auth-and-security.md`](./llm-auth-and-security.md) | **[Day 0]** JWT/API Key, Redis Token Bucket Rate Limiter, RAG RBAC & PII 마스킹 | ✅ 완료 |
| **04** | [`llm-guidelines.md`](./llm-guidelines.md) | LLM 프로젝트 전체 라이프사이클(Phase 0~5) 및 AI 코딩 어시스턴트 룰셋 | ✅ 완료 |
| **05** | [`llm-architecture-design.md`](./llm-architecture-design.md) | RAG 파이프라인, Vector DB(Qdrant/pgvector), 청킹, 하이브리드 검색 설계 | ✅ 완료 |
| **06** | [`prompt-templates-catalog.md`](./prompt-templates-catalog.md) | RTC-CF 원칙, 실전 System/User 프롬프트 템플릿 및 Few-shot 카탈로그 | ✅ 완료 |
| **07** | [`llm-eval-and-benchmarks.md`](./llm-eval-and-benchmarks.md) | RAGAS (Faithfulness/Relevance) 및 LLM-as-a-Judge 정량 평가 체계 | ✅ 완료 |
| **08** | `llm-agent-and-tools.md` | Function Calling / Tool-Use, ReAct 및 다단계 자율 에이전트 설계 | 📝 예정 |
| **09** | [`llm-automation-tool-spec.md`](./llm-automation-tool-spec.md) | LLM 프로젝트 초기화(Init) 및 룰 준수 지속 검증(Doctor) 자동화 CLI 설계서 | ✅ 완료 |

---

## 3. 각 문서별 상세 포함 내용 명세 (Detailed Specifications)

### 00. `llm-foundation-setup.md` (사전 필수 기반 환경 구축 가이드 - Day 0 Foundation)
- **주요 내용:**
  - LLM 개발 착수 전 선행 구축 4대 축(Docker, 보안, 인증/제어, ELF 로깅) 아키텍처 다이어그램
  - Day 0 준비 워크플로우 및 통합 준비 완료(Readiness) 체크리스트

---

### 01. `llm-logging-and-observability.md` (ELF/EFK 중앙 로그 모니터링 & LLMOps 가이드)
- **주요 내용:**
  - LLM 표준 구조화 JSON 로그 스키마 (TraceID, Tokens, Latency, Cost, Model)
  - Fluent Bit + Elasticsearch + Kibana 연동 설정 (`fluent-bit.conf`, `docker-compose.logging.yml`)
  - Spring Boot 3 Logback & FastAPI structlog 연동 코드
  - Kibana 대시보드 필수 지표 (토큰 추이, 지연시간 P99, 비용, 에러율) 및 텔레그램/슬랙 알림 템플릿

---

### 02. `llm-docker-and-sandbox.md` (Docker 컨테이너화 & Agent Sandbox 격리 가이드)
- **주요 내용:**
  - Multi-stage & Non-root 기반 FastAPI / Spring Boot 3 프로덕션 Dockerfile
  - `docker-compose.llm-dev.yml` (백엔드, Vector DB, Ollama, EFK 통합 기동)
  - LLM Agent 코드 실행을 위한 네트워크 차단(`network_mode: none`) & 자원 제한 일회성 Docker Sandbox 구현체

---

### 03. `llm-auth-and-security.md` (인증/인가, 토큰 제어 & 보안 가드레일 가이드)
- **주요 내용:**
  - Redis Token Bucket 알고리즘 기반 RPM/TPM 및 월간 토큰 예산 제어
  - RAG 문서 수준 접근 제어 (Document-level RBAC 메타데이터 필터링)
  - PII 실시간 자동 마스킹 파이프라인 (주민번호, 이메일, 전화번호, 카드번호)
  - Prompt Injection 방어를 위한 Delimiter 격리 기법 및 OWASP Top 10 for LLM 대응

---

### 04. `llm-guidelines.md` (LLM 프로젝트 라이프사이클 & AI 룰셋)
- **주요 내용:**
  - Phase 0(기반구축) ~ Phase 5(운영관제) 전체 라이프사이클
  - AI 어시스턴트(Gemini, Cursor 등) 코딩 규칙, API 응답 포맷 및 엄격한 금지사항

---

### 05. `llm-architecture-design.md` (RAG & 아키텍처 설계서 - 예정)
- **주요 내용:**
  - RAG 파이프라인 구성 (Loader -> Splitter -> Vector DB -> Hybrid Retriever -> Reranker)
  - 임베딩 모델 및 Vector DB(Qdrant, PGvector, Chroma) 비교 선정 가이드

---

### 06. `prompt-templates-catalog.md` (프롬프트 템플릿 카탈로그 - 예정)
- **주요 내용:**
  - 역할별 System Prompt (백엔드 아키텍트, 데이터 분석가, 보안 감사관 등)
  - 업무별 User Prompt (코드 리뷰, SQL 생성, 요약, 데이터 구조화 JSON 추출 등)

---

### 07. `llm-eval-and-benchmarks.md` (LLM 평가 및 검증 가이드 - 예정)
- **주요 내용:**
  - RAGAS (Faithfulness, Answer Relevance, Context Precision) 자동 측정
  - LLM-as-a-Judge를 활용한 회귀 테스트 파이프라인

---

### 08. `llm-agent-and-tools.md` (LLM Agent & Function Calling 개발 지침 - 예정)
- **주요 내용:**
  - OpenAPI Schema 기반 Tool 선언 기법 및 Function Calling 핸들러
  - Infinite Loop 방지 및 Maximum Step 제어

---

## 4. 변경 및 확장 이력 (Change Log)

- **2.1.0 (2026-08-10):** Day 0 사전 필수 구축 4대 인프라(00 Foundation, 01 ELF 로깅, 02 Docker & Sandbox, 03 Auth & Security) 문서 작성 완료 및 마스터 로드맵 개편.
- **2.0.0 (2026-07-26):** LLM 개발 지식베이스 구축 로드맵 (`llm-roadmap.md`) 최초 작성.
