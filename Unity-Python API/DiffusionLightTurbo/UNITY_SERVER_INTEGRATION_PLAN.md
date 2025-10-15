# Unity ↔ Python 서버 통합 계획서

  

## 📋 개요

  

DiffusionLight-Turbo를 Unity 애플리케이션과 통합하여 실시간 HDR 라이트 프로브 생성 서비스를 구축하기 위한 상세 계획입니다.

  

### 현재 파이프라인

1. `inpaint.py` - 크롬볼 인페인팅 (3개 노출값: 0, -2.5, -5 EV)

2. `ball2envmap.py` - 크롬볼 → 환경맵 변환

3. `exposure2hdr.py` - LDR 이미지들 → HDR 합성

  

### 처리 시간

- DiffusionLight-Turbo: **~30초** (단일 이미지)

- DiffusionLight (기존): ~30분

  

---

  

## 🏗️ 아키텍처 설계

  

### 1. 전체 구조

  

```

┌─────────────┐         HTTP/REST API          ┌──────────────┐

│   Unity     │ ─────────────────────────────> │ Python       │

│   Client    │                                 │ Flask Server │

│             │ <───────────────────────────── │              │

└─────────────┘         HDR File               └──────────────┘

                                                       │

                                                       ▼

                                                ┌──────────────┐

                                                │  Pipeline    │

                                                │  1. inpaint  │

                                                │  2. ball2env │

                                                │  3. hdr      │

                                                └──────────────┘

```

  

### 2. 통신 방식

  

**선택지:**

- ✅ **REST API** (권장): 구현 간단, Unity UnityWebRequest 사용

- WebSocket: 실시간 진행상황 필요시

- gRPC: 고성능 필요시

  

**선택 이유:**

- Unity에서 HTTP 요청 쉽게 구현 가능

- 비동기 처리 적합 (처리 시간 30초)

- 디버깅 및 테스트 용이

  

---

  

## 🔧 구현 계획

  

### Phase 1: Python 서버 구축 (Flask/FastAPI)

  

#### 1.1 API 엔드포인트 설계

  

```python

# 주요 엔드포인트

POST /api/generate-hdr

- Input: 이미지 파일 (PNG/JPG, 1024x1024)

- Output: job_id

  

GET /api/status/{job_id}

- Output: { status: "pending|processing|completed|failed", progress: 0-100 }

  

GET /api/download/{job_id}

- Output: HDR 파일 (.exr) + 메타데이터

  

POST /api/generate-hdr-sync (선택적)

- Input: 이미지 파일

- Output: HDR 파일 (동기식, 30초 대기)

```

  

#### 1.2 비동기 작업 큐

```python

# Celery 또는 Python multiprocessing 사용

- 작업 큐: Redis/RabbitMQ

- Worker: DiffusionLight 파이프라인 실행

- 동시 처리: GPU 메모리에 따라 1-2개

```

  

#### 1.3 파일 관리

```

uploads/          # 업로드된 원본 이미지

  └── {job_id}/

      └── input.png

  

processing/       # 중간 결과물

  └── {job_id}/

      ├── raw/

      ├── square/

      ├── envmap/

      └── hdr/

  

results/          # 최종 결과

  └── {job_id}/

      ├── result.exr

      └── metadata.json

  

# 자동 정리: 24시간 후 삭제

```

  

### Phase 2: Unity 클라이언트 구현

  

#### 2.1 이미지 캡처

```csharp

// Unity에서 스크린샷 캡처

Texture2D CaptureScreenshot()

{

    // 방법 1: RenderTexture 사용 (권장)

    RenderTexture rt = new RenderTexture(1024, 1024, 24);

    camera.targetTexture = rt;

    camera.Render();

    Texture2D screenshot = new Texture2D(1024, 1024, TextureFormat.RGB24, false);

    RenderTexture.active = rt;

    screenshot.ReadPixels(new Rect(0, 0, 1024, 1024), 0, 0);

    screenshot.Apply();

    return screenshot;

}

```

  

#### 2.2 서버 통신

