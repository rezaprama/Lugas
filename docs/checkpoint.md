# Checkpoint

Last updated: 24 October 2026. Current product name: **Lugas**.

## Current state

- Source repository: [rezaprama/Lugas](https://github.com/rezaprama/Lugas). Public site: <https://rezaprama.github.io/Lugas/>.
- The previous repository and Pages paths now serve compatibility redirects. The redirect pages preserve route, query, and hash, and remove only the old app's PWA caches.
- Rename and redirects are live. PRs #8–#11 are merged.
- This update consolidates migration details in `docs/migration.md`, removes obsolete current-brand wording from both READMEs, package and plugin descriptions, citation metadata, and site metadata, and fixes the old rollback instructions.

## Verified baseline

- CI passed on Python 3.10–3.13; CI, CodeQL, Dependency Review, and Pages deployment passed for PR #11.
- Local quality gate passed with 89 tests on Python 3.14. Earlier browser smoke covered English and Indonesian pages at 390 px; a repeat visual run was unavailable because Playwright is not installed here.
- PageSpeed Insights previously returned 100 in Performance, Accessibility, Best Practices, and SEO for the English home, Indonesian home, and Indonesian workbench on mobile and desktop. Field data was unavailable. A post-deploy recheck was rate-limited by the PSI endpoint (HTTP 429), so those scores were not reconfirmed.
- Meaning guard, offline checks, EYD V lint, and skill/package parity are documented in `docs/benchmarks.md`.

## Compatibility retained

- `rhetorilex`, `python -m rhetorilex`, `import rhetorilex`, and `$rhetorilex` remain aliases during the 0.x series.
- `RLX-*` IDs, the 0.2 dataset filenames and format/schema IDs, and browser preference keys remain stable. Published 0.2 records retain their original authorship labels for provenance.
- Keep current product copy and SEO metadata Lugas-only. Put migration details in `docs/migration.md`.

## Remaining work

- The limited PDKI lookup found a class-9 Lugas mark that includes some downloadable software. It is not trademark clearance; obtain a qualified review before commercial use or paid promotion. See `docs/brand/naming-2026-10.md`.
- PyPI publication has not been completed.
- Retry PageSpeed Insights after its request limit clears; the previous mobile and desktop scores remain the last successful report.
- Fresh blind held-out guard evaluation, small/local model benchmarks, and human review of Indonesian naturalness remain planned in `docs/benchmarks.md` and `ROADMAP.md`.
