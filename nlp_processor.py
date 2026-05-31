"""
nlp_processor.py
-----------------
Handles all NLP preprocessing: tokenization, stopword removal,
and stemming — fully offline, no NLTK corpus downloads required.

Uses:
  * regex-based word tokenizer
  * bundled English stopword list  
  * Porter stemmer (NLTK algorithm only — no data files needed)
"""

import re
from nltk.stem import PorterStemmer  # pure algorithm, no corpus download

# Bundled English stopwords (NLTK list, embedded to avoid network downloads)
_STOPWORDS_RAW = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "this","that","these","those","am","is","are","was","were","be","been",
    "being","have","has","had","having","did","doing","a","an","the","and",
    "but","if","or","because","as","until","while","of","at","by","for",
    "with","about","against","between","into","through","during","before",
    "after","above","below","to","from","up","down","in","out","on","off",
    "over","under","again","further","then","once","here","there","when",
    "where","all","both","each","few","more","most","other","some","such",
    "no","nor","not","only","same","so","than","too","very","s","t","just",
    "don","should","now","d","ll","m","o","re","ve","y","ain","aren","couldn",
    "didn","doesn","hadn","hasn","haven","isn","ma","mightn","mustn","needn",
    "shan","shouldn","wasn","weren","won","wouldn","will","also","would",
    "could","get","us",
}

# Keep question/intent words — meaningful for FAQ matching
_KEEP_WORDS = {
    'what','how','when','where','why','who','which','can','do','does',
    'is','are','will','please','help','need','want','find','know',
}

STOP_WORDS = _STOPWORDS_RAW - _KEEP_WORDS

_stemmer = PorterStemmer()


def clean_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text


def tokenize(text: str) -> list:
    """Regex-based word tokenizer — no NLTK data files needed."""
    return re.findall(r'\b[a-z][a-z0-9]*\b', clean_text(text))


def remove_stopwords(tokens: list) -> list:
    return [t for t in tokens if t not in STOP_WORDS]


def stem(tokens: list) -> list:
    return [_stemmer.stem(t) for t in tokens]


def preprocess(text: str) -> list:
    """Full pipeline: clean → tokenize → remove stopwords → stem."""
    return stem(remove_stopwords(tokenize(text)))


def preprocess_to_string(text: str) -> str:
    return " ".join(preprocess(text))


if __name__ == "__main__":
    samples = [
        "What is your return policy?",
        "How long does shipping take?",
        "Can I cancel my order?",
    ]
    for s in samples:
        print(f"\nInput  : {s}")
        print(f"Tokens : {tokenize(s)}")
        print(f"Stemmed: {preprocess(s)}")
