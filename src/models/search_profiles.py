"""Search profile definition used for job queries."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class SearchProfile:
    """Represents a search profile configuration."""

    id: str
    name: str
    query: str
    areas: List[str] = field(default_factory=list)
    salary_min: Optional[int] = None
    limit_per_run: Optional[int] = None
    candidate_profile: Optional[Dict[str, Any]] = None
