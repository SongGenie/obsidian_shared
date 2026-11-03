---
title: EmoAI 분석 결과 JSON 규격
created: 2026-10-23
status: 규격 확정
schema_version: 1.0.0
tags: [EmoAI, JSON, API, 데이터규격]
---

# EmoAI 분석 결과 JSON 규격

기획: [[GE_Agents/07_EmoAI_Agent/00_기획]]  
사전검증: [[GE_Agents/07_EmoAI_Agent/01_검증]]

**EmoAI 엔진 → 결과 저장 → 해석·질의응답 계층이 공유할 결과 규격 v1.0.0을 확정한다.** 이 문서·JSON Schema·교차 필드 검증기가 함께 계약을 구성한다. 기존 전시 엔진의 출력 코드를 변경하거나 새 규격의 실제 API를 배포한 상태는 아니다.

## 범위와 파일

결과 1개는 **테스트 1건의 참여자 1명·녹화 1개·콘텐츠 버전 1개**를 분석한 산출물이다. 여러 참여자의 집계와 A/B 비교는 이 결과들을 입력으로 하는 별도 계층에서 수행한다. 참여자가 여러 명 보이는 영상은 화자·얼굴 분리 전 이 규격의 단일 참여자 결과로 제출하지 않는다.

작업 접수·대기·진행·실패 상태, 인증·구매 권한, A2A Task 봉투, LLM 보고서 형식은 이 결과 규격에 포함하지 않는다. 작업 자체가 실패하면 실패 응답을 반환하고 성공 결과를 만들지 않는다. 처리는 끝났지만 신호가 없는 구간은 결측을 포함한 결과로 반환할 수 있다.

- [JSON Schema](자료/규격/analysis-result.schema.json)
- [교차 필드 검증기](자료/규격/validate_result.py)
- [검증 결과](자료/규격/contract_test_results.json)
- [정상 음성 예시](자료/규격/examples/normal_voice.json)
- [정상 무발화](자료/규격/examples/silence.json) / [음성 입력 없음](자료/규격/examples/audio_missing.json)
- [얼굴 품질 부족](자료/규격/examples/face_missing.json) / [콘텐츠 시간 불명](자료/규격/examples/unsynced.json)
- [STT 실패](자료/규격/examples/stt_failed.json) / [전사문 비공개](자료/규격/examples/redacted.json)

모든 예시의 `data_origin`은 `synthetic`이다. 사람이 실제로 보인 반응이나 모델 성능을 나타내지 않는다.

## 결과 전체 구조

| 필드 | 의미 |
| --- | --- |
| `schema_version` | 이번 계약은 `1.0.0` |
| `data_origin` | 실제 관측 `observed` / 합성 시험 `synthetic` |
| `analysis_id`, `test_id`, `participant_id` | 분석·테스트·가명 참여자 식별자 |
| `generated_at` | 결과 생성 시각. 시간대가 있는 ISO8601 문자열 |
| `recording` | 참여자 녹화 ID와 녹화 길이 |
| `content` | 시청 콘텐츠 ID·버전·전체 길이 |
| `audio_source` | 분석 음성의 출처·길이·참여자 귀속·녹화 시간과의 정렬 |
| `baseline` | 개인 무표정 기준선 확보 여부와 수집한 녹화 구간 |
| `methods` | 모델·수식·전처리·어휘 사전·STT의 버전과 잠재 입력 채널·표본 단위 |
| `content_mappings` | 녹화 시간에서 콘텐츠 시간으로의 구간별 매핑 |
| `segments` | 녹화 전체를 덮는 최대 1초 단위 결과 |
| `utterances` | 확정 전사문과 실제 오디오에 맞춘 구간 |
| `events` | 시각과 근거를 가진 AU 피크·관측 패턴 등 |
| `limitations` | 보정·시간 정렬·입력 품질 등 설명 가능한 제한 |

원본 영상 URL, 인증 토큰, 개인 실명, 68점 좌표는 이 기본 결과에 넣지 않는다. 원본 접근 권한과 저장소 위치는 서버에서 관리하고, 좌표 디버깅이 필요하면 별도 개발용 산출물로 분리한다. JSON의 ID만으로 권한을 보장할 수 없으며 API에서 고객·사용자 권한을 검증해야 한다.

