---
title: MiniMax H3 Audio T8 - ComfyUI 영상·오디오 노드
created: 2026-11-02
status: 정리
tags: [메모, ComfyUI, MiniMax, H3, AI영상, 오디오, 립싱크]
---

# MiniMax H3 Audio T8

- **저장소:** [T8mars/comfyui-minimax-h3-audio-T8](https://github.com/T8mars/comfyui-minimax-h3-audio-T8)
- **주제:** ComfyUI / 영상·오디오 동시 생성 / 레퍼런스 제어 / 립싱크 / 장편 영상
- **확인일:** 2026-11-02
- **확인 버전:** README 및 `pyproject.toml` 기준 **1.104.0**
- **정리 범위:** 공개 README, 상세 사용 문서, 설치 의존성 및 진입 코드 확인. 직접 설치하거나 GPU로 실행한 후기는 아님.

## 요약

**MiniMax H3 기반 영상과 오디오 생성 기능을 ComfyUI 워크플로로 확장하는 커스텀 노드 모음**이다. 텍스트·이미지·영상·음성을 입력으로 활용하고, 말하거나 노래하는 인물, 분할 장편 영상, 카메라 움직임과 후처리까지 연결할 수 있다.

저장소에는 노드 코드, 브라우저 UI, 예제 워크플로와 사용 문서가 들어 있다. **모델 가중치는 별도로 준비**해야 하며, 기본 H3 생성은 ComfyUI의 네이티브 H3 지원을 바탕으로 동작한다. 기능 개요는 [영문 README](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/README_EN.md), 세부 동작은 [상세 가이드](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/README_DETAILS_EN.md)에 정리되어 있다.

## 주요 기능

| 기능 | 내용 | 시작할 예제 |
| --- | --- | --- |
| 기본 영상·오디오 생성 | 텍스트(T2VA), 첫 프레임(I2VA), 끝 프레임(L2VA), 첫·끝 프레임(FL2VA), 단일·다중 참조 이미지(Ref2VA) | [기본 생성](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/01-basic-generation) |
| 음성·립싱크 | 참조 음성, 대사, 말하기·노래하기, 원본 오디오 유지와 최종 믹싱 | [오디오 제어](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/02-audio-control) |
| 뮤직비디오 | 분리한 보컬로 장면을 구동하고, 영상 조립 후 전체 원곡을 한 번 결합하는 Vocal Lock 방식 | [MV·립싱크](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/24-mv-lipsync) |
| 장편·이중 샘플링 | 두 모델의 4+4 단계 처리, 구간별 이어 만들기, 멀티 키프레임과 재개 기능 | [장편 영상](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/04-long-video) |
| 시각적 연출 | 샷·소재·오디오를 배치하는 T8 Obsidian Director | [Director Console](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/39-director-console) |
| 카메라·시간 편집 | Meridian 기반 카메라 움직임 및 소스 시간 편집 | [Meridian](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/37-meridian) |
| 기존 영상 보완 | 선택 구간의 얼굴 수정, 영상 외곽 확장, 기존 영상에 효과음 생성 | [얼굴 수정](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/06-face-refine) · [외곽 확장](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/27-video-outpaint) · [Foley](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/H07_FOLEY_USAGE.md) |
| 가속·메모리 관리 | OpenVDN, FastH3, 저 VRAM 노드 등 여러 선택 경로 | [가속 예제](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows/10-speed) |
| 미리보기·후처리 | TAEH3 근사 미리보기, Topaz, DLSS-NR 업스케일 및 프레임 보간 | [TAEH3](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/TAEH3_SAMPLING_PREVIEW_EXP.md) · [Topaz](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/TOPAZ_EXP.md) |

`T8 Obsidian Director`는 이 프로젝트의 ComfyUI 연출 UI 이름이다. 현재 메모를 보관하는 Obsidian 앱의 플러그인을 뜻하지 않는다.

## 설치와 준비

### 1. ComfyUI 준비

최근 네이티브 H3 API를 지원하는 ComfyUI가 필요하다. 노드가 전부 빨갛게 표시되거나 누락된다면 Core·프런트엔드·Manager 버전부터 확인한다. 패키지 메타데이터상 Python 요구사항은 **3.10 이상**이다.

### 2. 커스텀 노드 설치

ComfyUI 폴더를 기준으로 다음 명령을 실행한다.

```powershell
cd custom_nodes
git clone https://github.com/T8mars/comfyui-minimax-h3-audio-T8.git minimax-h3-audio-T8
```

또는 ComfyUI Manager에서 `MiniMax H3 Audio T8`을 검색한다. GitHub와 Registry의 공개 시점은 다를 수 있다. 설치·업데이트 후에는 **ComfyUI를 완전히 종료하고 다시 실행한 뒤 브라우저도 새로고침**한다.

기본 노드용 `requirements.txt`에는 추가 패키지가 없다. Torch, torchaudio, NumPy, Pillow, safetensors 등은 ComfyUI 환경을 사용한다. 선택형 Advanced·EXP 기능은 별도 의존성을 요구할 수 있다. [설치 안내](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/README_EN.md#install) · [기본 의존성](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/requirements.txt) · [패키지 정보](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/pyproject.toml)

### 3. 모델 배치

| 모델 종류 | ComfyUI 내부 폴더 |
| --- | --- |
| H3 diffusion 모델 | `models/diffusion_models` |
| Qwen3-VL 텍스트 인코더 | `models/text_encoders` |
| 영상·오디오 VAE | `models/vae` |
| Turbo 등 호환 LoRA | `models/loras` |
| 선택형 TAEH3 미리보기 모델 | `models/vae_approx` |

모델은 사용할 워크플로가 지정한 조합으로 준비한다. 이름이 비슷한 체크포인트라도 구조·양자화·LoRA 호환성이 같다고 볼 수 없다. 추가 모델 및 경로는 [모델 안내](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/README_EN.md#download-models)에서 확인한다.

## 처음 사용할 때의 순서

1. **기본 생성 예제 하나로 시작:** 짧은 텍스트 또는 첫 프레임 이미지로 모델 로딩, 영상과 소리 출력을 확인한다.
2. **예제의 자리표시자 교체:** 모델 파일과 입력 이미지·음성 경로를 자신의 파일로 바꾼다.
3. **오디오 제어 추가:** 대사·참조 음성·노래 등 필요한 목적의 예제로 이동한다.
4. **장편·이중 샘플링 확장:** 짧은 구간에서 확인한 뒤 길이를 늘리고 연결부, 색 변화, 인물 일관성을 확인한다.
5. **후처리 적용:** 업스케일·보간은 결과물을 확인한 뒤 별도 단계로 적용한다.

일반 문장 형태의 프롬프트로 시작하고 싶다면 [일반 프롬프트 워크플로 목록](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/examples/workflows/PLAIN_PROMPTS.md)을 참고한다. 전체 탐색은 [워크플로 디렉터리](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/tree/main/examples/workflows)를 이용한다.

## 사용 시 확인할 점

- **실험 기능:** `Advanced`·`EXP`는 해당 예제와 설명을 함께 따라야 한다. 특정 샘플이 통과했다는 기록은 모든 소재와 GPU에서 같은 품질을 보장한다는 뜻이 아니다.
- **립싱크와 음색:** 정확한 성문 일치, 단어별 타이밍, 모든 얼굴과 노래에 대한 완전한 동기화는 보장하지 않는다.
- **장편 연결부:** 이중 샘플링의 연결부 색 변화 등 알려진 한계가 있다. 긴 결과는 전체 속도로 직접 확인해야 한다.
- **GPU 메모리:** 일부 16GB GPU 테스트 기록이 있어도 모든 해상도·길이·모델 조합에서 16GB 실행이 보장되지는 않는다.
- **가속 조합:** LoRA, 샘플러, attention 패치를 임의로 여러 개 겹치지 말고 예제의 조합과 [패치 공존 정책](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/PATCH_STACK_POLICY.md)을 확인한다.
- **선택형 후처리:** Topaz·DLSS는 별도 프로그램과 실행 환경이 필요하다. TAEH3는 근사 미리보기용이며 최종 영상 VAE나 오디오 모델의 대체물이 아니다.
- **Windows 경로:** `Filename too long` 오류가 나면 [짧은 경로와 복구 안내](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/WINDOWS_PATHS.md)를 확인한다.

위 한계와 기능별 조건은 [README](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/README_EN.md#important-limits) 및 [상세 가이드](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/README_DETAILS_EN.md)에 근거한다.

## 라이선스

노드 소스는 **GPL-3.0-or-later**이며, 모델과 외부 리소스는 각각의 별도 라이선스를 따른다. README는 Meridian 가중치에 MiniMax H3 Community License, Omega에 FAIR 비상업 연구 라이선스가 적용된다고 명시한다. 코드가 공개되어 있다는 이유만으로 모든 모델의 상업 이용이 허용되는 것은 아니다. [라이선스 안내](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/README_EN.md#licenses-and-documentation)

특히 저장소의 [기본 모델·OpenVDN 설명](https://github.com/T8mars/comfyui-minimax-h3-audio-T8/blob/main/docs/README_ComfyUI.md)은 해당 MiniMax H3 라이선스의 적용 지역에서 **한국·미국·영국·EU가 제외된다**고 안내한다. 한국에서 사용할 계획이라면 다운로드할 모델의 실제 라이선스 원문과 적용 범위를 먼저 확인해야 한다. 이는 노드 코드의 GPL과 구분되는 모델 사용 조건이다.

## 참고 포인트

이 저장소는 단순한 생성 노드 하나보다 **H3로 영상·오디오 제작 과정을 구성하는 예제와 도구 모음**으로 볼 만하다. 참조 소재와 음성을 활용한 짧은 영상에서 출발해, 장편·MV·카메라 연출로 확장할 때 참고 가치가 있다.

기능이 넓고 실험 경로가 많으므로, 처음부터 모든 가속·보정 기능을 켜기보다는 목적에 맞는 기본 워크플로 하나를 익히는 접근이 적합해 보인다. 이 평가는 문서와 코드 구조를 바탕으로 한 판단이다.

## 한줄 메모

> ComfyUI에서 MiniMax H3 영상·오디오 생성부터 립싱크와 장편 연출까지 연결할 수 있는 확장 노드 모음. 모델 조합, 실험 기능의 한계와 모델 라이선스 확인이 핵심이다.
