"""
similarity_engine.py
---------------------
Builds a TF-IDF matrix over all FAQ questions and uses cosine
similarity to find the best match for a user query.

Also supports an intent-keyword fallback for short / ambiguous queries.
"""

import json
import os
from typing import Optional

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Local import
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from nlp.nlp_processor import preprocess_to_string, preprocess

# ─── Constants ────────────────────────────────────────────────────────────────
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "faqs.json")
MIN_CONFIDENCE = 0.15        # threshold below which we say "no good match"
HIGH_CONFIDENCE = 0.55       # threshold for a strong match

# Category-level intent keywords
INTENT_KEYWORDS = {
    "returns":      ["return", "refund", "exchange", "send", "back", "money", "replace", "item", "product", "bought", "purchas"],
    "shipping":     ["ship", "deliver", "track", "package", "arriv", "international", "express", "long", "take", "days"],
    "payments":     ["pay", "payment", "credit", "card", "paypal", "discount", "coupon", "promo"],
    "orders":       ["order", "cancel", "modify", "change", "placed"],
    "account":      ["password", "login", "account", "forgot", "reset", "sign"],
    "privacy":      ["data", "privacy", "personal", "safe", "secur", "gdpr", "information", "info"],
    "support":      ["contact", "support", "help", "phone", "email", "chat"],
    "rewards":      ["reward", "loyalty", "point", "earn", "redeem"],
    "warranty":     ["warranty", "guarantee", "defect", "broken", "repair"],
    "sustainability": ["eco", "green", "sustainable", "recycle", "environment"],
    "discounts":    ["student", "military", "discount", "veteran", "deal"],
}


class FAQMatcher:
    """
    Encapsulates the FAQ corpus and matching logic.
    Call `match(user_query)` to get the best answer.
    """

    def __init__(self, data_path: str = DATA_PATH):
        with open(data_path, "r", encoding="utf-8") as f:
            self.faqs: list[dict] = json.load(f)

        # Pre-process every FAQ question
        self.processed_questions: list[str] = [
            preprocess_to_string(faq["question"]) for faq in self.faqs
        ]

        # Build TF-IDF model
        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 2),    # unigrams + bigrams
            min_df=1,
            max_df=0.95,
            sublinear_tf=True,     # log(1+tf) — reduces impact of very common terms
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(self.processed_questions)

    # ─── Public API ───────────────────────────────────────────────────────────

    def match(self, user_query: str) -> dict:
        """
        Returns a result dict:
          {
            "answer": str,
            "matched_question": str,
            "confidence": float,      # 0.0 – 1.0
            "confidence_label": str,  # "high" | "medium" | "low" | "none"
            "category": str,
            "top_matches": list[dict] # top-3 alternatives
          }
        """
        processed_query = preprocess_to_string(user_query)

        # 1) TF-IDF cosine similarity
        query_vec = self.vectorizer.transform([processed_query])
        scores: np.ndarray = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        top_idx = int(np.argmax(scores))
        top_score = float(scores[top_idx])

        # 2) Intent-keyword fallback for very short / low-scoring queries
        if top_score < MIN_CONFIDENCE:
            intent_idx = self._intent_fallback(user_query, scores)
            if intent_idx is not None:
                top_idx = intent_idx
                top_score = max(top_score, MIN_CONFIDENCE)

        # 3) Build top-3 alternatives (excluding the winner)
        ranked = sorted(
            [(i, float(s)) for i, s in enumerate(scores) if i != top_idx],
            key=lambda x: x[1],
            reverse=True
        )[:2]
        top_matches = [
            {"question": self.faqs[i]["question"], "confidence": round(s, 3)}
            for i, s in ranked if s > 0.05
        ]

        confidence_label = self._label(top_score)

        if confidence_label == "none":
            return {
                "answer": (
                    "I'm sorry, I couldn't find a good match for your question. "
                    "Try rephrasing, or contact our support team at support@example.com "
                    "for personalised help."
                ),
                "matched_question": None,
                "confidence": round(top_score, 3),
                "confidence_label": "none",
                "category": None,
                "top_matches": [],
            }

        faq = self.faqs[top_idx]
        return {
            "answer": faq["answer"],
            "matched_question": faq["question"],
            "confidence": round(top_score, 3),
            "confidence_label": confidence_label,
            "category": faq["category"],
            "top_matches": top_matches,
        }

    def all_questions(self) -> list[str]:
        """Return the list of all FAQ questions (for display/autocomplete)."""
        return [faq["question"] for faq in self.faqs]

    # ─── Helpers ──────────────────────────────────────────────────────────────

    def _intent_fallback(self, raw_query: str, scores: np.ndarray) -> Optional[int]:
        """
        Check if any category keywords match. If so, return the index of
        the highest-scoring FAQ in that category (or None if no match).
        """
        tokens = set(preprocess(raw_query))
        matched_categories = []
        for category, keywords in INTENT_KEYWORDS.items():
            if tokens & set(keywords):
                matched_categories.append(category)

        if not matched_categories:
            return None

        # Among matching categories, pick the FAQ with the highest cosine score
        candidates = [
            (i, float(scores[i]))
            for i, faq in enumerate(self.faqs)
            if faq["category"] in matched_categories
        ]
        if not candidates:
            return None
        return max(candidates, key=lambda x: x[1])[0]

    @staticmethod
    def _label(score: float) -> str:
        if score >= HIGH_CONFIDENCE:
            return "high"
        if score >= MIN_CONFIDENCE:
            return "medium"
        return "none"


# ─── Quick test ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    matcher = FAQMatcher()
    queries = [
        "How can I send back a product?",
        "When will my package arrive?",
        "I forgot my password",
        "Do you have student deals?",
        "blah blah xyz",
    ]
    for q in queries:
        result = matcher.match(q)
        print(f"\nQ: {q}")
        print(f"  Matched : {result['matched_question']}")
        print(f"  Score   : {result['confidence']} ({result['confidence_label']})")
        print(f"  Answer  : {result['answer'][:80]}...")
