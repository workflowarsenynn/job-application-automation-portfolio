# Пример вывода (dry-run)

Ниже — синтетический фрагмент лога одной утренней сессии в режиме dry-run. В демо он демонстрирует последовательность действий: загрузка профилей, поиск вакансий, генерация сопроводительного письма, попытка отклика (без отправки) и запись в SQLite.

```
2024-03-12 07:00:01 [INFO] src.search_and_apply_demo: Starting demo workflow
2024-03-12 07:00:01 [INFO] src.search_and_apply_demo: Loaded 2 active profiles: Backend Python, Data Engineer
2024-03-12 07:00:01 [INFO] src.search_and_apply_demo: Running search for profile: Backend Python
2024-03-12 07:00:02 [INFO] src.search_and_apply_demo: Found 3 vacancies after filtering
2024-03-12 07:00:03 [INFO] src.search_and_apply_demo: Logged application for vacancy demo-1001 with status dry_run
2024-03-12 07:00:04 [INFO] src.search_and_apply_demo: Logged application for vacancy demo-1002 with status dry_run
2024-03-12 07:00:04 [INFO] src.search_and_apply_demo: Reached max applications (3); stopping.
2024-03-12 07:00:04 [INFO] src.search_and_apply_demo: Workflow finished
```

При включении реальной отправки (`send_applications=true`, `dry_run=false`) строки будут отмечать статус `sent` или `failed` и HTTP-код ответа, но реальные токены и идентификаторы не должны попадать в публичные логи.
