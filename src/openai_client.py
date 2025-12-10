"""OpenAI client wrapper for generating cover letters."""

from __future__ import annotations

import logging
from typing import Optional

try:
    from openai import OpenAI
except ImportError:  # pragma: no cover - optional dependency
    OpenAI = None  # type: ignore

from .config import Settings
from .models.vacancies import Vacancy
from . import prompts_demo, logging_utils


class OpenAIClient:
    """Thin wrapper around OpenAI Chat Completions API."""

    def __init__(self, settings: Settings, logger: Optional[logging.Logger] = None) -> None:
        self.settings = settings
        self.logger = logger or logging_utils.get_logger(__name__)
        self.client: Optional[OpenAI] = None
        if settings.OPENAI_API_KEY and OpenAI is not None:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def generate_cover_letter(self, vacancy: Vacancy, candidate_profile: str, dry_run: bool = True) -> str:
        """Generate a cover letter or return a deterministic demo message."""
        if dry_run or not self.client:
            return (
                f"This is a demo cover letter for {vacancy.title} at {vacancy.company_name}. "
                f"Candidate profile: {candidate_profile}."
            )

        user_message = prompts_demo.COVER_LETTER_USER_TEMPLATE.format(
            vacancy_title=vacancy.title,
            company_name=vacancy.company_name,
            vacancy_description=vacancy.description or "No description provided.",
            candidate_profile=candidate_profile,
        )
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompts_demo.SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
            temperature=0.3,
            max_tokens=320,
        )
        return completion.choices[0].message.content.strip()
