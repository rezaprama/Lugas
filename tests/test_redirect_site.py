from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from scripts.build_redirect_site import build, routes


class RedirectSiteTests(unittest.TestCase):
    def test_build_preserves_lugas_cache_and_creates_route_redirects(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "redirects"
            route_count = build(output)

            self.assertEqual(route_count, len(routes()))
            self.assertTrue((output / "index.html").is_file())
            self.assertTrue((output / "id" / "alat-parafrasa" / "index.html").is_file())
            self.assertTrue((output / "404.html").is_file())
            self.assertTrue((output / "data" / "phrases.json").is_file())

            service_worker = (output / "service-worker.js").read_text(encoding="utf-8")
            self.assertIn('const LEGACY_CACHE_PREFIX = "rhetorilex-pwa-";', service_worker)
            self.assertIn("key.startsWith(LEGACY_CACHE_PREFIX)", service_worker)
            self.assertNotIn("keys.map((key) => caches.delete(key))", service_worker)


if __name__ == "__main__":
    unittest.main()
