import os
from flask import Flask, request, render_template_string
import psycopg2
import sqlite3

app = Flask(__name__)

# Detect if running on Render
DATABASE_URL = os.environ.get("DATABASE_URL")

def get_connection():
    if DATABASE_URL:
        # Render PostgreSQL
        return psycopg2.connect(DATABASE_URL, sslmode="require")
    else:
        # Local fallback (SQLite)
        return sqlite3.connect("local.db")


def create_table():
    conn = get_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT,
            sapid TEXT,
            rollno TEXT,
            phone TEXT,
            email TEXT,
            branch TEXT,
            specialization TEXT
        )
        """)
    else:
        cur.execute("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            sapid TEXT,
            rollno TEXT,
            phone TEXT,
            email TEXT,
            branch TEXT,
            specialization TEXT
        )
        """)

    conn.commit()
    cur.close()
    conn.close()


create_table()


HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Student Database</title>
</head>
<body>
    <h2>Add Student</h2>
    <form method="POST" action="/add">
        Name: <input type="text" name="name"><br><br>
        SAP ID: <input type="text" name="sapid"><br><br>
        Roll No: <input type="text" name="rollno"><br><br>
        Phone: <input type="text" name="phone"><br><br>
        Email: <input type="text" name="email"><br><br>
        Branch: <input type="text" name="branch"><br><br>
        Specialization: <input type="text" name="specialization"><br><br>
        <button type="submit">Add</button>
    </form>

    <hr>

    <h2>Search Student</h2>
    <form method="GET" action="/search">
        Name: <input type="text" name="name">
        <button type="submit">Search</button>
    </form>

    {% if student %}
        <h3>Student Details:</h3>
        {{ student }}
    {% endif %}
</body>
</html>
"""


@app.route("/")
def home():
    return render_template_string(HTML_PAGE)


@app.route("/add", methods=["POST"])
def add():
    data = (
        request.form["name"],
        request.form["sapid"],
        request.form["rollno"],
        request.form["phone"],
        request.form["email"],
        request.form["branch"],
        request.form["specialization"]
    )

    conn = get_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        cur.execute("""
            INSERT INTO students
            (name, sapid, rollno, phone, email, branch, specialization)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, data)
    else:
        cur.execute("""
            INSERT INTO students
            (name, sapid, rollno, phone, email, branch, specialization)
            VALUES (?,?,?,?,?,?,?)
        """, data)

    conn.commit()
    cur.close()
    conn.close()

    return "Student Added Successfully! <br><a href='/'>Go Back</a>"


@app.route("/search")
def search():
    name = request.args.get("name")

    conn = get_connection()
    cur = conn.cursor()

    if DATABASE_URL:
        cur.execute("SELECT * FROM students WHERE name=%s", (name,))
    else:
        cur.execute("SELECT * FROM students WHERE name=?", (name,))

    student = cur.fetchone()

    cur.close()
    conn.close()

    return render_template_string(HTML_PAGE, student=student)


if __name__ == "__main__":
    app.run(debug=True)