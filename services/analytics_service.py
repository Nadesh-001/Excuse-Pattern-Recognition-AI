"""
Analytics Service — fetches, aggregates, and enriches analytics data.
"""
import logging
from repository.db import execute_query

logger = logging.getLogger(__name__)


class AnalyticsServiceError(Exception):
    """Raised when the analytics service fails to retrieve or process data."""
    pass


# ---------------------------------------------------------------------------
# AI integration (optional dependency)
# ---------------------------------------------------------------------------

try:
    from ai_demo import (
        analyze_excuses,
        predict_delay_risk,
        detect_anomaly,
        calculate_time_decay_score,
        calculate_wrs,
    )
    from services.ai_insights import generate_ai_insights, generate_executive_summary
    AI_ENABLED = True
except ImportError:
    AI_ENABLED = False
    logger.warning("AI Demo not available. Install: pip install scikit-learn numpy joblib")


# ---------------------------------------------------------------------------
# SQL queries — one pair (user / team) per logical concern.
# Never constructed via string replacement at runtime.
# ---------------------------------------------------------------------------

# -- Aggregated stats --

_STATS_USER = """
WITH user_tasks AS (
    SELECT COUNT(id) AS total_tasks FROM tasks WHERE assigned_to = %s
),
user_delays AS (
    SELECT
        COUNT(id)                                               AS total_delays,
        COUNT(DISTINCT task_id)                                 AS unique_delayed_tasks,
        COALESCE(AVG(score_authenticity), 0)                   AS avg_auth,
        COALESCE(AVG(score_avoidance), 0)                      AS avg_avoid,
        COUNT(CASE WHEN risk_level = 'Low'    THEN 1 END)      AS risk_low,
        COUNT(CASE WHEN risk_level = 'Medium' THEN 1 END)      AS risk_med,
        COUNT(CASE WHEN risk_level = 'High'   THEN 1 END)      AS risk_high
    FROM delays WHERE user_id = %s
)
SELECT ut.total_tasks, ud.total_delays, ud.unique_delayed_tasks,
       ud.avg_auth, ud.avg_avoid, ud.risk_low, ud.risk_med, ud.risk_high
FROM user_tasks ut CROSS JOIN user_delays ud;
"""

_STATS_TEAM = """
WITH team_tasks AS (
    SELECT COUNT(id) AS total_tasks FROM tasks
),
team_delays AS (
    SELECT
        COUNT(id)                                               AS total_delays,
        COUNT(DISTINCT task_id)                                 AS unique_delayed_tasks,
        COALESCE(AVG(score_authenticity), 0)                   AS avg_auth,
        COALESCE(AVG(score_avoidance), 0)                      AS avg_avoid,
        COUNT(CASE WHEN risk_level = 'Low'    THEN 1 END)      AS risk_low,
        COUNT(CASE WHEN risk_level = 'Medium' THEN 1 END)      AS risk_med,
        COUNT(CASE WHEN risk_level = 'High'   THEN 1 END)      AS risk_high
    FROM delays
)
SELECT tt.total_tasks, td.total_delays, td.unique_delayed_tasks,
       td.avg_auth, td.avg_avoid, td.risk_low, td.risk_med, td.risk_high
FROM team_tasks tt CROSS JOIN team_delays td;
"""

# -- Day-of-week trend --

_TREND_USER = """
SELECT TO_CHAR(submitted_at, 'Dy') AS day_name,
       EXTRACT(DOW FROM submitted_at) AS day_idx,
       COUNT(*) AS count
FROM delays WHERE user_id = %s
GROUP BY day_name, day_idx ORDER BY day_idx;
"""

_TREND_TEAM = """
SELECT TO_CHAR(submitted_at, 'Dy') AS day_name,
       EXTRACT(DOW FROM submitted_at) AS day_idx,
       COUNT(*) AS count
FROM delays
GROUP BY day_name, day_idx ORDER BY day_idx;
"""

# -- Reason categories --

