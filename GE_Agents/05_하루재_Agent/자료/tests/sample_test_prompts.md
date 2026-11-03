# 하루재 Agent 테스트 시나리오 및 샘플 프롬프트

Gemini Enterprise App의 **Agent Designer → Preview 탭**에서 하루재 Agent가 설계대로 작동하는지 검증하기 위한 테스트용 예문 모음입니다.

---

## 테스트 1: 기본 워크플로우 및 용어집/스타일 가이드 적용 검증

**목적**:
- `Shared Glossary` 용어(Large Language Model, Fine-tuning, Inference 등) 준수 여부 확인
- `Shared Style Guide` 규칙(최초 등장 시 영문 병기, 숫자와 SI 단위 `10 MB`, `500 GB` 사이 공백, 퍼센트 `99.9%` 붙여 쓰기) 확인

**입력 프롬프트 (복사하여 테스트)**:
```text
다음 영문을 번역해 주세요.

Our new Large Language Model architecture reduces memory overhead by 35.5% during real-time Inference. While previous models required at least 500GB of VRAM for Fine-tuning, this system can be operated by users with a lightweight 10MB configuration file and maintains 99.9% uptime across enterprise environments.
```

**기대 결과 체크리스트**:
- [ ] `Large Language Model`이 최초 등장 시 `대규모 언어 모델(Large Language Model, LLM)` 형태로 번역되었는가?
- [ ] `Inference` → `추론`, `Fine-tuning` → `파인튜닝`으로 용어집과 일치하는가?
- [ ] 수동태 표현(`can be operated by users`)이 윤문 단계에서 자연스러운 능동태로 다듬어졌는가?
- [ ] 단위 표기가 `500 GB`, `10 MB`(공백 있음) 및 `35.5%`, `99.9%`(공백 없음)로 교정되었는가?
- [ ] 최종 출력이 `[최종 번역문]`과 `[품질 검토]` 두 섹션으로만 깔끔하게 출력되었는가?

---

## 테스트 2: 모호한 표현 및 수치/부정문 정밀 감수 검증

**목적**:
- 원문의 이중 부정 및 조건절, 미묘한 수치 범위가 누락·오역 없이 정확히 번역 및 감수(`PASS`)되는지 확인

**입력 프롬프트 (복사하여 테스트)**:
```text
다음 텍스트를 번역해 주세요.

Unless the latency exceeds 150ms for more than 3 consecutive intervals, the fallback Agent will not be triggered automatically. Note that Artificial Intelligence safety guardrails cannot be bypassed under any circumstances, even by system administrators.
```

**기대 결과 체크리스트**:
- [ ] `Unless ... will not be triggered`의 조건-부정 관계가 반대로 번역되지 않았는가?
- [ ] `150 ms` 단위에 공백이 적용되었는가?
- [ ] `Artificial Intelligence` → `인공지능`, `Agent` → `에이전트` 용어집이 준수되었는가?

---

## 테스트 3: 내부 감수 과정 상세 확인 테스트 (디버깅용)

**목적**:
- 기본적으로 숨겨지는 각 Sub-Agent(번역 → 윤문 → 감수 → 교정)의 단계별 출력 메타데이터가 정상 생성되는지 확인

**입력 프롬프트 (복사하여 테스트)**:
```text
아래 문장을 번역해 주세요. 이번 요청에서는 디버깅을 위해 내부 Agent 간 검토 과정(번역, 윤문, 감수, 교정 각 단계의 출력과 메타데이터)도 마지막에 함께 보여주세요.

Deep Learning models often suffer from performance degradation when deployed to production environments without proper Prompt validation.
```
