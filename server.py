from flask import Flask, request, jsonify, render_template, redirect, session
from payments_stk import PayHeroSTK, CONFIG, generate_ticket, send_ticket_email
from datetime import datetime
import time
import sqlite3

app = Flask(__name__)
app.secret_key = "carlix_secret_key"

payhero = PayHeroSTK(CONFIG)

# ---------------- DATABASE ----------------
def get_db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn


def create_admin():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    """)

    existing = conn.execute("SELECT * FROM admins WHERE username=?", ("Charles",)).fetchone()
    if not existing:
        conn.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("Charles", "CarlixGroup@2026"))

    conn.commit()
    conn.close()


def create_tickets_table():
    conn = get_db()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS tickets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        tournament TEXT,
        amount INTEGER,
        ticket_ref TEXT,
        mpesa_code TEXT,
        used INTEGER DEFAULT 0,
        created_at TEXT
    )
    """)
    conn.commit()
    conn.close()


create_admin()
create_tickets_table()

# ---------------- ROUTES ----------------

# 🏠 HOMEPAGE
@app.route("/")
def home():
    return render_template("homePage.html")


# 🎟 TICKETS PAGE (🔥 THIS FIXES YOUR 404)
@app.route("/tickets")
def tickets():
    return render_template("tickets.html")


# 🔐 LOGIN
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        admin = conn.execute(
            "SELECT * FROM admins WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if admin:
            session["admin"] = username
            return redirect("/admin")
        else:
            return "Invalid login"

    return render_template("login.html")


# 🖥 ADMIN DASHBOARD
@app.route("/admin")
def admin():
    if "admin" not in session:
        return redirect("/login")
    return render_template("admin.html")


# 📷 QR SCANNER
@app.route("/scanner")
def scanner():
    if "admin" not in session:
        return redirect("/login")
    return render_template("scanner.html")


# 🚪 LOGOUT
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/")


# 💳 PAYMENT
@app.route("/pay", methods=["POST"])
def pay():

    data = request.json

    name = data["name"]
    phone = data["phone"]
    email = data["email"]
    tournament = data["tournament"]
    amount = data["amount"]

    reference = "TKO_" + datetime.now().strftime("%Y%m%d%H%M%S")

    result = payhero.initiate_stk_push(phone, amount, reference, name)

    if not result or not result.get("success"):
        return jsonify({"status": "error"})

    api_reference = result.get("reference")

    for _ in range(6):
        time.sleep(5)
        status = payhero.check_payment_status(api_reference)

        if status and status.get("status") == "SUCCESS":

            mpesa_code = status.get("provider_reference", "N/A")

            qr_path = generate_ticket(
                name,
                phone,
                tournament,
                amount,
                reference,
                mpesa_code
            )

            send_ticket_email(email, name, tournament, reference, qr_path)

            # SAVE TO DATABASE
            conn = get_db()
            conn.execute("""
            INSERT INTO tickets (name, email, phone, tournament, amount, ticket_ref, mpesa_code, used, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                name,
                email,
                phone,
                tournament,
                amount,
                reference,
                mpesa_code,
                0,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))
            conn.commit()
            conn.close()

            return jsonify({
                "status": "success",
                "reference": reference
            })

    return jsonify({"status": "failed"})


# 📊 ALL TICKETS
@app.route("/api/tickets")
def get_tickets():
    if "admin" not in session:
        return jsonify([])

    conn = get_db()
    tickets = conn.execute("SELECT * FROM tickets").fetchall()
    conn.close()

    return jsonify([dict(t) for t in tickets])


# 📊 LIVE STATS
@app.route("/api/stats")
def stats():
    if "admin" not in session:
        return jsonify({})

    conn = get_db()

    total = conn.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    used = conn.execute("SELECT COUNT(*) FROM tickets WHERE used=1").fetchone()[0]
    remaining = total - used
    revenue = total * 200

    conn.close()

    return jsonify({
        "total": total,
        "used": used,
        "remaining": remaining,
        "revenue": revenue
    })


# ✅ VERIFY QR
@app.route("/verify-ticket", methods=["POST"])
def verify_ticket():

    data = request.json
    qr_data = data.get("qr")

    print("QR SCANNED:\n", qr_data)

    reference = None

    for line in qr_data.split("\n"):
        if "Ticket Ref" in line:
            reference = line.split(":")[1].strip()

    if not reference:
        return jsonify({"status": "invalid"})

    conn = get_db()

    ticket = conn.execute(
        "SELECT * FROM tickets WHERE ticket_ref=?",
        (reference,)
    ).fetchone()

    if not ticket:
        return jsonify({"status": "invalid"})

    if ticket["used"] == 1:
        return jsonify({
            "status": "used",
            "name": ticket["name"],
            "tournament": ticket["tournament"],
            "mpesa": ticket["mpesa_code"]
        })

    conn.execute(
        "UPDATE tickets SET used=1 WHERE ticket_ref=?",
        (reference,)
    )
    conn.commit()
    conn.close()

    return jsonify({
        "status": "valid",
        "name": ticket["name"],
        "tournament": ticket["tournament"],
        "mpesa": ticket["mpesa_code"]
    })


# 🧪 TEST
@app.route("/test")
def test():
    return "Server is working!"


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)