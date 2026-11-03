"""Synthetic contract fixtures only; never real participant/model output."""
from copy import deepcopy
import json
from build_schema import ROOT, CORE, SPECS, EMOTIONS

def missing(key, reason, total=0):
    return {"status":"unavailable","value":None,"unit":SPECS[key][0],"reason":reason,
            "valid_samples":0,"total_samples":total,"valid_duration_sec":0,
            "method_id":method_for(key),"source_channels":[],
            "level":"unavailable" if SPECS[key][0]=="score_0_100" else None}

def method_for(key):
    if key.startswith("voice_"): return "voice-v1"
    if key.startswith("language_"): return "lexicon-v1"
    if key.startswith("au_"): return "au-v1"
    if key.startswith("emotion_") or key in ["valence","arousal"]: return "fusion-v1"
    return "score-v1"

def metric(key,value):
    m=missing(key,"unknown",30)
    m.update(status="available",value=value,reason=None,valid_samples=20,valid_duration_sec=0.8,
             source_channels=["face_model","face_au"])
    if key.startswith("voice_"): m.update(source_channels=["voice"],total_samples=32,valid_samples=20,valid_duration_sec=0.6)
    elif key.startswith("language_"): m.update(source_channels=["language"],total_samples=1,valid_samples=1,valid_duration_sec=0.7)
    elif key.startswith("au_"): m.update(source_channels=["face_au"])
    if SPECS[key][0]=="score_0_100": m["level"]="high" if value>=70 else "moderate" if value>=50 else "low"
    return m

def timing(start,end):
    return {"recording":{"start_sec":start,"end_sec":end},
            "content":{"start_sec":start+5,"end_sec":end+5},"mapping_id":"map-1"}

def normal():
    def method(kind,channels,unit,model=None):
        return {"kind":kind,"version":"synthetic-example-1","model_ref":model,"source_channels":channels,"sample_unit":unit}
    r={"schema_version":"1.0.0","data_origin":"synthetic","analysis_id":"analysis-demo-1","test_id":"test-demo-1",
       "participant_id":"participant-demo-1","generated_at":"2026-10-23T18:00:00+09:00",
       "recording":{"id":"recording-demo-1","duration_sec":3},
       "content":{"id":"content-demo-1","version":"A","duration_sec":30},
       "audio_source":{"id":"audio-demo-1","duration_sec":3,"origin":"recording_track","attribution":"participant_confirmed",
                       "alignment_status":"aligned","offset_to_recording_sec":0},
       "baseline":{"status":"captured","recording":{"start_sec":0,"end_sec":1}},
       "methods":{
           "score-v1":method("heuristic",["face_model","face_au"],"video_frame"),
           "fusion-v1":method("heuristic",["face_model","face_au","voice","language"],"video_frame"),
           "au-v1":method("model_inference",["face_au"],"video_frame","synthetic-au-model"),
           "voice-v1":method("signal_processing",["voice"],"audio_frame"),
           "lexicon-v1":method("lexicon",["language"],"utterance"),
           "stt-v1":method("model_inference",["voice"],"utterance","synthetic-stt-model")},
       "content_mappings":[{"id":"map-1","recording":{"start_sec":0,"end_sec":3},"content_start_sec":5,
                            "uncertainty_sec":0.04,"method":"manual_verified"}],
       "segments":[],"utterances":[],"events":[],"limitations":["Synthetic contract fixture; no measured human reaction."]}
    for i in range(3):
        speech=i==1
        measures={k:missing(k,"no_speech") for k in CORE}
        for k,v in {"attention":75,"interest":60,"engagement":62,"tension":20,"valence":0.2,"arousal":0.1}.items(): measures[k]=metric(k,v)
        measures["voice_energy_dbfs"]=metric("voice_energy_dbfs",-24 if speech else -70)
        if speech:
            for k,v in {"voice_pitch_hz":140,"voice_rate_sps":3,"language_valence":0.4,"language_arousal":0.1}.items(): measures[k]=metric(k,v)
        measures["au_raw_AU06"]=metric("au_raw_AU06",0.8)
        measures["au_delta_AU06"]=metric("au_delta_AU06",0.3) if i>0 else missing("au_delta_AU06","baseline_not_ready",30)
        for emo in EMOTIONS: measures["emotion_"+emo]=metric("emotion_"+emo,0.4 if emo=="Happiness" else 0.6 if emo=="Neutral" else 0)
        r["segments"].append({"id":f"seg-{i}","timing":timing(i,i+1),
            "face_quality":{"total_frames":30,"detected_frames":28,"trusted_frames":20},
            "audio":{"state":"speech" if speech else "silence","reason":None,"coverage_duration_sec":1,"speech_duration_sec":0.7 if speech else 0},
            "transcript":{"state":"available" if speech else "no_speech","reason":None if speech else "no_speech","utterance_ids":["utt-1"] if speech else []},
            "measurements":measures})
    r["utterances"]=[{"id":"utt-1","timing":timing(1.1,1.8),"timing_status":"aligned","text":"재미있네요",
        "redacted":False,"stt_method_id":"stt-v1","stt_confidence":None,"observed_at":"2026-10-23T18:00:00+09:00",
        "matched_terms":[{"term":"재미","polarity":"positive"}]}]
    r["events"]=[{"id":"evt-1","kind":"metric_peak","timing":timing(1,2),"peak_recording_sec":1.4,
        "metric_key":"au_raw_AU06","value":1.2,"evidence_segment_ids":["seg-1"]}]
    return r

