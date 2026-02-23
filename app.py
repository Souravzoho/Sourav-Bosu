import os
from flask import Flask, render_template, request, redirect, jsonify
from pymongo import MongoClient
import string
import random

app = Flask(__name__)

BASE_URL = os.getenv("BASE_URL")
API_KEY = os.getenv("gsyiwhgra999")

# MongoDB
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["urlshort"]
links = db["links"]

def generate_short():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/shorten", methods=["POST"])
def shorten():
    original = request.form.get("url")
    short_code = generate_short()

    links.insert_one({
        "original": original,
        "short": short_code,
        "clicks": 0
    })

    return BASE_URL + short_code

@app.route("/api/shorten", methods=["POST"])
def api_shorten():
    key = request.form.get("api_key")
    url = request.form.get("url")

    if key != API_KEY:
        return jsonify({"error": "Invalid API Key"})

    short_code = generate_short()

    links.insert_one({
        "original": url,
        "short": short_code,
        "clicks": 0
    })

    return jsonify({
        "short_url": BASE_URL + short_code
    })

@app.route("/<short_code>")
def verify1(short_code):
    return render_template("verify1.html", code=short_code)

@app.route("/verify/<short_code>")
def verify2(short_code):
    return render_template("verify2.html", code=short_code)

@app.route("/go/<short_code>")
def go(short_code):
    data = links.find_one({"short": short_code})
    if data:
        links.update_one(
            {"short": short_code},
            {"$inc": {"clicks": 1}}
        )
        return redirect(data["original"])
    return "Link not found"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