## 결측과 수치

지표의 공통 표현은 아래와 같다. 예시는 얼굴 품질 부족으로 집중을 산출하지 못한 상태다.

```json
{
  "status": "unavailable",
  "value": null,
  "unit": "score_0_100",
  "reason": "low_quality",
  "valid_samples": 0,
  "total_samples": 30,
  "valid_duration_sec": 0,
  "method_id": "score-v1",
  "source_channels": [],
  "level": "unavailable"
}
```

| 상태 | 규칙 |
| --- | --- |
| `available` | 수치 존재, `reason=null`, 유효 표본·유효 시간 > 0, 실제 사용 채널 존재 |
| `unavailable` | 입력·품질·기준선 등의 사유로 미산출. 값 null |
| `not_applicable` | 요청 기능이나 용도상 비적용. 값 null과 사유 표시 |
| `error` | 처리 시도 중 오류. 값 null과 사유 표시 |

`available` 이외에는 `valid_samples=0`, `valid_duration_sec=0`, `source_channels=[]`로 쓴다. `total_samples`는 검사한 후보 표본 수라 0이 아닐 수 있다. 실제 측정값 0은 `available / value=0`으로 보존한다. 결측을 0·낮음·중립으로 채우거나 이전 구간의 값을 복사하지 않는다. NaN·Infinity·중복 JSON 키도 거부한다.

사유 코드는 `face_missing`, `low_quality`, `baseline_missing`, `baseline_not_ready`, `audio_missing`, `no_speech`, `not_voiced`, `nonparticipant_audio`, `stt_unavailable`, `redacted`, `not_supported`, `processing_error`, `disabled`, `unknown`을 사용한다. 사유가 명확하면 `unknown` 대신 해당 코드를 사용한다.

`valid_samples`와 `total_samples`는 같은 단위이며 단위는 `methods[method_id].sample_unit`에 기록한다. 영상 프레임·오디오 분석 프레임·발화·시간 버킷은 서로 다른 표본이다. 서로 다른 지표의 표본 수를 합쳐 전체 신뢰도 퍼센트를 만들지 않는다. `valid_duration_sec`는 유효 신호가 차지한 시간의 합집합 길이로, 중복 프레임·중첩 창의 길이를 단순 합산하지 않는다.

`methods.source_channels`는 사용 가능한 입력 채널 목록이고, 각 측정값의 `source_channels`는 **그 값을 실제로 산출할 때 쓴 채널**이다. 무발화 구간의 융합 결과에 사용하지 않은 voice·language 채널을 기재하지 않는다.

## 시간축

모든 구간은 **초 단위의 `[start_sec, end_sec)`**다. 종료 시각은 다음 구간에 포함된다. 프레임 수나 처리 서버의 경과시간으로 미디어 시간을 대신하지 않는다. 녹화·콘텐츠 시간은 각 미디어 시작을 0으로 한다. `generated_at`, `observed_at`은 처리 시각으로 시간축에 사용하지 않는다.

매핑은 구간별 1배속으로 정의한다.

```text
content_time = recording_time - mapping.recording.start_sec
               + mapping.content_start_sec
```

예: 녹화 10~20초가 콘텐츠 30~40초에 해당하면, 녹화 12.5초의 반응은 콘텐츠 32.5초다. `uncertainty_sec`에는 동기화 오차의 추정 상한을 기록한다. 확인하지 않은 동기화에 0초 오차를 쓰지 않는다.

매핑마다 ID·녹화 범위·콘텐츠 시작 시각·확인 방식·오차를 제공한다. 콘텐츠 일시정지·재생 재개·탐색 지점에서 매핑을 나눈다. 콘텐츠 재시청으로 콘텐츠 시각이 되돌아가는 것은 허용하지만 녹화 범위끼리는 겹치면 안 된다. 재생 속도 변경·시간 늘이기는 v1에서 지원하지 않으며, 미리 1배속 시간축으로 정규화해야 한다.

