import os, sqlite3, hashlib, secrets, string, time
from functools import wraps
from flask import Flask, request, redirect, url_for, render_template, flash, session, abort
from werkzeug.security import check_password_hash, generate_password_hash

APP_SECRET = os.getenv("APP_SECRET", "dev-only-change-me")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "change-this-admin-password")
DB_PATH = os.getenv("DATABASE_PATH", "rewards.db")
POINTS_PER_BOX = int(os.getenv("POINTS_PER_BOX", "10"))
app = Flask(__name__)
app.secret_key = APP_SECRET

def db():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    with db() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS codes(
          id INTEGER PRIMARY KEY, code_hash TEXT UNIQUE NOT NULL,
          points INTEGER NOT NULL, status TEXT NOT NULL DEFAULT 'unused',
          redeemed_by TEXT, redeemed_at TEXT
        );
        CREATE TABLE IF NOT EXISTS redemptions(
          id INTEGER PRIMARY KEY, code_id INTEGER NOT NULL UNIQUE REFERENCES codes(id),
          customer TEXT NOT NULL, points INTEGER NOT NULL, redeemed_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS customers(
          email TEXT PRIMARY KEY, points INTEGER NOT NULL DEFAULT 0,
          boxes INTEGER NOT NULL DEFAULT 0
        );
        """)
        # One-time demo codes; real deployments should generate batches from admin.
        if con.execute("SELECT COUNT(*) FROM codes").fetchone()[0] == 0:
            for _ in range(5):
                raw = make_code()
                con.execute("INSERT OR IGNORE INTO codes(code_hash, points) VALUES (?,?)",
                            (hash_code(raw), POINTS_PER_BOX))

def make_code():
    alphabet = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    return "-".join("".join(secrets.choice(alphabet) for _ in range(4)) for _ in range(3))

def hash_code(code):
    return hashlib.sha256(code.replace("-", "").replace(" ", "").upper().encode()).hexdigest()

def admin_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        if not session.get("admin"):
            return redirect(url_for("admin_login"))
        return fn(*args, **kwargs)
    return wrapped

@app.get("/")
def home():
    return render_template("index.html")

@app.post("/redeem")
def redeem():
    email = request.form.get("email", "").strip().lower()
    code = request.form.get("code", "").strip()
    if not email or "@" not in email or len(email) > 254 or not code:
        flash("Enter a valid email address and the code inside your box.", "error")
        return redirect(url_for("home"))
    digest = hash_code(code)
    con = db()
    try:
        con.execute("BEGIN IMMEDIATE")
        row = con.execute("SELECT id, points, status FROM codes WHERE code_hash=?", (digest,)).fetchone()
        if row is None:
            con.rollback()
            flash("That code was not recognized. Check it and try again.", "error")
            return redirect(url_for("home"))
        if row["status"] != "unused":
            con.rollback()
            flash("This code has already been redeemed.", "error")
            return redirect(url_for("home"))
        con.execute("UPDATE codes SET status='redeemed', redeemed_by=?, redeemed_at=CURRENT_TIMESTAMP WHERE id=? AND status='unused'",
                    (email, row["id"]))
        if con.execute("SELECT changes()").fetchone()[0] != 1:
            con.rollback()
            flash("This code has already been redeemed.", "error")
            return redirect(url_for("home"))
        con.execute("""INSERT INTO customers(email,points,boxes) VALUES(?,?,1)
          ON CONFLICT(email) DO UPDATE SET points=points+excluded.points, boxes=boxes+1""",
                    (email, row["points"]))
        con.execute("INSERT INTO redemptions(code_id,customer,points) VALUES(?,?,?)",
                    (row["id"], email, row["points"]))
        con.commit()
        flash(f"Success! {row['points']} points added to {email}.", "success")
    except sqlite3.Error:
        con.rollback()
        flash("We couldn't process that code. Please try again.", "error")
    finally:
        con.close()
    return redirect(url_for("home"))

@app.get("/admin/login")
def admin_login():
    return render_template("login.html")

@app.post("/admin/login")
def admin_login_post():
    supplied = request.form.get("password", "")
    # Env value is plain configuration in this demo; production should store a password hash.
    if secrets.compare_digest(supplied, ADMIN_PASSWORD):
        session["admin"] = True
        return redirect(url_for("dashboard"))
    flash("Incorrect password.", "error")
    return redirect(url_for("admin_login"))

@app.post("/admin/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.get("/admin")
@admin_required
def dashboard():
    with db() as con:
        stats = {
          "customers": con.execute("SELECT COUNT(*) FROM customers").fetchone()[0],
          "points": con.execute("SELECT COALESCE(SUM(points),0) FROM customers").fetchone()[0],
          "redeemed": con.execute("SELECT COUNT(*) FROM codes WHERE status='redeemed'").fetchone()[0],
          "unused": con.execute("SELECT COUNT(*) FROM codes WHERE status='unused'").fetchone()[0]
        }
        customers = con.execute("SELECT email,points,boxes FROM customers ORDER BY points DESC LIMIT 100").fetchall()
        recent = con.execute("""SELECT customer,points,redeemed_at FROM redemptions
                                ORDER BY id DESC LIMIT 20""").fetchall()
    return render_template("dashboard.html", stats=stats, customers=customers, recent=recent)

@app.post("/admin/codes")
@admin_required
def create_codes():
    try:
        count = int(request.form.get("count", "0"))
    except ValueError:
        count = 0
    if count < 1 or count > 500:
        flash("Choose a batch size between 1 and 500.", "error")
        return redirect(url_for("dashboard"))
    generated = []
    with db() as con:
        for _ in range(count):
            raw = make_code()
            con.execute("INSERT INTO codes(code_hash,points) VALUES (?,?)", (hash_code(raw), POINTS_PER_BOX))
            generated.append(raw)
    session["new_codes"] = generated
    return redirect(url_for("code_batch"))

@app.get("/admin/codes/latest")
@admin_required
def code_batch():
    codes = session.pop("new_codes", [])
    if not codes:
        return redirect(url_for("dashboard"))
    return render_template("codes.html", codes=codes)

@app.get("/health")
def health():
    return {"status": "ok"}

if __name__ == "__main__":
    init_db()
    app.run(host="127.0.0.1", port=int(os.getenv("PORT", "5000")), debug=os.getenv("FLASK_DEBUG") == "1")
