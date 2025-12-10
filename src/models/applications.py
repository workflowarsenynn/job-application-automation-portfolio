"""Application log model for SQLite persistence."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class ApplicationLog:
    """Represents a single application attempt stored in SQLite."""

    vacancy_id: str
    profile_name: str
    status: str
    applied_at: datetime
    cover_letter_snippet: Optional[str]
    raw_response: Optional[str] = None
