"""
AI Insights Generator — rule-based interpretation of analytics and AI signals.
"""
from dataclasses import dataclass, asdict


# ---------------------------------------------------------------------------
# Thresholds — all business rules live here, nowhere else.
# ---------------------------------------------------------------------------

class RiskThresholds:
    HIGH_RISK_CRITICAL_PCT = 40   # % of high-risk entries → critical
    HIGH_RISK_WARNING_PCT  = 20   # % of high-risk entries → warning

class AuthThresholds:
    LOW  = 50
    HIGH = 75

class AvoidThresholds:
    HIGH_AVOIDANCE = 40  # below this → critical (inverted scale)

class DelayThresholds:
    CRITICAL = 50
    WARNING  = 30

class WRSThresholds:
    LOW  = 50
    HIGH = 75

class TrustThresholds:
    LOW = 50


# ---------------------------------------------------------------------------
# Insight shape — enforced by dataclass, not ad-hoc dicts.
# ---------------------------------------------------------------------------

SEVERITY_CRITICAL = "critical"
SEVERITY_WARNING  = "warning"
SEVERITY_STABLE   = "stable"

VALID_SEVERITIES = {SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_STABLE}

@dataclass
class Insight:
    text: str
    severity: str
    category: str

    def __post_init__(self):
        if self.severity not in VALID_SEVERITIES:
            raise ValueError(f"Invalid severity '{self.severity}'. Must be one of {VALID_SEVERITIES}")

    def to_dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------------------
# Insight generators — one function per logical domain.
# ---------------------------------------------------------------------------

def _risk_insights(risk_dist: dict) -> list[Insight]:
    total = sum(risk_dist.values())
    if not total:
        return []
    pct = (risk_dist.get("High", 0) / total) * 100
    if pct > RiskThresholds.HIGH_RISK_CRITICAL_PCT:
        return [Insight("⚠️ High proportion of critical delay risks detected.", SEVERITY_CRITICAL, "risk")]
    if pct > RiskThresholds.HIGH_RISK_WARNING_PCT:
        return [Insight("⚡ Moderate risk exposure across team.", SEVERITY_WARNING, "risk")]
    return [Insight("✅ Team risk levels are relatively stable.", SEVERITY_STABLE, "risk")]


def _auth_insights(avg_auth: float) -> list[Insight]:
    if avg_auth < AuthThresholds.LOW:
        return [Insight("🔍 Low authenticity trend detected in delay reasons.", SEVERITY_WARNING, "authenticity")]
    if avg_auth > AuthThresholds.HIGH:
        return [Insight("✨ Strong authenticity pattern across team delays.", SEVERITY_STABLE, "authenticity")]
    return []


def _avoidance_insights(avg_avoid: float) -> list[Insight]:
    if avg_avoid < AvoidThresholds.HIGH_AVOIDANCE:
        return [Insight("⚠️ High avoidance behavior detected in team.", SEVERITY_CRITICAL, "avoidance")]
    return []


def _delay_insights(delay_rate: float) -> list[Insight]:
    if delay_rate > DelayThresholds.CRITICAL:
        return [Insight("📊 Significant delay rate requires attention.", SEVERITY_CRITICAL, "delays")]
    if delay_rate > DelayThresholds.WARNING:
        return [Insight("📈 Moderate delay frequency observed.", SEVERITY_WARNING, "delays")]
    return []


