from pathlib import Path
import tempfile
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "memory"))
from provenance_state import ProvenanceState


def test_generated_self_claim_is_not_automatically_autobiography():
    s = ProvenanceState()
    t = s.record_utterance("Mira", "Haha. Me too.", "m1")
    s.add_generated_self_claim("has_pending_chores", True, t, "social mirror")
    r = s.resolve("Mira", "has_pending_chores")
    assert r["status"] == "candidate"
    assert r["value"] is True


def test_correction_can_supersede_bad_self_evidence_without_erasing_history():
    s = ProvenanceState()
    mt = s.record_utterance("Mira", "I have chores too.", "m1")
    bad = s.add_generated_self_claim("has_pending_chores", True, mt)
    ct = s.record_utterance("Cinder", "That's mine, not yours.", "c1")
    s.supersede(bad, ct, "Cinder", "speaker corrected ownership")
    s.add_other_report("Mira", "has_pending_chores", False, "Cinder", ct)
    r = s.resolve("Mira", "has_pending_chores")
    assert r["status"] == "candidate"
    assert r["value"] is False
    assert any(e.id == bad and e.superseded for e in s.evidence)
    assert len(s.corrections) == 1


def test_other_speaker_self_report_is_grounded_for_that_speaker():
    s = ProvenanceState()
    t = s.record_utterance("Cinder", "I have a pile of chores.", "c1")
    s.add_self_report("Cinder", "has_pending_chores", True, t)
    r = s.resolve("Cinder", "has_pending_chores")
    assert r["status"] == "established"
    assert r["value"] is True
    assert s.resolve("Mira", "has_pending_chores")["status"] == "unknown"


def test_supported_mira_fact_can_be_established_explicitly():
    s = ProvenanceState()
    t = s.record_utterance("Mira", "I like rain.", "m1")
    s.add_self_report("Mira", "likes_rain", True, t,
                      note="promoted by the learning layer, not raw generation alone")
    r = s.resolve("Mira", "likes_rain")
    assert r["status"] == "established"
    assert r["value"] is True


def test_pretend_claim_does_not_leak_into_reality():
    s = ProvenanceState()
    t = s.record_utterance("Mira", "Arrr, I'm a pirate.", "m1")
    s.add_evidence("Mira", "is_pirate", True, "Mira", t, "pretend", scope="play:pirate")
    assert s.resolve("Mira", "is_pirate")["status"] == "unknown"
    play = s.resolve("Mira", "is_pirate", scope="play:pirate")
    assert play["status"] == "candidate"


def test_round_trip_preserves_supersession_and_raw_utterance():
    s = ProvenanceState()
    mt = s.record_utterance("Mira", "Me too.", "m1")
    eid = s.add_generated_self_claim("was_washing_dishes", True, mt)
    ct = s.record_utterance("Cinder", "No, that was me.", "c1")
    s.supersede(eid, ct, "Cinder", "ownership correction")
    with tempfile.TemporaryDirectory() as td:
        p = Path(td) / "state.json"
        s.save(p)
        r = ProvenanceState.load(p)
    assert [u.text for u in r.utterances] == ["Me too.", "No, that was me."]
    assert r.evidence[0].superseded is True
    assert r.corrections[0]["target_evidence"] == eid
