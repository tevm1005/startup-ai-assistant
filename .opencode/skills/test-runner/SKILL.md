---
name: test-runner
description: Run pytest and report results
---

## How to run tests
- All tests: `.venv/bin/pytest tests/ -v`
- Single file: `.venv/bin/pytest tests/test_core.py -v`
- Report format: "X passed, Y failed. First failure: [detail]"
