from flask import render_template, current_app, session, abort
from app import app
from utils.flask_auth import auth_required
from services.analytics_service import get_analytics_data, AnalyticsServiceError

@app.route('/analytics')
@auth_required
def analytics():
    """Render the analytics dashboard for the current user."""
    user_id = session.get('user_id')
    role = session.get('user_role', 'employee')

    if not user_id:
        current_app.logger.warning("Analytics route reached with no user_id in session")
        abort(401)

    # Defaults ensure the template always receives the expected context keys,
    # whether the service call succeeds or fails.
    template_context = {
        'stats': {},
        'graphs': {},
        'ai_insights': [],
        'executive_summary': '',
        'role': role,
        'error': None,
    }

    try:
        kpis = get_analytics_data(user_id=user_id, role=role)
        template_context.update({
            'stats': kpis,
            'graphs': kpis.get('graphs', {}),
            'ai_insights': kpis.get('ai_insights', []),
            'executive_summary': kpis.get('executive_summary', ''),
        })
    except AnalyticsServiceError as e:
        current_app.logger.error("Analytics service error for user %s: %s", user_id, e)
        template_context['error'] = "Failed to load analytics data"
    except Exception as e:
        current_app.logger.error("Unexpected error in analytics route for user %s: %s", user_id, e, exc_info=True)
        template_context['error'] = "An unexpected error occurred"

    return render_template('analytics.html', **template_context)
