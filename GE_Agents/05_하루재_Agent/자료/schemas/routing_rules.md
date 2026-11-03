# 하루재 Agent 감수 분기(Routing) 및 예외 처리 규칙

이 문서는 **하루재 Orchestrator**가 **③ 감수 Agent (`Translation Reviewer`)**의 결과를 받아 다음 행동을 결정하는 상세 분기 규칙을 정의합니다.

---

## 1. 분기 의사결정 트리 (Decision Logic)

```text
IF review.status == "PASS"
    → ④ Korean Proofreader 호출 (최종 교정 단계 진행)

ELSE IF review.status == "REVISE" AND review.revision_count < 3
    ├─ Case A: 번역 정확성 오류 (Critical/Major: 오역, 누락, 추가, 수치 오류, 용어집 위반)
    │     → ① Translation Agent 재호출 (원문 + 현재 번역 + 감수 오류 + 수정 요청 전달)
    │     → ② Korean Editing Agent 재호출
    │     → ③ Translation Reviewer 재검토 (revision_count + 1)
    │
    └─ Case B: 표현 또는 문체 오류 (문맥 어색함, 번역투 잔존, 스타일 가이드 미준수)
          → ② Korean Editing Agent 재호출 (원문 + 현재 윤문 + 감수 지적사항 전달)
          → ③ Translation Reviewer 재검토 (revision_count + 1)

ELSE IF review.status == "REVISE" AND review.revision_count >= 3
    → 자동 재작업 루프 중단
    → ④ Korean Proofreader 호출 (표기/맞춤법만 정리)
    → 사용자 최종 결과의 [품질 검토] 섹션에 미해결 감수 이슈를 명시하여 보고
```

---

## 2. 재작업(REVISE) 전달 데이터 명세

Orchestrator가 `REVISE` 판정을 받아 하위 Agent에 재작업을 지시할 때는 반드시 아래 4가지 항목을 포함해야 합니다.

1. **원문 (`SOURCE`)**: 해당 문단 또는 전체 원문
2. **현재 결과물 (`TARGET`)**: 문제가 발생한 현재 번역문 또는 윤문본
3. **감수 오류 내역 (`ISSUES`)**: `Translation Reviewer`가 지적한 등급(Critical/Major) 및 상세 문제 설명
4. **구체적 수정 요청 (`ACTION`)**: `Translation Reviewer`가 제시한 `수정 제안` 내용
