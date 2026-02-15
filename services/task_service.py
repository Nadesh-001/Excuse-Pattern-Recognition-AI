from flask import current_app, abort
from repository.tasks_repo import (
    create_task, get_tasks_by_user, get_all_tasks, 
    update_task_status, get_task_by_id, update_task_completion, 
    delete_task as repo_delete_task
)
from repository.resources_repo import create_resource
from repository.delays_repo import create_delay, get_user_delay_history, count_user_delays
from services.activity_service import log_activity
from utils.time_utils import parse_time_input
from utils.scoring_engine import calculate_authenticity_score
from utils.task_formulas import (
    calculate_elapsed_time,
    calculate_task_status,
    is_task_delayed,
    calculate_elapsed_between,
)
from utils.pattern_engine import run_pattern_detection, apply_pattern_penalty
from datetime import datetime
from dataclasses import asdict
import json

def service_create_task(manager_id, title, description, assigned_to, priority, deadline, est_hours, est_minutes, category="General", links=None):
    """Create a new task with estimated time and category."""
    est_total_mins = parse_time_input(est_hours, est_minutes)
    
    # In this app, category is currently just stored in the task record if we update the repo,
    # but for now tasks_repo.create_task doesn't take category. 
    # Let's assume the user wants it tracked.
    
    task_id = create_task(title, description, assigned_to, manager_id, priority, deadline, est_total_mins)
    
    if links:
         for link in links:
              create_resource(task_id, 'link', link, 'External Link', 'Pending AI', {}, {}, 0)
              
    log_activity(manager_id, "CREATE_TASK", f"Created task '{title}' for user {assigned_to}")
    return task_id

def service_get_tasks(user_id, role):
    """Fetch tasks based on user role."""
    if role in ['admin', 'manager']:
        return get_all_tasks()
    return get_tasks_by_user(user_id)

def service_get_task_or_404(task_id):
    """Retrieve task by ID or raise Flask 404."""
    task = get_task_by_id(task_id)
    if not task:
        abort(404)
    return task

def _verify_task_ownership(user_id, role, task):
    """Raise PermissionError if user doesn't have access to the task."""
    if role in ['admin', 'manager']:
        return
    if task['assigned_to'] != user_id:
        raise PermissionError("You do not have permission to access this task.")

def service_complete_task(user_id, task_id):
    """Complete a task and log activity."""
    task = get_task_by_id(task_id)
    if not task:
        raise LookupError(f"Task {task_id} not found")
    
    # Ownership check
    if task['assigned_to'] != user_id:
        raise PermissionError("Only the assignee can complete this task.")
        
    completion_time = datetime.now()
    created_at = task['created_at']
    elapsed = calculate_elapsed_between(created_at, completion_time)
    elapsed_minutes = int(elapsed.total_seconds() / 60)
    estimated_minutes = task.get('estimated_minutes', 0)
    
    status = calculate_task_status(elapsed_minutes, estimated_minutes)
    update_task_completion(task_id, completion_time, status)
    
    log_activity(user_id, "COMPLETE_TASK", f"Completed task '{task['title']}' - Status: {status}")
    
    is_delayed_bool = is_task_delayed(elapsed_minutes, estimated_minutes)
    return {
        'status': status,
        'delayed': is_delayed_bool,
        'elapsed_minutes': elapsed_minutes,
        'estimated_minutes': estimated_minutes
    }

def service_submit_delay(user_id, task_id, reason, proof_file=None):
    """Submit delay analysis using AI and deterministic scoring."""
    from services.ai_service import analyze_excuse_with_ai, score_ai_signal
    
    task = get_task_by_id(task_id)
    if not task:
        raise LookupError("Task not found")
        
    if task['assigned_to'] != user_id:
        raise PermissionError("You can only submit delays for your own tasks.")

    # 1. AI Analysis
    ai_analysis = analyze_excuse_with_ai(reason)
    ai_score_val = score_ai_signal(ai_analysis)
    
    # 2. Context Calculation
    deadline_str = task.get('deadline')
    hours_left = 0
    is_after_deadline = False
    
    if deadline_str:
        try:
            deadline_dt = datetime.strptime(deadline_str, "%Y-%m-%d")
            now_naive = datetime.now()
            time_diff = deadline_dt - now_naive
            hours_left = int(time_diff.total_seconds() / 3600)
            is_after_deadline = time_diff.total_seconds() < 0
        except:
             pass

    # 3. Final Scoring
    current_delay_count = count_user_delays(user_id)
    history = get_user_delay_history(user_id, limit=5)

    scoring_breakdown = calculate_authenticity_score(
        reason=reason,
        delay_count=current_delay_count,
        priority=task.get('priority', 'Low'),
        hours_left=hours_left,
        has_proof=bool(proof_file),
        is_after_deadline=is_after_deadline,
        ai_score=ai_score_val
    )
    
    flags = run_pattern_detection(reason, history, (hours_left if is_after_deadline else None), is_after_deadline)
    final_auth_score = apply_pattern_penalty(scoring_breakdown.total, flags)
    
    # Calculate final risk level after pattern penalties
    risk_level = "High"
    if final_auth_score >= 75: 
        risk_level = "Low"
    elif final_auth_score >= 45: 
        risk_level = "Medium"
        
    # Convert ScoreBreakdown to result dict for compatibility
    scoring_result = asdict(scoring_breakdown)
    scoring_result['authenticity_score'] = final_auth_score
    scoring_result['risk_level'] = risk_level

    # 4. Handle Proof
    final_proof_path = None
    if proof_file:
         from services.upload_service import upload_file
         upload_res = upload_file(proof_file, folder="proofs")
         if upload_res['success']:
             final_proof_path = upload_res['path']

    # 5. DB Persistence
    ai_analysis['pattern_flags'] = flags
    create_delay(
        task_id=task_id, user_id=user_id, reason_text=reason, reason_audio_path=None,
        score_authenticity=final_auth_score, score_avoidance=100 - final_auth_score,
        risk_level=risk_level, ai_feedback=json.dumps(scoring_result),
        ai_analysis_json=json.dumps(ai_analysis), delay_duration=0, proof_path=final_proof_path
    )
    
    update_task_status(task_id, 'Delayed')
    log_activity(user_id, "SUBMIT_DELAY", f"Delay submitted for '{task['title']}' - Score: {final_auth_score}")
    
    return scoring_result

def service_delete_task(user_id, task_id, role):
    """Deletes a task with permission enforcement."""
    task = get_task_by_id(task_id)
    if not task:
        raise LookupError("Task not found")
        
    if role not in ['admin', 'manager'] and task['assigned_to'] != user_id:
        raise PermissionError("You do not have permission to delete this task")
        
    repo_delete_task(task_id)
    log_activity(user_id, "DELETE_TASK", f"Deleted task '{task['title']}'")
    return True
