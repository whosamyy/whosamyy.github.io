# Amy's Drink Diary

Starter project for CMU 15-113 HW6: a Flask + SQLite app for tracking matcha,
boba, coffee, and tea. CRUD features are not implemented yet.

## Run locally

From the repository root:

```sh
cd hw6-drink-diary
python3 -m venv /tmp/amy-drink-diary-venv
source /tmp/amy-drink-diary-venv/bin/activate
python -m pip install Flask
python app.py
```

Open http://127.0.0.1:5000 in your browser. Stop the server with Ctrl+C.
The development server runs with debug mode enabled for local use.

## Database setup

When the app loads, `init_db()` opens `drinks.db` beside `app.py` using
Python's built-in `sqlite3` module. SQLite creates the file if needed.
`CREATE TABLE IF NOT EXISTS drinks` creates the table only when it is missing,
so restarting the app preserves existing records.

The table contains `id`, `shop`, `drink_name`, `category`, `sugar_level`,
`ice_level`, `rating`, `date`, and `notes`. The main repository's `.gitignore`
already ignores `*.db` files.

## Structure

- `app.py`: Flask app, placeholder home route, and database initialization.
- `templates/`: reserved for regular HTML templates.
- `static/`: reserved for CSS and other static assets.
- `prompt_log.md`: original setup prompt.

There is no React, SQLAlchemy, or external database.
