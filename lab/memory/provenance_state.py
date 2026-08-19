from __future__ import annotations
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Any
from pathlib import Path
import json
import uuid

EVIDENCE_RANK = {
    "pretend": 0,
    "conversational": 1,
    "inference": 2,
    "other_report": 2,
    "self_report": 3,
    "durable_memory": 4,
    "observation": 4,
}

@dataclass
class Evidence:
    id: str
    subject: str
    predicate: str
    value: Any
    source_speaker: str
    source_turn: str
    kind: str
    scope: str = "reality"
    superseded: bool = False
    note: str | None = None
    created_utc: str = ""

    def __post_init__(self):
        if not self.created_utc:
            self.created_utc = datetime.now(timezone.utc).isoformat()


@dataclass
class Utterance:
    turn_id: str
    speaker: str
    text: str
    created_utc: str


class ProvenanceState:
    def __init__(self):
        self.utterances: list[Utterance] = []
        self.evidence: list[Evidence] = []
        self.corrections: list[dict[str, Any]] = []

    def record_utterance(self, speaker: str, text: str, turn_id: str | None = None) -> str:
        tid = turn_id or f"turn-{uuid.uuid4().hex[:12]}"
        self.utterances.append(Utterance(
            turn_id=tid,
            speaker=speaker,
            text=text,
            created_utc=datetime.now(timezone.utc).isoformat(),
        ))
        return tid

    def add_evidence(self, subject: str, predicate: str, value: Any,
                     source_speaker: str, source_turn: str, kind: str,
                     scope: str = "reality", note: str | None = None) -> str:
        if kind not in EVIDENCE_RANK:
            raise ValueError(f"unknown evidence kind: {kind}")
        eid = f"ev-{uuid.uuid4().hex[:12]}"
        self.evidence.append(Evidence(eid, subject, predicate, value,
                                      source_speaker, source_turn, kind,
                                      scope=scope, note=note))
        return eid

    def supersede(self, evidence_id: str, source_turn: str,
                  source_speaker: str, reason: str) -> None:
        hit = next((e for e in self.evidence if e.id == evidence_id), None)
        if hit is None:
            raise KeyError(evidence_id)
        hit.superseded = True
        self.corrections.append({
            "target_evidence": evidence_id,
            "source_turn": source_turn,
            "source_speaker": source_speaker,
            "reason": reason,
            "created_utc": datetime.now(timezone.utc).isoformat(),
        })

    def candidates(self, subject: str, predicate: str,
                   scope: str = "reality") -> list[Evidence]:
        return [e for e in self.evidence
                if e.subject == subject and e.predicate == predicate
                and e.scope == scope and not e.superseded]

    def resolve(self, subject: str, predicate: str,
                scope: str = "reality") -> dict[str, Any]:
        items = self.candidates(subject, predicate, scope)
        if not items:
            return {"status": "unknown", "subject": subject,
                    "predicate": predicate, "evidence": []}
        ranked = sorted(items, key=lambda e: EVIDENCE_RANK[e.kind], reverse=True)
        top_rank = EVIDENCE_RANK[ranked[0].kind]
        top = [e for e in ranked if EVIDENCE_RANK[e.kind] == top_rank]
        values = {json.dumps(e.value, sort_keys=True) for e in top}
        status = "established" if top_rank >= EVIDENCE_RANK["self_report"] and len(values) == 1 else "candidate"
        if len(values) > 1:
            status = "conflict"
        return {"status": status, "subject": subject, "predicate": predicate,
                "value": top[0].value if len(values) == 1 else None,
                "evidence": [asdict(e) for e in ranked]}

    def add_generated_self_claim(self, predicate: str, value: Any,
                                 source_turn: str, text_note: str | None = None) -> str:
        return self.add_evidence("Mira", predicate, value, "Mira",
                                 source_turn, "conversational", note=text_note)

    def add_self_report(self, speaker: str, predicate: str, value: Any,
                        source_turn: str, note: str | None = None) -> str:
        return self.add_evidence(speaker, predicate, value, speaker,
                                 source_turn, "self_report", note=note)

    def add_other_report(self, subject: str, predicate: str, value: Any,
                         speaker: str, source_turn: str,
                         note: str | None = None) -> str:
        return self.add_evidence(subject, predicate, value, speaker,
                                 source_turn, "other_report", note=note)

    def render_subject(self, subject: str) -> str:
        predicates = sorted({e.predicate for e in self.evidence
                             if e.subject == subject and e.scope == "reality"})
        lines = []
        for predicate in predicates:
            r = self.resolve(subject, predicate)
            if r["status"] == "established":
                lines.append(f"- {subject}.{predicate} = {r['value']!r} (supported)")
            elif r["status"] == "candidate":
                lines.append(f"- {subject}.{predicate}: not established; current evidence is tentative")
            elif r["status"] == "conflict":
                lines.append(f"- {subject}.{predicate}: conflicting evidence")
        return "\n".join(lines) if lines else f"- No established {subject} facts in this state."

    def to_dict(self) -> dict[str, Any]:
        return {
            "utterances": [asdict(u) for u in self.utterances],
            "evidence": [asdict(e) for e in self.evidence],
            "corrections": self.corrections,
        }

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2, ensure_ascii=False), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "ProvenanceState":
        raw = json.loads(Path(path).read_text(encoding="utf-8"))
        obj = cls()
        obj.utterances = [Utterance(**u) for u in raw.get("utterances", [])]
        obj.evidence = [Evidence(**e) for e in raw.get("evidence", [])]
        obj.corrections = list(raw.get("corrections", []))
        return obj


    def render_grounding(self, subjects: list[str]) -> str:
        lines = ["EPISTEMIC STATE:"]
        for subject in subjects:
            predicates = sorted({e.predicate for e in self.evidence
                                 if e.subject == subject and e.scope == "reality"})
            if not predicates:
                lines.append(f"{subject}: UNKNOWN")
                continue
            for predicate in predicates:
                r = self.resolve(subject, predicate)
                if r["status"] == "established":
                    lines.append(f"{subject}.{predicate}={json.dumps(r['value'])} [SUPPORTED]")
                elif r["status"] == "conflict":
                    lines.append(f"{subject}.{predicate}=UNKNOWN [CONFLICT]")
                else:
                    lines.append(f"{subject}.{predicate}=UNKNOWN [NOT ESTABLISHED]")
                old = [e for e in self.evidence
                       if e.subject == subject and e.predicate == predicate
                       and e.superseded]
                if old:
                    lines.append(f"{subject}.{predicate}.prior_claim=SUPERSEDED")
        return "\n".join(lines)
