from .db import execute_query, get_db_cursor

def create_task(title, description, assigned_to, created_by, priority, deadline, estimated_minutes):
    try:
        with get_db_cursor() as cursor:
            cursor.execute(
                "INSERT INTO tasks (title, description, assigned_to, created_by, status, priority, deadline, estimated_minutes) VALUES (%s, %s, %s, %s, 'Pending', %s, %s, %s) RETURNING id",
                (title, description, assigned_to, created_by, priority, deadline, estimated_minutes)
            )
            result = cursor.fetchone()
            if result:
                return result['id']
            raise Exception("Failed to get new task ID")
    except Exception as e:
        print(f"Error creating task: {e}")
        raise

def get_tasks_by_user(user_id):
    query = """
        SELECT id, title, description, assigned_to, created_by, status, 
               priority, deadline, estimated_minutes, created_at 
        FROM tasks 
        WHERE assigned_to = %s 
        ORDER BY created_at DESC
    """
    return execute_query(query, (user_id,))

def get_all_tasks():
    query = """
        SELECT 
            t.id, t.title, t.description, t.assigned_to, t.created_by, 
            t.status, t.priority, t.deadline, t.estimated_minutes, t.created_at,
            u_assign.email as assigned_to_email, 
            u_create.email as created_by_email 
        FROM tasks t
        LEFT JOIN users u_assign ON t.assigned_to = u_assign.id
        LEFT JOIN users u_create ON t.created_by = u_create.id
        ORDER BY t.created_at DESC
    """
    return execute_query(query)

def update_task_status(task_id, status):
    execute_query(
        "UPDATE tasks SET status=%s WHERE id=%s", 
        (status, task_id), 
        fetch=False
    )

def get_task_by_id(task_id):
    """Get task details by ID."""
    if not task_id:
        return None
        
    query = """
        SELECT id, title, description, assigned_to, created_by, status, 
               priority, deadline, estimated_minutes, created_at, completion_timestamp
        FROM tasks 
        WHERE id = %s
    """
    results = execute_query(query, (task_id,))
    return results[0] if results else None

def update_task_completion(task_id, completion_timestamp, status):
    """Update task with completion details."""
    row_count = execute_query(
        """
        UPDATE tasks 
        SET completion_timestamp = %s, status = %s
        WHERE id = %s
        """, 
        (completion_timestamp, status, task_id),
        fetch=False
    )
    
    if row_count == 0:
        raise ValueError(f"Task {task_id} not found")
    
    print(f"✅ Task {task_id} completed with status: {status}")

def delete_task(task_id):
    """Permanently delete a task."""
    execute_query(
        "DELETE FROM tasks WHERE id = %s",
        (task_id,),
        fetch=False
    )
    print(f"🗑️ Task {task_id} deleted")
