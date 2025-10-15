# Unity ↔ Python 서버 통합 (빠른 시작)

  

Unity에서 DiffusionLight-Turbo를 사용하여 실시간으로 HDR 라이트 프로브를 생성하는 시스템입니다.

  

## 🚀 빠른 시작 (3단계)

  

### 1️⃣ 서버 실행

  

```bash

# 의존성 설치

pip install flask flask-cors

  

# 서버 시작

python server.py

```

  

### 2️⃣ Unity 설정

  

1. `UnityClient/HDRGenerator.cs`를 Unity 프로젝트에 복사

2. GameObject에 스크립트 추가

3. Inspector에서 Server URL 설정: `http://localhost:5000`

  

### 3️⃣ 사용

  

Unity에서 버튼 클릭 또는 코드로 호출:

```csharp

GetComponent<HDRGenerator>().CaptureAndGenerate();

```

  

약 30초 후 HDR이 자동으로 적용됩니다! 🎉

  

---

  

## 📁 프로젝트 구조

  

```

DiffusionLight-Turbo/

├── server.py                          # Flask 서버 (메인)

├── test_server.py                     # 서버 테스트 스크립트

├── inpaint.py                         # 크롬볼 인페인팅

├── ball2envmap.py                     # 환경맵 변환

├── exposure2hdr.py                    # HDR 합성

├── Dockerfile                         # Docker 이미지

├── docker-compose.yml                 # Docker Compose 설정

├── requirements.txt                   # Python 의존성

├── UnityClient/

│   └── HDRGenerator.cs                # Unity 클라이언트 스크립트

├── UNITY_INTEGRATION_GUIDE.md         # 상세 가이드

└── UNITY_SERVER_INTEGRATION_PLAN.md   # 통합 계획서

```

  

---

  

## 📖 문서

  

- **[통합 계획서](UNITY_SERVER_INTEGRATION_PLAN.md)**: 전체 아키텍처, 설계, 배포 전략

- **[통합 가이드](UNITY_INTEGRATION_GUIDE.md)**: 단계별 설정 방법, 문제 해결

  

---

  

## 🧪 테스트

  

### 서버 테스트

```bash

# 헬스체크

curl http://localhost:5000/api/health

  

# 전체 워크플로우 테스트

python test_server.py example/1.jpg

```

  

### Unity 테스트

1. Unity Play 모드 실행

2. Console에서 로그 확인

3. 약 30초 후 결과 확인

  

---

  

## 🐳 Docker 배포

  

```bash

# 빌드 및 실행

docker-compose up -d

  

# 로그 확인

docker-compose logs -f

  

# 중지

docker-compose down

```

  

---

  

## ⚙️ 요구사항

  

### 서버

- **GPU**: NVIDIA GPU (VRAM 8GB+, RTX 3090 권장)

- **Python**: 3.8+

- **CUDA**: 11.8

- **OS**: Linux/Windows

  

### Unity

- **버전**: 2020.1 이상

- **플랫폼**: Windows, Mac, Linux, Android, iOS

- **.NET**: Standard 2.0+

  

---

  

## 🎯 주요 기능

  

✅ **빠른 처리**: ~30초 (기존 30분 대비 60배 빠름)  

✅ **간단한 통합**: REST API, 코드 몇 줄  

✅ **실시간 진행 표시**: 상태 폴링  

✅ **자동 적용**: Skybox/Reflection Probe 자동 업데이트  

✅ **확장 가능**: Docker, Kubernetes 지원  

  

---

  

## 📊 워크플로우

  

```

Unity (클라이언트)                    Python 서버

     │                                    │

     ├─ 1. 스크린샷 캡처 (1024x1024)     │

     │                                    │

     ├─ 2. POST /api/generate-hdr ───────>│

     │    (이미지 업로드)                 │

     │                                    ├─ inpaint.py (크롬볼)

     │                                    ├─ ball2envmap.py (환경맵)

     │                                    └─ exposure2hdr.py (HDR)

     │                                    │

     ├─ 3. GET /api/status/{job_id} <────┤

     │    (2초마다 폴링)                  │

     │                                    │

     ├─ 4. GET /api/download/{job_id} <──┤

     │    (HDR 다운로드)                  │

     │                                    │

     └─ 5. Skybox 적용                   │

```

  

---

  

## 🔧 API 엔드포인트

  

| 메서드 | 경로 | 설명 |

|--------|------|------|

| GET | `/api/health` | 서버 상태 확인 |

| POST | `/api/generate-hdr` | HDR 생성 요청 |

| GET | `/api/status/{job_id}` | 작업 상태 조회 |

| GET | `/api/download/{job_id}` | HDR 다운로드 |

| GET | `/api/jobs` | 모든 작업 목록 |

  

---

  

## ⚠️ 주의사항

  

1. **GPU 메모리**: 최소 8GB VRAM 필요

2. **처리 시간**: 서버 부하에 따라 30초~1분

3. **파일 크기**: EXR 파일은 5-10MB

4. **동시 처리**: GPU당 1-2개 제한 권장

5. **라이선스**: 상업적 사용 시 Stable Diffusion 라이선스 확인

  

---

  

## 🐛 문제 해결

  

### 서버 연결 안 됨

```bash

# 방화벽 확인

sudo ufw allow 5000

  

# 서버 로그 확인

python server.py

```

  

### GPU 메모리 부족

```python

# server.py에서 CPU offload 활성화

"--offload"

```

  

### Unity EXR 로드 실패

- Unity 2020.1+ 사용

- 플랫폼 설정에서 "Allow unsafe code" 활성화

  

더 많은 문제 해결 방법은 [통합 가이드](UNITY_INTEGRATION_GUIDE.md#4-문제-해결)를 참조하세요.

  

---

  

## 📈 성능

  

| 항목 | 값 |

|------|-----|

| 처리 시간 | ~30초 |

| GPU 메모리 | 8-12GB |

| HDR 해상도 | 512x256 (기본) |

| 입력 해상도 | 1024x1024 |

| EXR 파일 크기 | 5-10MB |

  

---

  

## 🎓 학습 자료

  

- [DiffusionLight-Turbo 논문](https://arxiv.org/abs/2507.01305)

- [프로젝트 페이지](https://diffusionlight.github.io/turbo/)

- [Colab 데모](https://colab.research.google.com/drive/1UcSp9mj77ZXAyTCvkcXVvC3DYznEyLwZ)

  

---

  

## 📄 라이선스

  

이 프로젝트는 원저자의 라이선스를 따릅니다. 상업적 사용 시:

- DiffusionLight-Turbo 라이선스 확인

- Stable Diffusion XL 라이선스 확인 (CreativeML OpenRAIL++-M)

  

---

  

## 🤝 기여

  

버그 리포트, 기능 제안, Pull Request를 환영합니다!

  

---

  

## 📞 지원

  

- GitHub Issues

- Email: (프로젝트 이메일)

  

---

  

**Made with ❤️ for Unity Developers**