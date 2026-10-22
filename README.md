# Lugas

**Clear writing. Same meaning.** A free, local skill for paraphrasing, editing, correcting, and translating academic and technical writing in **Indonesian and English** without changing numbers, citations, negation, or claim strength.

*Lugas was called **RhetoriLex** until v0.2. Old links, the `rhetorilex` command, `import rhetorilex`, and stable `RLX-*` IDs keep working; see [Migration](#migration-from-rhetorilex).*

[![CI](https://github.com/rezaprama/Lugas/actions/workflows/ci.yml/badge.svg)](https://github.com/rezaprama/Lugas/actions/workflows/ci.yml)
[![Pages](https://github.com/rezaprama/Lugas/actions/workflows/pages.yml/badge.svg)](https://github.com/rezaprama/Lugas/actions/workflows/pages.yml)
[![License: Apache-2.0](https://img.shields.io/badge/code-Apache--2.0-0f766e.svg)](LICENSE)
[![Data: CC BY 4.0](https://img.shields.io/badge/data-CC%20BY%204.0-0f766e.svg)](LICENSES/CC-BY-4.0.txt)

[Workbench (ID)](https://rezaprama.github.io/Lugas/id/alat-parafrasa/) · [Workbench (EN)](https://rezaprama.github.io/Lugas/en/paraphrase-workbench/) · [Bahasa Indonesia](README.id.md) · [Agent Skill](skills/lugas/SKILL.md) · [Benchmarks](docs/benchmarks.md) · [Provenance](PROVENANCE.md)

*Lugas* is Indonesian for plain, direct, and to the point: prose without padding. The tool's job is the same: understand the purpose, check the evidence, then choose the words.

## What it does

| Job | Example request | What Lugas keeps fixed |
| --- | --- | --- |
| Correct (*koreksi*) | "Koreksi ejaan saja" | sentence structure, correct word choices |
| Edit (*sunting*) | "Rapikan bahasanya" | claims, argument order, technical terms |
| Paraphrase (*parafrase*) | "Parafrasekan untuk tinjauan pustaka" | facts, numbers, citations, claim strength |
| Translate ID↔EN | "Terjemahkan ke bahasa Inggris akademik" | everything except decimal comma↔point |
| Summarise (*ringkas*) | "Ringkas untuk abstrak" | kept facts exact, contrasts and limitations |

It does not invent data or references, does not turn association into causation or "not significant" into "no effect", and does not promise to pass plagiarism or AI detectors. The author stays responsible for the final text.

## Three ways to use it

**1. Agent Skill (main product).** Copy `skills/lugas` to `.agents/skills/lugas` (one project) or `~/.codex/skills/lugas` (all projects), or install with:

```text
$skill-installer https://github.com/rezaprama/Lugas/tree/main/skills/lugas
```

The skill loads about 5.9 KB of instructions, plus the Indonesian reference (5.6 KB) only for Indonesian work. It routes by job, locks protected elements, and ends with a local check.

**2. Offline meaning guard (no model, no network).** Works with any model's output, including local models:

```bash
python skills/lugas/scripts/guard.py check source.txt rewrite.txt     # --translation / --summary
python skills/lugas/scripts/guard.py lint draft.txt                   # EYD V/KBBI and translationese hints
```

It compares numbers (decimal comma aware), statistics, citations, quotations, negation (*tidak, bukan, belum, tanpa* / not, no, without), hedges, association vs causation, direction, scope, and non-significance. Exit code 1 means a `high` finding. It is a lexical screen, not proof of meaning.

**3. Web workbench (PWA).** [Indonesian](https://rezaprama.github.io/Lugas/id/alat-parafrasa/) / [English](https://rezaprama.github.io/Lugas/en/paraphrase-workbench/). Choose a job and output language, build a compact prompt for any model, paste the answer back, and run the same meaning check in the browser. Optionally call your own OpenAI-compatible or Gemini endpoint (90 s timeout, cancel, truncation warning). Nothing is sent anywhere unless you enter an endpoint; the site has no backend, account, or analytics.

## Python CLI and API

```bash
git clone https://github.com/rezaprama/Lugas.git && cd Lugas
python -m pip install -e .
lugas check source.txt rewrite.txt
lugas lint draft.txt
lugas search "cautious interpretation" --stage discussion --limit 3
lugas explain RLX-QUA-001
```

```python
from lugas import Catalog, check_rewrite, lint_id

for finding in check_rewrite("Responden belum pernah dilatih.", "Responden sudah pernah dilatih."):
    print(finding.severity, finding.code)        # high negation-lost
results = Catalog.load().search("state a limitation", stage="discussion", limit=3)
```

The catalog behind search holds 96 original English patterns across 24 rhetorical functions and 144 writing skills (64 academic, 66 scientific, 14 paraphrasing) with Indonesian descriptions. Patterns are candidates, not authority.

## Evidence (measured 22 Oct 2026)

Full method, fixtures, and limits: [docs/benchmarks.md](docs/benchmarks.md).

- **Meaning guard vs v0.2 check** on an independently written held-out set (24 cases, 47 faulty rewrites): v0.2 substring check caught 49% with 25% false alarms on faithful rewrites; the new guard caught 81% with 29% false alarms before any tuning, and 85% with 0% after fixes informed by that set (so the second figure is optimistic).
- **Model runs** (one frontier Claude model, 16 ID/EN tasks, blind LLM judge): meaning errors 3 with a plain prompt, 0 with the v0.2 skill, 0 with Lugas v0.3. Naturalness was similar (4.6–4.8 / 5). Lugas did **not** reduce tokens versus v0.2 on this model (≈11 KB instructions each); it adds Indonesian rules at the same cost.
- **Workbench prompt** overhead fell from 788 to 576 characters per request (−27%) while adding output-language control and injection protection.

Not yet measured: smaller or local models, latency and cost per provider, human expert ratings, Lighthouse field data.

## Catalog model

Each canonical entry includes:

| Field | Purpose |
| --- | --- |
| `function` | Stable communicative purpose such as `identify_gap` or `state_limitation` |
| `template` | Original wording with explicit named slots |
| `stage` | Compatible manuscript stage |
| `claim_strength` | `tentative`, `bounded`, `assertive`, or `causal` |
| `evidence_requirement` | `none`, `contextual`, `observational`, `direct`, or `convergent` |
| `causal_design_required` | Prevents causal patterns from being treated as generic prose |
| `risk` | Editorial review level: `low`, `medium`, or `high` |
| `provenance` | Required `original_editorial` and `source_reuse: false` record |

See [data/taxonomy/taxonomy.v1.json](data/taxonomy/taxonomy.v1.json),
[data/contracts/evidence-claim.v1.json](data/contracts/evidence-claim.v1.json), and
[docs/data-model.md](docs/data-model.md).

## Research and discovery

The model is informed by research on genre and rhetorical moves
([10.1017/CBO9781139524827](https://doi.org/10.1017/CBO9781139524827)), stance and reader
interaction ([10.1177/1461445605050365](https://doi.org/10.1177/1461445605050365)),
and corpus phraseology and disciplinary variation
([10.1016/j.jeap.2019.01.003](https://doi.org/10.1016/j.jeap.2019.01.003)). These sources
orient original design; their prose, examples, and inventories are not incorporated.
Full research provenance is in [PROVENANCE.md](PROVENANCE.md).

Public positioning is also measured, not guessed. The
[discovery study](docs/discovery-research.md) and
[GitHub landscape](docs/github-landscape.md) record queries, metrics, timestamps,
interpretation limits, and structured evidence under [data/discovery](data/discovery/).
GitHub repository counts are supply/index signals—not web-search volume, user demand,
adoption, or quality. Direct Google Trends measurement was unavailable, so its recorded
values are explicit `null`; no proxy volume was invented.

## Build and verify

```bash
python scripts/validate_data.py
python scripts/build_data.py
python -m unittest discover -s tests -v
python scripts/package_plugin.py --output dist/lugas-plugin.zip
python scripts/bench_guard.py --fixture benchmarks/meaning-guard-heldout-v1.json
```

The test suite checks schemas, provenance, slot equality, evidence requirements, causal
guards, deterministic builds, retrieval behavior, frozen benchmark routing, CLI
behavior, and contract safety. Continuous integration repeats builds and compares
checksums.

## Architecture

```text
data/canonical/catalog.v1.jsonl
          |
          +--> data/dist/*                    portable data artifacts
          +--> src/lugas/resources/*          Python package
          +--> skills/lugas/assets/*     offline Agent Skill
          +--> docs/data/phrases.json          assembled Pages artifact

taxonomy + JSON Schema + evidence contract
          |
          +--> validator --> tests --> deterministic release gate
```

The browser explorer and paraphrase workbench are static HTML, CSS, and JavaScript. They have no account, backend, CDN dependency, telemetry, or Lugas manuscript database. Endpoint calls go directly from the user's browser to the endpoint they enter. A future shared-key hosted service would need a backend with server-held secrets, quota storage, abuse protection, and manuscript logging disabled by default.

## Source and rights boundary

The private workbook supplied for this project carries an academic-use and
no-redistribution notice. It was inspected locally only for non-expressive aggregate
structure and quality signals. It is ignored by Git, its cells and labels are absent
from this repository, every migration candidate remains unresolved, and **zero
source-derived items were promoted**.

Manchester Academic Phrasebank is citation/conceptual context only; its phrase inventory
was not imported or rewritten. BAWE is excluded. The Elsevier OA CC-BY Corpus v3 is
registered only as a possible future aggregate-validation source and was not ingested.
Full decisions, source links, and review rules are in [PROVENANCE.md](PROVENANCE.md),
[data/sources/source-registry.yaml](data/sources/source-registry.yaml), and
[reports/xlsx-audit.md](reports/xlsx-audit.md).

## Contributing

Contributions are welcome when wording is independently authored and evidence-safe.
Start with [CONTRIBUTING.md](CONTRIBUTING.md). New patterns require provenance, named
slots, taxonomy compatibility, evidence metadata, originality review, and tests. Never
attach a restricted workbook, source inventory, manuscript, or corpus excerpt to an
issue or pull request.

Security, confidential-draft, provenance, and rights concerns belong in the private
process described by [SECURITY.md](SECURITY.md). Project decisions are recorded in
[GOVERNANCE.md](GOVERNANCE.md) and [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md).

## Migration from RhetoriLex

| Old | New | Status |
| --- | --- | --- |
| `github.com/rezaprama/RhetoriLex` | `github.com/rezaprama/Lugas` | GitHub forwards the old repository and git URLs |
| `rezaprama.github.io/RhetoriLex/...` | `rezaprama.github.io/Lugas/...` | per-route redirect pages ([scripts/build_redirect_site.py](scripts/build_redirect_site.py)); old PWA worker is unregistered |
| `rhetorilex` command, `python -m rhetorilex` | `lugas` | alias kept in 0.x |
| `import rhetorilex` | `import lugas` | alias kept in 0.x with a `DeprecationWarning` |
| `skills/rhetorilex`, `$rhetorilex` | `skills/lugas`, `$lugas` | the skill answers to both names |
| `RLX-*` IDs, `rhetorilex-v0.2.*` data files, format IDs | unchanged | stable identifiers |

To roll back, rename the repository back to `RhetoriLex` and redeploy commit `f3fd63d`; no data or IDs changed.

## Project and creator

Lugas is created and maintained by
[Reza Prama Arviandi](https://rezaprama.com). Release history is in
[CHANGELOG.md](CHANGELOG.md); the public roadmap is in [ROADMAP.md](ROADMAP.md).

## License and citation

Software, configuration, tests, and Agent Skill code are Apache-2.0. Original data,
reports, benchmarks, assets, and documentation are CC BY 4.0. Machine-readable path
mapping lives in [REUSE.toml](REUSE.toml); third-party status lives in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Citation metadata for version 0.3.0 is available in [CITATION.cff](CITATION.cff).
Licensing documents state project policy, not legal advice.