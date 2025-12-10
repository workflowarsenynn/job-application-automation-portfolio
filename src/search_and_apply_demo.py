"""CLI entry point for a single demo run."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .config import Settings, get_settings
from .db import init_db, save_application, vacancy_already_applied
from .hh_client import JobBoardClient
from .logging_utils import get_logger
from .models.search_profiles import SearchProfile
from .models.vacancies import Vacancy
from .openai_client import OpenAIClient


def load_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_active_mode(path: Path) -> Dict[str, Any]:
    """Load active mode JSON (which profiles to run, limits, dry-run)."""
    return load_json(path)


def load_search_profiles(path: Path) -> List[SearchProfile]:
    """Load search profiles from JSON into dataclasses."""
    data = load_json(path)
    raw_profiles = data.get("profiles", []) if isinstance(data, dict) else []
    profiles: List[SearchProfile] = []
    for item in raw_profiles:
        profiles.append(
            SearchProfile(
                id=item.get("id", ""),
                name=item.get("name", ""),
                query=item.get("query", ""),
                areas=item.get("areas") or [],
                salary_min=item.get("salary_min"),
                limit_per_run=item.get("limit_per_run"),
                candidate_profile=item.get("candidate_profile"),
            )
        )
    return profiles


def render_candidate_profile(candidate_profile: Any) -> str:
    """Turn candidate_profile data into a human-friendly string."""
    if isinstance(candidate_profile, str):
        return candidate_profile
    if isinstance(candidate_profile, dict):
        parts = [f"{key}: {value}" for key, value in candidate_profile.items()]
        return "; ".join(parts)
    return "Generalist candidate"


def filter_vacancies(vacancies: Iterable[Vacancy], profile: SearchProfile) -> List[Vacancy]:
    """Apply basic filtering by salary and area."""
    filtered: List[Vacancy] = []
    for vacancy in vacancies:
        if profile.salary_min and vacancy.salary_from and vacancy.salary_from < profile.salary_min:
            continue
        if profile.areas and vacancy.area and vacancy.area not in profile.areas:
            continue
        filtered.append(vacancy)
    return filtered


def run_once(settings: Settings, dry_run_override: bool | None = None) -> Dict[str, int]:
    """Execute a single run of the demo workflow."""
    logger = get_logger("search_and_apply")
    init_db(demo=False)

    active_mode = load_active_mode(settings.ACTIVE_MODE_PATH)
    active_ids = set(active_mode.get("active_profiles", []))
    max_applications = int(active_mode.get("max_applications", 5))
    send_applications = bool(active_mode.get("send_applications", False))
    mode_dry_run = active_mode.get("dry_run", settings.DRY_RUN)
    effective_dry_run = mode_dry_run if dry_run_override is None else dry_run_override

    profiles = [p for p in load_search_profiles(settings.SEARCH_CONFIG_PATH) if p.id in active_ids]
    logger.info("Loaded %s active profiles: %s", len(profiles), ", ".join(p.name for p in profiles))

    job_client = JobBoardClient(settings, logger=logger)
    ai_client = OpenAIClient(settings, logger=logger)

    total_processed = 0
    total_logged = 0

    for profile in profiles:
        logger.info("Running search for profile: %s", profile.name)
        vacancies = job_client.search_vacancies(profile)
        vacancies = filter_vacancies(vacancies, profile)
        vacancies = [v for v in vacancies if not vacancy_already_applied(v.id)]

        per_profile_limit = profile.limit_per_run or max_applications
        vacancies = vacancies[:per_profile_limit]

        for vacancy in vacancies:
            if total_logged >= max_applications:
                logger.info("Reached max applications (%s).", max_applications)
                return {"processed": total_processed, "logged": total_logged}

            total_processed += 1
            detailed = job_client.get_vacancy_details(vacancy.id)
            candidate_profile_text = render_candidate_profile(profile.candidate_profile)
            cover_letter = ai_client.generate_cover_letter(
                detailed,
                candidate_profile=candidate_profile_text,
                dry_run=effective_dry_run,
            )
            response = job_client.apply_to_vacancy(
                detailed,
                cover_letter=cover_letter,
                dry_run=effective_dry_run or not send_applications,
            )
            status = response.get("status") or ("applied" if send_applications and not effective_dry_run else "dry_run")
            snippet = cover_letter[:180] + ("..." if len(cover_letter) > 180 else "")
            save_application(
                vacancy_id=detailed.id,
                profile_name=profile.name,
                status=status,
                cover_letter_snippet=snippet,
                raw_response=json.dumps(response),
            )
            total_logged += 1
            logger.info("Logged %s for vacancy %s", status, detailed.id)

    logger.info("Run finished: processed=%s, logged=%s", total_processed, total_logged)
    return {"processed": total_processed, "logged": total_logged}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo job-board search and apply flow.")
    parser.add_argument("--dry-run", dest="dry_run", action="store_true", help="Force dry-run mode.")
    parser.add_argument("--no-dry-run", dest="dry_run", action="store_false", help="Disable dry-run mode.")
    parser.set_defaults(dry_run=None)
    return parser.parse_args()


def main() -> None:
    settings = get_settings()
    args = parse_args()
    effective_settings = replace(settings, DRY_RUN=settings.DRY_RUN if args.dry_run is None else args.dry_run)
    summary = run_once(effective_settings, dry_run_override=effective_settings.DRY_RUN)
    print(f"Processed: {summary['processed']} | Logged: {summary['logged']}")


if __name__ == "__main__":
    main()
