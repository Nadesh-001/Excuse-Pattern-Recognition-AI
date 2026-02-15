# AI Demo Setup Instructions (Lightweight Version)

## Step 1: Install Required Libraries

Run the following command to install all required libraries for the AI demo:

```bash
pip install scikit-learn numpy joblib
```

**Note**: This lightweight version uses TF-IDF instead of SentenceTransformers, eliminating the need for PyTorch and large model downloads (~80-120MB). Perfect for college demos and low-spec laptops!

## Step 2: Verify Installation

Test that the AI demo is working correctly:

```bash
python -c "from ai_demo import analyze_excuses, predict_delay_risk, detect_anomaly; print('✅ AI Demo installed successfully!')"
```

## Step 3: Run the Application

Start your Flask application:

```bash
python app.py
```

## What the AI Demo Does

### 1. Semantic Excuse Analysis
- Analyzes similarity between excuse texts
- Detects repetitive patterns
- Provides originality score (0-100)
- Flags repetition if similarity > 75%

### 2. Delay Risk Prediction
- Predicts probability of future delays
- Uses logistic regression model
- Based on delay rate, authenticity, and risk scores
- Returns "High" or "Low" risk flag

### 3. Anomaly Detection
- Detects unusual patterns in delay behavior
- Uses Isolation Forest algorithm
- Requires at least 5 data points
- Flags anomalous behavior

## Accessing AI Results

The AI results are automatically included in the analytics data under the `ai` key:

```python
{
    "ai": {
        "excuse_ai": {
            "similarity_score": 0.45,
            "originality_score": 55,
            "repetition_flag": False
        },
        "prediction_ai": {
            "delay_probability": 0.35,
            "risk_flag": "Low"
        },
        "anomaly_ai": {
            "anomaly_flag": False,
            "anomaly_score": -0.12
        }
    }
}
```

## Troubleshooting

If you see the warning message:
```
⚠️ AI Demo not available. Install: pip install sentence-transformers scikit-learn numpy joblib
```

This means the required libraries are not installed. Run Step 1 above to install them.

The application will still work without AI features - they will simply be disabled gracefully.
