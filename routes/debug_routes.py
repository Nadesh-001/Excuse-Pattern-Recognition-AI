from flask import session, redirect, url_for, flash
from app import app
from datetime import datetime, timedelta, date
from repository.tasks_repo import create_task, update_task_status
from repository.delays_repo import create_delay
import random

@app.route("/debug")
def debug():
    """Debug endpoint - REMOVE IN PRODUCTION!"""
    return {
        "session": dict(session),
        "routes": list(app.url_map.iter_rules()),
        "endpoint_names": sorted(app.view_functions.keys())
    }

@app.route("/debug/generate_data")
def generate_sample_data():
    """Generates sample tasks & delays for the current user."""
    user_id = session.get('user_id')
    if not user_id:
        flash("Please log in first.", "error")
        return redirect(url_for('login'))

    print(f"⚡ Generating sample data for User {user_id}...")

    # 1. Create Completed Tasks (for efficiency score)
    for i in range(2): # Reduced from 5
        t_id = create_task(
            title=f"Completed Task {i+1}",
            description="Auto-generated completed task.",
            assigned_to=user_id,
            created_by=user_id,
            priority=random.choice(['Low', 'Medium', 'High']),
            deadline=date.today() - timedelta(days=random.randint(1, 5)),
            estimated_minutes=random.randint(30, 120)
        )
        update_task_status(t_id, 'Completed')

    # 2. Create Delayed Tasks (for patterns)
    reason_map = [
        {"text": "Heavy rain caused site flooding", "risk": "Low"},
        {"text": "Material delivery delayed by supplier", "risk": "High"}
    ]

    for i in range(2): # Reduced from 5
        t_id = create_task(
            title=f"Delayed Task {i+1}",
            description="Auto-generated delayed task.",
            assigned_to=user_id,
            created_by=user_id,
            priority='High',
            deadline=date.today() - timedelta(days=random.randint(1, 3)),
            estimated_minutes=60
        )
        update_task_status(t_id, 'Delayed')
        
        # Pick a random scenario
        scenario = random.choice(reason_map)

        # Add delay record
        create_delay(
            task_id=t_id,
            user_id=user_id,
            reason_text=scenario["text"],
            reason_audio_path=None,
            score_authenticity=random.randint(40, 80),
            score_avoidance=random.randint(10, 50),
            risk_level=scenario["risk"],
            ai_feedback="Auto-generated feedback.",
            ai_analysis_json={},
            delay_duration=24,
            proof_path=None
        )

    # 3. Create Pending Tasks (Active)
    for i in range(2): # Reduced from 3
        create_task(
            title=f"Pending Task {i+1}",
            description="Auto-generated pending task.",
            assigned_to=user_id,
            created_by=user_id,
            priority=random.choice(['Medium', 'High']),
            deadline=date.today() + timedelta(days=random.randint(1, 7)),
            estimated_minutes=random.randint(45, 180)
        )

    flash("⚡ Sample data loaded successfully!", "success")
    return redirect(url_for('dashboard'))