| 상황 | 표현과 처리 |
| --- | --- |
| 한 매핑 안의 구간 | `timing.recording`, `timing.content`, `mapping_id` 제공 |
| 정렬 미확인·콘텐츠 일시정지 등 대응 불가 | `content=null`, `mapping_id=null`; 녹화 시간만 유지 |
| 1초 결과가 매핑 경계를 넘음 | 경계에서 결과 구간을 나누어 각 구간을 최대 1초로 유지 |
| 발화·이벤트가 여러 매핑에 걸침 | 녹화 구간은 유지하되 연속된 단일 콘텐츠 범위를 보장할 수 없으면 콘텐츠 시간은 null. 텍스트를 임의 분할하지 않음 |

한 매핑에 온전히 들어가면 알려진 콘텐츠 시간을 숨기거나 다른 매핑으로 연결하지 않는다. 콘텐츠 시간이 null인 결과로 “광고 32초 장면에서 반응이 바뀌었다”고 설명하면 안 된다. 오차가 큰 구간도 오차보다 정밀하게 설명하지 않는다.

## 최대 1초 결과와 얼굴 품질

`segments`는 녹화 0초부터 종료까지 순서대로 이어지며 겹치거나 비어 있는 시간이 없어야 한다. 기본은 0~1, 1~2초이고 매핑 경계와 마지막 구간에서는 더 짧아질 수 있다. 얼굴이 사라진 시간도 구간 자체를 생략하지 않는다.

`face_quality`는 `trusted_frames ≤ detected_frames ≤ total_frames`로 기록한다. 신뢰 프레임이 0이면 얼굴 신호를 사용한 지표는 `available`일 수 없다. 음성만 사용해 별도로 정의한 지표까지 무조건 지우는 것은 아니며, 실제 사용 채널과 해당 산출 방법을 확인한다.

`baseline.status`는 `captured / unavailable / disabled`다. 확보했을 때만 기준선 녹화 범위를 넣는다. 기준선 구간이 끝나기 전의 보정 AU는 `baseline_not_ready`, 미확보라면 `baseline_missing`으로 쓴다. 기준선이 있다는 사실만으로 보정의 정확도가 검증됐다고 표시하지 않는다.

## 지표 이름과 단위

각 구간에는 아래 필수 지표 11개를 항상 넣으며 산출 불가도 공통 결측 표현으로 남긴다.

| 지표 | 범위·단위 | 해석 |
| --- | --- | --- |
| `attention`, `interest`, `engagement`, `tension` | 0~100, `score_0_100` | 알고리즘이 만든 추정 지표. 심리 상태 측정 정확도 아님 |
| `valence`, `arousal` | -1~1, `normalized` | 구간 융합 유인가·각성도 |
| `voice_pitch_hz` | 0 초과, `Hz` | 유성음에서 추정한 평균 F0. 무성 구간에 0을 넣지 않음 |
| `voice_energy_dbfs` | -160~0, `dBFS` | 디지털 신호 레벨. 실제 음압 dB SPL이 아님. 범위 밖·비유한 값은 결측 |
| `voice_rate_sps` | 0 이상, `syllables_per_sec` | 발화 구간의 음절 속도 추정. 방법 버전을 반드시 지정 |
| `language_valence`, `language_arousal` | -1~1, `normalized` | 확정·공개 가능한 전사문에 대한 어휘 분석 |

선택 지표는 다음과 같다. 생략은 해당 결과에서 제공하지 않았다는 뜻이며, 0이나 정상으로 간주하지 않는다.

| 지표 | 범위·단위 | 규칙 |
| --- | --- | --- |
| `voice_arousal` | 0~1, `normalized` | 음성 기반 각성도이며 확률·정확도로 설명하지 않음 |
| `au_raw_AU01` 등 | 0~5, `AU_0_5` | 원본 AU 강도의 구간 평균 |
| `au_delta_AU01` 등 | 0~5, `AU_0_5` | 개인 기준선·잡음 허용폭을 뺀 양의 변화량 평균. z점수 아님 |
| `emotion_Anger` 등 7개 | 0~1, `probability` | 융합 분포의 유효 프레임 평균. 전부 제공하거나 전부 생략 |

