from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "todo_secret_key"

def get_db_connection():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_db_connection()

    conn.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        password TEXT NOT NULL
    )
    """)
    conn.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task TEXT NOT NULL,
    description TEXT,
    status TEXT DEFAULT 'pending'
)
""")

    conn.commit()
    conn.close()
create_tables()

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()

        user = conn.execute(
            "SELECT * FROM users WHERE email = ? AND password = ?",
            (email, password)
        ).fetchone()

        conn.close()

        if user:
            return redirect("/dashboard")

        else:
            return "Invalid email or password"

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    conn = get_db_connection()

    pending_tasks = conn.execute(
        "SELECT * FROM tasks WHERE status = 'pending'"
    ).fetchall()

    completed_tasks = conn.execute(
        "SELECT * FROM tasks WHERE status = 'completed'"
    ).fetchall()

    conn.close()

    return render_template(
        "dashboard.html",
        pending_tasks=pending_tasks,
        completed_tasks=completed_tasks
    )

@app.route("/add_task", methods=["GET", "POST"])
def add_task():

    if request.method == "POST":

        task = request.form["task"]

        conn = get_db_connection()

        conn.execute(
            "INSERT INTO tasks (task) VALUES (?)",
            (task,)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    return render_template("add_task.html")

@app.route("/delete_task/<int:id>")
def delete_task(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/edit_task/<int:id>", methods=["GET", "POST"])
def edit_task(id):

    conn = get_db_connection()

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    if request.method == "POST":
        new_task = request.form["task"]

        conn.execute(
            "UPDATE tasks SET task = ? WHERE id = ?",
            (new_task, id)
        )

        conn.commit()
        conn.close()

        return redirect("/dashboard")

    conn.close()

    return render_template("edit_task.html", task=task)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        conn = get_db_connection()
        conn.execute(
            "INSERT INTO users (email, password) VALUES (?, ?)",
            (email, password)
        )
        conn.commit()
        conn.close()

        return redirect("/login")

    return render_template("register.html")

@app.route("/complete_task/<int:id>")
def complete_task(id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET status = 'completed' WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/dashboard")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)