_WEATHER_KEYWORDS  = ['%rain%','%storm%','%weather%','%flood%','%snow%','%temp%','%climate%']
_HEALTH_KEYWORDS   = ['%sick%','%ill%','%doctor%','%fever%','%appointment%','%health%','%injury%']
_LABOR_KEYWORDS    = ['%labor%','%staff%','%worker%','%shortage%','%absent%','%crew%','%team%']
_MATERIAL_KEYWORDS = ['%material%','%supply%','%delivery%','%stock%','%part%','%inventory%','%order%']
_ALL_KEYWORDS      = _WEATHER_KEYWORDS + _HEALTH_KEYWORDS + _LABOR_KEYWORDS + _MATERIAL_KEYWORDS

def _build_category_query(where_clause: str) -> str:
    all_kw = ", ".join(f"'{k}'" for k in _ALL_KEYWORDS)
    w  = ", ".join(f"'{k}'" for k in _WEATHER_KEYWORDS)
    h  = ", ".join(f"'{k}'" for k in _HEALTH_KEYWORDS)
    l  = ", ".join(f"'{k}'" for k in _LABOR_KEYWORDS)
    m  = ", ".join(f"'{k}'" for k in _MATERIAL_KEYWORDS)
    return f"""
    SELECT
        COUNT(CASE WHEN reason_text ILIKE ANY(ARRAY[{w}])  THEN 1 END) AS "Weather",
        COUNT(CASE WHEN reason_text ILIKE ANY(ARRAY[{h}])  THEN 1 END) AS "Sickness",
        COUNT(CASE WHEN reason_text ILIKE ANY(ARRAY[{l}])  THEN 1 END) AS "Labor",
        COUNT(CASE WHEN reason_text ILIKE ANY(ARRAY[{m}])  THEN 1 END) AS "Material",
        COUNT(CASE WHEN reason_text NOT ILIKE ALL(ARRAY[{all_kw}]) THEN 1 END) AS "Other"
    FROM delays {where_clause};
    """

_CATEGORY_USER = _build_category_query("WHERE user_id = %s")
_CATEGORY_TEAM = _build_category_query("")

# -- Trust trend (time series) --

_TRUST_TREND_USER = """
SELECT submitted_at::date AS date,
       AVG(score_authenticity) AS avg_authenticity,
       AVG(score_avoidance)    AS avg_avoidance
FROM delays WHERE user_id = %s
GROUP BY date ORDER BY date ASC LIMIT 30;
"""

_TRUST_TREND_TEAM = """
SELECT submitted_at::date AS date,
       AVG(score_authenticity) AS avg_authenticity,
       AVG(score_avoidance)    AS avg_avoidance
FROM delays
GROUP BY date ORDER BY date ASC LIMIT 30;
"""

# -- Excuse texts for NLP --

_EXCUSE_TEXTS_USER = """
SELECT reason_text, score_authenticity
FROM delays WHERE user_id = %s AND reason_text IS NOT NULL
ORDER BY submitted_at DESC LIMIT 20;
"""

_EXCUSE_TEXTS_TEAM = """
SELECT reason_text, score_authenticity
FROM delays WHERE reason_text IS NOT NULL
ORDER BY submitted_at DESC LIMIT 20;
"""

# -- Delay records for time-decay --

_DELAY_RECORDS_USER = """
SELECT score_authenticity AS authenticity, submitted_at
FROM delays WHERE user_id = %s
ORDER BY submitted_at DESC LIMIT 30;
"""

_DELAY_RECORDS_TEAM = """
SELECT score_authenticity AS authenticity, submitted_at
FROM delays ORDER BY submitted_at DESC LIMIT 30;
"""


# ---------------------------------------------------------------------------
# Query helpers — thin wrappers that pick the right query + params.
# ---------------------------------------------------------------------------

def _q(user_query, team_query, is_team: bool, user_id):
    """Execute the appropriate query variant and return rows."""
    if is_team:
        return execute_query(team_query, ())
    return execute_query(user_query, (user_id,) if user_query.count('%s') == 1 else (user_id, user_id))


# ---------------------------------------------------------------------------
# Data fetching — one function per concern.
# ---------------------------------------------------------------------------

def _fetch_stats(is_team: bool, user_id) -> dict:
    rows = _q(_STATS_USER, _STATS_TEAM, is_team, user_id)
    return rows[0] if rows else {}