AU 코드는 `01,02,04,05,06,07,09,10,12,14,15,17,20,23,25,26,45`만 허용한다. 감정 라벨은 `Anger,Disgust,Fear,Happiness,Neutral,Sadness,Surprise`로 고정한다. 감정 7개가 산출됐으면 모두 available이고 합은 오차 0.0001 이내에서 1이어야 한다. 감정 점수는 실제 감정의 진실 확률이나 시스템 정확도가 아니다.

4개 0~100 지표에만 `level`을 쓴다. 현행 프로파일에 맞춰 70 이상 high, 50 이상 moderate, 미만 low이며 결측은 unavailable이다. 나머지 지표의 level은 null이다. 이 임계값은 서비스의 분류 규칙이며 검증된 심리학적 경계가 아니다.

구간 값은 해당 구간의 유효 표본 평균이다. 전체 녹화 평균은 동일 방법·단위의 available 구간만 유효 시간으로 가중해 별도 계산한다. 서로 다른 엔진 버전·방법·원본 AU와 보정 AU를 합쳐 평균내지 않는다. 감정 확률 평균과 기존의 “1초별 대표 감정 점유 비율”도 서로 다른 값이다.

## 음성 출처와 상태

`audio_source.origin`은 `recording_track / external_track / none`이다. 외부 마이크는 파일 분석에 자동 혼합하지 않는다. 별도 녹음 파일로 확보해 참여자 귀속과 정렬을 확인한 뒤 external_track으로 처리한다.

`attribution`은 `participant_confirmed / content_only / mixed / unknown / not_applicable`이다. 콘텐츠 배경음만 있거나 참여자·배경음이 분리되지 않았거나 귀속을 모르면 해당 음성을 제외한다. VAD가 소리를 감지했다는 사실만으로 참여자 발화로 인정하지 않는다. 본 규격의 검증기는 귀속 선언의 일관성을 확인하며, 실제 화자 분리의 정확도를 검증하지 않는다.

외부 오디오 정렬은 `recording_time = audio_pts + offset_to_recording_sec`이다. 오프셋은 음수도 허용한다. 오디오 길이와 오프셋으로 실제 녹화에 겹치는 범위를 확인하며, 음성 coverage가 이 범위를 초과하면 거부한다. 녹화 내 오디오 트랙은 offset=0, aligned로 기록한다. 오디오 드리프트·속도차는 미리 정규화해야 한다.

| 구간 `audio.state` | 뜻 | 주요 후속 처리 |
| --- | --- | --- |
| `speech` | 참여자 오디오에서 발화를 관측 | pitch·rate·STT 사용 가능. 각 지표별 품질은 별도 확인 |
| `silence` | 유효 참여자 오디오를 확인했으나 무발화 | `speech_duration_sec=0`; pitch·rate·언어 지표 null. 음량은 산출 가능 |
| `unavailable` | 오디오가 없거나 사용할 수 없음 | 값 null·사유; 무발화로 바꾸지 않음 |
| `not_processed` | 음성 분석을 하지 않음 | disabled 등 사유 명시 |
| `error` | 디코딩·분석 실패 | processing_error 등 사유 명시 |
| `excluded` | 참여자 음성 귀속 미확인·배경음·혼합음 | nonparticipant_audio로 제외 |

speech/silence만 실제 `coverage_duration_sec > 0`과 숫자 speech_duration을 갖는다. 나머지는 coverage=0, speech_duration=null이다. coverage는 유효하게 확인한 오디오 시간이며 전체 파일 길이와 다르다. speech_duration은 coverage를 넘지 못한다. 분석하지 않은 무음 구간을 silence로 추정하지 않는다.

## STT와 언어

`transcript.state`는 `available / no_speech / unavailable / not_processed / error / redacted`다. no_speech는 유효 오디오에서 silence를 관측한 경우에만 사용한다. **STT 서버 장애·빈 결과·오디오 없음은 발화 없음의 증거가 아니다.**

확정 발화는 `utterances`에 저장하고 해당 발화가 겹치는 모든 segment가 ID로 참조한다. STT partial은 최종 결과에 누적하지 않는다. 발화 구간은 오디오의 실제 시작·종료 시각을 녹화 시간으로 변환해서 기록한다. 전사 완료 시각은 `observed_at`에 분리한다.

