# Real Project vs Demo

This repository is a safe, trimmed-down showcase. The production system includes additional capabilities that are intentionally omitted or simplified here.

## Present in production only
- Multi-account management with multiple resumes and switching logic.
- Advanced anti-abuse handling: dynamic rate limits, custom User-Agent rotation, backoff strategies.
- Telegram notifications and auto-replies with templated responses.
- Token refresh and secret management tailored to the target platform.
- Scheduler/daemon integrations (e.g., LaunchAgent) for unattended runs.
- Extended analytics, dashboards, and operational alerts.

## Simplified in the demo
- Single, static candidate profile per search config.
- Straightforward API calls without aggressive retry or throttling policies.
- Minimal SQLite schema (applications + cache) instead of richer reporting tables.
- OpenAI prompts kept generic and neutral; no production-specific wording or checks.
- Manual CLI entry point instead of orchestrated background jobs.
