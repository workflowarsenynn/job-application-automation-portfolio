# Flows

## Demo run
1. Load `.env` via `get_settings()` to resolve paths, base URL, token, and default dry-run flag.
2. Read `active_mode_demo.json` to pick active profile IDs, max_applications, send_applications, and dry-run override.
3. Read `search_configs_demo.json` and build `SearchProfile` objects (query, areas, salary_min, candidate_profile, optional per-profile limit).
4. For each active profile:
   - call `JobBoardClient.search_vacancies(profile)` to fetch a batch of vacancies;
   - filter by salary/area and drop vacancies already in SQLite (`vacancy_already_applied`);
   - trim to per-profile limit and global `max_applications`.
5. For each remaining vacancy:
   - fetch details via `get_vacancy_details`;
   - generate a cover letter with `OpenAIClient.generate_cover_letter` (stub if dry-run or missing key);
   - call `apply_to_vacancy` (real POST only if send_applications and not dry-run);
   - persist to SQLite with `save_application` (status, snippet, raw response JSON).
6. Print a short summary (`processed` / `logged`) to stdout.

## Error handling & logging
- `logging_utils.get_logger` configures console logging; API calls log debug/info and surface errors on non-2xx.
- `JobBoardClient.apply_to_vacancy` returns a structured error payload on request failures to keep the flow alive.
- SQLite writes are simple inserts; in case of DB path issues, the error surfaces immediately so the run fails fast.
