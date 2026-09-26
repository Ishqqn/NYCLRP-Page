from flask import Flask, render_template
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

DATABASE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "database.db"
)


def get_db():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_db()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_type TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    connection.execute("""
        CREATE TABLE IF NOT EXISTS staff_members (
            discord_id TEXT PRIMARY KEY,
            username TEXT NOT NULL,
            display_name TEXT NOT NULL,
            rank TEXT NOT NULL,
            status TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    connection.commit()
    connection.close()


def create_log(log_type, message):
    connection = get_db()

    connection.execute(
        """
        INSERT INTO logs (
            log_type,
            message,
            created_at
        )
        VALUES (?, ?, ?)
        """,
        (
            log_type,
            message,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
    )

    connection.commit()
    connection.close()


@app.route("/")
def home():
    connection = get_db()

    recent_logs = connection.execute(
        """
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 10
        """
    ).fetchall()

    connection.close()

    return render_template(
        "index.html",
        recent_logs=recent_logs
    )


@app.route("/staff")
def staff():
    return render_template("staff.html")


@app.route("/staff-online")
def staff_online():
    connection = get_db()

    staff_members = connection.execute(
        """
        SELECT *
        FROM staff_members
        ORDER BY
            CASE rank
                WHEN 'Ownership Team' THEN 1
                WHEN 'Devs Team' THEN 2
                WHEN 'Directive Team' THEN 3
                WHEN 'Executive Team' THEN 4
                WHEN 'Management Team' THEN 5
                WHEN 'Staff Supervisory Team' THEN 6
                WHEN 'Trial Supervisor' THEN 7
                WHEN 'Administration Team' THEN 8
                WHEN 'Trial Administrator' THEN 9
                WHEN 'Moderation Team' THEN 10
                WHEN 'Trial Moderator' THEN 11
                ELSE 99
            END,
            display_name
        """
    ).fetchall()

    connection.close()

    return render_template(
        "staff_online.html",
        staff_members=staff_members
    )


@app.route("/logs")
def logs():
    connection = get_db()

    logs_list = connection.execute(
        """
        SELECT *
        FROM logs
        ORDER BY id DESC
        LIMIT 100
        """
    ).fetchall()

    connection.close()

    return render_template(
        "logs.html",
        logs=logs_list
    )


@app.route("/server")
def server():
    return render_template("server.html")


if __name__ == "__main__":
    init_database()

    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )