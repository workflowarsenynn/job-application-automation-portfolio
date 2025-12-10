"""Prompt templates for cover letter generation."""

SYSTEM_PROMPT = (
    "You are a concise assistant that drafts friendly, professional cover letters "
    "for job applications."
)

COVER_LETTER_USER_TEMPLATE = (
    "Write a short cover letter for the vacancy:\n"
    "Title: {vacancy_title}\n"
    "Company: {company_name}\n"
    "Description: {vacancy_description}\n"
    "Candidate profile: {candidate_profile}\n"
    "Keep it polite and to the point."
)
