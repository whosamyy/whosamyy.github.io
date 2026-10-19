"""Flask and SQLite starter for Amy's Drink Diary."""

from pathlib import Path
import sqlite3

from datetime import date

from flask import Flask, abort, redirect, render_template, request, url_for


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


CATEGORIES = ["Matcha", "Boba", "Coffee", "Tea", "Other"]


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


@app.route("/")
def index():
    category = request.args.get("category", "")
    shop = request.args.get("shop", "")
    minimum = request.args.get("min_rating", "")
    sort = request.args.get("sort", "newest")
    # Only these fixed SQL fragments can be used for sorting.
    sort_options = {
        "newest": "date DESC, id DESC",
        "oldest": "date ASC, id ASC",
        "highest": "rating DESC, id DESC",
        "lowest": "rating ASC, id DESC",
    }
    if sort not in sort_options:
        sort = "newest"
    conditions = []
    values = []
    errors = []
    if category:
        conditions.append("category = ?")
        values.append(category)
    if shop:
        conditions.append("shop = ?")
        values.append(shop)
    if minimum:
        try:
            minimum_number = int(minimum)
            if not 1 <= minimum_number <= 10:
                raise ValueError
            conditions.append("rating >= ?")
            values.append(minimum_number)
        except ValueError:
            errors.append("Minimum rating must be an integer from 1 to 10.")
    query = "SELECT * FROM drinks"
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY " + sort_options[sort]
    connection = get_db()
    try:
        drinks = connection.execute(query, values).fetchall()
        shops = connection.execute("SELECT DISTINCT shop FROM drinks ORDER BY shop").fetchall()
        stats = connection.execute(
            "SELECT COUNT(*) AS total, AVG(rating) AS average FROM drinks"
        ).fetchone()
        favorite = connection.execute(
            "SELECT shop, COUNT(*) AS visits FROM drinks GROUP BY shop "
            "ORDER BY visits DESC, shop ASC LIMIT 1"
        ).fetchone()
        top_rated = connection.execute(
            "SELECT * FROM drinks WHERE rating >= ? ORDER BY rating DESC, id DESC", (9,)
        ).fetchall()
    finally:
        connection.close()
    return render_template(
        "index.html", drinks=drinks, categories=CATEGORIES, shops=shops,
        stats=stats, favorite=favorite, top_rated=top_rated, errors=errors,
        filters={"category": category, "shop": shop, "min_rating": minimum, "sort": sort},
    )


def validate_drink():
    fields = ["shop", "drink_name", "category", "sugar_level", "ice_level", "rating", "date", "notes"]
    drink = {field: request.form.get(field, "").strip() for field in fields}
    errors = []
    if not drink["shop"]:
        errors.append("Shop is required.")
    if not drink["drink_name"]:
        errors.append("Drink name is required.")
    if drink["category"] not in CATEGORIES:
        errors.append("Choose a valid category.")
    try:
        rating = int(drink["rating"])
        if not 1 <= rating <= 10:
            raise ValueError
    except ValueError:
        errors.append("Rating must be an integer from 1 to 10.")
    if drink["date"]:
        try:
            date.fromisoformat(drink["date"])
        except ValueError:
            errors.append("Enter a valid date (YYYY-MM-DD).")
    return drink, errors


@app.route("/add", methods=["GET", "POST"])
def add_drink():
    drink = {}
    errors = []
    if request.method == "POST":
        drink, errors = validate_drink()
        if not errors:
            connection = get_db()
            try:
                with connection:
                    connection.execute(
                        "INSERT INTO drinks (shop, drink_name, category, sugar_level, ice_level, rating, date, notes) "
                        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple(drink.values())
                    )
            finally:
                connection.close()
            return redirect(url_for("index"))
    return render_template("drink_form.html", drink=drink, errors=errors, categories=CATEGORIES, editing=False), 400 if errors else 200


@app.route("/edit/<int:drink_id>", methods=["GET", "POST"])
def edit_drink(drink_id):
    connection = get_db()
    try:
        drink = connection.execute("SELECT * FROM drinks WHERE id = ?", (drink_id,)).fetchone()
        if drink is None:
            abort(404)
        errors = []
        if request.method == "POST":
            drink, errors = validate_drink()
            if not errors:
                with connection:
                    connection.execute(
                        "UPDATE drinks SET shop = ?, drink_name = ?, category = ?, sugar_level = ?, "
                        "ice_level = ?, rating = ?, date = ?, notes = ? WHERE id = ?",
                        (*drink.values(), drink_id),
                    )
                return redirect(url_for("index"))
    finally:
        connection.close()
    return render_template("drink_form.html", drink=drink, errors=errors, categories=CATEGORIES, editing=True), 400 if errors else 200


@app.route("/delete/<int:drink_id>", methods=["POST"])
def delete_drink(drink_id):
    connection = get_db()
    try:
        with connection:
            result = connection.execute("DELETE FROM drinks WHERE id = ?", (drink_id,))
            if result.rowcount == 0:
                abort(404)
    finally:
        connection.close()
    return redirect(url_for("index"))


init_db()


if __name__ == "__main__":
    app.run(debug=True)
