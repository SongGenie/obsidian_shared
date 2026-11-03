"""Build the deterministic v1 result contract; standard library only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def obj(properties, required=None, **extra):
    return {"type": "object", "properties": properties, "required": list(properties) if required is None else required,
            "additionalProperties": False, **extra}

def enum(*values): return {"enum": list(values)}
def ref(name): return {"$ref": f"#/$defs/{name}"}
def arr(item, **extra): return {"type": "array", "items": item, **extra}
def nullable(schema): return {"anyOf": [schema, {"type": "null"}]}
ID = {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9_.:-]{0,127}$"}
TEXT = {"type": "string", "minLength": 1}
SEC = {"type": "number", "minimum": 0}
COUNT = {"type": "integer", "minimum": 0}
CHANNELS = ["face_model", "face_au", "voice", "language"]
REASONS = ["face_missing", "low_quality", "baseline_missing", "baseline_not_ready", "audio_missing",
           "no_speech", "not_voiced", "nonparticipant_audio", "stt_unavailable", "redacted",
           "not_supported", "processing_error", "disabled", "unknown"]
AU = ["01","02","04","05","06","07","09","10","12","14","15","17","20","23","25","26","45"]
EMOTIONS = ["Anger","Disgust","Fear","Happiness","Neutral","Sadness","Surprise"]

# Each key has a fixed unit and range; total/valid samples share a method-defined denominator.
SPECS = {k: ("score_0_100", 0, 100) for k in ["attention","interest","engagement","tension"]}
SPECS.update({k: ("normalized", -1, 1) for k in ["valence","arousal","language_valence","language_arousal"]})
SPECS.update({"voice_pitch_hz": ("Hz", 0.000001, None), "voice_energy_dbfs": ("dBFS", -160, 0),
              "voice_rate_sps": ("syllables_per_sec", 0, None), "voice_arousal": ("normalized",0,1)})
SPECS.update({f"au_{kind}_AU{au}": ("AU_0_5",0,5) for kind in ["raw","delta"] for au in AU})
SPECS.update({f"emotion_{emo}": ("probability",0,1) for emo in EMOTIONS})
CORE = ["attention","interest","engagement","tension","valence","arousal",
        "voice_pitch_hz","voice_energy_dbfs","voice_rate_sps","language_valence","language_arousal"]

defs = {}
defs["range"] = obj({"start_sec": SEC, "end_sec": SEC})
defs["timing"] = obj({"recording": ref("range"), "content": nullable(ref("range")), "mapping_id": nullable(ID)})
for key, (unit, low, high) in SPECS.items():
    number = {"type":"number", "minimum": low}
    if high is not None: number["maximum"] = high
    score = unit == "score_0_100"
    defs[f"metric_{key}"] = obj({
        "status": enum("available","unavailable","not_applicable","error"),
        "value": nullable(number), "unit": {"const":unit}, "reason": nullable(enum(*REASONS)),
        "valid_samples": COUNT, "total_samples": COUNT, "valid_duration_sec": SEC,
        "method_id": ID,
        "source_channels": arr(enum(*CHANNELS), uniqueItems=True),
        "level": enum("high","moderate","low","unavailable") if score else {"type":"null"}
    }, allOf=[{
        "if": {"properties":{"status":{"const":"available"}}},
        "then": {"properties":{"value":number,"reason":{"type":"null"},"valid_samples":{"minimum":1},
                                 "valid_duration_sec":{"exclusiveMinimum":0},
                                 "source_channels":{"minItems":1}, **({"level":enum("high","moderate","low")} if score else {})}},
        "else": {"properties":{"value":{"type":"null"},"reason":enum(*REASONS),"valid_samples":{"const":0},
                                 "valid_duration_sec":{"const":0}, "source_channels":{"maxItems":0}, **({"level":{"const":"unavailable"}} if score else {})}}
    }])
defs["method"] = obj({"kind": enum("model_inference","signal_processing","heuristic","lexicon"),
                      "version": TEXT, "model_ref": nullable(TEXT),
                      "source_channels": arr(enum(*CHANNELS), minItems=1, uniqueItems=True),
                      "sample_unit": enum("video_frame","audio_frame","utterance","time_bin")})
defs["mapping"] = obj({"id": ID,"recording":ref("range"),"content_start_sec":SEC,
                       "uncertainty_sec": SEC,"method":enum("sync_marker","manual_verified","embedded_timestamp")})
defs["segment"] = obj({
    "id":ID, "timing":ref("timing"),
    "face_quality":obj({"total_frames":COUNT,"detected_frames":COUNT,"trusted_frames":COUNT}),
    "audio":obj({"state":enum("speech","silence","unavailable","not_processed","error","excluded"),
                 "reason":nullable(enum(*REASONS)),"coverage_duration_sec":SEC,"speech_duration_sec":nullable(SEC)}),
    "transcript":obj({"state":enum("available","no_speech","unavailable","not_processed","error","redacted"),
                      "reason":nullable(enum(*REASONS)),"utterance_ids":arr(ID,uniqueItems=True)}),
    "measurements":obj({k:ref(f"metric_{k}") for k in SPECS}, required=CORE)
})
defs["utterance"] = obj({"id":ID,"timing":nullable(ref("timing")),
    "timing_status":enum("aligned","unavailable"), "text":nullable(TEXT),"redacted":{"type":"boolean"},
    "stt_method_id":ID,"stt_confidence":nullable({"type":"number","minimum":0,"maximum":1}),
    "observed_at":{"type":"string","format":"date-time"},
    "matched_terms":arr(obj({"term":TEXT,"polarity":enum("positive","negative","mixed")}))},
    allOf=[{"if":{"properties":{"timing_status":{"const":"aligned"}}},
            "then":{"properties":{"timing":ref("timing")}},"else":{"properties":{"timing":{"type":"null"}}}},
           {"if":{"properties":{"redacted":{"const":True}}},"then":{"properties":{"text":{"type":"null"},"matched_terms":{"maxItems":0}}},
            "else":{"properties":{"text":TEXT}}}])
defs["event"] = obj({"id":ID,"kind":enum("metric_peak","duchenne_smile_pattern","social_smile_pattern","brow_raise","gaze_away","tension_spike","channel_disagreement"),
                     "timing":ref("timing"),"peak_recording_sec":nullable(SEC),
                     "metric_key":nullable(enum(*SPECS)),"value":nullable({"type":"number"}),
                     "evidence_segment_ids":arr(ID,minItems=1,uniqueItems=True)})

schema = obj({
    "schema_version":{"const":"1.0.0"},"data_origin":enum("observed","synthetic"),
    "analysis_id":ID,"test_id":ID,"participant_id":ID,"generated_at":{"type":"string","format":"date-time"},
    "recording":obj({"id":ID,"duration_sec":{"type":"number","exclusiveMinimum":0}}),
    "content":obj({"id":ID,"version":TEXT,"duration_sec":{"type":"number","exclusiveMinimum":0}}),
    "audio_source":obj({"id":nullable(ID),"origin":enum("recording_track","external_track","none"),
                        "duration_sec":nullable({"type":"number","exclusiveMinimum":0}),
                        "attribution":enum("participant_confirmed","content_only","mixed","unknown","not_applicable"),
                        "alignment_status":enum("aligned","unknown","not_applicable"),"offset_to_recording_sec":nullable({"type":"number"})}),
    "baseline":obj({"status":enum("captured","unavailable","disabled"),"recording":nullable(ref("range"))}),
    "methods":{"type":"object","propertyNames":ID,"additionalProperties":ref("method"),"minProperties":1},
    "content_mappings":arr(ref("mapping")),"segments":arr(ref("segment"),minItems=1),
    "utterances":arr(ref("utterance")),"events":arr(ref("event")),
    "limitations":arr(TEXT,uniqueItems=True)
}, **{"$schema":"https://json-schema.org/draft/2020-12/schema",
      "$id":"urn:ableai:emoai:analysis-result:1.0.0",
      "title":"EmoAI single-participant recording result v1", "$defs":defs})

if __name__ == "__main__":
    (ROOT / "analysis-result.schema.json").write_text(json.dumps(schema,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Wrote analysis-result.schema.json")
