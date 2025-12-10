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
        response = self._request("GET", f"/vacancies/{vacancy_id}")
        return Vacancy.from_api(response.json())

    def apply_to_vacancy(self, vacancy: Vacancy, cover_letter: str, dry_run: bool = True) -> Dict[str, Any]:
        """Apply to a vacancy or return a dry-run payload."""
        if dry_run:
            self.logger.info("Dry-run apply to vacancy %s", vacancy.id)
            return {
                "status": "dry_run",
                "vacancy_id": vacancy.id,
                "message": "Dry-run mode; request not sent",
                "cover_letter_preview": cover_letter[:120],
            }

        payload = {"vacancy_id": vacancy.id, "message": cover_letter}
        try:
            response = self._request("POST", "/responses", json=payload)
            return response.json()
        except requests.RequestException as exc:
            self.logger.exception("Failed to apply to vacancy %s: %s", vacancy.id, exc)
            return {"status": "error", "error": str(exc), "payload": json.dumps(payload)}
