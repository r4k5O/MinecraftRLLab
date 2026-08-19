from __future__ import annotations
from .models import GlossaryEntry


def glossary_entries(tr) -> tuple[GlossaryEntry, ...]:
    result = []
    for term_id in ("agent", "reward", "epsilon", "episode"):
        result.append(GlossaryEntry(term_id, tr.text(f"glossary.{term_id}.term"), tr.text(f"glossary.{term_id}.explanation"), tr.text(f"glossary.{term_id}.kids")))
    return tuple(result)
