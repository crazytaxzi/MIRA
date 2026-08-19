from __future__ import annotations
from typing import Iterable
from provenance_state import ProvenanceState


def _phrase(predicate: str, value) -> str:
    words = predicate.replace("_", " ")
    if isinstance(value, bool):
        if words.startswith("has "):
            tail = words[4:]
            return f"has {tail}" if value else f"does not have {tail}"
        return words if value else f"not {words}"
    return f"{words} {value}"


def render_working_memory(state: ProvenanceState, subjects: Iterable[str]) -> str:
    """Turn provenance into compact scene memory rather than control instructions."""
    lines = ["Current remembered situation:"]
    for subject in subjects:
        predicates = sorted({
            e.predicate for e in state.evidence
            if e.subject == subject and e.scope == "reality"
        })
        for predicate in predicates:
            r = state.resolve(subject, predicate)
            if r["status"] == "established":
                lines.append(f"- {subject} {_phrase(predicate, r['value'])}.")
            elif r["status"] == "candidate":
                ev = r["evidence"][0]
                source = ev["source_speaker"]
                lines.append(
                    f"- {source} said {subject} {_phrase(predicate, r['value'])}; "
                    "that has not become a settled memory."
                )
            elif r["status"] == "conflict":
                words = predicate.replace("_", " ")
                lines.append(f"- Accounts conflict about {subject} and {words}.")

        corrected = [e for e in state.evidence if e.subject == subject and e.superseded]
        for old in corrected:
            lines.append(
                f"- An earlier claim that {subject} {_phrase(old.predicate, old.value)} "
                "was corrected and is no longer current."
            )
    return "\n".join(lines)
