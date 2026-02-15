from flask import render_template, session, abort
from app import app
from repository.db import test_connection
from repository.tasks_repo import get_tasks_by_user, get_all_tasks
from repository.delays_repo import get_delays_by_user, get_delays_all
from utils.flask_auth import auth_required
from utils.task_enrichment import enrich_task
from services.analytics_service import get_analytics_data, AnalyticsServiceError


# ---------------------------------------------------------------------------
# Metric aggregation — single-pass over tasks and delays.
# ---------------------------------------------------------------------------

def _compute_counts(tasks: list[dict], delays: list[dict]) -> dict:
    """Aggregate dashboard KPIs in a single pass over each collection."""
    pending = completed = delayed = 0

    for task in tasks:
        s = task.get('status')
        if s == 'Pending':
            pending += 1
        elif s == 'Completed':
            completed += 1
        elif s == 'Delayed':
            delayed += 1

    total_tasks = len(tasks)
    efficiency  = int((completed / total_tasks) * 100) if total_tasks > 0 else 0

    scores = [
        d['score_authenticity']
        for d in delays
        if d.get('score_authenticity') is not None
    ]
    auth_score = round(sum(scores) / len(scores), 1) if scores else 0

    return {
        'pending':       pending,
        'completed':     completed,
        'delayed_tasks': delayed,
        'total_delays':  len(delays),
        'total_tasks':   total_tasks,
        'efficiency':    efficiency,
        'auth_score':    auth_score,
    }


# ---------------------------------------------------------------------------
# Route
# ---------------------------------------------------------------------------

@app.route('/dashboard')
@auth_required
def dashboard():
    user_id   = session.get('user_id')
    user_role = session.get('user_role', 'employee')

    # @auth_required should guarantee user_id; fail loudly if the contract breaks.
    if not user_id:
        abort(401)

    if user_role == 'employee':
        tasks  = get_tasks_by_user(user_id)
        delays = get_delays_by_user(user_id)
    else:
        tasks  = get_all_tasks()
        delays = get_delays_all()

    counts = _compute_counts(tasks, delays)

    for task in tasks:
        enrich_task(task)

    # Pre-filter and slice active tasks for the template
    active_tasks = [t for t in tasks if t['status'] in ('Pending', 'Delayed')][:5]

    # Fetch real AI insights for the side panel
    ai_insights = []
    try:
        analytics = get_analytics_data(user_id=user_id, role=user_role)
        ai_insights = analytics.get('ai_insights', [])
    except (AnalyticsServiceError, Exception):
        # Gracefully fall back to empty insights on dashboard
        pass

    diagnostics = test_connection() if user_role == 'admin' else None

    return render_template(
        'dashboard.html',
        user_name=session.get('user_name'),
        counts=counts,
        tasks=tasks,
        active_tasks=active_tasks,
        ai_insights=ai_insights,
        role=user_role,
        delays=delays,
        diagnostics=diagnostics,
    )
