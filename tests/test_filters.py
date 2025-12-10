import os
from datetime import datetime, timezone
from pathlib import Path

from src import db
from src.config import get_settings
from src.models.vacancies import Vacancy
from src.search_and_apply_demo import filter_vacancies


def test_filter_vacancies_applies_rules():
    vacancies = [
        Vacancy(id="1", title="Ok", company_name="Co", salary_from=200000, area="remote"),
        Vacancy(id="2", title="Low", company_name="Co", salary_from=100000, area="remote"),
        Vacancy(id="3", title="Wrong area", company_name="Co", salary_from=300000, area="onsite"),
    ]
    class Profile:
        salary_min = 150000
        areas = ["remote"]
    filtered = filter_vacancies(vacancies, Profile())
    assert [v.id for v in filtered] == ["1"]


def test_db_write_and_check(tmp_path: Path, monkeypatch):
    db_path = tmp_path / "demo.db"
    monkeypatch.setenv("DB_PATH", str(db_path))
    get_settings.cache_clear()

    db.init_db(demo=True)
    assert db.vacancy_already_applied("demo-1001") is True
    assert db.vacancy_already_applied("nonexistent") is False

    db.save_application(
        vacancy_id="xyz",
        profile_name="Backend Python",
        status="dry_run",
        cover_letter_snippet="snippet",
        raw_response='{"status": "ok"}',
    )
    assert db.vacancy_already_applied("xyz") is True
