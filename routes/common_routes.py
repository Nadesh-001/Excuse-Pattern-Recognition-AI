from flask import request, jsonify, current_app, render_template, session
from app import app
from repository.db import get_db_connection
from services.upload_service import upload_file
from utils.flask_auth import auth_required
from repository.tasks_repo import get_all_tasks
from repository.delays_repo import get_delays_all

@app.route('/health')
def health():
    """Health check endpoint for production monitoring"""
    db_status = "disconnected"
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                 cursor.execute("SELECT 1")
                 db_status = "connected"
    except Exception:
        db_status = "disconnected"

    return {
        "status": "ok",
        "db": db_status,
        "ai": "configured"
    }, 200

@app.route("/upload", methods=["POST"])
@auth_required
def upload():
    """Generic file upload endpoint."""
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400
        
    file = request.files["file"]
    if file.filename == '':
        return {'error': 'No selected file'}, 400
        
    try:
        result = upload_file(file)
        if result['success']:
            return {"url": result['url'], "path": result['path']}
        else:
            return {"error": result['error']}, 400
    except Exception as e:
        current_app.logger.error(f"Upload error: {e}")
        return {"error": str(e)}, 500

@app.route('/search')
@auth_required
def universal_search():
    """Universal search across tasks, delays, and users with logging and semantic expansion"""
    query = request.args.get('q', '').strip()
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    user_id = session.get('user_id')
    
    # --- 1. Log the Search ---
    if query:
        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        "INSERT INTO search_logs (user_id, query) VALUES (%s, %s)",
                        (user_id, query)
                    )
                conn.commit()
        except Exception as e:
            current_app.logger.error(f"Failed to log search: {e}")

    # --- 2. Semantic Expansion (Mock AI) ---
    SEMANTIC_MAP = {
        'rain': ['weather', 'storm', 'flood', 'wet'],
        'sick': ['health', 'doctor', 'fever', 'medical'],
        'wifi': ['network', 'internet', 'connection', 'outage'],
        'late': ['delay', 'traffic', 'stuck'],
        'urgent': ['high', 'critical', 'asap']
    }
    
    expanded_terms = [query.lower()]
    for key, values in SEMANTIC_MAP.items():
        if key in query.lower():
            expanded_terms.extend(values)
            
    # --- 3. Execute Search ---
    try:
        # Search Tasks
        all_tasks = get_all_tasks()
        matched_tasks = []
        for t in all_tasks:
            # Check string overlap with any expanded term
            text_corpus = f"{t.get('title')} {t.get('description')} {t.get('priority')} {t.get('status')}".lower()
            if any(term in text_corpus for term in expanded_terms):
                matched_tasks.append(t)

        # Search Delays
        all_delays = get_delays_all()
        matched_delays = []
        for d in all_delays:
            text_corpus = f"{d.get('reason_text')} {d.get('task_title')} {d.get('risk_level')}".lower()
            if any(term in text_corpus for term in expanded_terms):
                matched_delays.append(d)
                
        # Search Users (Admin/Manager only typically, but open for global search demo)
        from repository.users_repo import get_all_users
        all_users = get_all_users()
        matched_users = [
            u for u in all_users
            if query.lower() in (u.get('full_name') or '').lower() or 
               query.lower() in (u.get('email') or '').lower()
        ]

        # --- 4. Get Trending & Recent Searches (for Empty State) ---
        trending = []
        recent_searches = []
        if not query:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    # Get most common recent queries (Global)
                    cur.execute("""
                        SELECT query, COUNT(*) as count 
                        FROM search_logs 
                        WHERE timestamp > NOW() - INTERVAL '7 days' 
                        GROUP BY query 
                        ORDER BY count DESC 
                        LIMIT 5
                    """)
                    trending = [row['query'] for row in cur.fetchall()]

                    # Get user's recent searches (Personal)
                    if user_id:
                        cur.execute("""
                            SELECT DISTINCT query 
                            FROM search_logs 
                            WHERE user_id = %s 
                            ORDER BY MAX(timestamp) DESC 
                            LIMIT 5
                        """, (user_id,))
                        recent_searches = [row['query'] for row in cur.fetchall()]

        return render_template('search.html', 
                             query=query, 
                             tasks=matched_tasks, 
                             delays=matched_delays,
                             users=matched_users,
                             trending=trending,
                             recent_searches=recent_searches)
                             
    except Exception as e:
        current_app.logger.error(f"Search error: {e}")
        return render_template('search.html', query=query, tasks=[], delays=[], users=[], error=str(e))

@app.route('/profile')
@auth_required
def profile():
    """User profile page"""
    user_name = session.get('user_name', 'Unknown User')
    email = session.get('email', 'Not available')
    role = session.get('user_role', 'employee')
    
    return render_template('profile.html', 
                         user_name=user_name, 
                         email=email,
                         role=role)
