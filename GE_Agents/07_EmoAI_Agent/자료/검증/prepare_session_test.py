"""Prepare an offline aggregation test. Reads source; writes only under this folder.

No network/model/LLM code is built. Struct-only headers remove OpenCV/OpenFace
build dependencies, preserving original data member definitions. This tests the
real analysis_session.cpp, not model inference or binary/source equivalence.
"""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = Path(r"C:\ableai\XR_workspace\Meta Glass\exhibition\FaceAnalysisWebView")
BUILD = ROOT / "session_build"
BUILD.mkdir(exist_ok=True)
manifest = []

def read(rel):
    p = SOURCE / rel
    data = p.read_bytes()
    manifest.append({"path": str(p), "sha256": hashlib.sha256(data).hexdigest()})
    return data.decode("utf-8-sig")

for name in ["analysis_session.cpp", "analysis_session.h", "affect_analyzer.h", "emotion_fusion.h"]:
    (BUILD / name).write_text(read("src/" + name), encoding="utf-8")
for name, struct in [("face_pipeline.h", "FaceAnalysisResult"), ("emotion_classifier.h", "EmotionResult")]:
    text = read("src/" + name)
    start = text.index("struct " + struct + " {")
    end = text.index("\n};", start) + len("\n};")
    (BUILD / name).write_text("#pragma once\n#include <string>\n#include <vector>\n#include <utility>\n" + text[start:end], encoding="utf-8")
(BUILD / "json.hpp").write_text(read("include/third_party/json.hpp"), encoding="utf-8")
manifest.append({"path": str(SOURCE / "build/bin/Release/face_analysis_webview.exe"),
                 "sha256": hashlib.sha256((SOURCE / "build/bin/Release/face_analysis_webview.exe").read_bytes()).hexdigest()})
(ROOT / "source_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print("Prepared original session source and struct-only dependency headers.")
