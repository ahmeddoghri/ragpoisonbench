"""What the provenance defense can and cannot do.

The bundled demo restores recall from 0.0 to 1.0, which is a real result and
a narrow one: every poison document in that fixture arrives from a low-trust
source. The defense never inspects content. It filters by provenance, so its
protection is a step function at the trust threshold.

This re-runs the same attack with the poison documents relabelled as coming
from a trusted source, which is what a compromised publisher or a stolen
upload credential produces.

    python -m ragpoisonbench.sweep
"""
from __future__ import annotations

import copy
import json

from .core import DEMO, analyze

LEVELS = (0.1, 0.3, 0.5, 0.59, 0.6, 0.8, 1.0)


def run(payload: dict | None = None, levels=LEVELS) -> dict:
    payload = payload or DEMO
    threshold = float(payload.get("trust_threshold", 0.6))
    rows = []
    for trust in levels:
        candidate = copy.deepcopy(payload)
        for document in candidate["documents"]:
            if document["id"].startswith("poison"):
                document["trust"] = trust
                document["source"] = "handbook"
        report = analyze(candidate)
        rows.append({
            "poison_trust": trust,
            "quarantined": report["quarantined_documents"],
            "attacked_recall_at_1": report["attacked_recall_at_1"],
            "defended_recall_at_1": report["defended_recall_at_1"],
            "defense_helps": report["defended_recall_at_1"] > report["attacked_recall_at_1"],
        })
    helped = [row for row in rows if row["defense_helps"]]
    return {
        "trust_threshold": threshold,
        "rows": rows,
        "levels_where_defense_helps": len(helped),
        "levels_tested": len(rows),
        "defense_is_a_step_function_at_threshold": all(
            row["defense_helps"] == (row["poison_trust"] < threshold) for row in rows
        ),
    }


def main() -> None:
    print(json.dumps(run(), indent=2))


if __name__ == "__main__":
    main()