def examples():
    r=normal(); out={"normal_voice":r}
    silence=deepcopy(r); silence["utterances"]=[]
    for s in silence["segments"]:
        s["audio"].update(state="silence",speech_duration_sec=0)
        s["transcript"]={"state":"no_speech","reason":"no_speech","utterance_ids":[]}
        for k in CORE:
            if k.startswith("language_") or k in ["voice_pitch_hz","voice_rate_sps"]: s["measurements"][k]=missing(k,"no_speech",32 if k.startswith("voice_") else 0)
    out["silence"]=silence
    absent=deepcopy(silence)
    absent["audio_source"]={"id":None,"duration_sec":None,"origin":"none","attribution":"not_applicable","alignment_status":"not_applicable","offset_to_recording_sec":None}
    for s in absent["segments"]:
        s["audio"]={"state":"unavailable","reason":"audio_missing","coverage_duration_sec":0,"speech_duration_sec":None}
        s["transcript"]={"state":"unavailable","reason":"audio_missing","utterance_ids":[]}
        for k in CORE:
            if k.startswith(("voice_","language_")): s["measurements"][k]=missing(k,"audio_missing")
    out["audio_missing"]=absent
    missing_face=deepcopy(silence)
    s=missing_face["segments"][1]; s["face_quality"]={"total_frames":30,"detected_frames":20,"trusted_frames":0}
    for k,m in list(s["measurements"].items()):
        if any(c.startswith("face_") for c in m["source_channels"]): s["measurements"][k]=missing(k,"low_quality",30)
    missing_face["events"]=[]
    out["face_missing"]=missing_face
    unknown=deepcopy(r); unknown["content_mappings"]=[]
    for record in unknown["segments"]+unknown["utterances"]+unknown["events"]:
        record["timing"].update(content=None,mapping_id=None)
    unknown["limitations"].append("Content alignment unknown; scene-specific statements unavailable.")
    out["unsynced"]=unknown
    failed=deepcopy(r); failed["utterances"]=[]
    for s in failed["segments"]:
        if s["audio"]["state"]=="speech":
            s["transcript"]={"state":"error","reason":"stt_unavailable","utterance_ids":[]}
            for k in ["language_valence","language_arousal"]: s["measurements"][k]=missing(k,"stt_unavailable")
    out["stt_failed"]=failed
    redacted=deepcopy(r); u=redacted["utterances"][0]; u.update(text=None,redacted=True,matched_terms=[])
    s=redacted["segments"][1]; s["transcript"].update(state="redacted",reason="redacted")
    for k in ["language_valence","language_arousal"]: s["measurements"][k]=missing(k,"redacted")
    out["redacted"]=redacted
    return out

if __name__=="__main__":
    folder=ROOT/"examples"; folder.mkdir(exist_ok=True)
    for name,value in examples().items():
        (folder/(name+".json")).write_text(json.dumps(value,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Wrote 7 synthetic fixtures")
