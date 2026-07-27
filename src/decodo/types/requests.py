from __future__ import annotations

try:
    from decodo.generated.targets import BatchRequest, ScrapeRequest
    __all__ = ["ScrapeRequest", "BatchRequest"]
except ImportError:
    __all__ = []