```csharp

IEnumerator UploadAndGenerateHDR(Texture2D image)

{

    // 1. 이미지를 PNG로 인코딩

    byte[] imageBytes = image.EncodeToPNG();

    // 2. Multipart form 생성

    WWWForm form = new WWWForm();

    form.AddBinaryData("image", imageBytes, "capture.png", "image/png");

    // 3. 업로드 및 job_id 받기

    using (UnityWebRequest request = UnityWebRequest.Post(serverUrl + "/api/generate-hdr", form))

    {

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)

        {

            JobResponse response = JsonUtility.FromJson<JobResponse>(request.downloadHandler.text);

            string jobId = response.job_id;

            // 4. 상태 폴링

            yield return StartCoroutine(PollJobStatus(jobId));

        }

    }

}

  

IEnumerator PollJobStatus(string jobId)

{

    while (true)

    {

        using (UnityWebRequest request = UnityWebRequest.Get(serverUrl + "/api/status/" + jobId))

        {

            yield return request.SendWebRequest();

            StatusResponse status = JsonUtility.FromJson<StatusResponse>(request.downloadHandler.text);

            if (status.status == "completed")

            {

                yield return StartCoroutine(DownloadHDR(jobId));

                break;

            }

            else if (status.status == "failed")

            {

                Debug.LogError("HDR generation failed");

                break;

            }

        }

        yield return new WaitForSeconds(2f); // 2초마다 폴링

    }

}

  

IEnumerator DownloadHDR(string jobId)

{

    using (UnityWebRequest request = UnityWebRequest.Get(serverUrl + "/api/download/" + jobId))

    {

        yield return request.SendWebRequest();

        if (request.result == UnityWebRequest.Result.Success)

        {

            // EXR 파일 저장 또는 직접 로드

            byte[] exrData = request.downloadHandler.data;

            SaveOrLoadHDR(exrData);

        }

    }

}

```

  

#### 2.3 HDR 처리

```csharp

// Unity에서 EXR 로드

void SaveOrLoadHDR(byte[] exrData)

{

    // 파일로 저장

    string path = Application.persistentDataPath + "/lightprobe.exr";

    File.WriteAllBytes(path, exrData);

    // Unity Cubemap/Texture2D로 로드

    Texture2D hdrTexture = new Texture2D(2, 2);

    hdrTexture.LoadImage(exrData); // EXR 자동 지원

    // Skybox 또는 Reflection Probe에 적용

    RenderSettings.skybox.SetTexture("_Tex", hdrTexture);

}

```

  

### Phase 3: 서버 코드 작성

  

#### 3.1 Flask 서버 예시

```python

# server.py

from flask import Flask, request, jsonify, send_file

from werkzeug.utils import secure_filename

import uuid

import os

import threading

from pathlib import Path

  

app = Flask(__name__)

  

# 작업 상태 저장

jobs = {}  # {job_id: {"status": "pending", "progress": 0}}

  

def run_pipeline(job_id, input_path):

    """백그라운드에서 파이프라인 실행"""

    try:

        jobs[job_id]["status"] = "processing"

        jobs[job_id]["progress"] = 10

        # 디렉토리 설정

        base_dir = f"processing/{job_id}"

        output_dir = f"{base_dir}/output"

        # 1. Inpaint

        os.system(f"python inpaint.py --dataset {input_path} --output_dir {output_dir}")

        jobs[job_id]["progress"] = 50

        # 2. Ball to envmap

        os.system(f"python ball2envmap.py --ball_dir {output_dir}/square --envmap_dir {output_dir}/envmap")

        jobs[job_id]["progress"] = 75

        # 3. Exposure to HDR

        os.system(f"python exposure2hdr.py --input_dir {output_dir}/envmap --output_dir {output_dir}/hdr")

        jobs[job_id]["progress"] = 95

        # 결과 이동

        result_dir = f"results/{job_id}"

        os.makedirs(result_dir, exist_ok=True)

        # HDR 파일 복사

        hdr_file = list(Path(f"{output_dir}/hdr").glob("*.exr"))[0]

        os.system(f"cp {hdr_file} {result_dir}/result.exr")

        jobs[job_id]["status"] = "completed"

        jobs[job_id]["progress"] = 100

    except Exception as e:

        jobs[job_id]["status"] = "failed"

        jobs[job_id]["error"] = str(e)

  

@app.route('/api/generate-hdr', methods=['POST'])

def generate_hdr():

    if 'image' not in request.files:

        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']

    job_id = str(uuid.uuid4())

    # 파일 저장

    upload_dir = f"uploads/{job_id}"

    os.makedirs(upload_dir, exist_ok=True)

    input_path = f"{upload_dir}/input.png"

    file.save(input_path)

    # 작업 등록 및 백그라운드 실행

    jobs[job_id] = {"status": "pending", "progress": 0}

    thread = threading.Thread(target=run_pipeline, args=(job_id, upload_dir))

    thread.start()

    return jsonify({"job_id": job_id}), 202

  

@app.route('/api/status/<job_id>', methods=['GET'])

def get_status(job_id):

    if job_id not in jobs:

        return jsonify({"error": "Job not found"}), 404

    return jsonify(jobs[job_id])

  

@app.route('/api/download/<job_id>', methods=['GET'])

def download_hdr(job_id):

    if job_id not in jobs or jobs[job_id]["status"] != "completed":

        return jsonify({"error": "Result not available"}), 404

    result_path = f"results/{job_id}/result.exr"

    return send_file(result_path, mimetype='image/x-exr')

  

if __name__ == '__main__':

    app.run(host='0.0.0.0', port=5000)

```

  

