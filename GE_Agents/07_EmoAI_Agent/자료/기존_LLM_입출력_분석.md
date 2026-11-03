---
title: 기존 EmoAI LLM 입출력 분석
created: 2026-10-23
tags: [EmoAI, LLM, API, JSON]
---

# 기존 EmoAI LLM 입출력 분석

상위 기획: [[GE_Agents/07_EmoAI_Agent/00_기획]]

전시 프로젝트 소스를 읽어 정리했다. 실제 API 호출이나 실행 로그에서 추출한 결과는 아니다. 아래 숫자가 포함된 JSON은 구조 설명용 가상 예시다.

## 프롬프트 파일과 적용 순서

원본: `C:\ableai\XR_workspace\Meta Glass\exhibition\FaceAnalysisWebView\prompts\llm_system_prompt.txt`.

프로젝트 보관본: [시스템 프롬프트](llm_system_prompt.txt). 2026-10-23 확인 시 원본과 `deploy/windows/EMOAI/program/llm_system_prompt.txt`의 SHA256은 동일했다.

`llm_client.cpp`는 실행 파일 옆 → 현재 작업 폴더 → 현재 작업 폴더의 `prompts/` 순서로 같은 이름의 파일을 찾고, 없으면 코드 내 기본 지침을 사용한다. 기본 지침은 아동·아바타 응답 전략 용도라 외부 파일의 일반 관찰용 지침과 다르다. 실제 실행 시 적용된 파일은 실행 위치와 함께 확인해야 한다.

## OpenAI 입력과 출력

`LlmClient::generate_report()`는 `/v1/chat/completions`로 아래 두 메시지를 보낸다.

```text
system: llm_system_prompt.txt의 전체 내용
user: 세션 요약 데이터:\n + llm_summary_json
temperature: 0.4
model: 실행 시 설정한 모델명
```

영상·음성 원본이나 68점 좌표를 직접 이 호출에 넣지 않는다. 확정 전사문은 `speech`로 포함된다. 현재 요약 JSON에는 피치·음량·발화속도 원시 시계열, 감정 어휘 매칭 목록, 채널별 불일치 시계열이 독립 필드로 들어가지 않는다. 융합 결과에 영향을 주는 것과 원신호를 LLM에 직접 제공하는 것은 구분한다.

응답에서 `choices[0].message.content`를 문자열로 읽는다. 고정 JSON 출력 스키마를 강제하지 않고 프롬프트로 아래 형식을 요청한다.

```text
[정서 상태 | 신뢰도: <높음/보통/낮음/관측불충분>]
정서: <현재 정서 한 줄 요약>
집중: <높음/보통/낮음 + 근거 한 가지>
흥미: <높음/보통/낮음 + 추세>
변화: <감정 전환/미소/긴장/시선이탈 등>
발화: <내용 요약과 표정 지표와의 일치 여부, 또는 발화 없음>
관찰: <관측 경향을 종합한 한 문장>
```

위 내용은 출력 템플릿이며 실제 생성 결과 예시가 아니다.

## 구간 JSON 생성 과정

1. `AnalysisSession::start()`가 단일 활성 세션을 시작한다. 수집 중 다시 시작하면 기존 수집분을 폐기한다.
2. `record()`가 분석 프레임을 받고 전체 프레임 수·얼굴 검출 수를 센다. 유효하고 신뢰 가능한 프레임만 지표 집계에 사용한다.
3. 세션 경과초를 정수로 나누어 1초 버킷을 만든다. 융합 감정 점수와 각 지표를 모아 버킷별 대표 감정·평균을 계산한다.
4. `finish()`가 마지막 버킷을 닫고 구간 전체의 평균·최댓값·비율·이벤트·추세를 생성한다.
5. 로그용 JSON에는 `prompt_state.guidance`가 있지만 OpenAI 전송본에서는 이 필드를 삭제한다.

전시 `x.js`는 약 20초마다 `/api/analysis/result`를 호출한다. 서버는 이전 구간을 마감하고 다음 구간을 먼저 시작한 뒤 LLM을 호출한다. 구간 길이는 호출 간격에 좌우되므로 정확히 20초인 고정 영상 청크로 보지 않는다.

시간 기준은 원본 영상 재생 위치가 아니라 세션 시작 후 실제 경과시간이다. `speech[].t`도 확정 전사문을 세션에 기록한 시점의 경과초다. 발화 시작 시각이나 원본 영상 타임코드와 동일하다고 전제하지 않는다.

## 주요 JSON 필드

