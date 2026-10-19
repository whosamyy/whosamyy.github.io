# Context from my IDE setup:

## Active file: index.html

## Open tabs:
- index.html: index.html
- prompt_log.md: lock-in-bro/prompt_log.md
- README.md: lock-in-bro/README.md

## My request:
Inside my current whosamyy.github.io repository, create a new folder called:

hw6-drink-diary

This is for CMU 15-113 HW6.

For now, only create the starter structure and database setup.

Create:

hw6-drink-diary/
  app.py
  README.md
  prompt_log.md
  templates/
  static/

The project is called "Amy's Drink Diary". It will be a Flask + SQLite app for tracking drinks like matcha, boba, coffee, and tea.

Use:
- Python
- Flask
- Python's built-in sqlite3 module
- regular HTML/CSS
- no React
- no SQLAlchemy
- no external database

In app.py:

1. Set up a basic Flask app.
2. Create a SQLite database called drinks.db if it does not already exist.
3. Create a table called drinks with these columns:

id INTEGER PRIMARY KEY AUTOINCREMENT
shop TEXT NOT NULL
drink_name TEXT NOT NULL
category TEXT NOT NULL
sugar_level TEXT
ice_level TEXT
rating INTEGER NOT NULL
date TEXT
notes TEXT

Make sure the database initialization does not erase existing data when the app restarts.

Add *.db to the main repository's .gitignore if it is not already ignored.

Do not implement all CRUD features yet.

Do not commit or push anything.

Also add this exact prompt verbatim to hw6-drink-diary/prompt_log.md.

When finished, tell me:
- which files you created
- how the database is initialized
- how I can run the Flask app locally