#### 3.2 개선된 버전 (Celery + Redis)

```python

# 더 견고한 구현을 위해 Celery 사용

from celery import Celery

import subprocess

  

celery = Celery('tasks', broker='redis://localhost:6379/0', backend='redis://localhost:6379/0')

  

@celery.task(bind=True)

def process_hdr(self, job_id, input_path):

    """Celery 작업으로 파이프라인 실행"""

    self.update_state(state='PROGRESS', meta={'progress': 10})

    # ... 파이프라인 실행 코드 ...

```

  

---

  

## 🚀 배포 전략

  

### 1. 개발 환경

```bash

# Python 서버

conda activate diffusionlight-turbo

python server.py

  

# Unity

- localhost:5000으로 테스트

```

  

### 2. 프로덕션 환경

  

#### 2.1 서버 스펙

- **GPU**: NVIDIA RTX 3090 이상 (VRAM 24GB 권장)

- **CPU**: 8코어 이상

- **RAM**: 32GB 이상

- **Storage**: SSD 100GB+ (임시 파일용)

  

#### 2.2 Docker 배포

```dockerfile

# Dockerfile

FROM nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04

  

# 환경 설정

RUN apt-get update && apt-get install -y python3 python3-pip

  

# 의존성 설치

COPY requirements.txt .

RUN pip3 install -r requirements.txt

  

# 모델 다운로드 (사전에)

COPY models/ /app/models/

  

# 서버 코드

COPY . /app

WORKDIR /app

  

EXPOSE 5000

CMD ["python3", "server.py"]

```

  

```bash

# 빌드 및 실행

docker build -t diffusionlight-server .

docker run --gpus all -p 5000:5000 diffusionlight-server

```

  

#### 2.3 Kubernetes (선택적)

```yaml

# deployment.yaml

apiVersion: apps/v1

kind: Deployment

metadata:

  name: diffusionlight-server

spec:

  replicas: 2  # GPU 2개 사용시

  template:

    spec:

      containers:

      - name: server

        image: diffusionlight-server:latest

        resources:

          limits:

            nvidia.com/gpu: 1

```

  

---

  

## 📊 모니터링 및 최적화

  

### 1. 성능 모니터링

- **처리 시간**: 각 단계별 시간 측정

- **GPU 사용률**: nvidia-smi 모니터링

- **큐 길이**: 대기 중인 작업 수

- **에러율**: 실패한 요청 비율

  

### 2. 최적화 전략

  

#### 2.1 배치 처리

```python

# 여러 이미지를 한 번에 처리

# inpaint.py는 이미 배치 지원

python inpaint.py --dataset batch_folder --output_dir output

```

  

#### 2.2 캐싱

```python

# 동일한 이미지 요청시 캐시 사용

import hashlib

  

def get_image_hash(image_data):

    return hashlib.sha256(image_data).hexdigest()

  

# 캐시 확인

image_hash = get_image_hash(uploaded_file)

cached_result = check_cache(image_hash)

if cached_result:

    return cached_result

```

  

#### 2.3 모델 최적화

```python

# inpaint.py에 이미 torch.compile 옵션 있음

python inpaint.py --use_torch_compile ...

```

  

---

  

## 🔒 보안 고려사항

  

### 1. 입력 검증

```python

# 파일 크기 제한

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

  

# 이미지 형식 검증

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

  

# 이미지 내용 검증

from PIL import Image

img = Image.open(file)

if img.size != (1024, 1024):

    return error("Image must be 1024x1024")

```

  

### 2. Rate Limiting

```python

from flask_limiter import Limiter

  

limiter = Limiter(app, key_func=lambda: request.remote_addr)

  

@app.route('/api/generate-hdr', methods=['POST'])

@limiter.limit("10 per hour")  # IP당 시간당 10개 제한

def generate_hdr():

    ...

```

  

### 3. 인증 (선택적)

```python

# API 키 인증

@app.before_request

def authenticate():

    api_key = request.headers.get('X-API-Key')

    if api_key != VALID_API_KEY:

        return jsonify({"error": "Unauthorized"}), 401

```

  

---

  

## 🧪 테스트 계획

  

### 1. 단위 테스트

```python

# test_api.py

def test_upload_image():

    response = client.post('/api/generate-hdr',

                          data={'image': test_image})

    assert response.status_code == 202

    assert 'job_id' in response.json

  

def test_job_status():

    response = client.get(f'/api/status/{job_id}')

    assert response.json['status'] in ['pending', 'processing', 'completed', 'failed']

```

  

### 2. 통합 테스트

