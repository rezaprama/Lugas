"""The browser guard (docs/guard.js) must agree with the Python guard on every benchmark item."""

from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rhetorilex.guard import check  # noqa: E402

NODE_SCRIPT = r"""
const g = require(process.argv[1]);
const d = JSON.parse(require('fs').readFileSync(process.argv[2], 'utf8'));
const out = {};
for (const c of d.cases) {
  const o = { translation: ['id-en', 'en-id'].includes(c.lang), summary: ['ringkas', 'summary'].includes(c.task) };
  out[c.id] = g.check(c.source, c.good, o).map(f => f.severity + ':' + f.code);
  c.bad.forEach((b, i) => { out[c.id + '.' + (i + 1)] = g.check(c.source, b.rewrite, o).map(f => f.severity + ':' + f.code); });
}
process.stdout.write(JSON.stringify(out));
"""


@unittest.skipUnless(shutil.which("node"), "node is required for the parity test")
class GuardParityTests(unittest.TestCase):
    def test_python_and_browser_guard_agree(self) -> None:
        for name in ("meaning-guard-v1.json", "meaning-guard-heldout-v1.json"):
            fixture = ROOT / "benchmarks" / name
            result = subprocess.run(
                ["node", "-e", NODE_SCRIPT, str(ROOT / "docs" / "guard.js"), str(fixture)],
                capture_output=True, text=True, check=True,
            )
            js = json.loads(result.stdout)
            data = json.loads(fixture.read_text(encoding="utf-8"))
            for case in data["cases"]:
                opts = {"translation": case["lang"] in {"id-en", "en-id"}, "summary": case["task"] in {"ringkas", "summary"}}
                items = [(case["id"], case["good"])] + [(f"{case['id']}.{i + 1}", b["rewrite"]) for i, b in enumerate(case["bad"])]
                for key, rewrite in items:
                    with self.subTest(fixture=name, item=key):
                        py = [f"{f.severity}:{f.code}" for f in check(case["source"], rewrite, **opts)]
                        self.assertEqual(py, js[key])


if __name__ == "__main__":
    unittest.main()
