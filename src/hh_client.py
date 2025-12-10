"""Abstract job-board HTTP client."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional

import requests

from .config import Settings
from .models.search_profiles import SearchProfile
from .models.vacancies import Vacancy
from . import logging_utils


class JobBoardClient:
    """Lightweight client for a generic job-board API."""

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None) -> None:
        self.settings = settings
        self.base_url = settings.JOB_BOARD_API_BASE_URL.rstrip("/")
        self.session = requests.Session()
        self.logger = logger or logging_utils.get_logger(__name__)

    def _fake_vacancies(self, profile: SearchProfile) -> List[Vacancy]:
        """Return a small synthetic list of vacancies for offline demo mode."""
        area = profile.areas[0] if profile.areas else "remote"
        base_salary = profile.salary_min or 150000
        demo_items: List[Vacancy] = []
        for idx in range(1, 4):
            salary_from = base_salary + (idx - 1) * 10000
            salary_to = salary_from + 20000
            demo_items.append(
                Vacancy(
                    id=f"demo-{idx}",
                    title=f"{profile.name} (Demo Vacancy #{idx})",
                    company_name="Demo Company",
                    area=area,
                    salary_from=salary_from,
                    salary_to=salary_to,
                    description=(
                        f"This is a demo vacancy for profile '{profile.query}'. "
                        "Used in offline dry-run mode without hitting the API."
                    ),
                    url=f"https://example.com/demo-vacancies/demo-{idx}",
                )
            )
        return demo_items

    def _fake_vacancy_details(self, vacancy_id: str) -> Vacancy:
        """Create a deterministic fake vacancy detail record."""
        return Vacancy(
            id=vacancy_id,
            title=f"Demo Vacancy {vacancy_id}",
            company_name="Demo Company",
            area="remote",
            salary_from=180000,
            salary_to=210000,
            description="Offline demo vacancy details. No network request was made.",
            url=f"https://example.com/demo-vacancies/{vacancy_id}",
        )

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.settings.JOB_BOARD_ACCESS_TOKEN:
            headers["Authorization"] = f"Bearer {self.settings.JOB_BOARD_ACCESS_TOKEN}"
        return headers

    def _request(self, method: str, path: str, **kwargs: Any) -> requests.Response:
        url = f"{self.base_url}{path}"
        self.logger.debug("Request %s %s", method, url)
        response = self.session.request(method, url, headers=self._headers(), timeout=30, **kwargs)
        if not response.ok:
            self.logger.error("API error %s: %s", response.status_code, response.text[:500])
            response.raise_for_status()
        return response

    def search_vacancies(self, profile: SearchProfile) -> List[Vacancy]:
        """Search vacancies using profile parameters."""
        if self.settings.DRY_RUN:
            self.logger.info("Using offline demo vacancies for profile %s", profile.name)
            return self._fake_vacancies(profile)

        params: Dict[str, Any] = {
            "text": profile.query,
            "page": 0,
            "per_page": profile.limit_per_run or 20,
        }
        if profile.areas:
            params["area"] = ",".join(profile.areas)
        if profile.salary_min:
            params["salary_from"] = profile.salary_min

        response = self._request("GET", "/vacancies", params=params)
        payload = response.json()
        items = payload.get("items", []) if isinstance(payload, dict) else payload
        return [Vacancy.from_api(item) for item in items]

    def get_vacancy_details(self, vacancy_id: str) -> Vacancy:
        """Fetch a single vacancy and return it as a model."""
        if self.settings.DRY_RUN:
            self.logger.info("Returning offline demo vacancy details for %s", vacancy_id)
            return self._fake_vacancy_details(vacancy_id)

        response = self._request("GET", f"/vacancies/{vacancy_id}")
        return Vacancy.from_api(response.json())

    def apply_to_vacancy(self, vacancy: Vacancy, cover_letter: str, dry_run: bool = True) -> Dict[str, Any]:
        """Apply to a vacancy or return a dry-run payload."""
        if dry_run or self.settings.DRY_RUN:
            self.logger.info("Dry-run apply to vacancy %s", vacancy.id)
            return {
                "status": "dry_run",
                "vacancy_id": vacancy.id,
                "message_preview": cover_letter[:160],
            }

        payload = {"vacancy_id": vacancy.id, "message": cover_letter}
        try:
            response = self._request("POST", "/responses", json=payload)
            return response.json()
        except requests.RequestException as exc:
            self.logger.exception("Failed to apply to vacancy %s: %s", vacancy.id, exc)
            return {"status": "error", "error": str(exc), "payload": json.dumps(payload)}
