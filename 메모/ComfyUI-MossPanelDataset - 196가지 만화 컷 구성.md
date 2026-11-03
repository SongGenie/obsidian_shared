---
title: ComfyUI-MossPanelDataset - 196가지 만화 컷 구성
created: 2026-11-03
status: 정리
tags: [메모, ComfyUI, MOSSImage, AI만화, AI웹툰, 스토리보드, 오픈소스]
---

# ComfyUI-MossPanelDataset - 196가지 만화 컷 구성

- **GitHub:** [sepiablue-ai/ComfyUI-MossPanelDataset](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset)
- **공유 원문:** [Kamimoto X 게시물](https://x.com/sep_is_heim/status/2117089771948478826)
- **주제:** MOSS-Image / 만화 페이지 생성 / 컷 레이아웃 / 스토리보드
- **확인일:** 2026-11-03
- **정리 기준:** 공식 저장소 README 확인. 직접 설치·생성 테스트는 하지 않음.

## 요약

**ComfyUI에서 만화 컷 배치를 미리보기로 선택하고, 인물·장면·대사를 입력해 MOSS-Image로 만화 페이지를 생성하는 커스텀 노드**다.

2~6컷으로 구성된 **196가지 레이아웃**을 제공한다. 노드가 MOSS용 프롬프트를 구성하므로 기본 사용에서는 JSON이나 컷 좌표를 직접 작성할 필요가 없다. 레이아웃마다 별도의 워크플로를 받을 필요도 없다. [공식 README](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#readme)

## 주요 기능

- **레이아웃 선택:** 미리보기 이미지로 일반 직선형·대각선형·특수형 배치를 고르고, 컷 수·종류·이름으로 필터링하거나 즐겨찾기에 등록한다.
- **컷 입력 자동 조정:** 배치를 바꾸면 컷 입력 노드와 연결이 자동으로 늘거나 줄어든다. 줄인 컷의 입력값은 보관했다가 컷 수를 다시 늘리면 복원한다.
- **인물·장면·대사 입력:** 공통 인물의 외형과 컷별 상황, 등장인물, 화자와 대사를 설정한다.
- **대사 원문 전달:** 대사는 표시할 언어로 입력한다. 번역이나 추가 LLM을 사용하지 않는다. 일본어 입력도 그대로 전달하지만 글자 재현의 정확성을 보장하지는 않는다.
- **빈 컷 생성:** 인물·장면·대사를 제외하고 테두리만 생성하는 모드를 제공한다.
- **로컬 카탈로그:** 미리보기와 배치 데이터가 포함되어 설치 후 카탈로그 탐색에는 외부 서비스 접속이 필요 없다.

노드 UI는 일본어이며, 인물 외형과 장면 설명은 영어 입력을 안내한다. [기능·사용법](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#features)

## 레이아웃 구성

| 페이지 컷 수 | 레이아웃 수 |
| --- | ---: |
| 2컷 | 38 |
| 3컷 | 39 |
| 4컷 | 40 |
| 5컷 | 40 |
| 6컷 | 39 |
| 합계 | 196 |

미리보기는 MOSS가 생성한 빈 컷 이미지다. 노드는 좌표와 설명으로 생성 모델을 유도하며, 미리보기의 테두리를 결과 이미지에 그대로 복사하거나 합성하는 방식은 아니다. [레이아웃 구성](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#bundled-layouts)

## 설치와 모델 준비

Python 3.10 이상과 **네이티브 MOSS-Image 지원이 있는 ComfyUI**가 필요하다. 개발자는 ComfyUI v0.42.0·Python 3.13에서 확인했다. `CLIPLoader`에 `moss_image` 유형이 없거나 `EmptyFlux2LatentImage` 노드가 없다면 ComfyUI 업데이트가 필요하다.

ComfyUI 폴더에서 설치한다.

```powershell
cd custom_nodes
git clone https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset.git
```

`data`, `images`, `web`을 포함한 전체 저장소가 필요하다. 노드 전용 추가 Python 패키지나 설치 스크립트는 없으며, 확인 시점에는 Comfy Registry에 등록되지 않았다.

동봉 워크플로가 사용하는 파일은 다음과 같다. 경로는 ComfyUI 기준이다.

| 모델 파일 | 배치 폴더 |
| --- | --- |
| `moss_image_sft_int8_convrot.safetensors` | `models/diffusion_models/` |
| `qwen3.5_9b_int8_convrot.safetensors` | `models/text_encoders/` |
| `flux2-vae.safetensors` | `models/vae/` |

가중치는 동봉되거나 자동 다운로드되지 않는다. [Comfy-Org 모델 페이지](https://huggingface.co/Comfy-Org/MOSS-Image)와 [MOSS 공식 ComfyUI 안내](https://github.com/OpenMOSS/MOSS-Image/blob/main/comfyui/README.md)를 참고해 준비하고, 로더에서 파일과 `moss_image` 유형을 지정한다. 설치 후 ComfyUI를 재시작하고 브라우저를 새로고침한다. [설치·환경 안내](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#installation)

## 기본 사용 흐름

1. 동봉된 [make_manga.json](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset/blob/main/example_workflows/make_manga.json)을 ComfyUI에 끌어다 놓거나 템플릿에서 연다.
2. 미리보기에서 원하는 컷 구성을 선택한다.
3. 공통 인물 설정에 이름과 영어 외형 설명을 입력한다.
4. 각 컷의 장면을 영어로 쓰고 등장인물을 선택한다.
5. 화자와 대사를 입력한다. 무언 컷은 대사를 비우고, 배경만 필요한 컷은 인물 없음을 선택한다.
6. 실행 후 컷 수·인물·대사·말풍선을 확인하고 워크플로를 저장한다.

빈 틀만 필요하면 출력 항목을 `空のコマ枠`로 바꾼다. 프롬프트를 직접 확인·수정하려면 별도 [make_manga_edit_prompt.json](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset/blob/main/example_workflows/make_manga_edit_prompt.json)을 사용한다. 이 편집 모드에서는 유효한 JSON 구조를 유지해야 한다.

인물과 대사 등 작업 내용은 ComfyUI 워크플로에 저장한다. 즐겨찾기는 브라우저 로컬 저장소에 기록되어 다른 브라우저로 자동 이동하지 않는다. [사용법](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#usage)

## 실행 조건과 한계

개발자는 원본 데이터셋을 **Windows·RTX 3060 12GB**에서 생성했다고 설명한다. 동봉 설정은 **1024×1536, 25스텝, CFG 2.5, `er_sde` / `simple`, DMD LoRA 없음**이다. 이는 해당 환경의 사례이며 모든 GPU에서 같은 메모리·속도를 보장하는 수치는 아니다.

- 공통 캐릭터는 **2명**, 컷당 최대 **2명·대사 2개**다.
- 컷 형태·비율·개수가 생성마다 달라질 수 있다. 대각선·특수형도 다각형 마스크로 강제하는 방식이 아니다.
- 인물과 말풍선은 단순한 고정 위치를 사용한다. 장면별 최적 배치나 말풍선 꼬리 방향을 추론하지 않는다.
- 글자 오타·깨짐, 인물 혼동, 컷 수 변화가 발생할 수 있다. 생성 후 테두리와 문자를 덧씌워 자동 보정하지 않는다.
- 공통 외형 설정을 반복해도 여러 페이지의 캐릭터 일관성이 보장되지는 않는다.

실행 조건과 제약은 [README 환경 안내](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#requirements-and-models) 및 [제한 사항](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#limitations)을 참고한다.

## 활용 가능성

짧은 만화, 교육·홍보 콘텐츠의 만화 시안, 영상 스토리보드의 초기 컷 구성에 활용할 만하다. 빈 컷 모드는 페이지 배치를 먼저 탐색할 때 유용해 보인다. 완성 원고로 사용하기 전에는 컷 흐름과 문자, 인물 일관성을 별도로 검수하는 과정이 필요하다.

프로젝트 자체 코드·레이아웃 데이터·동봉 미리보기는 **MIT 라이선스**다. 모델과 ComfyUI 등 외부 구성요소에는 각각의 라이선스가 적용된다. [라이선스 안내](https://github.com/sepiablue-ai/ComfyUI-MossPanelDataset#license-and-credits)

## 한줄 메모

> 196가지 컷 배치를 골라 인물·장면·대사로 만화 페이지를 생성하는 MOSS-Image용 ComfyUI 노드. 컷 구성과 시안 제작을 간소화하며, 레이아웃 재현·문자·인물 일관성은 결과 검수가 필요하다.
