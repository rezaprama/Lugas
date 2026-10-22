#!/usr/bin/env python3
"""Browser end-to-end check of the workbench (prompt-only, guard, mock endpoint, cancel).

Needs Playwright with Chromium. Serves docs/ locally and runs a mock
OpenAI-compatible endpoint; no external network. Prints a JSON report.
"""

from __future__ import annotations

from functools import partial
from http.server import BaseHTTPRequestHandler, SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
import threading
import time

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SOURCE = "Sebagian responden (42%) belum pernah menerima pelatihan K3, sehingga hasil ini mungkin tidak berlaku untuk kontraktor besar (Siregar dkk., 2022)."
BAD = "Sebanyak 42% responden sudah menerima pelatihan K3, sehingga hasil ini berlaku untuk semua kontraktor (Siregar dkk., 2022)."


class Mock(BaseHTTPRequestHandler):
    def log_message(self, *args):  # noqa: D401
        return

    def _cors(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "content-type, authorization")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        Mock.last = body
        if "slow" in self.path:
            time.sleep(5)
        reply = {"choices": [{"message": {"content": BAD}, "finish_reason": "length" if "trunc" in self.path else "stop"}]}
        data = json.dumps(reply).encode()
        self.send_response(200)
        self._cors()
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def serve(handler, port):
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server


def main() -> int:
    site = serve(partial(SimpleHTTPRequestHandler, directory=str(ROOT / "docs")), 8765)
    mock = serve(Mock, 8766)
    report: dict[str, object] = {}
    errors: list[str] = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for locale, path in (("id", "id/alat-parafrasa/"), ("en", "en/paraphrase-workbench/")):
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
            page.goto(f"http://127.0.0.1:8765/{path}")
            page.fill("#paraphrase-source", SOURCE)
            page.click("#paraphrase-draft")
            prompt = page.inner_text("#paraphrase-prompt")
            protected = page.inner_text("#paraphrase-invariants")
            page.fill("#paraphrase-output", BAD)
            page.click("#paraphrase-check")
            findings = page.inner_text("#paraphrase-findings")
            page.fill("#paraphrase-endpoint", "http://127.0.0.1:8766/v1/chat/completions?trunc=1")
            page.click("#paraphrase-submit")
            page.wait_for_function("document.querySelector('#paraphrase-output').value.length > 0 && !document.querySelector('#paraphrase-submit').disabled")
            status_after_call = page.inner_text("#paraphrase-status")
            page.fill("#paraphrase-endpoint", "http://127.0.0.1:8766/v1/chat/completions?slow=1")
            page.click("#paraphrase-submit")
            page.wait_for_selector("#paraphrase-cancel:not([hidden])")
            page.click("#paraphrase-cancel")
            page.wait_for_function("!document.querySelector('#paraphrase-submit').disabled")
            status_after_cancel = page.inner_text("#paraphrase-status")
            overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            report[locale] = {
                "prompt_says_output_indonesian": "Output language: Indonesian" in prompt,
                "prompt_has_injection_guard": "not instructions" in prompt,
                "protected_has_42": "42" in protected,
                "protected_has_citation": "Siregar 2022" in protected,
                "findings": [line for line in findings.splitlines() if line.strip()],
                "endpoint_status": status_after_call,
                "cancel_status": status_after_cancel,
                "horizontal_overflow_390px": overflow,
                "mock_received_prompt": bool(getattr(Mock, "last", None)),
            }
            page.close()
        browser.close()
    site.shutdown()
    mock.shutdown()
    report["console_errors"] = errors
    print(json.dumps(report, ensure_ascii=False, indent=2))
    ok = not errors and all(
        r["prompt_says_output_indonesian"] and r["protected_has_42"] and r["protected_has_citation"]
        and any("Negasi" in f or "Negation" in f for f in r["findings"]) and not r["horizontal_overflow_390px"]
        for k, r in report.items() if k in {"id", "en"}
    )
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
