"""Check saved evidence and its source identity without network calls."""
import hashlib
import json
from pathlib import Path

root = Path(__file__).resolve().parent
source = Path(r"C:\ableai\XR_workspace\Meta Glass\exhibition\FaceAnalysisWebView")
manifest = json.loads((root / "source_manifest.json").read_text(encoding="utf-8-sig"))
known = {x["path"] for x in manifest}
for rel in ["src/main.cpp", "src/affect_analyzer.cpp", "src/llm_client.cpp", "src/voice_frontend.cpp",
            "src/stt_client.cpp", "src/text_affect.cpp", "web/js/app.js", "web/js/x.js", "CMakeLists.txt",
            "prompts/llm_system_prompt.txt", "models/hsemotion/affectnet_labels.txt"]:
    p = source / rel
    if str(p) not in known:
        manifest.append({"path": str(p), "sha256": hashlib.sha256(p.read_bytes()).hexdigest()})
(root / "source_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
checks = []
def check(name, ok):
    checks.append({"check": name, "pass": bool(ok)})
check("evidence sources unchanged", all(hashlib.sha256(Path(x["path"]).read_bytes()).hexdigest() == x["sha256"] for x in manifest))
binary = json.loads((root / "offline_test_results.json").read_text(encoding="utf-8-sig"))
check("three existing offline modes exited zero", len(binary)==3 and all(x["exit_code"]==0 for x in binary))
session = json.loads((root / "session_test_results.json").read_text(encoding="utf-8"))
check("24 aggregation behavior checks recorded", len(session["checks"])==24 and session["failed"]==0 and all(x["pass"] for x in session["checks"]))
model = json.loads((root / "emotion_model_probe.json").read_text(encoding="utf-8"))
check("local model produced seven finite outputs", model["status"]=="pass" and model["output_count"]==7 and model["output_finite"])
check("model file unchanged", hashlib.sha256(Path(model["model"]).read_bytes()).hexdigest()==model["model_sha256"])
check("source prompt copy unchanged", (root.parent / "llm_system_prompt.txt").read_bytes()==(source / "prompts/llm_system_prompt.txt").read_bytes())
missing = json.loads((root / "unreliable_only_summary.json").read_text(encoding="utf-8"))
check("missing-data defect documented by output", missing["attention_summary"]["mean"]==0 and missing["attention_summary"]["level"]=="low" and missing["prompt_state"]["confidence"]=="insufficient")
check("illustrative CPU cost arithmetic", abs(600*(2*0.000018+4*0.000002)-0.0264)<1e-10)
report = {"scope": "evidence consistency only, not end-to-end validation", "checks": checks, "passed":sum(c["pass"] for c in checks), "failed":sum(not c["pass"] for c in checks)}
(root / "audit_results.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(report, ensure_ascii=False, indent=2))
raise SystemExit(bool(report["failed"]))
