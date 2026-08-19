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


def _render_focus(state: ProvenanceState, subject: str, predicate: str) -> str:
    reality = [e for e in state.evidence
               if e.subject == subject and e.predicate == predicate
               and e.scope == "reality" and not e.superseded]
    play = [e for e in state.evidence
            if e.subject == subject and e.predicate == predicate
            and e.scope != "reality" and not e.superseded]
    if reality:
        r = state.resolve(subject, predicate)
        if r["status"] == "established":
            return f"- {subject} {_phrase(predicate, r['value'])}."
        if r["status"] == "conflict":
            return f"- Memory is unsettled about whether {subject} {predicate.replace('_', ' ')}."
        return f"- A claim about whether {subject} {predicate.replace('_', ' ')} exists, but it is not settled."
    if play:
        return f"- {subject} {predicate.replace('_', ' ')} only within play or pretend; that is not a real-life memory."
    return f"- There is no remembered evidence that {subject} {predicate.replace('_', ' ')}."


def render_working_memory(state: ProvenanceState, subjects: Iterable[str],
                          focus: Iterable[tuple[str, str]] = ()) -> str:
    """Project compact scene memory; focus can request relevant unknown/play facts."""
    lines = ["Current remembered situation:"]
    rendered = set()
    for subject, predicate in focus:
        lines.append(_render_focus(state, subject, predicate))
        rendered.add((subject, predicate))
    for subject in subjects:
        predicates = sorted({e.predicate for e in state.evidence
                             if e.subject == subject and e.scope == "reality"})
        for predicate in predicates:
            if (subject, predicate) in rendered:
                continue
            r = state.resolve(subject, predicate)
            if r["status"] == "established":
                lines.append(f"- {subject} {_phrase(predicate, r['value'])}.")
            elif r["status"] == "candidate":
                ev = r["evidence"][0]
                lines.append(f"- {ev['source_speaker']} said {subject} {_phrase(predicate, r['value'])}; that is not settled memory.")
            elif r["status"] == "conflict":
                lines.append(f"- Accounts conflict about {subject} and {predicate.replace('_', ' ')}.")
        for old in [e for e in state.evidence if e.subject == subject and e.superseded]:
            lines.append(f"- An earlier claim that {subject} {_phrase(old.predicate, old.value)} was corrected and is no longer current.")
    return "\n".join(lines)
