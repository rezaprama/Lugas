#!/usr/bin/env python3
"""Score model-run outputs with the deterministic guard and Indonesian lint.

Context sizes are character counts of the instructions each condition loads.
Token figures are estimates (characters / 4) because no Claude tokenizer is
available offline; treat them as relative, not billing-grade.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from rhetorilex.guard import check, lint_id  # noqa: E402

RUNS = ROOT / "benchmarks" / "model-runs"


def main() -> int:
    tasks = {t["id"]: t for t in json.loads((RUNS / "tasks-v1.json").read_text())["tasks"]}
    context = json.loads((RUNS / "context-sizes.json").read_text())
    report = {}
    for path in sorted(RUNS.glob("run-*.json")):
        run = json.loads(path.read_text())
        cond = run["condition"]
        rows = []
        for out in run["outputs"]:
            t = tasks[out["id"]]
            translation = t["lang"] in {"id-en", "en-id"}
            summary = t["task"] in {"ringkas", "summary"}
            f = check(t["source"], out["rewrite"], translation=translation, summary=summary)
            out_lang_id = t["lang"] == "id"
            lint = [h for h in lint_id(out["rewrite"]) if h["level"] == "K"] if out_lang_id else []
            src_lint = [h for h in lint_id(t["source"]) if h["level"] == "K"] if out_lang_id else []
            rows.append({
                "id": out["id"],
                "high": [x.code for x in f if x.severity == "high"],
                "medium": [x.code for x in f if x.severity == "medium"],
                "lint_k_source": len(src_lint),
                "lint_k_output": len(lint),
                "response_chars": len(out["response"]),
                "rewrite_chars": len(out["rewrite"]),
            })
        n = len(rows)
        ctx = context[cond]
        report[cond] = {
            "items": n,
            "items_with_high_finding": sum(bool(r["high"]) for r in rows),
            "high_findings": sum(len(r["high"]) for r in rows),
            "medium_findings": sum(len(r["medium"]) for r in rows),
            "id_lint_k_remaining": sum(r["lint_k_output"] for r in rows),
            "id_lint_k_in_sources": sum(r["lint_k_source"] for r in rows),
            "mean_response_chars": round(sum(r["response_chars"] for r in rows) / n),
            "context_chars_per_call": ctx,
            "est_input_overhead_tokens_per_call": round(ctx / 4),
            "est_output_tokens_mean": round(sum(r["response_chars"] for r in rows) / n / 4),
            "rows": rows,
        }
    (RUNS / "scores-v1.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    for cond, r in report.items():
        print(cond, {k: v for k, v in r.items() if k != "rows"})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
