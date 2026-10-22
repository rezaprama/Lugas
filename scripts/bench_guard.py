#!/usr/bin/env python3
"""Score the meaning guard against the frozen meaning-guard benchmark.

Compares the current guard (src/rhetorilex/guard.py) with a faithful Python port of
the v0.2.0 workbench check (English regex invariants, max 40 items, substring match).
Writes a JSON report; prints a short table.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhetorilex.guard import check  # noqa: E402


def legacy_invariants(source: str) -> list[str]:
    """Port of docs/app.js extractInvariants() at v0.2.0."""
    values: list[str] = []

    def add(pattern: str, flags: int = 0) -> None:
        for m in re.finditer(pattern, source, flags):
            v = m.group(0).strip()
            if v and v not in values:
                values.append(v)

    add(r"\([A-Z][^()]{0,90}\d{4}[a-z]?[^()]*\)")
    add(r"\[[0-9,\s-]+\]")
    add(r"\b\d+(?:[.,]\d+)?(?:\s?(?:%|percent|weeks?|months?|years?|days?|kg|g|mg|ml|cm|mm|m|n|p|CI|OR|RR|HR))?\b", re.I)
    add(r"\b(no|not|without|never|cannot|only|within|under|may|might|could|suggests?|associated with|correlated with|predicts?|causes?|caused|led to|increased|decreased|reduced)\b", re.I)
    return values[:40]


def legacy_flags(source: str, rewrite: str) -> list[str]:
    out = rewrite.casefold()
    return [item for item in legacy_invariants(source) if item.casefold() not in out]


def run(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for case in data["cases"]:
        translation = case["lang"] in {"id-en", "en-id"}
        summary = case["task"] in {"ringkas", "summarise", "summary"}
        good = check(case["source"], case["good"], translation=translation, summary=summary)
        rows.append({
            "case": case["id"], "kind": "good",
            "new_flag": any(f.severity == "high" for f in good),
            "new_codes": [f.code for f in good],
            "legacy_flag": bool(legacy_flags(case["source"], case["good"])),
        })
        for i, bad in enumerate(case["bad"], 1):
            found = check(case["source"], bad["rewrite"], translation=translation, summary=summary)
            codes = {f.code for f in found if f.severity in {"high", "medium"}}
            rows.append({
                "case": f"{case['id']}.{i}", "kind": "bad",
                "new_flag": bool(codes),
                "new_codes": sorted(codes),
                "expected": bad["expect"],
                "expected_hit": sorted(set(bad["expect"]) & codes),
                "legacy_flag": bool(legacy_flags(case["source"], bad["rewrite"])),
            })
    bads = [r for r in rows if r["kind"] == "bad"]
    goods = [r for r in rows if r["kind"] == "good"]
    expected_total = sum(len(r["expected"]) for r in bads)
    expected_hit = sum(len(r["expected_hit"]) for r in bads)
    summary = {
        "benchmark": f"{data['benchmark']} {data['version']}",
        "cases": len(goods),
        "bad_rewrites": len(bads),
        "new_detection_rate": round(sum(r["new_flag"] for r in bads) / len(bads), 3),
        "new_expected_code_recall": round(expected_hit / expected_total, 3),
        "new_false_positive_rate_on_good": round(sum(r["new_flag"] for r in goods) / len(goods), 3),
        "legacy_detection_rate": round(sum(r["legacy_flag"] for r in bads) / len(bads), 3),
        "legacy_false_positive_rate_on_good": round(sum(r["legacy_flag"] for r in goods) / len(goods), 3),
    }
    return {"summary": summary, "rows": rows}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=ROOT / "benchmarks" / "meaning-guard-v1.json")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    report = run(args.fixture)
    if args.output:
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    for key, value in report["summary"].items():
        print(f"{key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
