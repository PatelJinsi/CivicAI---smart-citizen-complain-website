"""
AI Engine for Smart Citizen Complaint System
Handles: Category Prediction, Urgency Detection, Sentiment Analysis
"""

import os
import re
import joblib
import numpy as np
from pathlib import Path

# ─── TRAINING DATA ────────────────────────────────────────────────────────────

TRAINING_DATA = [
    # Road complaints
    ("The road in our area has huge potholes and is very dangerous", "road"),
    ("Street is broken and full of pits causing accidents", "road"),
    ("Road damage near school causing issues for children", "road"),
    ("Large crater on main road, vehicles getting damaged", "road"),
    ("Road is not repaired since months, full of holes", "road"),
    ("The footpath is broken and dangerous for pedestrians", "road"),
    ("Bridge near river has cracks and needs immediate repair", "road"),
    ("Pothole on highway caused my vehicle damage", "road"),
    ("Road construction debris left blocking traffic", "road"),
    ("Speed breaker is damaged and causing accidents", "road"),
    ("The main road is severely damaged after rains", "road"),
    ("Road in colony is dug up and not filled for weeks", "road"),
    ("Traffic signal is not working at main intersection", "road"),
    ("Footbridge is broken and risky for walkers", "road"),
    ("Divider on road is damaged and causing accidents", "road"),

    # Water complaints
    ("Water leakage on main road wasting water since days", "water"),
    ("No water supply in our area for the past 3 days", "water"),
    ("Dirty water coming from tap, not safe for drinking", "water"),
    ("Water pipe burst near my house flooding the street", "water"),
    ("Drainage is blocked causing water to overflow", "water"),
    ("Sewage water mixing with drinking water supply", "water"),
    ("Underground pipeline is leaking near park", "water"),
    ("Water tank in building not cleaned, causing disease", "water"),
    ("Sewage overflow near school creating health hazard", "water"),
    ("Water supply is irregular and pressure is very low", "water"),
    ("Drain is blocked with garbage causing flooding", "water"),
    ("Municipal water pipe is broken, water wasted", "water"),
    ("No water for 5 days, residents are suffering", "water"),
    ("Stagnant water on road after rain not draining", "water"),
    ("Borewell water is muddy and undrinkable", "water"),

    # Garbage complaints
    ("Garbage not collected from our area since one week", "garbage"),
    ("Waste dump near park is overflowing and smells terrible", "garbage"),
    ("Garbage bin not emptied for days attracting animals", "garbage"),
    ("Illegal garbage dumping happening near residential area", "garbage"),
    ("Dead animal on road not removed for days", "garbage"),
    ("Sanitation workers not coming for garbage collection", "garbage"),
    ("Open garbage dump near school causing health problems", "garbage"),
    ("Waste is being burned creating smoke and pollution", "garbage"),
    ("Bio-medical waste dumped illegally on street", "garbage"),
    ("Garbage container is full and overflowing since 3 days", "garbage"),
    ("Cleaning workers not sweeping roads causing filth", "garbage"),
    ("Rats and insects due to uncollected garbage in colony", "garbage"),
    ("Construction waste dumped on public road", "garbage"),
    ("Public dustbin broken and garbage scattered", "garbage"),
    ("Waste pile near hospital dangerous for public health", "garbage"),

    # Electricity complaints
    ("Street light not working making road dark and dangerous", "electricity"),
    ("Power cut in our area since last night", "electricity"),
    ("Electricity wire hanging low over road dangerous", "electricity"),
    ("Transformer making loud noise and sparking", "electricity"),
    ("No electricity for 12 hours due to fault", "electricity"),
    ("Street light pole fallen on road blocking traffic", "electricity"),
    ("Electric meter giving wrong readings overcharging", "electricity"),
    ("Illegal electricity connections creating fire risk", "electricity"),
    ("Streetlight wire broken and sparking dangerously", "electricity"),
    ("Frequent power trips in our locality", "electricity"),
    ("Electric pole tilted and about to fall on road", "electricity"),
    ("Substation making strange noise near school", "electricity"),
    ("Half the street lights in colony are not working", "electricity"),
    ("Power cable hanging low after storm, dangerous", "electricity"),
    ("Generator not working in hospital area causing issues", "electricity"),

    # Other complaints
    ("Stray dogs attacking people in colony", "other"),
    ("Construction work creating too much noise at night", "other"),
    ("Park benches broken and not repaired", "other"),
    ("Public toilet not maintained and very dirty", "other"),
    ("Illegal encroachment on public land", "other"),
    ("Tree branch fallen on road needs to be cleared", "other"),
    ("Public property vandalized near metro station", "other"),
    ("Noise pollution from factory disturbing residents", "other"),
    ("Mosquito breeding in nearby pond causing malaria", "other"),
    ("Unauthorized construction near residential area", "other"),
]


# ─── URGENCY KEYWORDS ─────────────────────────────────────────────────────────

URGENCY_KEYWORDS = {
    'critical': [
        'accident', 'injured', 'injury', 'dead', 'death', 'dangerous', 'fire',
        'explosion', 'sparking', 'electrocution', 'emergency', 'urgent', 'critical',
        'life threatening', 'falling', 'collapsed', 'flood', 'disease', 'epidemic',
        'hospital', 'severe', 'immediate', 'drowning', 'gas leak',
    ],
    'high': [
        'broken', 'damaged', 'leaking', 'overflow', 'blocked', 'overflowing',
        'hazard', 'unsafe', 'risky', 'pothole', 'burst', 'no water', 'no electricity',
        'dark', 'night', 'children', 'school', 'attacked', 'spreading', 'smell',
    ],
    'medium': [
        'problem', 'issue', 'complaint', 'not working', 'dirty', 'garbage',
        'waste', 'months', 'weeks', 'irregular', 'missing', 'absent', 'days',
    ],
    'low': [
        'repair', 'fix', 'request', 'please', 'kindly', 'need', 'require',
        'should', 'maintain', 'clean',
    ],
}


