# EmoAI Content Reaction Agent — Google Cloud Marketplace 등록 문구 (초안)

## 기본 정보

| 항목 | 내용 |
| --- | --- |
| 제품명 | EmoAI Content Reaction Agent |
| 제공사 | AbleAI Co., Ltd. (에이블에이아이) |
| 등록 유형 | AI Agent as a Service (A2A) |
| 카테고리 | AI Agents › Marketing & Advertising, Media & Entertainment |
| 지원 언어 | 한국어, 영어 (분석 대상 음성·발화) |

## 한 줄 소개 (Tagline)

**EN:** Know the moment your audience leans in — or tunes out.
**KO:** 시청자가 몰입하는 순간과 떠나는 순간을 정확히 짚어 드립니다.

## 짧은 설명 (Short description, 200자 이내)

**EN:** EmoAI measures how consenting viewers react to ads, trailers, and video content — emotion, attention, interest, and engagement, second by second — and answers your questions about any scene, right inside Gemini Enterprise.

**KO:** 광고·예고편·영상 콘텐츠를 본 시청자(동의자)의 정서, 집중도, 흥미, 몰입도를 초 단위로 분석하고, 장면별 질문에 Gemini Enterprise 안에서 바로 답합니다.

## 상세 설명 (Long description)

**EN**

Surveys tell you what viewers say. EmoAI shows you how they actually reacted.

Upload a recording of your test audience watching your content. EmoAI analyzes each viewer's face (FACS action units), voice, and speech against that person's own neutral baseline, then returns segment-by-segment curves for emotion, attention, interest, and engagement, along with the peaks, drop-offs, and a plain-language summary.

Then just ask: "Why did engagement drop at 2:30?" or "Which ending worked better?" EmoAI answers with the evidence behind each finding.

- **Per-person baseline:** Every face is different. EmoAI calibrates to each viewer's neutral expression, reducing false readings from resting facial features.
- **Multimodal:** Combines facial action units, voice tone and tremor, and speech content.
- **A/B comparison:** Compare reactions to two or more cuts of the same content.
- **Explainable:** Each finding cites the facial and vocal cues behind it.
- **Proven in broadcast:** Used throughout SBS's anniversary documentary series "Upload" (Korea).

**KO**

설문은 시청자가 "말한 것"을 알려 주지만, EmoAI는 시청자가 "실제로 어떻게 반응했는지"를 보여 줍니다.

시청자가 콘텐츠를 보는 모습을 녹화해 올리면, EmoAI가 각 시청자의 무표정을 기준값으로 삼아 표정(FACS Action Unit), 음성, 발화를 분석합니다. 결과로 정서·집중도·흥미·몰입도의 구간별 곡선, 반응이 정점에 오른 장면과 이탈한 장면, 그리고 이해하기 쉬운 요약을 제공합니다.

이어서 "2분 30초에서 몰입도가 왜 떨어졌어?", "어느 엔딩이 더 반응이 좋았어?"처럼 물으면, 근거와 함께 답합니다.

- **개인 기준선:** 사람마다 다른 무표정을 기준으로 잡아, 원래 표정 때문에 생기는 오판을 줄입니다.
- **멀티모달 분석:** 표정 AU, 음성의 톤과 떨림, 발화 내용을 함께 봅니다.
- **A/B 비교:** 같은 콘텐츠의 여러 버전에 대한 반응을 비교합니다.
- **설명 가능성:** 결과마다 근거가 된 표정·음성 신호를 함께 제시합니다.
- **방송 레퍼런스:** SBS 창사특집 다큐멘터리 「업로드」 1·2·3부 전편에 사용되었습니다.

## 주요 활용 사례 (Use cases)

1. **광고 사전 테스트:** 집행 전 광고 시안에 대한 반응 비교
2. **예고편·트레일러 편집:** 이탈 구간 확인과 컷 조정
3. **방송·OTT 콘텐츠 평가:** 회차·장면별 몰입도 분석
4. **기업 교육 영상 개선:** 집계된 몰입도로 강의 순서·길이 조정 (개인 평가 아님)

## 사용 원칙 (Responsible use)

**EN**
- Analyze only recordings of participants who have given informed consent.
- Not for employee monitoring, hiring decisions, or evaluating individual students. Training-content results are reported in aggregate only.
- Not a medical device. Results do not diagnose any health or mental condition.
- Results are reference information; final decisions remain with people.
- Source video is deleted after analysis; only results are retained.

**KO**
- 사전 동의한 참여자의 영상만 분석합니다.
- 직원 감시, 채용 평가, 학생 개인 평가에는 사용할 수 없습니다. 교육 콘텐츠 분석은 집계 결과로만 제공합니다.
- 의료기기가 아니며, 건강·정신 상태를 진단하지 않습니다.
- 분석 결과는 참고자료이며, 최종 판단은 사람이 합니다.
- 원본 영상은 분석 후 삭제하고 결과만 보관합니다.

## 가격 (안)

미확정. 과금 단위는 테스트 건(콘텐츠 1편 × 참여자 최대 N명)으로 하고, 원가 산출 → 경쟁가(Realeyes 셀프서비스 편당 약 $850~1,250) 대비 하향 → 국내 파일럿 3~5곳으로 확정합니다. 가설: 테스트 1건(참여자 30명까지) $300~600.

## 등록 전 확인할 것

- [ ] Agent Card의 `example-ableai.com` 주소를 실제 서비스 도메인으로 교체
- [ ] OAuth 서버와 Dynamic Client Registration 구현
- [ ] Google Cloud Partner Network 가입, Google Cloud 담당자를 통한 에이전트 추천
- [ ] 이용약관·개인정보처리방침에 위 사용 원칙 반영 (EU 판매 시 AI Act 검토)
- [ ] 아이콘(512×512)과 데모 영상 준비
