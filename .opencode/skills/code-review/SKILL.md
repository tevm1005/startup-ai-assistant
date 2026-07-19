---
name: code-review
description: Review Python code for quality, security, and project conventions
---

## What to check
1. **Type safety** — all functions have type hints
2. **Error handling** — async calls wrapped in try/except, proper logging
3. **SQL/DB** — no raw SQL, use SQLAlchemy ORM
4. **Secrets** — no API keys or tokens in code
5. **Tests** — new code has corresponding tests
6. **Naming** — snake_case for functions/variables, PascalCase for classes
7. **Async** — all I/O operations use async/await properly
