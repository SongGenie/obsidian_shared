---
title: 주간 보고 자동화 POC
created: 2026-10-15
status: POC
tags: [GE, Agent, 주간보고, 자동화, Slack]
---

# 주간 보고 자동화 POC

기획 문서: [[GE_Agents/01_주간_보고_자동화/00_기획]]  
사전 검증: [[GE_Agents/01_주간_보고_자동화/01_검증]]
공통 제약: [[GE_Agents/공통_도입_제약]]

## 목적과 범위

주간 보고 자동화의 핵심 흐름을 실제 환경에서 시험했다. POC 결과는 기능 측면에서 완료다. Gmail은 GWS 구독이 필요해 사용하지 않으며, 출력은 Slack 메시지로 정했다.

## POC 결과: 완료 (2026-10-16)

### 완료 항목

- Slack을 GE에 데이터 스토어 형태로 연동했다.
- 인증 후 주간 데이터를 읽었다.
- 읽은 내용을 사용자에게 Slack 메시지로 전송했다.
- GE에서 예약을 설정할 수 있음을 확인했다.
- 예약 실행 후 Slack 메시지를 보내려면 사용자가 별도 승인을 눌러야 함을 확인했다.

위 결과는 사용자가 실제 환경에서 확인해 공유한 내용이다. 주간 데이터 읽기부터 Slack 전달까지의 기본 경로는 동작하지만, 사용자 승인 단계 때문에 완전 무인 정기 발송은 아니다. 사용자는 이 승인 방식이 운영상 애매하다고 평가했다.

### 이메일 경로 제외

- Gmail 발송은 GWS 구독이 필요하므로 사용하지 않는다.
- MailPlug를 통한 이메일 발송은 현재 POC 범위에 포함하지 않는다.
- 주간 보고 결과의 전달 채널은 Slack으로 정했다.

## 추가 제약: GWS/GCP 사용 금지

현재 Gemini Enterprise app만 구독되어 있으며 Google Workspace(GWS) 및 Google Cloud Platform(GCP)은 사용하지 않아야 한다. 별도 GWS/GCP 서비스는 추가 비용을 발생시킬 수 있어 설계 후보에서 제외한다. 세부 기준은 [[GE_Agents/공통_도입_제약]]에 기록했다.

- Gmail/GWS와 Google Drive를 이메일·저장 대안으로 사용하지 않는다.
- GCP 프로젝트, API, Cloud Run, GCP 기반 MCP 서버나 스케줄러를 도입하지 않는다.
- Gemini Enterprise app의 기존 구독에 포함된 기능과 과금 범위를 확인한다.

## 미해결: Slack Connector의 GCP 비용 및 정책 적합성

- Google 공식 설정 절차상 Slack 데이터 스토어 생성에는 Google Cloud 프로젝트 선택 및 Billing 옵션 선택이 포함된다. 따라서 Slack Connector는 기술적으로 GCP 프로젝트/Billing 구성과 연결된다. [Slack 데이터 스토어 설정](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/slack/set-up-data-store)
- Slack 데이터 스토어는 federated 방식으로 검색 질의를 Slack API에 전달한다. 이 사실만으로 개별 조회에 별도 GCP 사용료가 부과되는지는 판단할 수 없다. [Slack connector 개요](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/slack)
- Gemini Enterprise 좌석 구독은 기능별 할당량을 제공하며, 초과 과금이 활성화되면 한도 초과 사용에 종량제 요금이 발생할 수 있다. Pay-as-you-go edition은 사용량 기준 과금이다. 이 비용 설명은 Slack Connector의 별도 호출 요금 발생을 직접 증명하지 않으므로 실제 프로젝트의 Usage & Spending 및 Cloud Billing 확인이 필요하다. [할당량과 초과 사용](https://docs.cloud.google.com/gemini/enterprise/docs/quotas-and-overages), [비용 관리](https://docs.cloud.google.com/gemini/enterprise/docs/manage-costs-overview), [비용 보기](https://docs.cloud.google.com/gemini/enterprise/docs/view-costs)
- 설정 전제에는 Slack AI search가 포함된 Slack 플랜도 있다. 실제 Slack 계약에 포함되는지 확인한다. [Slack 데이터 스토어 사전 조건](https://docs.cloud.google.com/gemini/enterprise/docs/connectors/slack/set-up-data-store)

**판정: 실제 추가 비용과 조직의 GCP 금지 정책 적합성은 미확인이다.** 데이터 스토어가 연결된 프로젝트, Gemini Enterprise 에디션/과금 유형과 초과 과금 상태, 사용량 및 청구 내역, Slack 계약을 관리자가 확인해야 한다. 기능 POC는 완료했으나 이 확인 전에는 운영 확대 및 정기 운영을 승인된 경로로 간주하지 않는다.

## 운영 전 남은 확인 사항

- [ ] 데이터 스토어에 연결된 GCP 프로젝트와 Billing 상태를 관리자에게 확인
- [ ] Gemini Enterprise 에디션/과금 유형, 사용량 할당량 및 초과 과금 활성화 여부 확인
- [ ] Usage & Spending과 Cloud Billing에서 해당 사용량/비용 확인
- [ ] 기존 Slack 데이터 스토어가 조직의 GCP 사용 금지 정책에서 허용되는지 확인
- [ ] 예약 후 승인 대기 메시지를 누가 언제 처리할지 결정
- [ ] 필요하면 승인/미승인, 실패, 동일 주차 재실행 처리를 추가 검증

## 완료 판정 범위

- **기능 POC:** 완료 — GE에서 Slack 주간 데이터 읽기, Slack 메시지 작성/전송, 예약 설정 가능 여부를 확인했다.
- **자동 발송:** 미완료 — 예약 실행 후 전송 전에 사용자의 승인이 필요하다.
- **이메일:** 범위 제외 — Gmail은 GWS 구독 요건으로 사용하지 않는다.
- **비용/정책 적합성:** 미확인 — Slack Connector와 GCP 프로젝트/Billing 구성의 실제 비용 및 조직 정책 승인을 확인해야 한다.

> `status: POC`는 이 문서가 POC 단계의 기록임을 나타낸다. 기능 시험은 완료했지만, 운영 전 비용·정책 확인과 승인 처리 방식 결정이 남아 있다.