# ─── DEPARTMENT MAPPING ───────────────────────────────────────────────────────

DEPARTMENT_MAP = {
    'road':        'Public Works Department',
    'water':       'Water Supply & Sewerage Board',
    'garbage':     'Municipal Sanitation Department',
    'electricity': 'Electricity Distribution Department',
    'other':       'General Administration Department',
}


# ─── MODEL TRAINING ───────────────────────────────────────────────────────────

MODEL_PATH = Path(__file__).parent / 'complaint_model.pkl'


def train_and_save_model():
    """Train the complaint classifier and save to disk."""
    from sklearn.pipeline import Pipeline
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression

    texts = [item[0] for item in TRAINING_DATA]
    labels = [item[1] for item in TRAINING_DATA]

    pipeline = Pipeline([
        ('tfidf', TfidfVectorizer(
            ngram_range=(1, 2),
            max_features=5000,
            stop_words='english',
            lowercase=True,
        )),
        ('clf', LogisticRegression(
            max_iter=1000,
            C=1.0,
            random_state=42,
        )),
    ])

    pipeline.fit(texts, labels)
    joblib.dump(pipeline, MODEL_PATH)
    print(f"[AI Engine] Model trained and saved to {MODEL_PATH}")
    return pipeline


def load_model():
    """Load model from disk, train if not found."""
    if MODEL_PATH.exists():
        return joblib.load(MODEL_PATH)
    return train_and_save_model()


# Load model on import
try:
    _model = load_model()
except Exception as e:
    print(f"[AI Engine] Warning: Could not load model — {e}")
    _model = None


# ─── AI FUNCTIONS ─────────────────────────────────────────────────────────────

def predict_category(text: str) -> dict:
    """
    Predict complaint category using trained NLP classifier.
    Returns: { 'category': str, 'confidence': float, 'department': str }
    """
    global _model
    if _model is None:
        _model = train_and_save_model()

    prediction = _model.predict([text])[0]
    probabilities = _model.predict_proba([text])[0]
    classes = _model.classes_
    confidence = float(max(probabilities))

    department = DEPARTMENT_MAP.get(prediction, 'General Administration Department')

    return {
        'category': prediction,
        'confidence': round(confidence * 100, 1),
        'department': department,
    }


def detect_urgency(text: str) -> int:
    """
    Detect urgency level of complaint on a 0–100 scale.
    Returns: int (urgency score)
    """
    text_lower = text.lower()
    score = 10  # base score

    # Critical keywords → +30 each (max 60)
    critical_hits = sum(1 for kw in URGENCY_KEYWORDS['critical'] if kw in text_lower)
    score += min(critical_hits * 30, 60)

    # High keywords → +15 each (max 30)
    high_hits = sum(1 for kw in URGENCY_KEYWORDS['high'] if kw in text_lower)
    score += min(high_hits * 15, 30)

    # Medium keywords → +8 each (max 16)
    medium_hits = sum(1 for kw in URGENCY_KEYWORDS['medium'] if kw in text_lower)
    score += min(medium_hits * 8, 16)

    # Time mentions boost → "days", "weeks", "months"
    if re.search(r'\d+\s*(day|week|month)', text_lower):
        score += 10

    # Exclamation marks → urgency signal
    score += min(text.count('!') * 5, 10)

    # Long complaint text → more detail = more serious
    if len(text) > 200:
        score += 5

    return min(int(score), 100)


def analyze_sentiment(text: str) -> str:
    """
    Analyze sentiment of complaint text using VADER.
    Returns: 'positive' | 'neutral' | 'negative' | 'frustrated'
    """
    try:
        from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
        analyzer = SentimentIntensityAnalyzer()
        scores = analyzer.polarity_scores(text)
        compound = scores['compound']

        # Check for frustration indicators
        frustration_words = [
            'again', 'still', 'already', 'months', 'weeks', 'never', 'always',
            'nobody', 'nothing', 'useless', 'pathetic', 'terrible', 'worst',
            'disgusting', 'shameful', 'ridiculous',
        ]
        text_lower = text.lower()
        is_frustrated = any(w in text_lower for w in frustration_words)

        if compound >= 0.05:
            return 'positive'
        elif compound <= -0.4 and is_frustrated:
            return 'frustrated'
        elif compound <= -0.05:
            return 'negative'
        else:
            return 'neutral'

    except ImportError:
        # Fallback: simple keyword-based sentiment
        text_lower = text.lower()
        negative_words = ['bad', 'dangerous', 'broken', 'damaged', 'terrible', 'worst', 'horrible']
        if any(w in text_lower for w in negative_words):
            return 'negative'
        return 'neutral'


def analyze_complaint(title: str, description: str) -> dict:
    """
    Master function: runs all AI analysis on a complaint.
    Returns complete AI analysis dict.
    """
    full_text = f"{title}. {description}"

    category_result = predict_category(full_text)
    urgency_score = detect_urgency(full_text)
    sentiment = analyze_sentiment(full_text)

    return {
        'category': category_result['category'],
        'category_confidence': category_result['confidence'],
        'urgency_score': urgency_score,
        'sentiment': sentiment,
        'department_name': category_result['department'],
    }