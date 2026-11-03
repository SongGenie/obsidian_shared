#include "analysis_session.h"
#include "json.hpp"
#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <thread>
using json = nlohmann::json;

// Same fixed label mapping; no inference implementation linked.
const char* affect_emotion_label(int i) {
    static const char* names[] = {"Anger", "Disgust", "Fear", "Happiness", "Neutral", "Sadness", "Surprise"};
    return i >= 0 && i < 7 ? names[i] : "Unknown";
}
int main() {
    json checks = json::array();
    int failed = 0;
    auto check = [&](bool ok, const char* label) {
        checks.push_back({{"check", label}, {"pass", ok}});
        if (!ok) ++failed;
    };
    auto near = [](double a, double b) { return std::abs(a-b) < 0.011; };
    AnalysisSession s;
    AnalysisSession::Summary sum;
    check(!s.finish(sum), "inactive session has no summary");
    s.start("empty");
    check(!s.finish(sum), "zero frame session has no summary");
    check(!s.active(), "empty finish closes session");
    s.start("discard");
    s.discard();
    check(!s.active() && !s.finish(sum), "discard closes without summary");

    FaceAnalysisResult f;
    f.detection_success = true;
    f.certainty = 0.95f;
    f.aus_intensity = {{"06", 1.0}, {"12", 2.0}};
    AffectFrameMetrics a;
    a.valid = a.reliable = true;
    a.gaze_valid = true;
    a.is_screen_gaze = true;
    a.valence = 0.3;
    a.arousal = 0.1;
    a.interest = 60;
    a.engagement = 60;
    a.tension = 20;
    a.fused_probs[4] = 1.0;
    s.start("synthetic-normal");
    for (int i = 0; i < 3; ++i) {
        a.attention = 20 + 40*i;
        f.aus_intensity[0].second = 1 + i;
        if (i == 2) { a.fused_probs[4] = 0; a.fused_probs[3] = 1; }
        s.record(f,a);
        if (i < 2) std::this_thread::sleep_for(std::chrono::milliseconds(1050));
    }
    a.reliable = false;
    s.record(f,a); // detected but unreliable
    f.detection_success = false;
    s.record(f,a); // not detected
    s.record_speech("synthetic positive utterance", 0.4);
    check(s.finish(sum), "normal summary generated");
    auto j = json::parse(sum.llm_summary_json);
    auto display = json::parse(sum.display_summary_json);
    check(j["frames_collected"] == 5, "frame count includes detected and missing");
    check(near(j["face_detected_ratio"], 0.8), "detection denominator is all frames");
    check(near(j["reliable_face_ratio"], 0.75), "reliability denominator is detected frames");
    check(near(j["attention_summary"]["mean"], 60), "unreliable samples excluded from average");
    check(j["attention_summary"]["level"] == "moderate", "score 60 classified moderate");
    check(j["attention_summary"]["trend"]["label"] == "rising", "bucket first/second half trend rising");
    check(near(j["attention_summary"]["trend"]["delta"], 60), "trend uses bucket halves rather than endpoints");
    check(near(j["au_mean"]["AU06"], 2), "AU mean uses trusted frames");
    check(near(j["au_peak"]["AU06"], 3), "AU peak preserved");
    check(near(j["emotion_distribution"]["Neutral"], 0.67), "emotion distribution counts bucket winners");
    check(j["dominant_timeline"].size() == 2, "timeline contains emotion transitions only");
    check(j["speech_count"] == 1 && j["speech"].size() == 1, "final transcript included");
    check(display["prompt_state"].contains("guidance") && !j["prompt_state"].contains("guidance"), "guidance removed only from LLM payload");
    check(!j.contains("affect_timeline") && !j.contains("voice") && !j.contains("landmarks2D"), "LLM payload omits full timeline voice raw and landmarks");
    check(!s.active() && !s.finish(sum), "second finish does not replay stored result");
    std::ofstream("synthetic_session_summary.json") << j.dump(2);

    s.start("unreliable-only");
    f.detection_success = true;
    a.reliable = false;
    s.record(f,a);
    s.finish(sum);
    auto missing = json::parse(sum.llm_summary_json);
    check(missing["prompt_state"]["confidence"] == "insufficient", "unreliable-only confidence insufficient");
    check(missing["attention_summary"]["mean"] == 0 && missing["attention_summary"]["level"] == "low", "current gap: no trusted data serialized as zero/low");
    std::ofstream("unreliable_only_summary.json") << missing.dump(2);

    s.start("before-restart");
    a.reliable = true;
    s.record(f,a);
    auto restart = s.start("after-restart");
    check(restart.restarted, "active start reports restart");
    check(!s.finish(sum), "restart drops previous samples");
    json report = {{"scope", "Original C++ session aggregation with synthetic metrics; no inference or network"},
                   {"checks", checks}, {"failed", failed}, {"passed", checks.size()-failed}};
    std::ofstream("session_test_results.json") << report.dump(2);
    std::cout << report.dump(2) << std::endl;
    return failed ? 1 : 0;
}
