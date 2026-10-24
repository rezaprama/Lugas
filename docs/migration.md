# Migration and compatibility

Lugas is the current project name and source repository. This page records compatibility
paths for previous installs and links.

| Previous identifier or path | Current path | Status |
| --- | --- | --- |
| `github.com/rezaprama/RhetoriLex` | `github.com/rezaprama/Lugas` | The previous repository name now serves per-route Pages redirects; use the current repository for source and releases. |
| `rezaprama.github.io/RhetoriLex/...` | `rezaprama.github.io/Lugas/...` | The redirect site preserves the route, query, and hash, and unregisters the old PWA worker. |
| `rhetorilex` command, `python -m rhetorilex` | `lugas` | Both commands remain available during the 0.x series. |
| `import rhetorilex` | `import lugas` | The compatibility import remains available and emits `DeprecationWarning`. |
| `skills/rhetorilex`, `$rhetorilex` | `skills/lugas`, `$lugas` | The skill keeps the previous trigger as an alias. |
| `RLX-*` IDs, `rhetorilex-v0.2.*` data files, format IDs | unchanged | Stable identifiers; do not rename without a versioned migration. |

The old repository name is occupied by the redirect repository, so changing the source
repository back requires coordinating both repositories and both Pages deployments. The
old local-storage keys (`rhetorilex.locale` and `rhetorilex.theme`) are retained so
existing browser preferences continue to work.

The published 0.2 dataset snapshot also keeps its original format IDs, schema IDs, filenames, and authorship labels for compatibility and provenance. New product copy, package metadata, and site metadata use Lugas.
