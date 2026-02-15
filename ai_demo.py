from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import IsolationForest
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import joblib
import os
from datetime import datetime, date

# -----------------------------
# 1️⃣ SEMANTIC EXCUSE ANALYSIS (Lightweight NLP)
# -----------------------------
def analyze_excuses(excuse_texts):
    """
    Analyzes similarity between excuses to detect repetitive patterns.
    Uses TF-IDF vectorization and cosine similarity (lightweight alternative to transformers).
    
    Args:
        excuse_texts: List of excuse strings
        
    Returns:
        dict with similarity_score, originality_score, repetition_flag
    """
    if len(excuse_texts) < 2:
        return {
            "similarity_score": 0,
            "originality_score": 100,
            "repetition_flag": False
        }

    # TF-IDF Vectorization (lightweight, no model download needed)
    # max_features=500 limits vocabulary size → saves RAM
    vectorizer = TfidfVectorizer(max_features=500)
    tfidf_matrix = vectorizer.fit_transform(excuse_texts)

    # Calculate cosine similarity
    sim_matrix = cosine_similarity(tfidf_matrix)

    # Get average similarity (excluding diagonal)
    upper_triangle = sim_matrix[np.triu_indices(len(excuse_texts), k=1)]
    avg_similarity = float(np.mean(upper_triangle))

    originality = round((1 - avg_similarity) * 100, 2)

    return {
        "similarity_score": round(avg_similarity, 3),
        "originality_score": originality,
        "repetition_flag": avg_similarity > 0.7  # Slightly lower threshold for TF-IDF
    }

# -----------------------------
# 2️⃣ DELAY RISK PREDICTION (Machine Learning)
# -----------------------------
MODEL_PATH = "delay_model.pkl"

def train_demo_model():
    """
    Trains a simple logistic regression model for delay risk prediction.
    Uses demo data for college presentation purposes.
    """
    # Demo training dataset
    # Features: [delay_rate, avg_auth, risk_score]
    X = np.array([
        [10, 80, 90],
        [40, 50, 60],
        [60, 40, 30],
        [20, 85, 95],
        [75, 35, 20],
    ])

    y = np.array([0, 1, 1, 0, 1])  # 1 = High Delay Risk

    model = LogisticRegression()
    model.fit(X, y)

    joblib.dump(model, MODEL_PATH)


def predict_delay_risk(delay_rate, avg_auth, risk_score):
    """
    Predicts delay risk based on historical patterns using ML.
    
    Args:
        delay_rate: Percentage of delayed tasks
        avg_auth: Average authenticity score
        risk_score: Average risk score
        
    Returns:
        dict with delay_probability and risk_flag
    """
    if not os.path.exists(MODEL_PATH):
        train_demo_model()

    model = joblib.load(MODEL_PATH)

    features = [[delay_rate, avg_auth, risk_score]]

    probability = model.predict_proba(features)[0][1]

    return {
        "delay_probability": round(float(probability), 3),
        "risk_flag": "High" if probability > 0.6 else "Low"
    }

# -----------------------------
# 3️⃣ ANOMALY DETECTION (Unsupervised Learning)
# -----------------------------
def detect_anomaly(delay_history):
    """
    Detects anomalous patterns in delay behavior using Isolation Forest.
    Identifies sudden unusual behavior changes.
    
    Args:
        delay_history: List of numerical delay metrics
        
    Returns:
        dict with anomaly_flag and anomaly_score
    """
    if len(delay_history) < 5:
        return {
            "anomaly_flag": False,
            "anomaly_score": 0
        }

    # Keep only last 10 records for efficiency
    delay_history = delay_history[-10:]

    model = IsolationForest(contamination=0.2)
    data = np.array(delay_history).reshape(-1, 1)

    model.fit(data)

    prediction = model.predict(data)

    return {
        "anomaly_flag": bool(prediction[-1] == -1),
        "anomaly_score": float(model.decision_function(data)[-1])
    }

# -----------------------------
# 4️⃣ TIME-DECAY TRUST SCORING (Intelligent Weighting)
# -----------------------------
def calculate_time_decay_score(delay_records):
    """
    Calculates trust score with time-decay weighting.
    Recent behavior affects score more than old behavior.
    
    Formula: weight = exp(-0.05 * days_old)
    
    Args:
        delay_records: List of dicts with 'authenticity', 'submitted_at'
        
    Returns:
        dict with weighted_trust_score and decay_applied
    """
    if not delay_records:
        return {
            "weighted_trust_score": 0,
            "decay_applied": False
        }
    
    today = date.today()
    weighted_sum = 0
    weight_sum = 0
    
    for record in delay_records:
        # Calculate days old
        submitted_date = record.get('submitted_at')
        if isinstance(submitted_date, str):
            submitted_date = datetime.strptime(submitted_date, '%Y-%m-%d').date()
        elif isinstance(submitted_date, datetime):
            submitted_date = submitted_date.date()
        
        days_old = (today - submitted_date).days
        
        # Time-decay weight: exp(-0.05 * days_old)
        weight = np.exp(-0.05 * days_old)
        
        # Weighted score
        authenticity = record.get('authenticity', 0)
        weighted_sum += authenticity * weight
        weight_sum += weight
    
    weighted_score = weighted_sum / weight_sum if weight_sum > 0 else 0
    
    return {
        "weighted_trust_score": round(float(weighted_score), 2),
        "decay_applied": True
    }

# -----------------------------
# 5️⃣ BEHAVIORAL RELIABILITY SCORE (WRS - Composite AI Metric)
# -----------------------------
def calculate_wrs(avg_auth, avg_risk_val, delay_rate, repetition_penalty=0, generic_penalty=0):
    """
    Calculates Weighted Reliability Score (WRS) - Composite AI metric.
    
    Components:
    - Authenticity (60% weight)
    - Risk severity (30% weight)
    - Stability bonus (10 points if delay_rate < 30%)
    - Repetition penalty
    - Generic excuse penalty
    
    Args:
        avg_auth: Average authenticity score (0-100)
        avg_risk_val: Average risk value (0-100, higher is better)
        delay_rate: Percentage of delayed tasks
        repetition_penalty: Penalty for repetitive excuses (0-10)
        generic_penalty: Penalty for generic excuses (0-10)
        
    Returns:
        dict with wrs_score, components breakdown
    """
    # Base WRS calculation
    authenticity_component = avg_auth * 0.6
    risk_component = avg_risk_val * 0.3
    stability_bonus = 10 if delay_rate < 30 else 0
    
    # Calculate WRS
    wrs = authenticity_component + risk_component + stability_bonus
    
    # Apply penalties
    wrs -= repetition_penalty
    wrs -= generic_penalty
    
    # Ensure WRS is within 0-100
    wrs = max(0, min(100, wrs))
    
    return {
        "wrs_score": round(float(wrs), 1),
        "components": {
            "authenticity_contribution": round(authenticity_component, 1),
            "risk_contribution": round(risk_component, 1),
            "stability_bonus": stability_bonus,
            "repetition_penalty": repetition_penalty,
            "generic_penalty": generic_penalty
        }
    }