def _fetch_dow_trend(is_team: bool, user_id) -> dict:
    """Return a {day_name: count} map ordered Mon–Sun."""
    rows = _q(_TREND_USER, _TREND_TEAM, is_team, user_id)
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    counts = {d: 0 for d in days}
    for row in rows:
        idx = int(row['day_idx'])
        list_idx = (idx - 1) if idx > 0 else 6
        counts[days[list_idx]] = row['count']
    return counts


def _fetch_categories(is_team: bool, user_id) -> dict:
    rows = _q(_CATEGORY_USER, _CATEGORY_TEAM, is_team, user_id)
    raw = rows[0] if rows else {}
    return {k: int(v) for k, v in raw.items()}


def _fetch_trust_trend(is_team: bool, user_id) -> tuple[list, list, list]:
    rows = _q(_TRUST_TREND_USER, _TRUST_TREND_TEAM, is_team, user_id)
    dates, auth, avoid = [], [], []
    for row in rows:
        dates.append(str(row['date']))
        auth.append(float(row['avg_authenticity']) if row['avg_authenticity'] else 0.0)
        avoid.append(float(row['avg_avoidance'])   if row['avg_avoidance']    else 0.0)
    return dates, auth, avoid


def _fetch_excuse_texts(is_team: bool, user_id) -> list[str]:
    rows = _q(_EXCUSE_TEXTS_USER, _EXCUSE_TEXTS_TEAM, is_team, user_id)
    return [row['reason_text'] for row in rows if row['reason_text']]


def _fetch_delay_records(is_team: bool, user_id) -> list[dict]:
    rows = _q(_DELAY_RECORDS_USER, _DELAY_RECORDS_TEAM, is_team, user_id)
    return [{'authenticity': r['authenticity'], 'submitted_at': r['submitted_at']} for r in rows]


# ---------------------------------------------------------------------------
# Derived metrics
# ---------------------------------------------------------------------------

def _compute_metrics(stats: dict) -> dict:
    """Derive delay_rate, avg_risk_val, and wrs from raw stats."""
    total_tasks          = stats.get('total_tasks', 0)
    unique_delayed_tasks = stats.get('unique_delayed_tasks', 0)
    avg_auth             = float(stats.get('avg_auth', 0))
    risk_low             = int(stats.get('risk_low', 0))
    risk_med             = int(stats.get('risk_med', 0))
    risk_high            = int(stats.get('risk_high', 0))

    delay_rate = round((unique_delayed_tasks / total_tasks * 100), 1) if total_tasks > 0 else 0.0

    total_risk_count = risk_low + risk_med + risk_high
    avg_risk_val = (
        ((risk_low * 100) + (risk_med * 50)) / total_risk_count
        if total_risk_count > 0 else 100
    )

    stability_bonus = 10 if delay_rate < 30 else 0
    wrs = round((avg_auth * 0.6) + (avg_risk_val * 0.3) + stability_bonus, 1)

    return {
        'total_tasks':    total_tasks,
        'total_delays':   stats.get('total_delays', 0),
        'avg_auth':       avg_auth,
        'avg_avoid':      float(stats.get('avg_avoid', 0)),
        'risk_low':       risk_low,
        'risk_med':       risk_med,
        'risk_high':      risk_high,
        'delay_rate':     delay_rate,
        'avg_risk_val':   avg_risk_val,
        'wrs':            wrs,
    }


# ---------------------------------------------------------------------------
# AI enrichment
# ---------------------------------------------------------------------------

