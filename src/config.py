"""Configuration helpers for the demo project."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment and defaults."""

    DB_PATH: Path
    CONFIG_DIR: Path
    SEARCH_CONFIG_PATH: Path
    ACTIVE_MODE_PATH: Path
    JOB_BOARD_API_BASE_URL: str
    JOB_BOARD_ACCESS_TOKEN: Optional[str]
    OPENAI_API_KEY: Optional[str]
    DRY_RUN: bool


def _parse_bool(value: Optional[str], default: bool = True) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached settings instance."""
    load_dotenv()

    config_dir = Path(os.getenv("CONFIG_DIR", BASE_DIR / "config"))
    search_config_path = Path(os.getenv("SEARCH_CONFIG_PATH", config_dir / "search_configs_demo.json"))
    active_mode_path = Path(os.getenv("ACTIVE_MODE_PATH", config_dir / "active_mode_demo.json"))

    return Settings(
        DB_PATH=Path(os.getenv("DB_PATH", BASE_DIR / "db" / "demo.db")),
        CONFIG_DIR=config_dir,
        SEARCH_CONFIG_PATH=search_config_path,
        ACTIVE_MODE_PATH=active_mode_path,
        JOB_BOARD_API_BASE_URL=os.getenv("JOB_BOARD_API_BASE_URL", "https://api.example.com"),
        JOB_BOARD_ACCESS_TOKEN=os.getenv("JOB_BOARD_ACCESS_TOKEN") or None,
        OPENAI_API_KEY=os.getenv("OPENAI_API_KEY") or None,
        DRY_RUN=_parse_bool(os.getenv("DRY_RUN"), default=True),
    )
