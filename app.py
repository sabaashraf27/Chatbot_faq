"""
app.py
-------
Flask web application exposing the FAQ chatbot via REST endpoints
and a polished chat UI.
"""

import os
import sys

from flask import Flask, jsonify, render_template, request

# Allow sibling imports
sys.path.insert(0, os.path.dirname(__file__))
from nlp.similarity_engine import FAQMatcher

# ─── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__, template_folder="templates", static_folder="static")
app.config["JSON_SORT_KEYS"] = False

# Initialise matcher once at startup (loads & vectorises FAQs)
matcher = FAQMatcher()

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the chat UI."""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    POST /api/chat
    Body: { "message": "<user question>" }
    Returns: {
        "answer": str,
        "matched_question": str | null,
        "confidence": float,
        "confidence_label": str,
        "category": str | null,
        "top_matches": list
    }
    """
    data = request.get_json(silent=True) or {}
    user_message = (data.get("message") or "").strip()

    if not user_message:
        return jsonify({"error": "Empty message"}), 400

    result = matcher.match(user_message)
    return jsonify(result)


@app.route("/api/faqs", methods=["GET"])
def list_faqs():
    """Return all FAQ questions (useful for autocomplete / quick-picks)."""
    return jsonify({"questions": matcher.all_questions()})


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "faq_count": len(matcher.faqs)})


# ─── Entry point ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, port=port)
