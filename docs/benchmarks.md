# Benchmarks (v0.3.0, measured 22 October 2026)

All fixtures are original synthetic passages (numbers, names, and citations invented). No text comes from naskah-id or its corpus, the restricted workbook, or published articles. Reproduce with the commands under each section.

## 1. Meaning guard

**Question.** Does the offline guard catch meaning changes in a rewrite without flagging faithful rewrites, and is it better than the v0.2 workbench check?

**Fixtures.**

| Set | Cases | Faulty rewrites | Written by | Used to tune the guard? |
| --- | --- | --- | --- | --- |
| `benchmarks/meaning-guard-v1.json` (dev) | 16 (12 ID, 3 EN, 1 ID→EN) | 25 | same author as the guard | yes |
| `benchmarks/meaning-guard-heldout-v1.json` | 24 (16 ID, 5 EN, 3 ID→EN) | 47 | a separate agent with no access to the guard or dev set | first run untouched; later fixes were informed by it |

Each case has one faithful rewrite and one or two faulty rewrites labelled with the expected error codes.

**Metrics.** *Detection*: share of faulty rewrites with at least one `high` or `medium` finding. *False alarms*: share of faithful rewrites with a `high` finding. *Code recall*: share of expected error codes reported.

**Baseline.** `legacy` is a Python port of the v0.2 `extractInvariants()` check: English-only regexes, 40-item cap, substring matching.

| Set | Check | Detection | False alarms | Code recall |
| --- | --- | --- | --- | --- |
| held-out, before any tuning | legacy v0.2 | 49% | 25% | n/a |
| held-out, before any tuning | guard 1.0 (first run) | 81% | 29% | 63% |
| held-out, after fixes | guard 1.0 (released) | 85% | 0% | 77% |
| dev | guard 1.0 (released) | 100% | 0% | 98% |

The honest generalisation estimate is the **first held-out run**. Fixes made after it (unit-agnostic number matching, spelled-out numbers, lexical negatives such as *di luar cakupan*/*rather than*, Indonesian suffixes *-nya*, polarity pairs, a broader non-significance pattern) are general rules, but they were chosen after seeing held-out errors, so the released figures are optimistic. A fresh held-out set is needed for the next estimate.

**Known blind spots** (still missed): values swapped between two categories (dry vs wet season), dropped qualifiers that are not quantifiers (*pada akhir pekan*), subtle strengthening without booster words, and any paraphrase whose meaning shift uses vocabulary outside the lexicon. The guard is a screen, not a judge.

**Parity.** `docs/guard.js` (browser) and `src/lugas/guard.py` give identical findings on all 112 items (`tests/test_guard_parity.py`).

```bash
python scripts/bench_guard.py --fixture benchmarks/meaning-guard-heldout-v1.json
```

Results: `benchmarks/results/`.

## 2. Model runs: plain prompt vs skill v0.2 vs skill v0.3

**Question.** Does the skill improve meaning fidelity and Indonesian quality, and at what instruction cost?

**Setup.** 16 tasks (11 dev + 5 held-out sources; 12 Indonesian, 2 English, 1 ID→EN, plus summaries) in `benchmarks/model-runs/tasks-v1.json`. Each condition ran in a separate, fresh sub-agent of the same frontier Claude model (configured model ID `claude-opus-5-5`; the serving model is not independently verified), reading only its condition's instructions:

| Condition | Instructions loaded per task |
| --- | --- |
| A plain | none: the request and the source only |
| B skill v0.2 | v0.2 `SKILL.md` + `evidence-preservation.md` + `paraphrasing.md` (10,832 chars) |
| C2 skill v0.3 (released) | v0.3 `SKILL.md` + `bahasa-indonesia.md` for ID tasks or `evidence-preservation.md` for EN (mean 11,182 chars) |

An earlier v0.3 draft (C) produced 44% longer replies and dropped a contrast in one summary; the delivery and summary rules were tightened (C2). C2 was evaluated on the same tasks after that change.

**Scoring.** (1) Deterministic guard findings against the source. (2) A blind LLM judge (separate sub-agent, candidates shuffled, origin hidden) counted meaning errors, checked scope, and rated naturalness 1–5.

| Condition | Guard `high` findings | Judge: meaning errors | Judge: scope OK | Judge: naturalness | Mean reply length |
| --- | --- | --- | --- | --- | --- |
| A plain | 1 | 3 | 16/16 | 4.75 | 282 chars |
| B skill v0.2 | 0 | 0 | 15/16 | 4.69 | 402 chars |
| C2 skill v0.3 | 0 | 0 | 15/16 | 4.62 | 391 chars |

Plain-prompt errors: a hedge strengthened (*mengindikasikan* → *menunjukkan*), "this statement" broadened to "similar statements", and a summary that dropped a contrast. Both skills avoided them. The one scope miss for B and C2 was the same "make concise" item that did not get shorter.

**Interpretation.**

- With a strong model, both skills remove the meaning errors a plain prompt makes on this set; v0.3 matches v0.2, it does not beat it.
- **No token saving versus v0.2 was shown.** v0.3 loads about the same instruction volume (≈2.8k tokens, estimated at 4 chars/token) and adds Indonesian rules within it. Against a plain prompt, any skill costs those extra input tokens.
- Sample size is small (16 tasks, one model, one judge model from the same family). Differences of one item are not meaningful.

```bash
python scripts/score_model_runs.py
```

Data: `benchmarks/model-runs/` (runs, judge outputs, randomisation keys, summaries).

## 3. Workbench prompt size

Same 16 sources, Indonesian page, prompt-only mode, measured in a headless browser:

| Version | Mean instruction overhead (prompt minus source) | Output language selectable |
| --- | --- | --- |
| v0.2 (`safe` mode) | 788 chars | no (English only) |
| v0.3 (`paraphrase`) | 576 chars (−27%) | yes |

Data: `benchmarks/results/workbench-prompt-size-v1.json`.

## 4. Workbench end-to-end

`python scripts/e2e_workbench.py` serves the site and a mock OpenAI-compatible endpoint locally and checks, on a 390 px viewport in both locales: prompt-only output, Indonesian output instruction, protected values and citations, guard findings for a faulty rewrite, endpoint call with truncation warning, cancel, no horizontal overflow, and no console errors.

## Not measured yet

- Smaller or local models (Ollama, Gemma, Qwen), where a skill and guard are expected to matter more.
- Latency and cost per provider; token counts with each provider's tokenizer.
- Human expert ratings of Indonesian naturalness.
- Lighthouse field data (CrUX); see the site audit notes in `docs/checkpoint.md`.
