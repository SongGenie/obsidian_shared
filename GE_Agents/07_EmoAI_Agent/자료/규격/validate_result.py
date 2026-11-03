"""v1 schema + cross-field validator. No network or engine/model calls.

Usage: python validate_result.py examples/normal_voice.json
Requires an already-installed jsonschema with Draft202012Validator.
"""
import json
import math
import re
import sys
from datetime import datetime
from pathlib import Path
from jsonschema import Draft202012Validator, FormatChecker
from build_schema import ROOT, SPECS, EMOTIONS

EPS = 1e-6

def loads(text):
    def unique(pairs):
        out = {}
        for key, value in pairs:
            if key in out: raise ValueError(f"duplicate JSON key: {key}")
            out[key] = value
        return out
    def invalid(value): raise ValueError(f"non-finite JSON constant: {value}")
    return json.loads(text, object_pairs_hook=unique, parse_constant=invalid)

def load(path):
    return loads(Path(path).read_text(encoding="utf-8-sig"))

def validate(data):
    errors = []
    def reject(message): errors.append(message)
    def finite(node):
        if isinstance(node, float) and not math.isfinite(node): reject("non-finite number")
        elif isinstance(node, dict):
            for item in node.values(): finite(item)
        elif isinstance(node, list):
            for item in node: finite(item)
    finite(data)
    schema = load(ROOT / "analysis-result.schema.json")
    errors.extend(f"schema:{'/'.join(map(str,e.absolute_path))}: {e.message}" for e in Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(data))
    if errors: return errors
    # Some offline jsonschema installations lack optional RFC3339 packages.
    # Enforce timezone-aware timestamp syntax independently of format plugins.
    for value in [data["generated_at"]]+[u["observed_at"] for u in data["utterances"]]:
        try:
            if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})",value): raise ValueError()
            datetime.fromisoformat(value.replace("Z","+00:00"))
        except ValueError: reject("timestamp must be valid ISO8601 with timezone (leap seconds unsupported)")
    duration = data["recording"]["duration_sec"]
    methods = data["methods"]
    def interval(r, maximum, where):
        if r["end_sec"] <= r["start_sec"] or r["end_sec"] > maximum + EPS:
            reject(where + ": invalid interval or outside media duration")
    def overlaps(a,b): return a["start_sec"] < b["end_sec"]-EPS and b["start_sec"] < a["end_sec"]-EPS
    def unique_ids(items, label):
        ids = [x["id"] for x in items]
        if len(ids) != len(set(ids)): reject(label + ": duplicate id")
        return {x["id"]:x for x in items}
    mappings = unique_ids(data["content_mappings"], "mapping")
    previous = 0
    for m in data["content_mappings"]:
        r = m["recording"]
        interval(r,duration,"mapping")
        if r["start_sec"] < previous-EPS: reject("mapping: overlap or unsorted")
        previous = r["end_sec"]
        if m["content_start_sec"]+r["end_sec"]-r["start_sec"] > data["content"]["duration_sec"]+EPS:
            reject("mapping: outside content")
    def timing(t, label, split_required=False):
        r = t["recording"]
        interval(r,duration,label)
        m = mappings.get(t["mapping_id"])
        containing = [x for x in mappings.values() if r["start_sec"] >= x["recording"]["start_sec"]-EPS and r["end_sec"] <= x["recording"]["end_sec"]+EPS]
        if m is None:
            if t["mapping_id"] is not None or t["content"] is not None: reject(label+": unresolved mapping")
            if containing: reject(label+": known mapping cannot be suppressed")
            # A boundary crossing must be split, not silently downgraded to unknown.
            if split_required and any(overlaps(r,x["recording"]) for x in mappings.values()): reject(label+": split at mapping boundary")
            return
        if t["content"] is None: reject(label+": mapped content time missing"); return
        if r["start_sec"] < m["recording"]["start_sec"]-EPS or r["end_sec"] > m["recording"]["end_sec"]+EPS:
            reject(label+": interval crosses mapping boundary")
        interval(t["content"],data["content"]["duration_sec"],label+" content")
        for edge in ["start_sec","end_sec"]:
            expected = m["content_start_sec"]+r[edge]-m["recording"]["start_sec"]
            if abs(t["content"][edge]-expected)>EPS: reject(label+": inconsistent content mapping")

    audio = data["audio_source"]
    if audio["origin"] == "none":
        if audio["id"] is not None or audio["duration_sec"] is not None or audio["attribution"] != "not_applicable" or audio["alignment_status"] != "not_applicable" or audio["offset_to_recording_sec"] is not None:
            reject("audio_source: absent source must have null id/offset and not_applicable metadata")
    else:
        if audio["id"] is None or audio["duration_sec"] is None or audio["attribution"] == "not_applicable" or audio["alignment_status"] == "not_applicable": reject("audio_source: present source metadata missing")
        if (audio["alignment_status"] == "aligned") != (audio["offset_to_recording_sec"] is not None): reject("audio_source: offset/alignment mismatch")
        if audio["origin"] == "recording_track" and (audio["alignment_status"] != "aligned" or audio["offset_to_recording_sec"] != 0): reject("audio_source: recording track must have offset zero")
    baseline = data["baseline"]
    if baseline["status"] == "captured":
        if baseline["recording"] is None: reject("baseline: captured range missing")
        else: interval(baseline["recording"],duration,"baseline")
    elif baseline["recording"] is not None: reject("baseline: unavailable baseline has range")

    segments = unique_ids(data["segments"],"segment")
    utterances = unique_ids(data["utterances"],"utterance")
    events = unique_ids(data["events"],"event")
    # All referenceable records share a namespace for future evidence references.
    all_ids = list(segments)+list(utterances)+list(events)
    if len(all_ids)!=len(set(all_ids)): reject("record ids must be globally unique")
    previous = 0
    referenced_utterances = set()
    for s in data["segments"]:
        label=s["id"]; timing(s["timing"],label,split_required=True)
        r=s["timing"]["recording"]; span=r["end_sec"]-r["start_sec"]
        if abs(r["start_sec"]-previous)>EPS: reject(label+": timeline gap/overlap or unsorted")
        if span > 1+EPS: reject(label+": segment exceeds one second")
        previous=r["end_sec"]
        q=s["face_quality"]
        if not q["trusted_frames"]<=q["detected_frames"]<=q["total_frames"]: reject(label+": invalid face counts")
        a=s["audio"]; state=a["state"]
        if a["coverage_duration_sec"]>span+EPS: reject(label+": audio coverage exceeds interval")
        if state in ["speech","silence"]:
            if a["reason"] is not None or a["coverage_duration_sec"]<=0 or a["speech_duration_sec"] is None: reject(label+": valid audio missing coverage or speech state")
            elif a["speech_duration_sec"]>a["coverage_duration_sec"]+EPS: reject(label+": speech exceeds coverage")
            if state=="silence" and a["speech_duration_sec"]!=0: reject(label+": silence must have zero speech")
            if state=="speech" and (a["speech_duration_sec"] is None or a["speech_duration_sec"]<=0): reject(label+": speech requires positive duration")
            if audio["origin"]=="none" or audio["attribution"]!="participant_confirmed" or audio["alignment_status"]!="aligned": reject(label+": participant audio not confirmed and aligned")
            elif audio["duration_sec"] is not None and audio["offset_to_recording_sec"] is not None:
                left=audio["offset_to_recording_sec"]; right=left+audio["duration_sec"]
                overlap=max(0,min(r["end_sec"],right)-max(r["start_sec"],left))
                if a["coverage_duration_sec"]>overlap+EPS: reject(label+": audio coverage exceeds source duration/mapping")
        else:
            if a["reason"] is None or a["speech_duration_sec"] is not None: reject(label+": invalid unavailable audio state")
            if a["coverage_duration_sec"]!=0: reject(label+": unusable audio coverage must be zero")
        if audio["origin"]=="none" and (state!="unavailable" or a["reason"]!="audio_missing"): reject(label+": missing source must be audio_missing")
        if audio["attribution"] in ["content_only","mixed","unknown"] and (state!="excluded" or a["reason"]!="nonparticipant_audio"): reject(label+": unconfirmed audio must be excluded")
        t=s["transcript"]
        if t["state"]=="no_speech" and (state!="silence" or t["reason"]!="no_speech"): reject(label+": no_speech requires observed silence")
        if t["state"]=="available":
            if not t["utterance_ids"] or t["reason"] is not None: reject(label+": available transcript needs references and no error")
        elif t["state"]=="redacted":
            if not t["utterance_ids"] or t["reason"]!="redacted": reject(label+": redacted transcript needs references/reason")
        elif t["utterance_ids"] or t["reason"] is None: reject(label+": unavailable transcript must have reason and no references")
        for uid in t["utterance_ids"]:
            u=utterances.get(uid)
            if u is None: reject(label+": unresolved utterance"); continue
            referenced_utterances.add(uid)
            if u["timing"] is None or not overlaps(r,u["timing"]["recording"]): reject(label+": utterance has no overlapping media time")
            if (t["state"]=="redacted") != u["redacted"]: reject(label+": transcript redaction state mismatch")
        measures=s["measurements"]
        for key,v in measures.items():
            mid=v["method_id"]; method=methods.get(mid)
            if method is None: reject(label+": unresolved method "+mid); continue
            if v["valid_samples"]>v["total_samples"] or v["valid_duration_sec"]>span+EPS: reject(label+":"+key+": invalid sample count/duration")
            if not set(v["source_channels"])<=set(method["source_channels"]): reject(label+":"+key+": undeclared method input")
            if v["status"]!="available": continue
            sources=v["source_channels"]
            if any(c in sources for c in ["face_model","face_au"]) and q["trusted_frames"]==0: reject(label+":"+key+": no trusted face evidence")
            if method["sample_unit"]=="video_frame" and (v["total_samples"]>q["total_frames"] or v["valid_samples"]>q["trusted_frames"]): reject(label+":"+key+": video sample count exceeds evidence")
            if "voice" in sources and state not in ["speech","silence"]: reject(label+":"+key+": no usable audio evidence")
            if "voice" in sources and v["valid_duration_sec"]>a["coverage_duration_sec"]+EPS: reject(label+":"+key+": voice duration exceeds audio coverage")
            if "language" in sources and t["state"]!="available": reject(label+":"+key+": no visible transcript evidence")
            if key.startswith("voice_") and ("voice" not in sources or (key!="voice_energy_dbfs" and state!="speech")): reject(label+":"+key+": voice metric needs speech")
            if key.startswith("language_") and "language" not in sources: reject(label+":"+key+": language metric lacks language source")
            if key.startswith("au_") and "face_au" not in sources: reject(label+":"+key+": AU metric lacks muscle source")
            if key.startswith("au_delta_") and (baseline["status"]!="captured" or baseline["recording"] is None or baseline["recording"]["end_sec"]>r["start_sec"]+EPS): reject(label+":"+key+": baseline not ready")
            if SPECS[key][0]=="score_0_100":
                expected="high" if v["value"]>=70 else "moderate" if v["value"]>=50 else "low"
                if v["level"]!=expected: reject(label+":"+key+": wrong score level")
        emotion=[measures.get("emotion_"+e) for e in EMOTIONS]
        if any(x is not None for x in emotion):
            if any(x is None for x in emotion): reject(label+": emotion vector must have all seven labels")
            elif any(x["status"]=="available" for x in emotion):
                if not all(x["status"]=="available" for x in emotion): reject(label+": partial emotion probability vector")
                elif abs(sum(x["value"] for x in emotion)-1)>1e-4: reject(label+": emotion probabilities do not sum to one")
    if abs(previous-duration)>EPS: reject("timeline must cover entire recording, including missing intervals")

    for u in data["utterances"]:
        if u["stt_method_id"] not in methods: reject(u["id"]+": unknown STT method")
        else:
            method=methods[u["stt_method_id"]]
            if method["kind"]!="model_inference" or "voice" not in method["source_channels"] or method["sample_unit"]!="utterance": reject(u["id"]+": invalid STT method provenance")
        if audio["origin"]=="none" or audio["attribution"]!="participant_confirmed": reject(u["id"]+": participant audio source not confirmed")
        if u["timing"] is not None:
            timing(u["timing"],u["id"])
            if audio["alignment_status"]!="aligned": reject(u["id"]+": audio alignment unknown")
            elif audio["offset_to_recording_sec"] is not None and audio["duration_sec"] is not None:
                r=u["timing"]["recording"]; offset=audio["offset_to_recording_sec"]
                if r["start_sec"]<offset-EPS or r["end_sec"]>offset+audio["duration_sec"]+EPS: reject(u["id"]+": utterance outside source audio time")
            if u["id"] not in referenced_utterances: reject(u["id"]+": timed utterance not referenced by transcript")
            for s in segments.values():
                if overlaps(u["timing"]["recording"],s["timing"]["recording"]):
                    if u["id"] not in s["transcript"]["utterance_ids"] or s["audio"]["state"]!="speech": reject(u["id"]+": every overlapping segment must reference utterance with speech state")
    for e in data["events"]:
        timing(e["timing"],e["id"])
        r=e["timing"]["recording"]
        if e["peak_recording_sec"] is not None and not r["start_sec"]<=e["peak_recording_sec"]<r["end_sec"]: reject(e["id"]+": peak outside event interval")
        evidence=[]
        for sid in e["evidence_segment_ids"]:
            s=segments.get(sid)
            if s is None or not overlaps(r,s["timing"]["recording"]): reject(e["id"]+": missing/non-overlapping evidence segment")
            else: evidence.append(s)
        if e["kind"]=="metric_peak":
            key=e["metric_key"]
            if key is None or e["value"] is None or e["peak_recording_sec"] is None: reject(e["id"]+": metric peak needs key/value/time")
            else:
                _,low,high=SPECS[key]
                if e["value"]<low or (high is not None and e["value"]>high): reject(e["id"]+": event value outside metric range")
                if not any(s["measurements"].get(key,{}).get("status")=="available" and s["timing"]["recording"]["start_sec"]<=e["peak_recording_sec"]<s["timing"]["recording"]["end_sec"] for s in evidence): reject(e["id"]+": peak has no available metric evidence at peak time")
        elif e["metric_key"] is not None or e["value"] is not None: reject(e["id"]+": non-metric event must not invent scalar value")
        if not any(any(m["status"]=="available" for m in s["measurements"].values()) for s in evidence): reject(e["id"]+": no available event evidence")
        if e["kind"] in ["duchenne_smile_pattern","social_smile_pattern","brow_raise","gaze_away","tension_spike"] and not any(s["face_quality"]["trusted_frames"]>0 for s in evidence): reject(e["id"]+": face event has no trusted face")
    return errors

if __name__ == "__main__":
    if len(sys.argv)!=2: raise SystemExit("usage: python validate_result.py RESULT.json")
    try: errors=validate(load(sys.argv[1]))
    except (ValueError,OSError) as exc: errors=[str(exc)]
    print(json.dumps({"valid":not errors,"errors":errors},ensure_ascii=False,indent=2))
    raise SystemExit(bool(errors))
