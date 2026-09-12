# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Flask web app that lists courses and shows per-course detail pages, plus a contact form. Data is hardcoded in memory — there is no database, ORM, or persistence layer.

## Commands

A `venv/` already exists in the repo root. On Windows, call it explicitly rather than relying on an activated shell:

```powershell
& .\venv\Scripts\python.exe src\app.py                      # run app -> http://127.0.0.1:5000
& .\venv\Scripts\python.exe -m unittest discover -s tests   # all tests
& .\venv\Scripts\python.exe -m unittest tests.test_app      # one file
& .\venv\Scripts\python.exe -m unittest tests.test_app.AppTestCase.test_index   # one test
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
```

Tests must be run from the repo root — `tests/test_app.py` resolves `src/` relative to its own file but the `tests.test_app` module path assumes cwd is the root.

## Architecture

### Import path is implicit, not a package

Neither `src/` nor `tests/` has an `__init__.py`. Modules import each other flat (`from views import ...`, `from models import courses`), which only resolves because:

- `python src/app.py` puts `src/` on `sys.path` as the script directory, and
- `tests/test_app.py` manually does `sys.path.insert(0, ...src)` before `from app import app`.

So the app **cannot** be started as `python -m src.app` or imported as `src.app`, and any new module under `src/` must keep using flat imports. Changing this means touching the sys.path shim in the tests too.

### Routing is decoupled from views

[src/app.py](src/app.py) registers every route with `add_url_rule()` instead of `@app.route()`. View functions in [src/views.py](src/views.py) are plain functions with no Flask decorators, so they stay importable and testable on their own. Adding a route means editing both files: define the function in `views.py`, register it in `app.py`. Non-GET methods must be declared at registration (see the `contact` rule's `methods=['GET', 'POST']`).

### Course "IDs" are 1-based list positions

There is no `id` field on `Course` ([src/models.py](src/models.py)). The URL segment is an index:

- [index.html](src/templates/index.html) builds links with `url_for('course', course_id=loop.index)` (Jinja's 1-based loop counter).
- [views.py:10](src/views.py#L10) reverses it with `int(course_id) - 1` and bounds-checks against `len(courses)`.

Reordering or removing entries in the `courses` list silently changes every course URL, and tests assert on specific indices (`/course/4` is the Go course). `int(course_id)` also raises on a non-numeric segment — that path returns a 500, not the 404 the out-of-range branch returns.

### Form handling is hand-rolled

The contact view uses no Flask-WTF, no CSRF token, no flash/redirect. On POST it validates into an `errors` dict and re-renders `contact.html` with the submitted values so fields repopulate; on success it re-renders with `success=True`. Template logic branches on the presence of `errors` / `success`. Keep new forms in this shape unless deliberately introducing a form library. Successful submissions are only `print()`ed — nothing is stored or emailed.

### Templates and styling

All templates extend [layout.html](src/templates/layout.html) (`{% block title %}` / `{% block content %}`), which owns the header nav and footer. New pages need a nav entry there.

[src/static/css/styles.css](src/static/css/styles.css) defines design tokens in `:root` that mirror `.claude/skills/ui-designer/references/design-system.md`. Reuse those variables rather than introducing new literal colors or spacing values.

### Greeting when starting the service

`python src/app.py` prints a banner before handing off to Flask:

```
========================================
  Course Explainer
  Running at http://127.0.0.1:5000
========================================
```

`startup_banner()` in [src/app.py](src/app.py) only builds the string — the `print()` and `app.run()` live in the `__main__` block, so importing `app` (as the tests do) stays side-effect free. Two constraints to preserve when editing it:

- The URL is derived from the `HOST`/`PORT` constants that are also passed to `app.run()`, so the greeting can't drift from where the server actually binds.
- The print is guarded by `os.environ.get('WERKZEUG_RUN_MAIN') != 'true'`. The debug reloader re-executes this module in a child process; without the guard the banner appears twice.

### Dependency notes

`requirements.txt` lists `gunicorn` and `python-dotenv`, but nothing in the code loads dotenv and there is no WSGI/Procfile entrypoint — the flat-import layout means gunicorn would need its working directory set to `src/`. There is no `.env` file in the repo.

## Development Workflow

### Add unit tests

Any change needs matching tests in [tests/test_app.py](tests/test_app.py), and the suite must pass before you're done. Tests drive `app.test_client()` and assert on raw response bytes (`assertIn(b'...', response.data)`), so they are tightly coupled to template copy — editing user-facing text in a template usually means updating the corresponding assertion.

### Verify changes with Playwright (MANDATORY)

After implementing any new feature:

1. Start the app if it isn't already running (`& .\venv\Scripts\python.exe src\app.py`).
2. Use the Playwright MCP tool against `http://127.0.0.1:5000`.
3. Navigate to and interact with the new feature to confirm it works.
4. Screenshot it and save to `test-output/` (create the folder if needed) as `feature-name-verification-YYYY-MM-DD.png`.

The `ui-testing-agent` subagent automates this loop and is the preferred way to run it.

## Repo-specific tooling

- `.claude/skills/ui-designer/` — design-system rules and a `run_and_verify.py` helper that boots Flask and waits for it to answer on port 5000. Invoked for any styling/layout work.
- `.claude/agents/ux-design-planner.md` — design-first agent to run *before* coding a new UI feature.
- `.claude/commands/implement_ui_user_story.md` — chains design → implement + test → visual verification.
