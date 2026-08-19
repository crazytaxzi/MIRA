from __future__ import annotations
from provenance_state import ProvenanceState


def render_durable_subject(state: ProvenanceState, subject: str) -> str:
    """Project only established autobiographical state into aged working memory."""
    predicates = sorted({
        e.predicate for e in state.evidence
        if e.subject == subject and e.scope == "reality"
    })
    lines: list[str] = []
    for predicate in predicates:
        resolved = state.resolve(subject, predicate)
        if resolved["status"] == "established":
            lines.append(
                f"- {subject}.{predicate} = {resolved['value']!r} (supported)"
            )
    if not lines:
        return f"- No established {subject} facts in this state."
    return "\n".join(lines)
