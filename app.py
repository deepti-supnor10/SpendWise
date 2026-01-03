from flask import Flask, render_template, request, redirect, session
import sqlite3
import pandas as pd
from sklearn.linear_model import LinearRegression
from database import init_db, get_connection

app = Flask(__name__)
app.secret_key = "spendwise_secret"

init_db()

# ---------- LOGIN ----------
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("INSERT OR IGNORE INTO users (email) VALUES (?)", (email,))
        conn.commit()
        conn.close()

        session["user"] = email
        return redirect("/dashboard")

    return render_template("login.html")


# ---------- DASHBOARD ----------
@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    df = pd.read_sql(
        "SELECT * FROM expenses WHERE user_email = ?",
        conn,
        params=(session["user"],)
    )
    conn.close()

    total = df["amount"].sum() if not df.empty else 0
    count = len(df)
    avg = round(total / count, 2) if count else 0

    return render_template("dashboard.html",
                           total=total,
                           count=count,
                           average=avg,
                           user=session["user"])


# ---------- ADD EXPENSE ----------
@app.route("/add", methods=["GET", "POST"])
def add_expense():
    if "user" not in session:
        return redirect("/")

    if request.method == "POST":
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        INSERT INTO expenses (user_email, date, category, amount, note)
        VALUES (?, ?, ?, ?, ?)
        """, (
            session["user"],
            request.form["date"],
            request.form["category"],
            float(request.form["amount"]),
            request.form.get("note", "")
        ))

        conn.commit()
        conn.close()
        return redirect("/dashboard")

    return render_template("add_expense.html")


# ---------- ANALYTICS ----------
@app.route("/analytics")
def analytics():
    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    df = pd.read_sql(
        "SELECT category, SUM(amount) as total FROM expenses WHERE user_email = ? GROUP BY category",
        conn,
        params=(session["user"],)
    )
    conn.close()

    data = dict(zip(df["category"], df["total"])) if not df.empty else {}
    return render_template("analytics.html", data=data)


# ---------- PREDICTION ----------
@app.route("/predict")
def predict():
    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    df = pd.read_sql(
        "SELECT date, amount FROM expenses WHERE user_email = ? ORDER BY date",
        conn,
        params=(session["user"],)
    )
    conn.close()

    if len(df) < 5:
        prediction = "Not enough data"
    else:
        df["day"] = range(1, len(df) + 1)
        X = df[["day"]]
        y = df["amount"]

        model = LinearRegression()
        model.fit(X, y)

        prediction = round(model.predict([[len(df) + 1]])[0], 2)

    return render_template("predict.html", prediction=prediction)


# ---------- RESET USER DASHBOARD ----------
@app.route("/reset", methods=["POST"])
def reset():
    if "user" not in session:
        return redirect("/")

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE user_email = ?", (session["user"],))
    conn.commit()
    conn.close()

    return redirect("/dashboard")


# ---------- LOGOUT ----------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)
