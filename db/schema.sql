CREATE TABLE IF NOT EXISTS applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    vacancy_id TEXT NOT NULL,
    profile_name TEXT NOT NULL,
    status TEXT NOT NULL,
    applied_at TEXT NOT NULL,
    cover_letter_snippet TEXT,
    raw_response TEXT
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_applications_vacancy ON applications (vacancy_id);

CREATE TABLE IF NOT EXISTS vacancies_cache (
    id TEXT PRIMARY KEY,
    title TEXT,
    company TEXT,
    area TEXT,
    salary_from INTEGER,
    salary_to INTEGER,
    description_snippet TEXT,
    url TEXT
);