def _ai_insights(ai_data: dict) -> list[Insight]:
    results = []

    excuse_ai = ai_data.get("excuse_ai", {})
    if excuse_ai.get("repetition_flag"):
        sim = excuse_ai.get("similarity_score", 0)
        results.append(Insight(
            f"🤖 Repeated excuse patterns identified using NLP similarity ({sim:.0%}).",
            SEVERITY_WARNING, "ai_nlp"
        ))

    prediction_ai = ai_data.get("prediction_ai", {})
    if prediction_ai.get("risk_flag") == "High":
        prob = prediction_ai.get("delay_probability", 0)
        results.append(Insight(
            f"🔮 AI predicts high probability of future delays ({prob:.0%}).",
            SEVERITY_CRITICAL, "ai_prediction"
        ))

    anomaly_ai = ai_data.get("anomaly_ai", {})
    if anomaly_ai.get("anomaly_flag"):
        results.append(Insight(
            "🚨 Behavioral anomaly detected in recent activity.",
            SEVERITY_CRITICAL, "ai_anomaly"
        ))

    time_decay_ai = ai_data.get("time_decay_ai", {})
    weighted_score = time_decay_ai.get("weighted_trust_score", 0)
    if weighted_score < TrustThresholds.LOW:
        results.append(Insight(
            f"⏰ Recent behavior shows declining trust (weighted score: {weighted_score:.1f}).",
            SEVERITY_WARNING, "ai_trust"
        ))

    wrs_ai = ai_data.get("wrs_ai", {})
    wrs = wrs_ai.get("wrs_score", 0)
    if wrs < WRSThresholds.LOW:
        results.append(Insight(
            f"📉 Low behavioral reliability score detected (WRS: {wrs:.1f}).",
            SEVERITY_CRITICAL, "ai_wrs"
        ))
    elif wrs > WRSThresholds.HIGH:
        results.append(Insight(
            f"⭐ Excellent behavioral reliability score (WRS: {wrs:.1f}).",
            SEVERITY_STABLE, "ai_wrs"
        ))

    return results


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def generate_ai_insights(analytics_data: dict, ai_data: dict) -> list[dict]:
    """
    Generate insights from analytics and AI signals.

    Returns a list of plain dicts (not Insight objects) so callers and
    templates don't need to know about the internal dataclass.
    """
    insights: list[Insight] = []
    insights += _risk_insights(analytics_data.get("risk_distribution", {}))
    insights += _auth_insights(analytics_data.get("avg_auth_score", 0))
    insights += _avoidance_insights(analytics_data.get("avg_avoidance_score", 0))
    insights += _delay_insights(analytics_data.get("delay_rate", 0))
    if ai_data:
        insights += _ai_insights(ai_data)

    if not insights:
        insights.append(Insight("✅ All metrics within normal ranges.", SEVERITY_STABLE, "general"))

    return [i.to_dict() for i in insights]


def generate_executive_summary(role: str, analytics_data: dict, ai_data: dict) -> str:
    """
    Generate a role-appropriate executive summary paragraph.

    Sentences are collected into a list and joined, so each conditional
    branch is independently readable and there's no string mutation.
    """
    risk_dist  = analytics_data.get("risk_distribution", {})
    avg_auth   = analytics_data.get("avg_auth_score", 0)
    avg_avoid  = analytics_data.get("avg_avoidance_score", 0)
    delay_rate = analytics_data.get("delay_rate", 0)

    high_risk   = risk_dist.get("High", 0)
    medium_risk = risk_dist.get("Medium", 0)

    prediction_flag  = (ai_data or {}).get("prediction_ai", {}).get("risk_flag", "Low")
    anomaly_flag     = (ai_data or {}).get("anomaly_ai", {}).get("anomaly_flag", False)
    repetition_flag  = (ai_data or {}).get("excuse_ai", {}).get("repetition_flag", False)
    wrs_score        = (ai_data or {}).get("wrs_ai", {}).get("wrs_score", 0)

    sentences: list[str] = []

    if role == "admin":
        sentences.append(
            f"The team currently shows {high_risk} high-risk and "
            f"{medium_risk} medium-risk delays, with an authenticity average of {avg_auth:.1f}%."
        )
        if anomaly_flag:
            sentences.append("An anomaly has been detected in recent team behavior.")
        if prediction_flag == "High":
            sentences.append("AI predicts elevated delay probability across upcoming tasks.")
        elif wrs_score < WRSThresholds.LOW:
            sentences.append("Weighted reliability score indicates declining team performance.")
        else:
            sentences.append("Team stability appears within acceptable thresholds.")
        if repetition_flag:
            sentences.append("Repeated excuse patterns detected across submissions.")

    elif role == "manager":
        sentences.append(
            f"The team delay rate is {delay_rate:.1f}%, with "
            f"{medium_risk + high_risk} moderate-to-high risk cases."
        )
        if avg_auth < AuthThresholds.HIGH:
            sentences.append("Authenticity trends require monitoring.")
        else:
            sentences.append("Authenticity trends remain strong.")
        if prediction_flag == "High":
            sentences.append("AI indicates increased risk for future delays.")
        if anomaly_flag:
            sentences.append("Unusual behavioral patterns detected in team activity.")
        if avg_avoid < AvoidThresholds.HIGH_AVOIDANCE:
            sentences.append("High avoidance behavior observed.")

    elif role == "employee":
        sentences.append(
            f"Your current delay rate is {delay_rate:.1f}% with {high_risk} high-risk submissions."
        )
        if repetition_flag:
            sentences.append("Repeated excuse patterns have been detected.")
        if anomaly_flag:
            sentences.append("Recent activity shows unusual behavioral patterns.")
        if prediction_flag == "High":
            sentences.append("AI predicts higher delay risk for your upcoming tasks.")
        if avg_auth > AuthThresholds.HIGH:
            sentences.append("Overall credibility remains strong.")
        elif avg_auth < AuthThresholds.LOW:
            sentences.append("Consider improving submission authenticity to build trust.")
        if wrs_score > WRSThresholds.HIGH:
            sentences.append("Your behavioral reliability score is excellent.")

    return " ".join(sentences) if sentences else "Insufficient data for executive summary."
