"""Compatibility alias: RhetoriLex is now Lugas.

``import rhetorilex`` keeps working and re-exports the ``lugas`` API. New code
should ``import lugas``. This alias will stay for at least the 0.x series.
"""

from __future__ import annotations

import warnings

from lugas import *  # noqa: F401,F403
from lugas import __all__, __version__  # noqa: F401
from lugas import catalog, cli, contracts, guard  # noqa: F401

warnings.warn(
    "The 'rhetorilex' package is now 'lugas'; import lugas instead.",
    DeprecationWarning,
    stacklevel=2,
)