STT가 실제 발화 시간을 제공하지 못하면 `timing_status=unavailable`, `timing=null`로 원문을 별도 보관할 수 있다. 이 발화를 특정 segment의 근거로 연결하거나 얼굴과의 동시성을 설명하면 안 된다. 녹화 시간은 알지만 콘텐츠 정렬만 모를 때는 timing_status=aligned, timing.content=null로 구분한다.

`stt_confidence`는 엔진이 실제로 제공한 값만 사용하고 없으면 null이다. 확신 퍼센트를 LLM이 생성하지 않는다. `stt_method_id`는 STT 모델 종류·버전이 있는 method를 참조한다.

비공개 발화는 `redacted=true`, `text=null`, `matched_terms=[]`로 남긴다. 해당 segment의 transcript도 redacted이며, 언어 지표를 null로 처리한다. v1은 segment 단위 비공개를 적용하며 일부 발화만 공개되는 복합 정책은 다음 버전에서 별도 정의한다. 얼굴·음성 수치가 유효하면 해당 채널의 분석까지 없애지는 않는다.

## 시각과 근거가 있는 이벤트

각 이벤트는 ID·녹화 구간·콘텐츠 대응·근거 segment ID를 가진다. AU 등 수치 피크는 아래 형식이다. 예시는 축약본이다.

```json
{
  "id": "evt-1",
  "kind": "metric_peak",
  "timing": {
    "recording": {"start_sec": 1, "end_sec": 2},
    "content": {"start_sec": 6, "end_sec": 7},
    "mapping_id": "map-1"
  },
  "peak_recording_sec": 1.4,
  "metric_key": "au_raw_AU06",
  "value": 1.2,
  "evidence_segment_ids": ["seg-1"]
}
```

peak는 이벤트 구간 안에 있어야 하고, 그 시점의 근거 segment에서 해당 지표가 available이어야 한다. 구간 평균만 가진 기존 자료에서 피크 발생 시각을 추정해 채우지 않는다. `value` 단위는 metric_key의 정의를 따른다.

추가 이벤트 종류는 `duchenne_smile_pattern`, `social_smile_pattern`, `brow_raise`, `gaze_away`, `tension_spike`, `channel_disagreement`다. 근육·신호 조합을 관측했다는 이름이며 진심·감정의 원인을 판정하지 않는다. 수치 피크가 아닌 이벤트는 metric_key와 value를 null로 둔다. 근거 목록이 비어 있거나 존재하지 않는 ID를 참조하면 거부한다.

## GE와 LLM의 소비 규칙

1. 스키마와 교차 필드 검사 모두 통과한 결과만 해석 계층에 넘긴다.
2. available 수치와 유효 시간·채널·방법을 함께 전달한다. null을 채워 추론하거나 서로 다른 분모의 신뢰도를 결합하지 않는다.
3. 구간별 설명은 `analysis_id → segment/event/utterance ID → 실제 시각`을 근거로 남긴다.
4. 콘텐츠 시간이 없으면 녹화 시간 기준으로만 설명하고 장면 귀속은 미확인으로 쓴다.
5. 무발화면 언어 분석을 생략하고, STT 장애면 발화 내용을 확인하지 못했다고 설명한다. 두 상황을 같게 요약하지 않는다.
6. 비공개 텍스트·감정 어휘를 복원하지 않는다. 근거 없는 AU 피크 시각·채널별 confidence를 만들지 않는다.
7. 모든 신호가 결측이면 해석을 생성하지 않고 관측 불충분을 반환한다. 얼굴만 없는 경우 음성·언어 분석은 그 채널 근거에 한해 제공한다.
8. 합성 예시는 실제 고객 반응 보고서에 섞지 않는다. 개선 제안은 관측 사실과 분리하고 인과관계를 단정하지 않는다.

LLM의 보고서·인용 정확도와 API의 고객별 권한은 별도 통합시험 대상이다. JSON 검증기 통과가 이를 보장하지 않는다.

## 기존 JSON과의 대응

이 버전은 기존 JSON에 바로 필드를 더하는 방식이 아니라 **새 결과 계약**이다. 기존 파일은 보존하며 기계적인 변환으로 없는 근거를 만들지 않는다.

