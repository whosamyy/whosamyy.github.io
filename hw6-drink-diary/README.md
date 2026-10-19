# Amy's Drink Diary

A café-themed Flask + SQLite app for CMU 15-113 HW6. Track matcha, boba,
coffee, tea, and other drinks using regular HTML/CSS and Python's `sqlite3`.

## Run locally

From the repository root, set up Flask once:

```sh
python3 -m venv /tmp/amy-drink-diary-venv
/tmp/amy-drink-diary-venv/bin/python -m pip install Flask
```

Start the app from the repository root:

```sh
/tmp/amy-drink-diary-venv/bin/python hw6-drink-diary/app.py
```

Open http://127.0.0.1:5000. Stop with Ctrl+C. Debug mode is for local development.
The virtual environment lives in `/tmp`; recreate it if your computer removes it.

## CRUD routes

| Operation | Route | Behavior |
| --- | --- | --- |
| Create | `/add` (GET/POST) | Show the form; insert a drink on valid submission. |
| Read | `/` (GET) | Show drink cards, filters, sorting, stats, and Top Rated. |
| Update | `/edit/<drink_id>` (GET/POST) | Prefill a drink's fields; save changes. |
| Delete | `/delete/<drink_id>` (POST) | Delete by id after browser confirmation. |

Shop, drink name, a listed category, and an integer rating from 1 to 10 are
required. Optional dates must be valid ISO dates. Invalid submissions show
errors and preserve the form inputs. Missing drink ids return 404.

## SQL and database

`init_db()` creates `drinks.db` beside `app.py` if missing, then uses
`CREATE TABLE IF NOT EXISTS`. It never clears existing drinks. Database files
are ignored by the main repository's `.gitignore`.

Insert, update, delete, id lookups, and filter values use `?` placeholders.
Category and shop filters use exact matches; minimum rating uses `>=`.
Active filters are joined with `AND` in the SQL `WHERE` clause.
Sorting uses `ORDER BY` fragments from a fixed dictionary, never raw user input.
Newest/oldest use the drink date, then id to break ties. Blank dates appear
last for newest and first for oldest. Rating sorts use id descending for ties.

Stats and Top Rated cover the entire diary, even when filters are active.
Stats use `COUNT`, `AVG`, and `GROUP BY shop`; most-visited shop ties are broken
alphabetically. Top Rated shows ratings 9 and 10. An empty diary shows an
em dash for the average and most visited shop.

## Files

- `app.py`: database setup, SQL queries, validation, and routes.
- `templates/base.html`: shared header, navigation, and errors.
- `templates/index.html`: cards, filters, stats, and Top Rated.
- `templates/drink_form.html`: shared add/edit form.
- `static/style.css`: responsive pink, cream, and brown styling.
- `prompt_log.md`: original prompts, preserved verbatim.

JavaScript is used only for the delete confirmation. No SQLAlchemy, React,
external database, or deployment is involved.
