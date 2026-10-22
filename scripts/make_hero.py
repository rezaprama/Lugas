#!/usr/bin/env python3
"""Render the 1200x630 social preview from the built English home page."""

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import shutil
import threading

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


class Quiet(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        return


server = ThreadingHTTPServer(("127.0.0.1", 8781), partial(Quiet, directory=str(ROOT / "docs")))
threading.Thread(target=server.serve_forever, daemon=True).start()
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630})
    page.emulate_media(color_scheme="light")
    page.goto("http://127.0.0.1:8781/en/")
    page.wait_for_load_state("networkidle")
    page.screenshot(path=str(ROOT / "assets" / "lugas-hero.png"))
    browser.close()
server.shutdown()
shutil.copyfile(ROOT / "assets" / "lugas-hero.png", ROOT / "docs" / "assets" / "lugas-hero.png")
print("wrote assets/lugas-hero.png")
