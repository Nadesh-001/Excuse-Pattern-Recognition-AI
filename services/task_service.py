from repository.tasks_repo import create_task, get_tasks_by_user, get_all_tasks, update_task_status, get_task_by_id, update_task_completion
from repository.resources_repo import create_resource, get_resources_by_task
from repository.delays_repo import create_delay, get_user_delay_history, count_user_delays
from services.activity_service import log_activity
from utils.time_utils import parse_time_input
from utils import scoring_engine
from datetime import datetime
import os

def service_create_task(manager_id, title, description, assigned_to, priority, deadline, est_hours, est_minutes, links=None, files=None):
    # Validation could go here
    est_total_mins = parse_time_input(est_hours, est_minutes)
    
    task_id = create_task(title, description, assigned_to, manager_id, priority, deadline, est_total_mins)
    
    # Handle attachments
    # This logic was previously in UI, moving here implies passing file objects which is tricky with Streamlit
    # For now, we'll keep simple logic: UI handles upload to disk, Service handles DB record
    if links:
         for link in links:
              # In a real app, AI analysis of link would happen here
              create_resource(task_id, 'link', link, 'External Link', 'Pending AI', {}, {}, 0)
              
    log_activity(manager_id, "CREATE_TASK", f"Created task '{title}' for user {assigned_to}")
    return task_id

def service_get_tasks(user_id, role):
    if role in ['admin', 'manager']:
        return get_all_tasks()
    else:
        return get_tasks_by_user(user_id)

def service_complete_task(user_id, task_id, task_title):
    """
    Complete a task with explicit formula-based status calculation.
    
    Uses:
    - Formula 1: Elapsed time calculation
    - Formula 2: Delay detection
    - Formula 3: Task status determination
    - Formula 4: Delay duration calculation
    """
    # Get task details
    task = get_task_by_id(task_id)
    if not task:
        raise ValueError(f"Task {task_id} not found")
    
    # Record completion timestamp
    completion_time = datetime.now()
    
    # Formula 1: Calculate elapsed time
    created_at = task['created_at']
    elapsed = scoring_engine.calculate_elapsed_time(created_at, completion_time)
    elapsed_minutes = int(elapsed.total_seconds() / 60)
    
    estimated_minutes = task.get('estimated_minutes', 0)
    
    # Formula 3: Determine task status (Completed vs Completed Over Time)
    status = scoring_engine.calculate_task_status(elapsed_minutes, estimated_minutes)
    
    # Update task with completion details
    update_task_completion(task_id, completion_time, status)
    
    log_activity(user_id, "COMPLETE_TASK", f"Completed task '{task_title}' - Status: {status}")
    
    # Formula 2: Check if delayed
    is_delayed = scoring_engine.is_task_delayed(elapsed_minutes, estimated_minutes)
    
    if is_delayed:
        # Formula 4: Calculate delay duration
        delay_duration = scoring_engine.calculate_delay_duration(elapsed_minutes, estimated_minutes)
        
        return {
            'status': status,
            'delayed': True,
            'delay_duration': delay_duration,
            'elapsed_minutes': elapsed_minutes,
            'estimated_minutes': estimated_minutes
        }
    
    return {
        'status': status,
        'delayed': False,
        'elapsed_minutes': elapsed_minutes,
        'estimated_minutes': estimated_minutes
    }

def service_submit_delay(user_id, task_id, task_title, reason, audio_file_path=None):
    """
    Submit delay analysis using EXPLICIT FORMULAS (not AI).
    
    Uses:
    - Formulas 6-11: Authenticity scoring (5 rules)
    - Formula 12: Avoidance score
    - Formula 13: Category classification
    - Formula 5: Delay count
    - Formulas 16-18: Risk level calculation
    """
    # Get task to retrieve delay_duration
    task = get_task_by_id(task_id)
    delay_duration = 0
    
    if task and task.get('completion_timestamp'):
        # Calculate delay duration if already completed
        created_at = task['created_at']
        completion_time = task['completion_timestamp']
        elapsed = scoring_engine.calculate_elapsed_time(created_at, completion_time)
        elapsed_minutes = int(elapsed.total_seconds() / 60)
        estimated_minutes = task.get('estimated_minutes', 0)
        delay_duration = scoring_engine.calculate_delay_duration(elapsed_minutes, estimated_minutes)
    
    # Get user's delay history for Formula 10 (behavioral consistency)
    user_history = get_user_delay_history(user_id, limit=5)
    
    # ACADEMIC FORMULA-BASED ANALYSIS (Formulas 6-13)
    analysis = scoring_engine.analyze_excuse(reason, user_history)
    
    # Formula 5: Get delay count for risk calculation
    current_delay_count = count_user_delays(user_id)
    
def service_submit_delay(user_id, task_id, task_title, reason, audio_file_path=None, proof_file=None):
    """
    Analyzes delay excuse using AI Formulas and records it.
    """
    # ... (analysis logic) ...
    # Perform Analysis (Formula 5)
    analysis = scoring_engine.analyze_excuse(reason)
    
    # Formula 4: Calculate delay duration (Simulated for now, real implementation would track time diff)
    delay_duration = 0 
    
    # Get current delay count for risk calculation
    current_delay_count = count_user_delays(user_id)
    
    # Formulas 16-18: Calculate risk level based on delay count
    risk_level = scoring_engine.calculate_risk_level(current_delay_count + 1)  # +1 for this new delay

    # Handle Proof File
    proof_path = None
    if proof_file:
        upload_dir = "uploads/proofs"
        os.makedirs(upload_dir, exist_ok=True)
        # Unique filename
        filename = f"{task_id}_{int(datetime.now().timestamp())}_{proof_file.name}"
        proof_path = os.path.join(upload_dir, filename)
        with open(proof_path, "wb") as f:
            f.write(proof_file.getbuffer())
    
    # Store delay with formula-based results
    delay_id = create_delay(
        task_id=task_id,
        user_id=user_id,
        reason_text=reason,
        reason_audio_path=audio_file_path,
        score_authenticity=analysis['authenticity_score'],
        score_avoidance=analysis['avoidance_score'],
        risk_level=risk_level,
        ai_feedback=analysis.get('explanation', ''),  # Formula explanation, not AI
        ai_analysis_json=analysis,  # Stores rule breakdown and category
        delay_duration=delay_duration,
        proof_path=proof_path
    )
    
    # Update task status to mark as delayed
    update_task_status(task_id, 'Delayed')
    
    log_activity(
        user_id, 
        "SUBMIT_DELAY", 
        f"Delay submitted for task '{task_title}' - Auth: {analysis['authenticity_score']}%, Risk: {risk_level}"
    )
    
    # Return complete analysis
    return {
        'delay_id': delay_id,
        'authenticity_score': analysis['authenticity_score'],
        'avoidance_score': analysis['avoidance_score'],
        'category': analysis['category'],
        'risk_level': risk_level,
        'rule_breakdown': analysis['rule_breakdown'],
        'explanation': analysis['explanation'],
        'delay_duration': delay_duration
    }
