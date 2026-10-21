# FashionGram E2E tests

[![E2E tests](https://github.com/andrew84eg-ops/fashiongram-e2e/actions/workflows/e2e.yml/badge.svg)](https://github.com/andrew84eg-ops/fashiongram-e2e/actions/workflows/e2e.yml)

End-to-end and API test suite for [FashionGram](https://github.com/andrew84eg-ops/FashionGram), a digital-closet web app, written in **Python + pytest + Playwright** with the **Page Object Model**, and run automatically by **GitHub Actions** on every push.

**45 tests · 41 passing · 4 documenting confirmed defects.** Building the suite surfaced 5 real bugs, written up with steps, expected vs actual and root cause in [BUG_REPORTS.md](BUG_REPORTS.md). For four of them the fix is verified: with [the patch](docs/suggested-fix.patch) applied, their tests pass.

## What is covered

| Area | File | What it checks |
| --- | --- | --- |
| Auth API | `tests/api/test_auth_api.py` | Sign-up, sign-in, session token, duplicate email (422), weak password and bad email (400), wrong password (401) |
| Sign-in & access | `tests/ui/test_auth.py` | Sign-up and sign-in forms, error messages, field validation, all 6 private pages redirect anonymous visitors |
| Closet | `tests/ui/test_closet.py` | 8-piece starter closet, insight line, every category filter, category + colour together, reset |
| Add item | `tests/ui/test_add_item.py` | Photo upload, required photo and title, duplicate white-top warning |
| Fitting room | `tests/ui/test_fitting_room.py` | Empty board blocked, look saved to a date and occasion, auto-naming, deleting a look |
| Privacy | `tests/ui/test_privacy.py` | Two members: a private piece is invisible to the other member, even by direct URL; a public one is visible |
| Known defects | `tests/ui/test_known_defects.py` | The correct behaviour for FG-002 to FG-005, expected to fail until fixed |

## How it is built

```
pages/           Page objects: one class per screen, locators by role and label
tests/api/       HTTP tests against /api/auth/*
tests/ui/        Browser tests
utils/           Test data, generated photos, server-call decoding
scripts/         App readiness check + warm-up, CI summary
conftest.py      Fixtures: fresh member per test, signed-in pages, multi-user sessions
```

Design decisions:

- **Isolation.** Every test signs up its own new member, so tests never share state and can run in any order.
- **Fast setup.** Members are created through the API and the browser reuses the session cookie. Only the tests about login use the login form.
- **No sleeps.** Every wait is on a real signal: an element, a URL, or a specific backend response.
- **Known bugs as strict expected failures.** A defect test fails today. The moment a fix lands it passes, strict mode flags it, and the marker must be removed, so fixes are never silent.
- **Deterministic race reproduction.** FG-002 is intermittent in real use. The test holds one backend call (`ensureProfile`) at the network layer to reproduce it every time.
- **Artifacts on failure.** Playwright traces and screenshots are kept for failing tests, plus an HTML report for every run.

## Run it locally

Requirements: Node 22, Python 3.10+.

```bash
# 1. Start the app (it uses a built-in local database, nothing external)
git clone https://github.com/andrew84eg-ops/FashionGram app
cd app && npm install && npm run dev      # serves http://127.0.0.1:8080
cd ..

# 2. Run the tests
pip install -r requirements.txt
python -m playwright install chromium
python scripts/wait_for_app.py            # waits for the app and warms it up
python -m pytest                          # full suite
python -m pytest -m smoke                 # quick smoke run
python -m pytest -m api                   # API tests only
python -m pytest --headed --slowmo 300    # watch it run
```

The HTML report is written to `reports/report.html`.

## Continuous integration

`.github/workflows/e2e.yml` runs on every push and pull request, weekly on Monday, and on demand. It checks out both repositories, starts the app, runs the suite, writes a pass/fail summary to the run page, and uploads the report, traces and app log.

## Author

Andrew N. Soliman · Cairo. Built with AI coding agents (Claude Code) as part of my automation workflow.
