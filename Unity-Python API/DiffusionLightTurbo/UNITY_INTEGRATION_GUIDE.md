# Unity 통합 가이드

## 📋 목차

1. [서버 설정](#1-서버-설정)

2. [Unity 클라이언트 설정](#2-unity-클라이언트-설정)

3. [사용 방법](#3-사용-방법)

4. [문제 해결](#4-문제-해결)

  

---

  

## 1. 서버 설정

  

### 1.1 의존성 설치

  

```bash

# Conda 환경 생성 (선택적)

conda env create -f environment.yml

conda activate diffusionlight-turbo

  

# Python 패키지 설치 (Flask 포함)

pip install -r requirements.txt

```

  

### 1.2 모델 확인

  

처음 실행 시 Stable Diffusion 모델이 자동으로 다운로드됩니다 (~7GB).

사전에 다운로드하려면:

  

```bash

python -c "from diffusers import DiffusionPipeline; DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0')"

```

  

### 1.3 서버 실행

  

#### 개발 모드 (로컬)

  

```bash

python server.py

```

  

서버가 `http://localhost:5000`에서 실행됩니다.

  

#### 프로덕션 모드

  

```bash

# Gunicorn 사용 (권장)

pip install gunicorn

gunicorn -w 4 -b 0.0.0.0:5000 --timeout 600 server:app

  

# 또는 uWSGI

pip install uwsgi

uwsgi --http 0.0.0.0:5000 --wsgi-file server.py --callable app --processes 4

```

  

### 1.4 서버 테스트

  

```bash

# 헬스체크

curl http://localhost:5000/api/health

  

# 전체 워크플로우 테스트

python test_server.py example/1.jpg

```

  

---

  

## 2. Unity 클라이언트 설정

  

### 2.1 스크립트 추가

  

1. Unity 프로젝트를 엽니다

2. `Assets/Scripts` 폴더 생성 (없으면)

3. `HDRGenerator.cs` 파일을 `Assets/Scripts` 폴더에 복사

  

### 2.2 GameObject에 컴포넌트 추가

  

1. Hierarchy에서 빈 GameObject 생성 (이름: `HDRManager`)

2. `HDRGenerator` 스크립트를 GameObject에 추가

3. Inspector에서 설정:

   - **Server URL**: 서버 주소 입력 (예: `http://192.168.1.100:5000`)

   - **Capture Camera**: Main Camera 드래그 & 드롭

   - **Capture Width/Height**: 1024 (기본값)

  

### 2.3 UI 버튼 추가 (선택적)

  

UI 버튼으로 캡처를 트리거하려면:

  

1. Canvas 생성: `GameObject > UI > Canvas`

2. Button 생성: `GameObject > UI > Button`

3. Button 텍스트: "Generate HDR Light Probe"

4. `HDRGenerator` Inspector에서:

   - **Capture Button**: Button 연결

   - **Progress Bar**: Slider 연결 (선택적)

   - **Status Text**: Text 연결 (선택적)

  

### 2.4 스크립트에서 직접 호출

  

```csharp

// 다른 스크립트에서 HDR 생성 트리거

HDRGenerator hdrGen = FindObjectOfType<HDRGenerator>();

if (hdrGen != null)

{

    hdrGen.CaptureAndGenerate();

}

```

  

---

  

## 3. 사용 방법

  

### 3.1 기본 사용

  

1. Unity에서 Play 모드 실행

2. "Generate HDR Light Probe" 버튼 클릭

3. 진행 상황 확인 (약 30초 소요)

4. 완료되면 Skybox가 자동으로 업데이트 (옵션 활성화 시)

  

### 3.2 생성된 파일 확인

  

HDR 파일은 다음 위치에 저장됩니다:

  

- **Windows**: `C:\Users\{Username}\AppData\LocalLow\{CompanyName}\{ProductName}\HDR_Results\`

- **Mac**: `~/Library/Application Support/{CompanyName}/{ProductName}/HDR_Results/`

- **Android**: `/storage/emulated/0/Android/data/{com.company.product}/files/HDR_Results/`

  

Unity에서 경로 확인:

```csharp

Debug.Log(Application.persistentDataPath);

```

  

### 3.3 HDR을 Reflection Probe에 적용

  

```csharp

// HDRGenerator.cs 수정 또는 다른 스크립트에서

ReflectionProbe probe = FindObjectOfType<ReflectionProbe>();

if (probe != null)

{

    probe.mode = UnityEngine.Rendering.ReflectionProbeMode.Custom;

    probe.customBakedTexture = hdrTexture; // Cubemap으로 변환 필요

}

```

  

### 3.4 커스텀 워크플로우

  

```csharp

// 특정 위치/각도에서 캡처

Camera tempCamera = new GameObject("TempCamera").AddComponent<Camera>();

tempCamera.transform.position = targetPosition;

tempCamera.transform.rotation = targetRotation;

  

HDRGenerator hdrGen = GetComponent<HDRGenerator>();

// captureCamera를 tempCamera로 변경

hdrGen.CaptureAndGenerate();

```

  

---

  

## 4. 문제 해결

  

### 4.1 서버 연결 실패

  

**증상**: `Server health check failed`

  

**해결 방법**:

1. 서버가 실행 중인지 확인: `curl http://localhost:5000/api/health`

2. 방화벽 설정 확인

3. Unity Inspector에서 Server URL 확인

4. 네트워크 연결 확인 (외부 서버 사용 시)

  

### 4.2 업로드 실패

  

**증상**: `Upload failed: 400 Bad Request`

  

**해결 방법**:

1. 이미지 크기 확인 (최대 10MB)

2. 이미지 형식 확인 (PNG, JPG만 허용)

3. 서버 로그 확인: `python server.py`에서 에러 메시지 확인

  

### 4.3 처리 시간 초과

  

**증상**: `Timeout: Processing took too long`

  

**해결 방법**:

1. 서버 GPU 메모리 확인 (최소 8GB VRAM 권장)

2. 다른 작업이 실행 중인지 확인

3. `HDRGenerator.cs`에서 타임아웃 늘리기:

   ```csharp

   int maxAttempts = 180; // 6분으로 증가

   ```

  

### 4.4 HDR 파일 로드 실패

  

**증상**: `Failed to load HDR texture`

  

**해결 방법**:

1. Unity 플랫폼 설정 확인:

   - Edit > Project Settings > Player

   - "Allow unsafe code" 체크 (필요 시)

2. EXR 지원 확인:

   - Unity 2020.1 이상 권장

3. 수동으로 파일 Import:

   - EXR 파일을 Unity Assets 폴더로 복사

   - Inspector에서 Texture Type을 "Default" 또는 "Cubemap"으로 설정

  

### 4.5 GPU 메모리 부족

  

**증상**: 서버 로그에 `CUDA out of memory`

  

**해결 방법**:

1. `inpaint.py` 옵션 조정:

   ```bash

   # server.py의 run_pipeline 함수에서

   "--offload"  # CPU offload 활성화

   "--denoising_step", "20"  # 스텝 수 감소 (품질 저하)

   ```

2. 동시 요청 수 제한

3. 더 강력한 GPU 사용

  

### 4.6 안드로이드/iOS 빌드 문제

  

**증상**: 모바일에서 실행 안 됨

  

**해결 방법**:

1. Android: 인터넷 권한 추가

   - Edit > Project Settings > Player > Android

   - "Internet Access" = "Require"

2. iOS: App Transport Security 설정

   - Info.plist에 추가:

   ```xml

   <key>NSAppTransportSecurity</key>

   <dict>

       <key>NSAllowsArbitraryLoads</key>

       <true/>

   </dict>

   ```

3. HTTPS 사용 권장 (프로덕션)

  

---

  

## 5. 고급 설정

  

### 5.1 서버 설정 커스터마이즈

  

`server.py` 수정:

  

```python

# 최대 파일 크기 변경

MAX_FILE_SIZE = 20 * 1024 * 1024  # 20MB

  

# 포트 변경

app.run(port=8080)

  

# 파일 보관 기간 변경

cutoff_time = datetime.now() - timedelta(hours=48)  # 48시간

```

  

### 5.2 파이프라인 파라미터 조정

  

`server.py`의 `run_pipeline` 함수에서:

  

```python

# 품질 향상 (느림)

cmd_inpaint = [

    "python", "inpaint.py",

    "--denoising_step", "50",  # 30 -> 50

    "--ball_size", "512",  # 더 큰 크롬볼

    ...

]

  

# 속도 우선 (품질 저하)

cmd_inpaint = [

    "python", "inpaint.py",

    "--denoising_step", "20",  # 30 -> 20

    "--algorithm", "turbo_pred",  # 더 빠른 알고리즘

    ...

]

```

  

### 5.3 캐싱 구현

  

동일한 이미지에 대한 재처리 방지:

  

```python

import hashlib

  

def get_image_hash(image_path):

    with open(image_path, 'rb') as f:

        return hashlib.sha256(f.read()).hexdigest()

  

# run_pipeline 전에 캐시 확인

image_hash = get_image_hash(input_path)

cached_result = check_cache(image_hash)

if cached_result:

    return cached_result

```

  

### 5.4 Docker 배포

  

```bash

# Dockerfile 빌드

docker build -t diffusionlight-turbo .

  

# 실행

docker run --gpus all -p 5000:5000 -v $(pwd)/server_data:/app/server_data diffusionlight-turbo

```

  

---

  

## 6. API 레퍼런스

  

### POST /api/generate-hdr

  

HDR 생성 요청

  

**Request:**

- Method: `POST`

- Content-Type: `multipart/form-data`

- Body: `image` (파일)

  

**Response:**

```json

{

  "job_id": "550e8400-e29b-41d4-a716-446655440000",

  "status": "accepted",

  "message": "Processing started"

}

```

  

### GET /api/status/{job_id}

  

작업 상태 조회

  

**Response:**

```json

{

  "status": "processing",

  "progress": 45,

  "current_step": "Converting to environment map",

  "created_at": "2025-10-14T10:30:00"

}

```

  

### GET /api/download/{job_id}

  

HDR 파일 다운로드

  

**Response:**

- Content-Type: `image/x-exr`

- Body: EXR 파일 데이터

  

### GET /api/health

  

서버 헬스체크

  

**Response:**

```json

{

  "status": "ok",

  "timestamp": "2025-10-14T10:30:00",

  "active_jobs": 2

}

```

  

---

  

## 7. 성능 최적화 팁

  

1. **이미지 크기**: 정확히 1024x1024로 전처리 (Unity에서)

2. **동시 요청**: GPU당 1-2개 제한

3. **네트워크**: 로컬 네트워크 사용 (지연시간 최소화)

4. **캐싱**: 동일한 장면은 캐시 사용

5. **압축**: 네트워크가 느리면 JPEG 사용 (품질 저하)

  

---

  

## 8. 라이선스 및 크레딧

  

- **DiffusionLight-Turbo**: 원저자 라이선스 참조

- **Stable Diffusion XL**: CreativeML OpenRAIL++-M License

- **Flask**: BSD License

  

상업적 사용 시 각 라이선스를 확인하세요.

  

---

  

## 9. 추가 자료

  

- [DiffusionLight-Turbo 논문](https://arxiv.org/abs/2507.01305)

- [프로젝트 페이지](https://diffusionlight.github.io/turbo/)

- [Unity Networking 문서](https://docs.unity3d.com/ScriptReference/Networking.UnityWebRequest.html)

- [Flask 문서](https://flask.palletsprojects.com/)

  

---

  

## 📧 지원

  

문제가 발생하면:

1. 서버 로그 확인 (`python server.py` 출력)

2. Unity Console 로그 확인

3. GitHub Issues에 리포트

4. `test_server.py`로 서버 독립 테스트

  

Happy coding! 🚀