def _run_ai_analysis(
    is_team: bool,
    user_id,
    metrics: dict,
    trend_auth: list[float],
) -> dict:
    """Run all five AI features. Returns an empty dict if AI is disabled or fails."""
    if not AI_ENABLED:
        return {}
    try:
        excuse_texts   = _fetch_excuse_texts(is_team, user_id)
        delay_records  = _fetch_delay_records(is_team, user_id)

        excuse_ai = (
            analyze_excuses(excuse_texts)
            if len(excuse_texts) >= 2
            else {"similarity_score": 0, "originality_score": 100, "repetition_flag": False}
        )

        anomaly_ai = (
            detect_anomaly(trend_auth)
            if len(trend_auth) >= 5
            else {"anomaly_flag": False, "anomaly_score": 0}
        )

        time_decay_ai = (
            calculate_time_decay_score(delay_records)
            if delay_records
            else {"weighted_trust_score": 0, "decay_applied": False}
        )

        repetition_penalty = 10 if excuse_ai.get('repetition_flag') else 0

        return {
            'excuse_ai':     excuse_ai,
            'prediction_ai': predict_delay_risk(metrics['delay_rate'], metrics['avg_auth'], metrics['avg_risk_val']),
            'anomaly_ai':    anomaly_ai,
            'time_decay_ai': time_decay_ai,
            'wrs_ai':        calculate_wrs(metrics['avg_auth'], metrics['avg_risk_val'], metrics['delay_rate'], repetition_penalty, 0),
        }
    except Exception as e:
        logger.error("AI analysis failed: %s", e)
        return {}


# ---------------------------------------------------------------------------
# Graph builders — presentation config isolated from data logic.
# ---------------------------------------------------------------------------

_TRANSPARENT  = "rgba(0,0,0,0)"
_FONT_WHITE   = {"color": "#fff"}
_BASE_LAYOUT  = {"paper_bgcolor": _TRANSPARENT, "plot_bgcolor": _TRANSPARENT, "font": _FONT_WHITE}


def _gauge(value: float, title: str, bar_color: str, steps: list) -> dict:
    return {
        "data": [{
            "type": "indicator", "mode": "gauge+number", "value": value,
            "title": {"text": title},
            "gauge": {"axis": {"range": [0, 100]}, "bar": {"color": bar_color}, "steps": steps},
        }],
        "layout": _BASE_LAYOUT,
    }


