"""Contract acceptance/rejection tests, no engine or network calls."""
from copy import deepcopy
from pathlib import Path
import json
from importlib.metadata import version
from jsonschema import Draft202012Validator
from build_schema import ROOT
from build_examples import normal, missing
from validate_result import validate, load, loads

results=[]
def record(name,expected,errors):
    accepted=not errors
    results.append({"case":name,"expected_valid":expected,"actual_valid":accepted,"pass":accepted==expected,
                    "first_error":errors[0] if errors else None})

def bad(name,mutate):
    r=normal(); mutate(r); record(name,False,validate(r))

def replace(r,path,value):
    for key in path[:-1]: r=r[key]
    r[path[-1]]=value

if __name__=="__main__":
    Draft202012Validator.check_schema(load(ROOT/"analysis-result.schema.json"))
    for path in sorted((ROOT/"examples").glob("*.json")): record(path.stem,True,validate(load(path)))
    base=["segments",1,"measurements","attention"]
    cases=[
        ("available_null",base+["value"],None),
        ("unavailable_zero",base+["status"],"unavailable"),
        ("missing_reason",base+["reason"],"low_quality"),
        ("score_outside_range",base+["value"],101),
        ("wrong_unit",base+["unit"],"percent"),
        ("wrong_score_level",base+["level"],"low"),
        ("valid_samples_exceed_total",base+["valid_samples"],31),
        ("duration_exceeds_segment",base+["valid_duration_sec"],1.5),
        ("available_without_source",base+["source_channels"],[]),
        ("unknown_method",base+["method_id"],"not-registered"),
        ("undeclared_method_channel",base+["source_channels"],["language"]),
        ("bad_face_count",["segments",1,"face_quality","trusted_frames"],31),
        ("no_trusted_face",["segments",1,"face_quality","trusted_frames"],0),
        ("gap_in_recording",["segments",1,"timing","recording","start_sec"],1.1),
        ("overlap_recording",["segments",1,"timing","recording","start_sec"],0.9),
        ("outside_recording",["segments",2,"timing","recording","end_sec"],4),
        ("incorrect_content_time",["segments",1,"timing","content","start_sec"],8),
        ("unresolved_time_mapping",["segments",1,"timing","mapping_id"],"absent"),
        ("mapping_outside_content",["content_mappings",0,"content_start_sec"],29),
        ("negative_duration",["recording","duration_sec"],-1),
        ("silence_with_pitch",["segments",1,"audio","state"],"silence"),
        ("speech_without_audio",["audio_source","origin"],"none"),
        ("content_audio_as_participant",["audio_source","attribution"],"content_only"),
        ("external_audio_unknown_sync",["audio_source","alignment_status"],"unknown"),
        ("audio_overcoverage",["segments",1,"audio","coverage_duration_sec"],2),
        ("speech_longer_than_coverage",["segments",1,"audio","speech_duration_sec"],2),
        ("pitch_zero_unvoiced",["segments",1,"measurements","voice_pitch_hz","value"],0),
        ("no_baseline_for_delta",["baseline","status"],"unavailable"),
        ("baseline_finishes_late",["baseline","recording","end_sec"],2),
        ("probabilities_not_normalized",["segments",1,"measurements","emotion_Happiness","value"],0.9),
        ("unresolved_transcript",["segments",1,"transcript","utterance_ids"],["absent"]),
        ("timestamp_not_datetime",["utterances",0,"observed_at"],"not-a-time"),
        ("timestamp_without_timezone",["generated_at"],"2026-10-23T18:00:00"),
        ("invalid_calendar_date",["generated_at"],"2026-02-30T18:00:00Z"),
        ("audio_source_too_short",["audio_source","duration_sec"],0.5),
        ("wrong_STT_provenance",["utterances",0,"stt_method_id"],"score-v1"),
        ("peak_outside_event",["events",0,"peak_recording_sec"],2),
        ("unresolved_event_evidence",["events",0,"evidence_segment_ids"],["absent"]),
        ("metric_peak_no_value",["events",0,"value"],None),
        ("redacted_with_text",["utterances",0,"redacted"],True),
        ("schema_version_mismatch",["schema_version"],"2.0.0"),
        ("duplicate_segment_id",["segments",1,"id"],"seg-0"),
    ]
    for name,path,value in cases: bad(name,lambda r,p=path,v=value:replace(r,p,v))
    bad("unknown_property",lambda r:r.update(tenant_secret="must-not-be-here"))
    bad("partial_emotion_vector",lambda r:r["segments"][0]["measurements"].pop("emotion_Anger"))
    bad("duplicate_mapping",lambda r:r["content_mappings"].append(deepcopy(r["content_mappings"][0])))
    def silence_with_language(r):
        s=r["segments"][1]; s["audio"]["state"]="silence"; s["audio"]["speech_duration_sec"]=0
        s["transcript"]={"state":"no_speech","reason":"no_speech","utterance_ids":[]}; r["utterances"]=[]
    bad("language_without_speech",silence_with_language)
    def suppress_mapping(r): r["segments"][1]["timing"].update(content=None,mapping_id=None)
    bad("suppress_known_mapping",suppress_mapping)
    def untrusted_value(r):
        s=r["segments"][1]; s["face_quality"]["trusted_frames"]=0
        s["measurements"]["attention"]["value"]=0; s["measurements"]["attention"]["level"]="low"
    bad("old_missing_as_zero_defect",untrusted_value)
    def no_speech_with_stt_error(r): r["segments"][1]["transcript"].update(state="no_speech",reason="stt_unavailable",utterance_ids=[])
    bad("stt_failure_is_not_silence",no_speech_with_stt_error)
    r=normal(); r["segments"][1]["measurements"]["attention"].update(value=0,level="low")
    record("actual_observed_zero_is_valid",True,validate(r))
    r=normal(); r["audio_source"].update(origin="external_track",offset_to_recording_sec=-0.25,duration_sec=3.25)
    record("aligned_external_audio_negative_offset",True,validate(r))
    r=normal(); r["segments"][1]["measurements"]["voice_pitch_hz"]=missing("voice_pitch_hz","not_voiced",32)
    record("unvoiced_pitch_is_null",True,validate(r))
    r=normal()
    r["content_mappings"]=[
        {"id":"map-1","recording":{"start_sec":0,"end_sec":1},"content_start_sec":5,"uncertainty_sec":0.04,"method":"manual_verified"},
        {"id":"map-2","recording":{"start_sec":2,"end_sec":3},"content_start_sec":5,"uncertainty_sec":0.04,"method":"manual_verified"}]
    r["segments"][1]["timing"].update(content=None,mapping_id=None)
    r["segments"][2]["timing"].update(content={"start_sec":5,"end_sec":6},mapping_id="map-2")
    r["utterances"][0]["timing"].update(content=None,mapping_id=None)
    r["events"][0]["timing"].update(content=None,mapping_id=None)
    record("pause_gap_and_content_replay",True,validate(r))
    r=normal(); r["utterances"][0].update(timing=None,timing_status="unavailable")
    r["segments"][1]["transcript"]={"state":"unavailable","reason":"unknown","utterance_ids":[]}
    for key in ["language_valence","language_arousal"]: r["segments"][1]["measurements"][key]=missing(key,"unknown")
    record("untimed_STT_is_preserved_without_segment_claim",True,validate(r))
    r=load(ROOT/"examples/audio_missing.json")
    r["audio_source"].update(id="audio-background",origin="recording_track",duration_sec=3,attribution="content_only",alignment_status="aligned",offset_to_recording_sec=0)
    for s in r["segments"]:
        s["audio"].update(state="excluded",reason="nonparticipant_audio")
        s["transcript"]["reason"]="nonparticipant_audio"
        for key in s["measurements"]:
            if key.startswith(("voice_","language_")): s["measurements"][key]=missing(key,"nonparticipant_audio")
    record("background_audio_is_explicitly_excluded",True,validate(r))
    r=load(ROOT/"examples/audio_missing.json"); r["events"]=[]; r["baseline"]={"status":"unavailable","recording":None}
    for s in r["segments"]:
        s["face_quality"].update(detected_frames=0,trusted_frames=0)
        for key,value in list(s["measurements"].items()):
            if any(c.startswith("face_") for c in value["source_channels"]) or key.startswith("au_delta_"): s["measurements"][key]=missing(key,"face_missing",30)
    record("all_channels_missing_keeps_timeline_without_zero_scores",True,validate(r))
    # Strict JSON parsing must reject nonstandard constants and duplicate keys.
    for name,payload in [("duplicate_json_keys",'{"schema_version":"1.0.0","schema_version":"2.0.0"}'),("nonfinite_json",'{"x":NaN}')]:
        try: loads(payload); errors=[]
        except ValueError as exc: errors=[str(exc)]
        record(name,False,errors)
    report={"schema_version":"1.0.0","jsonschema_version":version("jsonschema"),
            "scope":"synthetic contract tests only; no deployed engine/API or cloud calls",
            "passed":sum(x["pass"] for x in results),"failed":sum(not x["pass"] for x in results),"cases":results}
    (ROOT/"contract_test_results.json").write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print(json.dumps({k:v for k,v in report.items() if k!="cases"},indent=2))
    for x in results:
        if not x["pass"]: print(x)
    raise SystemExit(bool(report["failed"]))
