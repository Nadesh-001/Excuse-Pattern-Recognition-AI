from flask import request, session, jsonify, render_template, current_app
from app import app, csrf
from services.chat_service import get_chat_response
from services.analytics_service import get_analytics_data
from repository.tasks_repo import get_tasks_by_user, get_all_tasks
from utils.flask_auth import auth_required

@app.route('/chatbot')
@auth_required
def chatbot():
    """Renders the chatbot UI."""
    return render_template('chatbot.html')

@app.route('/chatbot/api', methods=['POST'])
@csrf.exempt  # Exempt from CSRF for JSON API
def chatbot_api():
    """Handles chat API requests."""
    if 'user_id' not in session: 
        return {'error': 'Unauthorized'}, 401
    
    data = request.json
    if not data:
        return {'error': 'No data provided'}, 400
        
    prompt = data.get('message')
    conversation_history = data.get('history', [])
    
    if not prompt: 
        return {'error': 'No message provided'}, 400
        
    user_id = session['user_id']
    user_role = session.get('user_role', 'employee')
    
    # Fetch real analytics for context
    kpis = get_analytics_data(user_id=user_id, role=user_role)
    
    user_context = f"""
    User: {session.get('user_name')} ({user_role})
    Stats:
    - Avg Authenticity: {kpis.get('avg_auth_score')}%
    - Risk Distribution: {kpis.get('risk_distribution')}
    - Pending Tasks: {len([t for t in get_tasks_by_user(user_id) if t['status'] == 'Pending']) if user_role == 'employee' else 'N/A'}
    """

    # --- Contextual Query Handling ---
    prompt_lower = prompt.lower()
    
    if "quick insights" in prompt_lower or "performance" in prompt_lower:
        auth = kpis.get('avg_auth_score', 0)
        low_risk = kpis.get('risk_low', 0)
        return {'response': f"🚀 **Quick Insights:**<br>• Your average Authenticity Signal is **{auth}%**.<br>• You have **{low_risk}** low-risk delay submissions.<br>• Trend: Your trust index is {'stable' if auth > 70 else 'needs improvement'}.<br>How else can I help?"}

    if "pending" in prompt_lower or "status" in prompt_lower:
        tasks = get_tasks_by_user(user_id) if user_role == 'employee' else get_all_tasks()
        pending = [t for t in tasks if t['status'] == 'Pending']
        return {'response': f"You have **{len(pending)}** pending tasks. Your next deadline is **{pending[0]['deadline'] if pending else 'N/A'}**."}
    
    try:
        # Pass conversation history if you want context (frontend needs to send it)
        # For now, we'll pass an empty list if not provided
        response_text = get_chat_response(prompt, conversation_history, user_context=user_context)
        return {'response': response_text}
    except Exception as e:
        current_app.logger.error(f"Chatbot Error: {e}")
        return {'error': str(e)}, 500