def _build_graphs(metrics: dict, dow_counts: dict, categories: dict,
                  trend_dates: list, trend_auth: list, trend_avoid: list) -> dict:
    rl, rm, rh = metrics['risk_low'], metrics['risk_med'], metrics['risk_high']
    days = list(dow_counts.keys())

    return {
        "status_pie": {
            "data": [{"labels": ["Low", "Medium", "High"], "values": [rl, rm, rh], "type": "pie",
                      "marker": {"colors": ["#10b981", "#f59e0b", "#ef4444"]}}],
            "layout": {**_BASE_LAYOUT, "title": "Risk Level Distribution"},
        },
        "gauge_auth": _gauge(
            round(metrics['avg_auth'], 1), "Avg Authenticity", "#10b981",
            [{"range": [0,  40], "color": "rgba(239,68,68,0.3)"},
             {"range": [40, 60], "color": "rgba(245,158,11,0.3)"},
             {"range": [60,100], "color": "rgba(16,185,129,0.3)"}],
        ),
        "gauge_avoidance": _gauge(
            round(metrics['avg_avoid'], 1), "Avg Avoidance", "#ef4444",
            [{"range": [0,  20], "color": "rgba(16,185,129,0.3)"},
             {"range": [20, 40], "color": "rgba(245,158,11,0.3)"},
             {"range": [40,100], "color": "rgba(239,68,68,0.3)"}],
        ),
        "gauge_wrs": _gauge(
            metrics['wrs'], "Reliability (WRS)", "#6366f1",
            [{"range": [0,  50], "color": "rgba(239,68,68,0.2)"},
             {"range": [50, 80], "color": "rgba(245,158,11,0.2)"},
             {"range": [80,100], "color": "rgba(99,102,241,0.2)"}],
        ),
        "line_chart": {
            "data": [{"x": days, "y": list(dow_counts.values()), "type": "scatter",
                      "mode": "lines+markers", "line": {"color": "#10b981", "width": 3}}],
            "layout": {**_BASE_LAYOUT, "title": "Strategic Trend (Day of Week)",
                       "xaxis": {"title": "Day"}, "yaxis": {"title": "Delay Volume"}},
        },
        "trend_over_time": {
            "data": [
                {"x": trend_dates, "y": trend_auth, "type": "scatter", "mode": "lines+markers",
                 "name": "Authenticity", "line": {"color": "#10b981", "width": 2}, "marker": {"size": 6}},
                {"x": trend_dates, "y": trend_avoid, "type": "scatter", "mode": "lines+markers",
                 "name": "Avoidance",  "line": {"color": "#ef4444", "width": 2}, "marker": {"size": 6}},
            ],
            "layout": {**_BASE_LAYOUT, "title": "Score Trends Over Time",
                       "xaxis": {"title": "Date"}, "yaxis": {"title": "Score"},
                       "showlegend": True, "legend": {"x": 0.7, "y": 1}},
        },
        "categories": {
            "data": [{"x": list(categories.keys()), "y": list(categories.values()),
                      "type": "bar", "marker": {"color": "#60a5fa"}}],
            "layout": {**_BASE_LAYOUT, "title": "Reason Categories"},
        },
    }


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_analytics_data(user_id=None, role: str = 'employee') -> dict:
    """
    Fetch and enrich analytics data for a user or the whole team.

    Raises:
        AnalyticsServiceError: on any database or processing failure.
    """
    logger.debug("get_analytics_data called: user_id=%s role=%s", user_id, role)

    if not user_id:
        logger.warning("get_analytics_data called with no user_id — returning empty state")
        return _empty_analytics_state()

    try:
        is_team = role in ('admin', 'manager')

        # 1. Core stats and derived metrics
        stats   = _fetch_stats(is_team, user_id)
        metrics = _compute_metrics(stats)

        # 2. Supplementary series
        dow_counts              = _fetch_dow_trend(is_team, user_id)
        categories              = _fetch_categories(is_team, user_id)
        trend_dates, t_auth, t_avoid = _fetch_trust_trend(is_team, user_id)

        # 3. AI enrichment
        ai_results = _run_ai_analysis(is_team, user_id, metrics, t_auth)

        # 4. Graphs (presentation layer — separate from data logic)
        graphs = _build_graphs(metrics, dow_counts, categories, trend_dates, t_auth, t_avoid)

        # 5. Insights and summary — analytics_summary built once, used twice
        analytics_summary = {
            "risk_distribution": {
                "Low":    metrics['risk_low'],
                "Medium": metrics['risk_med'],
                "High":   metrics['risk_high'],
            },
            "avg_auth_score":      metrics['avg_auth'],
            "avg_avoidance_score": metrics['avg_avoid'],
            "delay_rate":          metrics['delay_rate'],
        }

        ai_insights = []
        executive_summary = ""

        if AI_ENABLED:
            try:
                if ai_results:
                    ai_insights = generate_ai_insights(analytics_summary, ai_results)
                executive_summary = generate_executive_summary(role, analytics_summary, ai_results)
            except Exception as e:
                logger.error("AI insights/summary generation failed: %s", e)

        return {
            "avg_auth_score":      round(metrics['avg_auth'], 1),
            "avg_avoidance_score": round(metrics['avg_avoid'], 1),
            "wrs_score":           metrics['wrs'],
            "risk_low":            metrics['risk_low'],
            "risk_med":            metrics['risk_med'],
            "risk_high":           metrics['risk_high'],
            "risk_distribution":   analytics_summary["risk_distribution"],
            "delay_rate_by_user":  [],   # TODO: implement team velocity query
            "generic_excuse_ratio": 0,   # TODO: implement via ai_results
            "team_risk_index":     metrics['wrs'],
            "trust_trend":         [],   # Exposed via graphs["trend_over_time"]
            "graphs":              graphs,
            "ai":                  ai_results,
            "ai_insights":         ai_insights,
            "executive_summary":   executive_summary,
            "total_delays":        metrics['total_delays'],
        }

    except AnalyticsServiceError:
        raise
    except Exception as e:
        logger.exception("Analytics service error for user_id=%s", user_id)
        raise AnalyticsServiceError(f"Database or processing error in analytics: {e}") from e


def _empty_analytics_state() -> dict:
    return {
        "avg_auth_score": 0, "avg_avoidance_score": 0, "wrs_score": 0,
        "risk_low": 0, "risk_med": 0, "risk_high": 0,
        "risk_distribution": {"Low": 0, "Medium": 0, "High": 0},
        "delay_rate_by_user": [], "generic_excuse_ratio": 0,
        "team_risk_index": 0, "trust_trend": [], "graphs": {},
        "ai": {}, "ai_insights": [], "executive_summary": "",
        "total_delays": 0
    }
