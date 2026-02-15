from flask import render_template, session, redirect, url_for, flash, current_app
from app import app
from utils.flask_auth import manager_required
from repository.users_repo import get_all_users, get_user_by_id
from services.analytics_service import get_analytics_data
from repository.tasks_repo import get_tasks_by_user

@app.route('/team')
@manager_required
def team_directory():
    """Shows all employees with summarized risk profiles."""
    try:
        users = get_all_users(active_only=True)
        employees = [u for u in users if u['role'] == 'employee']
        
        # Enrich with basic stats
        for emp in employees:
            stats = get_analytics_data(user_id=emp['id'], role='employee')
            emp['avg_auth'] = stats.get('avg_auth_score', 0)
            emp['delay_count'] = stats.get('risk_low', 0) + stats.get('risk_med', 0) + stats.get('risk_high', 0)
            emp['risk_level'] = "High" if emp['avg_auth'] < 45 else ("Medium" if emp['avg_auth'] < 75 else "Low")
            
        return render_template('team_directory.html', employees=employees)
    except Exception as e:
        current_app.logger.error(f"Team directory error: {e}")
        return redirect(url_for('dashboard'))

@app.route('/team/user/<int:user_id>')
@manager_required
def employee_profile(user_id):
    """Detailed drill-down of a single employee's performance."""
    try:
        user = get_user_by_id(user_id)
        if not user or user['role'] != 'employee':
            flash("Employee not found.", "error")
            return redirect(url_for('team_directory'))
            
        stats = get_analytics_data(user_id=user_id, role='employee')
        tasks = get_tasks_by_user(user_id)
        
        return render_template('employee_profile.html', 
                             employee=user, 
                             stats=stats, 
                             graphs=stats.get('graphs', {}),
                             tasks=tasks)
    except Exception as e:
        current_app.logger.error(f"Employee profile error: {e}")
        return redirect(url_for('team_directory'))