| 필드 | 실제 계산·의미 |
| --- | --- |
| `duration_sec`, `frames_collected` | 세션 길이·받은 분석 프레임 수 |
| `face_detected_ratio` | 검출 프레임 / 전체 프레임 |
| `reliable_face_ratio` | 신뢰 프레임 / 검출 프레임. 전체 프레임이 분모가 아님 |
| `emotion_distribution` | 유효 1초 버킷의 대표 감정별 비율. 감정 확률의 단순 평균이 아님 |
| `dominant_timeline` | 대표 감정이 바뀐 시점과 라벨 |
| `au_mean`, `au_peak` | 신뢰 프레임의 AU 평균·최댓값. 최댓값 발생 시각은 없음 |
| `head_movement`, `gaze` | 머리 회전·위치 및 시선각 표준편차 |
| `va_mean` | 유인가·각성도 평균 |
| `attention_summary`, `interest_summary` | 평균·수준·추세 및 시선/몸 기울임/눈썹 등 보조 집계 |
| `engagement_summary`, `tension_summary` | 평균·수준·추세 |
| `signal_summary`, `event_counts` | 미소·눈썹·긍정/부정 활성 비율 및 이벤트 횟수 |
| `undetected_spans` | 미검출 구간의 경과초 쌍 |
| `speech`, `speech_count` | 전사문·기록 경과초·발화 길이와 개수 |
| `prompt_state` | 코드가 계산한 신뢰도 등급·정서 표현·지표 수준 |

집중 등 수준은 평균 70 이상 `high`, 50 이상 `moderate`, 나머지 `low`로 나눈다. 추세는 내부 1초 버킷 목록의 전반부와 후반부 평균 차이가 +8 초과면 `rising`, -8 미만이면 `falling`, 그 외 `stable`이다. 이 임계값은 구현 규칙이며 성능이 검증됐다는 뜻은 아니다.

## 전송 JSON의 축약 예시

설명용 가상 값이며 일부 필드·AU를 생략했다.

```json
{
  "duration_sec": 20.0,
  "frames_collected": 500,
  "face_detected_ratio": 0.96,
  "reliable_face_ratio": 0.90,
  "emotion_distribution": {"Neutral": 0.6, "Happiness": 0.4},
  "dominant_timeline": [
    {"t": 0, "emotion": "Neutral"},
    {"t": 12, "emotion": "Happiness"}
  ],
  "au_mean": {"AU06": 0.4, "AU12": 0.8},
  "au_peak": {"AU06": 1.5, "AU12": 2.4},
  "va_mean": {"valence": 0.35, "arousal": 0.2},
  "attention_summary": {
    "mean": 74,
    "level": "high",
    "screen_gaze_ratio": 0.88,
    "gaze_valid_ratio": 0.92,
    "trend": {"label": "stable", "delta": 3}
  },
  "speech": [{"t": 14.2, "duration": 1.5, "text": "재미있네요"}],
  "speech_count": 1,
  "undetected_spans": [],
  "prompt_state": {
    "confidence": "high",
    "emotion_state": "밝고 편안함",
    "valence": 0.35,
    "arousal": 0.2,
    "attention_level": "high",
    "interest_level": "moderate",
    "engagement_level": "moderate",
    "tension_level": "low"
  }
}
```

## GE 연동에서 보완할 점

내부 `affect_timeline_`의 1초별 값 전체는 현재 전송 JSON에 포함되지 않는다. AU 피크 시각·미소 이벤트 시각도 전송하지 않는다. 따라서 구간 수준 요약은 가능하지만 정확한 초 단위 원인 설명이나 발화 순간과 지표의 정밀 대조에는 근거가 부족하다.

GE에 전달할 결과에는 콘텐츠·버전·참여자·구간 ID, 콘텐츠 시작/종료 타임코드, 1초별 지표, 시각이 있는 이벤트와 채널별 품질 정보를 추가하는 안을 검토한다. 현재 `/api/analysis/result`는 LLM 설명문과 메타데이터를 반환하므로 내부 구조화 JSON을 외부로 제공하는 경로도 필요하다.

## 코드 근거

- [프롬프트 로딩과 OpenAI 요청](<C:/ableai/XR_workspace/Meta Glass/exhibition/FaceAnalysisWebView/src/llm_client.cpp>)
- [구간 집계와 JSON 생성](<C:/ableai/XR_workspace/Meta Glass/exhibition/FaceAnalysisWebView/src/analysis_session.cpp>)
- [세션 구조](<C:/ableai/XR_workspace/Meta Glass/exhibition/FaceAnalysisWebView/src/analysis_session.h>)
- [20초 호출 루프](<C:/ableai/XR_workspace/Meta Glass/exhibition/FaceAnalysisWebView/web/js/x.js:216>)
