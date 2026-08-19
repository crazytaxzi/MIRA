from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "memory"))
from provenance_state import ProvenanceState
from durable_view import render_durable_subject


def test_durable_view_omits_repeated_unsupported_self_story():
    s = ProvenanceState()
    for i in range(5):
        t = s.record_utterance("Mira", "I worked in a hotel.", f"m{i}")
        s.add_generated_self_claim("worked_in_hotel", True, t)
    assert "worked_in_hotel" not in render_durable_subject(s, "Mira")


def test_durable_view_keeps_supported_lived_fact():
    s = ProvenanceState()
    t = s.record_utterance("Mira", "I like rain.", "m1")
    s.add_self_report("Mira", "likes_rain", True, t, note="supported lived episode")
    view = render_durable_subject(s, "Mira")
    assert "likes_rain" in view
    assert "supported" in view


def test_correction_preserves_history_but_omits_superseded_claim():
    s = ProvenanceState()
    t1 = s.record_utterance("Mira", "I have chores too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, t1)
    t2 = s.record_utterance("Cinder", "Those are mine, not yours.", "c1")
    s.supersede(bad, t2, "Cinder", "ownership correction")
    view = render_durable_subject(s, "Mira")
    assert "has_pending_chores" not in view
    assert any(u.turn_id == "m1" and "chores" in u.text for u in s.utterances)
    assert any(e.id == bad and e.superseded for e in s.evidence)
