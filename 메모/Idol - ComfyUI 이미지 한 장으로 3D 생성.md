---
title: Idol - ComfyUI 이미지 한 장으로 3D 생성
created: 2026-11-03
status: 정리
tags: [메모, Idol, ComfyUI, TripoSplat, ImageTo3D, GaussianSplatting, AI모델]
---

# Idol - ComfyUI 이미지 한 장으로 3D 생성

- **ComfyUI 패키지:** [Comfy-Org/Idol](https://huggingface.co/Comfy-Org/Idol)
- **원본 모델:** [speridlabs/idol](https://huggingface.co/speridlabs/idol)
- **SDK:** [speridlabs/idol-sdk](https://github.com/speridlabs/idol-sdk)
- **주제:** 단일 이미지 기반 3D 생성 / ComfyUI / 3D Gaussian Splatting
- **확인일:** 2026-11-03

## 요약

**Idol은 사진이나 AI 생성 이미지 한 장으로 3D Gaussian Splat 오브젝트를 만드는 Sperid Labs의 모델**이다. 입력 이미지에 보이지 않는 옆면과 뒷면도 추정해 생성하며, 원본 SDK는 결과를 표준 3DGS `.ply` 파일로 저장한다. [원본 모델 설명](https://huggingface.co/speridlabs/idol)

공유된 소식의 핵심은 기존 Idol 모델을 **ComfyUI에서 사용할 수 있도록 Comfy-Org가 재구성한 패키지**다. 공유 자료에 따르면 TripoSplat을 파인튜닝한 모델이며, 기존 TripoSplat 워크플로에서 모델을 교체해 활용할 수 있다. 원본 SDK에서도 TripoSplat 기반임을 밝힌다. [ComfyUI 패키지](https://huggingface.co/Comfy-Org/Idol) · [SDK 설명](https://github.com/speridlabs/idol-sdk#acknowledgements)

> 확인 범위: 원본 모델 카드와 SDK README는 직접 확인했다. Comfy-Org 페이지는 조사 도구에서 열리지 않아, 패키지의 호환성과 아래 파일 배치는 사용자가 제공한 자료를 기준으로 정리했다. 직접 실행한 후기는 아니다.

## 핵심 특징

- **입력:** 단일 오브젝트의 사진, 렌더 이미지 또는 AI 생성 이미지.
- **출력:** 최대 **1,048,576개 Gaussian**으로 구성된 3DGS. 원본 SDK 기본값은 262,144개다.
- **전처리:** 원본 SDK는 배경 제거와 오브젝트 중심 크롭을 수행한다.
- **메모리:** 개발사는 전체 요청의 최대 GPU 메모리를 약 **7.2GB**로 안내한다. ComfyUI에서 다른 모델을 함께 사용할 때의 실제 사용량은 달라질 수 있다.
- **속도:** 설정과 GPU에 따라 달라진다. 원본 공개 표의 50스텝·262,144 Gaussian 조건에서 RTX 4090은 약 19.1초로, 모든 환경에서 수 초 이내 처리가 보장되는 것은 아니다.

수치와 기본 동작은 [원본 모델 카드](https://huggingface.co/speridlabs/idol)에 근거한다.

## ComfyUI 모델 파일 구성

공유 자료에서 안내한 배치 경로다. `ComfyUI` 폴더 기준이며, 실제 사용 전 [패키지 페이지](https://huggingface.co/Comfy-Org/Idol)의 최신 안내와 대조한다.

| 파일 | 배치 경로 |
| --- | --- |
| Idol 생성 모델 | `models/diffusion_models/idol_fp16.safetensors` |
| DINOv3 이미지 인코더 | `models/clip_vision/dino_v3_vit_h_bf16.safetensors` |
| FLUX.2 VAE | `models/vae/flux2-vae.safetensors` |
| Idol 디코더 | `models/vae/idol_decoder_fp16.safetensors` |

활용 흐름은 **입력 이미지 준비 → 호환 TripoSplat 워크플로에 모델 지정 → 3D 생성 → Gaussian Splat 뷰어에서 여러 방향 확인**으로 정리할 수 있다. 실제 저장 형식과 저장 노드 구성은 사용하는 ComfyUI 워크플로에서 확인한다.

## 3DGS와 일반 메시의 차이

3D Gaussian Splat은 공간에 배치된 Gaussian으로 외형을 표현하는 방식이다. 일반적인 삼각형 폴리곤 메시와 구조가 다르므로, `.ply`로 저장된다고 해서 바로 메시 편집·리깅·3D 프린팅에 사용할 수 있는 것은 아니다. 후속 작업에는 해당 표현을 지원하는 도구나 별도 변환 과정이 필요하다.

## 활용 가능성

- 제품 이미지나 캐릭터 소품을 여러 방향에서 살펴보는 시각화 시안.
- 배경 오브젝트와 3D 콘셉트의 빠른 프로토타입 제작.
- ComfyUI 이미지 생성과 연결한 **이미지 생성 → 3D 변환** 제작 흐름.

위 항목은 활용 아이디어다. 보이지 않는 뒷면은 실제 측정값이 아니라 모델의 추정이므로, 정확한 치수와 형상 복원이 필요한 작업에는 별도 검증이 필요하다.

## 참고 사항

원본 SDK는 Python 3.10 이상, PyTorch 2.5 이상과 CUDA NVIDIA GPU 환경을 안내한다. DINOv3와 FLUX.2-dev의 접근 조건 동의 및 Hugging Face 인증도 요구한다. 이는 **원본 SDK 설치 조건**이며 ComfyUI 패키지 설치 절차와 구분해서 확인한다. Idol의 Apache-2.0 표기와 별개로 함께 사용하는 인코더·VAE의 이용 조건도 확인한다. [SDK 설치 안내](https://github.com/speridlabs/idol-sdk#install) · [원본 모델](https://huggingface.co/speridlabs/idol)

## 한줄 메모

> 이미지 한 장을 3D Gaussian Splat으로 바꾸는 Idol의 ComfyUI 활용 소식. 빠른 3D 시안 제작에 참고할 만하며, 메시와의 차이와 추정된 뒷면의 정확도를 확인해야 한다.

## 원문 링크

- [Comfy-Org Idol 패키지](https://huggingface.co/Comfy-Org/Idol)
- [Sperid Labs Idol 원본 모델](https://huggingface.co/speridlabs/idol)
- [Idol SDK](https://github.com/speridlabs/idol-sdk)
- [공유된 X 게시물](https://x.com/aiaicreate/status/2117169907473215844)
