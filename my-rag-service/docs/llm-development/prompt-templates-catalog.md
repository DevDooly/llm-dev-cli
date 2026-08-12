# 📜 프롬프트 템플릿 & Few-shot 카탈로그 (Prompt Engineering Catalog)

> **"환각을 억제하고 예측 가능한 고품질 출력을 보장하는 실전 System/User 프롬프트 및 Few-shot 템플릿 모음"**

---

## 1. 프롬프트 구성 5대 핵심 원칙 (RTC-CF Framework)

모든 System Prompt는 아래 5대 요소를 명확히 분리하여 선언해야 합니다.

| 요소 | 영문 명칭 | 세부 지침 | 예시 |
| :---: | :--- | :--- | :--- |
| **R** | **Role (역할)** | 모델의 페르소나 및 전문 도메인 정의 | "너는 10년 차 수석 백엔드 아키텍트이다." |
| **T** | **Task (작업)** | 달성해야 하는 구체적인 단일 목표 명시 | "사용자 질문에 대해 사내 규정 문서에 기반하여 답변하라." |
| **C** | **Context (맥락)** | 도메인 배경, 검색된 문서(Context), 사전 정보 주입 | "아래는 사내 복지 규정 및 출장비 지급 지침 청크이다." |
| **C** | **Constraints (제약)** | 하지 말아야 할 행동, 금지 사항, Fallback 규칙 | "제공된 문서에 근거가 없으면 모른다고 답변하고 절대 추측하지 마라." |
| **F** | **Format (형식)** | 출력할 데이터 구조(JSON/Markdown/Schema) 정의 | "반드시 지정된 JSON 스키마 형식으로만 응답하라." |

---

## 2. RAG 표준 System Prompt 템플릿

```markdown
# Role & Purpose
당신은 사내 지식베이스 기반의 전문 AI 어시스턴트입니다. 사용자 질문에 대해 아래 제공된 [Context]를 바탕으로 객관적이고 정확한 답변을 작성하세요.

# Strict Constraints
1. 반드시 [Context]에 명시된 사실만을 기반으로 답변하세요.
2. [Context]에서 답변의 근거를 찾을 수 없는 경우, "제공된 사내 문서에서 관련 정보를 찾을 수 없습니다."라고 정직하게 답변하세요.
3. 절대로 존재하지 않는 사실이나 외부 지식을 추측하여 지어내지 마세요 (No Hallucination).
4. 답변 말미에 참고한 문서의 [출처: 문서명 / 페이지]를 반드시 표기하세요.

# Context
<<<DOCUMENT_CHUNKS>>>
{context}
<<<END_OF_DOCUMENT_CHUNKS>>>

# User Query
<<<USER_QUERY>>>
{query}
<<<END_OF_USER_QUERY>>>
```

---

## 3. 구조화 JSON 추출 (Pydantic Output) 프롬프트

```markdown
# Task: 영수증/인보이스 데이터 구조화 추출
제공된 문서 텍스트에서 결제 정보 및 품목 목록을 추출하여 아래 JSON 스키마 규격으로만 응답하세요. 마크다운 백틱(```json) 없이 순수 JSON 문자열만 출력해야 합니다.

# JSON Schema:
{
  "vendor_name": "상호명 (문자열)",
  "biz_number": "사업자등록번호 (문자열, 마스킹 처리됨)",
  "trans_date": "거래일자 (YYYY-MM-DD)",
  "items": [
    { "name": "품목명", "quantity": 1, "unit_price": 10000, "total_price": 10000 }
  ],
  "total_amount": 10000,
  "tax_amount": 1000
}
```

---

## 4. Few-shot 분류 프롬프트 템플릿

```markdown
# Task: 고객 VoC 상담 로그 감성 및 카테고리 분류

# Examples:
Input: "로그인이 계속 튕기고 결제 화면에서 앱이 꺼집니다. 환불해주세요!"
Output: {"sentiment": "NEGATIVE", "category": "BUG_REPORT", "urgency": "HIGH"}

Input: "다크모드 지원해주셔서 눈이 훨씬 편하네요. 감사합니다."
Output: {"sentiment": "POSITIVE", "category": "COMPLIMENT", "urgency": "LOW"}

Input: "법인 카드 영수증 출력은 어디서 하나요?"
Output: {"sentiment": "NEUTRAL", "category": "INQUIRY", "urgency": "MEDIUM"}

# Actual Input:
Input: "{user_feedback}"
Output:
```

---

## 📋 프롬프트 엔지니어링 체크리스트

- [ ] **RTC-CF 5대 요소 검증:** 모든 System Prompt에 Role, Task, Context, Constraints, Format 명시 완료
- [ ] **구문 분리(Delimiter) 적용:** Prompt Injection 방어를 위해 `<<<TAG>>>` 구문 격리자 적용
- [ ] **환각 방지 제약 명시:** "근거가 없으면 모른다고 답하라"는 Fallback 룰 명시
- [ ] **Pydantic 스키마 연동:** 구조화 출력 프롬프트에 JSON 필드 타입 및 검증 로직 연결