```csharp

// Unity 테스트

[Test]

public void TestHDRGeneration()

{

    Texture2D testImage = LoadTestImage();

    string jobId = UploadImage(testImage);

    // 완료 대기 (최대 60초)

    bool completed = WaitForCompletion(jobId, timeout: 60);

    Assert.IsTrue(completed);

    // HDR 다운로드 및 검증

    byte[] hdrData = DownloadHDR(jobId);

    Assert.IsTrue(hdrData.Length > 0);

}

```

  

### 3. 부하 테스트

```bash

# Apache Bench로 동시 요청 테스트

ab -n 100 -c 10 -T 'multipart/form-data' http://server:5000/api/generate-hdr

```

  

---

  

## 📅 구현 일정 (예상)

  

| 주차 | 작업 | 담당 |

|------|------|------|

| 1주차 | Python Flask 서버 기본 구조 | Backend |

| 2주차 | 파이프라인 통합 및 비동기 처리 | Backend |

| 3주차 | Unity 클라이언트 구현 | Frontend |

| 4주차 | 통합 테스트 및 디버깅 | Full Stack |

| 5주차 | Docker 배포 및 최적화 | DevOps |

| 6주차 | 모니터링 및 프로덕션 배포 | Full Stack |

  

---

  

## 🎯 대안 및 고급 기능

  

### 1. WebSocket으로 실시간 진행상황

```python

# Flask-SocketIO 사용

from flask_socketio import SocketIO, emit

  

socketio = SocketIO(app)

  

def run_pipeline_with_updates(job_id, input_path):

    socketio.emit('progress', {'job_id': job_id, 'progress': 10})

    # ... 작업 수행 ...

    socketio.emit('progress', {'job_id': job_id, 'progress': 50})

```

  

```csharp

// Unity에서 SocketIO 클라이언트 사용

socket.On("progress", (data) => {

    UpdateProgressBar(data.progress);

});

```

  

### 2. 썸네일 미리보기

```python

# LDR 프리뷰 이미지 생성 (HDR 완성 전)

# exposure2hdr.py에 --preview_output 옵션 있음

python exposure2hdr.py --preview_output ...

```

  

### 3. 클라우드 배포 (AWS/GCP)

- **AWS**: EC2 P3 인스턴스 (V100 GPU)

- **GCP**: Compute Engine with T4/V100 GPU

- **비용 최적화**: Spot Instance 사용

  

---

  

## 📝 체크리스트

  

### Backend (Python)

- [ ] Flask/FastAPI 서버 기본 구조

- [ ] 파일 업로드 엔드포인트

- [ ] 비동기 작업 큐 (Celery/Threading)

- [ ] 상태 조회 API

- [ ] 파일 다운로드 API

- [ ] 에러 핸들링

- [ ] 로깅 시스템

- [ ] 임시 파일 정리 스크립트

  

### Frontend (Unity)

- [ ] 스크린샷 캡처 기능

- [ ] HTTP 클라이언트 구현

- [ ] 비동기 통신 (Coroutine)

- [ ] 진행 상황 UI

- [ ] EXR 파일 로드

- [ ] Skybox/Reflection Probe 적용

- [ ] 에러 처리 및 재시도

  

### DevOps

- [ ] Docker 이미지 빌드

- [ ] 환경 변수 설정

- [ ] GPU 드라이버 확인

- [ ] 모델 파일 준비

- [ ] 서버 배포

- [ ] 모니터링 설정

- [ ] 백업 전략

  

### Testing

- [ ] 단위 테스트

- [ ] 통합 테스트

- [ ] 부하 테스트

- [ ] 다양한 이미지로 테스트

  

---

  

## 💡 참고 자료

  

### 기술 문서

- [Unity UnityWebRequest](https://docs.unity3d.com/ScriptReference/Networking.UnityWebRequest.html)

- [Flask Documentation](https://flask.palletsprojects.com/)

- [Celery Documentation](https://docs.celeryproject.org/)

- [OpenEXR Format](https://www.openexr.com/)

  

### 샘플 코드

- Unity HTTP 클라이언트: [Unity-RESTClient](https://github.com/proyecto26/RestClient)

- Python 비동기 처리: [Flask-Celery](https://flask.palletsprojects.com/en/2.3.x/patterns/celery/)

  

---

  

## 🚨 주의사항

  

1. **GPU 메모리**: DiffusionLight는 VRAM 많이 사용 (~10GB). 동시 요청 제한 필요.

2. **처리 시간**: 30초는 최소값. 서버 부하시 더 길어질 수 있음.

3. **파일 크기**: EXR 파일은 PNG보다 큼 (~5-10MB). 네트워크 대역폭 고려.

4. **모델 다운로드**: 최초 실행시 Stable Diffusion 모델 자동 다운로드 (~7GB). 사전에 준비.

5. **라이선스**: 상업용 사용시 Stable Diffusion 라이선스 확인.

  

---

  

## 📧 문의

  

추가 질문이나 구현 중 문제가 생기면 언제든 연락주세요!