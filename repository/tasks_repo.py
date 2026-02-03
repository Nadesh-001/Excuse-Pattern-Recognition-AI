from .db import get_conn
import mysql.connector

def create_task(title, description, assigned_to, created_by, priority, deadline, estimated_minutes):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO tasks (title, description, assigned_to, created_by, priority, deadline, estimated_minutes) VALUES (%s, %s, %s, %s, %s, %s, %s)",
            (title, description, assigned_to, created_by, priority, deadline, estimated_minutes)
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        cursor.close()
        conn.close()

def get_tasks_by_user(user_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        # Fetch status as well. Explicit columns to reduce memory overhead.
        query = """
            SELECT id, title, description, assigned_to, created_by, status, 
                   priority, deadline, estimated_minutes, created_at 
            FROM tasks 
            WHERE assigned_to = %s 
            ORDER BY created_at DESC
        """
        cursor.execute(query, (user_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def get_all_tasks():
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        # Explicit columns + Joins
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
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

def update_task_status(task_id, status):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE tasks SET status=%s WHERE id=%s", (status, task_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def get_task_by_id(task_id):
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT id, title, description, assigned_to, created_by, status, 
                   priority, deadline, estimated_minutes, created_at 
            FROM tasks 
            WHERE id = %s
        """
        cursor.execute(query, (task_id,))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

def get_task_by_id(task_id):
    """Get task details by ID for formula calculations."""
    if not task_id:
        raise ValueError("Task ID cannot be empty")
    
    conn = get_conn()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT id, title, description, assigned_to, created_by, status, 
                   priority, deadline, estimated_minutes, created_at, completion_timestamp
            FROM tasks 
            WHERE id = %s
        """, (task_id,))
        return cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"❌ Error fetching task {task_id}: {e}")
        raise
    finally:
        cursor.close()
        conn.close()

def update_task_completion(task_id, completion_timestamp, status):
    """Update task with completion details (Formula 1, 3)."""
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE tasks 
            SET completion_timestamp = %s, status = %s
            WHERE id = %s
        """, (completion_timestamp, status, task_id))
        conn.commit()
        
        if cursor.rowcount == 0:
            raise ValueError(f"Task {task_id} not found")
        
        print(f"✅ Task {task_id} completed with status: {status}")
    except mysql.connector.Error as e:
        conn.rollback()
        print(f"❌ Error updating task completion: {e}")
        raise
    finally:
        cursor.close()
        conn.close()
