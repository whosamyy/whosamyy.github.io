"""Flask and SQLite starter for Amy's Drink Diary."""

from pathlib import Path
import sqlite3

from flask import Flask


app = Flask(__name__)
DATABASE = Path(__file__).resolve().parent / "drinks.db"


def init_db():
    """Create the database and drinks table without changing existing data."""
    with sqlite3.connect(DATABASE) as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS drinks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                shop TEXT NOT NULL,
                drink_name TEXT NOT NULL,
                category TEXT NOT NULL,
                sugar_level TEXT,
                ice_level TEXT,
                rating INTEGER NOT NULL,
                date TEXT,
                notes TEXT
            )
            """
        )


@app.route("/")
def index():
    return "Amy's Drink Diary — Flask + SQLite starter."


init_db()


if __name__ == "__main__":
    app.run(debug=True)
