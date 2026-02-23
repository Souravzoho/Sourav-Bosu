from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
import string
import random

app = Flask(__name__)

BASE_URL = "http://127.0.0.1:5000/"
API_KEY = "YOUR_SECRET_API_KEY"

# Create DB
def init_db():
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS links
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  original TEXT,
                  short TEXT)''')
    conn.commit()
    conn.close()

init_db()

# Generate short code
def generate_short():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    original = request.form.get("url")
    short_code = generate_short()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO links (original, short) VALUES (?,?)",
              (original, short_code))
    conn.commit()
    conn.close()

    return BASE_URL + short_code

# API System
@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    key = request.form.get("api_key")
    url = request.form.get("url")

    if key != API_KEY:
        return jsonify({"error": "Invalid API Key"})

    short_code = generate_short()

    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("INSERT INTO links (original, short) VALUES (?,?)",
              (url, short_code))
    conn.commit()
    conn.close()

    return jsonify({
        "short_url": BASE_URL + short_code
    })

# Step 1
@app.route("/<short_code>")
def verify1(short_code):
    return render_template("verify1.html", code=short_code)

# Step 2
@app.route("/verify/<short_code>")
def verify2(short_code):
    return render_template("verify2.html", code=short_code)

# Final Redirect
@app.route("/go/<short_code>")
def go(short_code):
    conn = sqlite3.connect("database.db")
    c = conn.cursor()
    c.execute("SELECT original FROM links WHERE short=?", (short_code,))
    data = c.fetchone()
    conn.close()

    if data:
        return redirect(data[0])
    return "Link not found"

if __name__ == "__main__":
    app.run(debug=True)
