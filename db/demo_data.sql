INSERT INTO applications (vacancy_id, profile_name, status, applied_at, cover_letter_snippet, raw_response)
VALUES
('demo-1001', 'Backend Python', 'applied', '2024-01-05T10:00:00Z', 'Interested in backend Python role...', '{"status": "sent", "code": 200}'),
('demo-1002', 'Data Engineer', 'skipped', '2024-01-06T12:15:00Z', 'Skipped due to salary mismatch', NULL),
('demo-1003', 'MLOps', 'dry_run', '2024-01-07T09:30:00Z', 'Demo cover letter snippet', '{"status": "dry_run"}');
