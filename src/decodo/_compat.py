from __future__ import annotations

import sys
from enum import Enum

if sys.version_info >= (3, 11):
    from enum import StrEnum
else:

    class StrEnum(str, Enum):
        """Backport of ``enum.StrEnum`` (3.11+): members are strings and ``str()`` gives the value."""

        def __str__(self) -> str:
            return str(self.value)

        def __format__(self, format_spec: str) -> str:
            return str.__format__(str(self.value), format_spec)


__all__ = ["StrEnum"]
