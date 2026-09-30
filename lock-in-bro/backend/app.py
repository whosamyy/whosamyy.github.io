import os
from flask import Flask, jsonify, render_template
from models import db


def create_app():
    app = Flask(__name__)
    database_url = os.environ.get("DATABASE_URL", "sqlite:///lock_in_bro.db")
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    @app.get("/api/health")
    def health():
        return jsonify(status="healthy")

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    @app.cli.command("init-db")
    def init_db():
        """Create missing tables in the configured database."""
        db.create_all()
        print("Database initialized.")

    return app


app = create_app()
if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000)
