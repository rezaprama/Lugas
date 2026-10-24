"""RhetoriLex -> Lugas migration keeps old imports and commands working."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys
import unittest
import warnings

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))


class CompatibilityTests(unittest.TestCase):
    def test_old_import_reexports_new_api(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            sys.modules.pop("rhetorilex", None)
            import rhetorilex  # noqa: PLC0415
        import lugas  # noqa: PLC0415

        self.assertIs(rhetorilex.Catalog, lugas.Catalog)
        self.assertEqual(rhetorilex.__version__, lugas.__version__)
        self.assertTrue(any(issubclass(w.category, DeprecationWarning) for w in caught))
        self.assertEqual(rhetorilex.Catalog.load().get("RLX-QUA-001").id, "RLX-QUA-001")

    def test_old_module_entrypoint_runs(self) -> None:
        env = {"PYTHONPATH": str(ROOT / "src")}
        for module in ("rhetorilex", "lugas"):
            result = subprocess.run(
                [sys.executable, "-W", "ignore", "-m", module, "explain", "RLX-QUA-001"],
                capture_output=True, text=True, env=env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("RLX-QUA-001", result.stdout)

    def test_both_console_scripts_declared(self) -> None:
        text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('lugas = "lugas.cli:main"', text)
        self.assertIn('rhetorilex = "lugas.cli:main"', text)

    def test_stable_ids_unchanged(self) -> None:
        import lugas  # noqa: PLC0415

        ids = {entry.id for entry in lugas.Catalog.load().entries}
        self.assertEqual(len(ids), 96)
        self.assertTrue(all(i.startswith("RLX-") for i in ids))


if __name__ == "__main__":
    unittest.main()
