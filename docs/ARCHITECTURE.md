# Architecture

The demo is intentionally small but mirrors the main layers of the production system.

## Layers
- **CLI** (`src/search_and_apply_demo.py`) — entry point: loads settings/JSON configs, iterates active profiles, calls API + AI, records results.
- **API client** (`src/hh_client.py`) — HTTP wrapper over abstract endpoints `/vacancies` and `/responses`, builds headers from settings, converts payloads into `Vacancy`.
- **AI layer** (`src/openai_client.py` + `src/prompts_demo.py`) — produces cover letters via OpenAI or a deterministic stub in dry-run.
- **Data layer** (`src/db.py` + `db/schema.sql`) — SQLite schema for `applications` (+ optional `vacancies_cache`), helpers to init DB and append application rows.
- **Configuration** (`src/config.py` + `config/*.json` + `.env`) — settings loader (paths, base URL, tokens, dry-run flag) plus JSON search profiles and active mode toggles.
- **Models** (`src/models/*`) — dataclasses for `Vacancy` and `SearchProfile` used across API, AI, and orchestration.

## Data flow
```
search_and_apply_demo (CLI)
    -> loads Settings + active_mode + search profiles
    -> JobBoardClient.search_vacancies(profile)  -----> Job-board API (/vacancies)
    -> filter + deduplicate via SQLite
    -> JobBoardClient.get_vacancy_details(id) ---> Job-board API (/vacancies/{id})
    -> OpenAIClient.generate_cover_letter(...) -> OpenAI (or dry-run stub)
    -> JobBoardClient.apply_to_vacancy(...) ---> Job-board API (/responses) [skipped in dry-run]
    -> db.save_application(...) ---------------> SQLite (applications table)
```
