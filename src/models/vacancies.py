"""Vacancy domain models."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Vacancy:
    """Represents a vacancy returned by the job-board API."""

    id: str
    title: str
    company_name: str
    area: Optional[str] = None
    salary_from: Optional[int] = None
    salary_to: Optional[int] = None
    description: Optional[str] = None
    url: Optional[str] = None

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "Vacancy":
        """Create a Vacancy from a generic API payload."""
        salary = data.get("salary") or {}
        return cls(
            id=str(data.get("id")),
            title=data.get("title") or "Untitled vacancy",
            company_name=data.get("company") or data.get("employer") or "Unknown company",
            area=data.get("area"),
            salary_from=_safe_int(salary.get("from")),
            salary_to=_safe_int(salary.get("to")),
            description=data.get("description"),
            url=data.get("url") or data.get("alternate_url"),
        )


def _safe_int(value: Any) -> Optional[int]:
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
