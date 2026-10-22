"""Lugas (formerly RhetoriLex): local, meaning-safe academic paraphrase and editing tools."""

from .catalog import Catalog, Entry, SearchResult
from .contracts import ContractIssue, check_entry_contract
from .guard import Finding, check as check_rewrite, lint_id

__all__ = [
    "Catalog",
    "ContractIssue",
    "Entry",
    "Finding",
    "SearchResult",
    "check_entry_contract",
    "check_rewrite",
    "lint_id",
]
__version__ = "0.3.0"
