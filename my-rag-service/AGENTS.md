# AI Agent & Assistant Guidelines

본 프로젝트는 LLM 기반 애플리케이션 표준 거버넌스 가이드라인(`docs/llm-development/`)을 준수하여 개발됩니다.

---

## 🚨 필수 준수 4대 원칙 (Core Principles)

| 구분 | 영역 | 필수 준수 항목 | 세부 지침 |
| :---: | :--- | :--- | :--- |
| **01** | 🔒 **보안** | API 키 / 시크릿 하드코딩 금지 | 환경변수(`.env`) 및 Secret Manager를 통해서만 주입 |
| **02** | 🐳 **격리** | Docker 샌드박스 실행 | Agent 생성 코드는 네트워크 차단 컨테이너에서 격리 실행 |
| **03** | 📊 **로깅** | 구조화 JSON 로깅 (MDC) | TraceID, 토큰 소모량, 지연시간(Latency), 비용 필수 기록 |
| **04** | 🛡️ **인가** | Document-level RBAC | RAG 검색 시 사용자 권한 필터링 및 PII 자동 마스킹 적용 |

---

## 📋 AI 코딩 표준 지침 요약 (Coding Standards)

| 항목 | 표준 사양 | 금지 사항 |
| :--- | :--- | :--- |
| **Backend** | Python 3.11+ / FastAPI, Java 21 / Spring Boot 3.x | 레거시 라이브러리 및 미검증 외부 패키지 임의 추가 |
| **API Schema** | `{ "success": true, "data": ..., "error": null }` | 비표준/비정형 텍스트 응답 반환 |
| **Logging** | Logback JSON Encoder / structlog (JSON 포맷) | `print()`, `System.out.println()` 직접 출력 |
| **PII 보호** | 주민번호, 이메일, 전화번호 자동 마스킹 | 민감 개인정보 원문 프롬프트/로그 주입 |
| **Exception** | Global Exception Handler를 통한 일관된 에러 응답 | 에러 스택트레이스 클라이언트 노출 |

---

## 📂 참고 문서 바로가기
- 🏗️ **Day 0 인프라 가이드:** `docs/llm-development/llm-foundation-setup.md`
- 📊 **로깅 & 옵저버빌리티:** `docs/llm-development/llm-logging-and-observability.md`
- 🐳 **도커 & 샌드박스:** `docs/llm-development/llm-docker-and-sandbox.md`
- 🛡️ **보안 & 인증 가이드:** `docs/llm-development/llm-auth-and-security.md`
- 📘 **개발 가이드 & 룰셋:** `docs/llm-development/llm-guidelines.md`
