"""Offline CPU model compatibility probe on a generated gray image, not a face.
No network, no personal data, no emotion-accuracy or video-throughput claim.
"""
import hashlib
import json
import time
from pathlib import Path
import cv2
import numpy as np

root = Path(__file__).resolve().parent
models = Path(r"C:\ableai\XR_workspace\Meta Glass\exhibition\FaceAnalysisWebView\models\hsemotion")
model = models / "emotions_mobilenet.tflite"
report = {"scope": "synthetic gray image, local CPU only, different OpenCV runtime from shipped executable",
          "opencv_version": cv2.__version__, "model": str(model),
          "model_sha256": hashlib.sha256(model.read_bytes()).hexdigest(),
          "labels": (models / "affectnet_labels.txt").read_text(encoding="utf-8-sig").splitlines()}
try:
    cv2.setNumThreads(2)
    t = time.perf_counter()
    net = cv2.dnn.readNetFromTFLite(str(model))
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    report["load_seconds"] = round(time.perf_counter()-t, 4)
    blob = cv2.dnn.blobFromImage(np.full((224,224,3), 127, dtype=np.uint8), 1.0, (224,224),
                                (103.939,116.779,123.68), swapRB=False, crop=False)
    net.setInput(blob)
    t = time.perf_counter()
    out = net.forward()
    report.update({"forward_seconds": round(time.perf_counter()-t, 4), "output_shape": list(out.shape),
                   "output_finite": bool(np.isfinite(out).all()), "output_count": int(out.size),
                   "status": "pass" if out.size == len(report["labels"]) and np.isfinite(out).all() else "fail"})
except Exception as exc:
    report.update({"status": "unverified_runtime_incompatibility", "error": str(exc)})
(root / "emotion_model_probe.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
