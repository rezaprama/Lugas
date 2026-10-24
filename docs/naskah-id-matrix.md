# What Lugas learned from naskah-id

Reviewed: [nothinx/naskah-id](https://github.com/nothinx/naskah-id) at commit `1954c79` (22 Oct 2026). License: MIT for the repository except `contoh/korpus/`, which is CC BY-SA 4.0. Approach: observe, adopt useful principles, and write original material. **No file, rule text, regex, example, or corpus passage from naskah-id was copied into Lugas.** The Indonesian reference credits naskah-id for the principles it adapted.

## Capability matrix

| Capability | naskah-id | Lugas v0.2 (pre-rename) | Lugas v0.3 | Benefit | Token cost | Risk | Priority / status |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Explicit job scope (koreksi/sunting/tulis ulang/tulis) | table in SKILL.md | implicit "route the request" | 5-job table incl. translate and summarise | stops over-editing | small (in SKILL.md) | none | P0 / **done** |
| Concrete Indonesian rules (EYD V, KBBI) | references per topic | none (UI only) | `bahasa-indonesia.md`, loaded only for ID work | real Indonesian output | +5.6 KB, ID tasks only | rules can be over-applied | P0 / **done** |
| K / G / AI severity split | yes | no | K / T (translationese) / G | prioritises fixes by job | negligible | none | P1 / **done** |
| "Do not over-correct" list | `pertahankan.md` | no | section 4 of ID reference | protects passives, hedges, field terms | small | none | P0 / **done** |
| Before/after examples that keep facts | `contoh/` | English only | original ID example in reference; site examples | shows the standard | small | none | P1 / partial |
| Deterministic local checker | `periksa.py` (style patterns) | substring check in browser | meaning guard (ID/EN) + ID lint, Python and browser | catches meaning drift with any model | zero model tokens | false alarms, lexical blind spots | P0 / **done** |
| Meaning-preservation check | in prompt checklist | 40-item English regex | numbers, stats, citations, quotes, negation, hedges, causality, direction, scope | core differentiator | zero model tokens | not proof of meaning | P0 / **done** |
| Placeholder markers for missing data/refs | `[PERLU DATA]`, `[PERLU RUJUKAN]` | `[citation needed]` | `[PERLU DATA/RUJUKAN]` and `[NEEDS DATA/SOURCE]` | consistent, searchable gaps | negligible | none | P1 / **done** |
| Reference lookup (OpenAlex) | `openalex.py` | none | not adopted | could verify DOIs | network, privacy | sends queries out; DOI ≠ support | P2 / deferred (opt-in later) |
| Scenario evals | `evals/cases.json` (criteria for review) | 12 English retrieval cases | 40 meaning-guard cases + 16-task model runs, scored | measurable quality | offline | small samples | P0 / **done** |
| AI-use disclosure template | in KONTRAK.md | no | not adopted | journal compliance | small | venue rules vary | P2 / open |
| English writing | out of scope | yes | yes | international use | – | – | keep |
| Structured catalog, CLI/API, PWA | no | yes | yes | reuse, offline search | – | – | keep |

## Where Lugas differs on purpose

- **Bilingual.** naskah-id excludes English manuscripts; Lugas covers ID, EN, and ID↔EN translation with one guard.
- **Checks meaning, not only style.** naskah-id's checker targets style and spelling patterns; the Lugas guard compares source and rewrite for changed facts and claims.
- **Same check everywhere.** The guard runs in the skill, the CLI, and the browser with identical results.
- **Progressive loading.** The Indonesian reference is read only for Indonesian work, keeping English tasks lighter.

## License notes

Principles and ideas are not copyrightable, but credit is given in `skills/lugas/references/bahasa-indonesia.md`. If code from naskah-id is ever reused, keep its MIT notice in `THIRD_PARTY_NOTICES.md`. Do not import `contoh/korpus/` (CC BY-SA 4.0) into Lugas data, which is CC BY 4.0.
