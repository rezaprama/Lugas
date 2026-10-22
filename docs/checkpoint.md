# Checkpoint (handoff for the next session)

Last updated: 22 October 2026, v0.3.0 release work.

## Done

- Baseline re-verified from source and tests (69 → 87 tests now).
- Offline meaning guard (Python, skill copy, browser port with parity test) and Indonesian lint.
- Workbench: job and output-language selectors, Indonesian output, compact prompt (−27%), paste-and-check, timeout/cancel/truncation/CORS handling, no daily cap.
- Skill rewritten (scope table, protected-element lock, `bahasa-indonesia.md`, lean replies).
- Benchmarks: guard dev + independent held-out sets; model runs A/B/C/C2 with blind judging; prompt size; browser E2E. See `docs/benchmarks.md`.
- naskah-id adoption matrix: `docs/naskah-id-matrix.md`.
- Name chosen by maintainer: **Lugas** (`docs/brand/naming-2026-10.md`). Rename applied in code, site, docs, plugin, CITATION; aliases kept.
- Redirect-site generator for the old Pages path: `scripts/build_redirect_site.py`.

## Decisions

- Hosting stays on GitHub Pages (no Cloudflare credentials in session; no new costs).
- Removed the 3/day browser cap; no hosted shared-key AI service (would need backend, quota, abuse protection; not justified yet).
- Dataset files (`rhetorilex-v0.2.*`), `RLX-*` IDs, and format identifiers stay unchanged until a data release.
- Generated redirect site is not committed (`migration/rhetorilex-pages/` is ignored); it is pushed to its own repository.

## Release status and blockers

See the release notes in `CHANGELOG.md` and the session report. Items that need the maintainer:

- Create an empty public repository `rezaprama/RhetoriLex` (after the rename) if the session cannot, then run `python scripts/build_redirect_site.py` and push `migration/rhetorilex-pages/` to it with Pages enabled (source: branch `main`, root).
- PyPI publication of `lugas` (needs a PyPI account/token; not done).
- Trademark search before commercial use.

## Next

1. Fresh held-out set (written blind) to re-estimate guard accuracy; add value-swap and qualifier-drop detection.
2. Model runs with a small local model (Ollama) and token counts per provider tokenizer.
3. Human review of Indonesian naturalness on 20–30 real (consented) passages.
4. Indonesian before/after examples per manuscript section on the site.
5. Lighthouse: recheck after each site change; collect CrUX when traffic allows.
