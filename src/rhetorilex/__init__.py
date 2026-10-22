"""RhetoriLex: offline, evidence-aware academic rhetoric templates."""

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
__version__ = "0.2.0"
