"""
Sample Data Generator for Testing AI Features
Creates realistic delay data for the current user to test analytics and AI features.
"""

from flask import session, flash, redirect, url_for, current_app
from app import app
from utils.flask_auth import auth_required
from repository.db import execute_query
from datetime import datetime, timedelta
import random

@app.route('/api/load-sample-data', methods=['POST'])
@auth_required
def load_sample_data():
    """
    Populates the database with sample tasks and delays for the current user.
    This enables testing of all 5 AI features and analytics visualizations.
    """
    try:
        user_id = session.get('user_id')
        
        # Sample excuse texts (varied to test TF-IDF similarity detection)
        sample_excuses = [
            "Unexpected server outage caused significant delays in deployment",
            "Team member fell ill, had to redistribute workload",
            "Client requested last-minute changes to requirements",
            "Database migration took longer than anticipated",
            "Network connectivity issues prevented remote access",
            "Third-party API was down for maintenance",
            "Power outage in the office building",
            "Critical bug discovered during testing phase",
            "Waiting for approval from stakeholders",
            "Hardware failure required emergency replacement",
            # Repetitive excuses to test AI pattern detection
            "Server issues caused delays",
            "Server problems led to setbacks",
            "Unexpected server downtime",
        ]
        
        # Sample task titles
        task_titles = [
            "Q4 Report Preparation",
            "Database Schema Migration",
            "API Integration Testing",
            "User Authentication Module",
            "Frontend UI Redesign",
            "Performance Optimization",
            "Security Audit Implementation",
            "Mobile App Development",
        ]
        
        # Create sample tasks
        task_ids = []
        for i, title in enumerate(task_titles[:5]):  # Create 5 tasks
            deadline = (datetime.now() + timedelta(days=random.randint(7, 30))).date()
            priority = random.choice(['Low', 'Medium', 'High'])
            
            query = """
            INSERT INTO tasks (title, description, assigned_to, priority, deadline, status, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id
            """
            result = execute_query(query, (
                title,
                f"Sample task for testing AI analytics features - {title}",
                user_id,
                priority,
                deadline,
                random.choice(['Pending', 'In Progress', 'Delayed']),
                datetime.now()
            ))
            
            if result:
                task_ids.append(result[0]['id'])
        
        # Create sample delays with varied characteristics
        delays_created = 0
        for i in range(12):  # Create 12 delays
            if not task_ids:
                break
                
            task_id = random.choice(task_ids)
            excuse_text = sample_excuses[i % len(sample_excuses)]
            
            # Vary scores to create interesting analytics
            if i < 4:
                # High authenticity, low avoidance (good behavior)
                auth_score = random.uniform(75, 95)
                avoid_score = random.uniform(70, 90)
                risk_level = 'Low'
            elif i < 8:
                # Medium scores
                auth_score = random.uniform(50, 75)
                avoid_score = random.uniform(50, 70)
                risk_level = random.choice(['Low', 'Medium'])
            else:
                # Low authenticity, high avoidance (concerning behavior)
                auth_score = random.uniform(20, 50)
                avoid_score = random.uniform(20, 50)
                risk_level = random.choice(['Medium', 'High'])
            
            # Vary submission dates for time-decay testing
            days_ago = random.randint(1, 30)
            submitted_at = datetime.now() - timedelta(days=days_ago)
            
            query = """
            INSERT INTO delays (user_id, task_id, reason_text, score_authenticity, score_avoidance, risk_level, submitted_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            execute_query(query, (
                user_id,
                task_id,
                excuse_text,
                round(auth_score, 1),
                round(avoid_score, 1),
                risk_level,
                submitted_at
            ))
            delays_created += 1
        
        flash(f"✅ Sample data loaded! Created {len(task_ids)} tasks and {delays_created} delays for testing.", "success")
        current_app.logger.info(f"Sample data loaded for user {user_id}: {len(task_ids)} tasks, {delays_created} delays")
        
    except Exception as e:
        current_app.logger.error(f"Error loading sample data: {e}")
        flash(f"❌ Error loading sample data: {str(e)}", "error")
    
    return redirect(url_for('analytics'))