| 기존 항목 | 새 계약에서의 처리 |
| --- | --- |
| `duration_sec` | 실제 녹화 길이를 확인한 뒤 recording.duration_sec 사용. 세션 처리시간을 대입하지 않음 |
| `frames_collected`, 검출·신뢰 비율 | segment의 실제 프레임 수로 보관. 집계 비율에서 정수 프레임을 역산하지 않음 |
| `attention_summary.mean` 등 | 1초별 measurements로 새로 출력. 20초 평균을 20개 segment에 복사하지 않음 |
| `au_mean`, `au_peak` | 원본 AU 평균·피크 집계로 보존. 1초별 값·피크 시각을 새로 수집해야 새 계약에 반영 가능 |
| `emotion_distribution` | 대표 감정 버킷 점유율로 별도 보존. 확률 평균인 emotion_*로 바꾸지 않음 |
| `dominant_timeline` | 세션 경과시간을 콘텐츠 시간으로 취급하지 않음 |
| `speech[].t` | 기록 시점이므로 실제 발화 타이밍으로 복사 금지 |
| `prompt_state`·최종 해석문 | 결과 수치와 분리. LLM 출력이나 상태 표현을 실제 관측값으로 재입력하지 않음 |

현재 생성된 기존 집계 JSON은 새 스키마의 적합 예제가 아니다. 실제 녹화 시간·오디오·1초 지표를 확보하기 전에는 완전한 v1 변환기를 만들지 않는다. 반대로 과거 형식을 필요로 하는 화면에는 별도 legacy 집계 뷰를 제공할 수 있지만, 1초 감정 확률 평균과 대표 감정 점유율의 차이를 유지해야 한다.

## 검증과 변경 관리

JSON Schema Draft 2020-12는 필수 필드·enum·범위·조건부 null을 검사한다. 별도 검증기는 시간 구간·ID 참조·오디오 정렬·기준선 준비·샘플 분모·확률 합·STT 귀속·점수 수준을 검사한다. JSON Schema 하나만 적용하면 교차 필드 규칙을 모두 검사할 수 없다.

2026-10-23 현재 로컬에 이미 설치된 Python과 jsonschema 4.25.1로 **65개 검사 통과, 실패 0**을 확인했다. 정상 7종 외에 관측된 실제 0·외부 오디오 정렬·무성음 결측·콘텐츠 정지와 재시청·시간 미확인 전사·배경음 제외·전체 결측을 수락하고, 결측의 0 변환·음성 귀속 오류·시간/참조 불일치·잘못된 날짜·스키마 버전 오류 등을 거부했다. 이는 합성 데이터의 계약 시험이며 실제 엔진 구현 검증이나 클라우드 호출은 아니다.

재현 명령은 현재 PC 기준이다. 패키지를 새로 설치하거나 네트워크로 스키마를 가져오지 않는다.

```powershell
& 'C:\Users\user\miniconda3\python.exe' 'GE_Agents/07_EmoAI_Agent/자료/규격/test_contract.py'
& 'C:\Users\user\miniconda3\python.exe' 'GE_Agents/07_EmoAI_Agent/자료/규격/validate_result.py' 'GE_Agents/07_EmoAI_Agent/자료/규격/examples/normal_voice.json'
```

[스키마 생성 코드](자료/규격/build_schema.py)와 [예시 생성 코드](자료/규격/build_examples.py)를 같이 보관한다. 변경 시 생성 파일도 갱신하고 [계약 시험](자료/규격/test_contract.py)을 실행한다. 방법·모델·보정 수식 변경은 method 버전을 바꾸고, 필드·단위·결측·시간 의미를 바꾸면 schema_version을 올린다. v1 검증기는 정확히 1.0.0만 수락하며, 새 버전은 별도 스키마·검증기를 배포한다.

단일 결과가 매우 길어지면 서버에서 분할 저장·조회하되 수신 측은 전체 결과를 조립해 검사한다. 페이지 API·장기 영상 chunk 규격은 이번 v1 계약과 별도다.

참고: [JSON Schema Validation](https://json-schema.org/draft/2020-12/json-schema-validation), [조건부 스키마](https://json-schema.org/understanding-json-schema/reference/conditionals).
