# AI Agent & Assistant Guidelines

본 프로젝트는 LLM 기반 애플리케이션 표준 거버넌스 가이드라인(`docs/llm-development/`)을 준수하여 개발됩니다.

## 🚨 필수 준수 4대 원칙
1. **[보안]** API 키 및 민감 정보를 소스코드에 하드코딩하지 않습니다.
2. **[격리]** Agent 코드 실행 시 반드시 네트워크가 차단된 Docker 샌드박스를 사용합니다.
3. **[로깅]** 모든 LLM 트랜잭션은 TraceID와 토큰 사용량을 포함하여 JSON 구조화 로그로 기록합니다.
4. **[인가]** RAG 검색 시 사용자 권한에 따른 Document-level RBAC 필터링을 필수 적용합니다.
