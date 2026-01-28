import streamlit as st
import bcrypt
import mysql.connector
from database.connection import get_db_connection

def init_session_state():
    """Initialize session state variables if they don't exist."""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    if 'user_role' not in st.session_state:
        st.session_state.user_role = None
    if 'user_id' not in st.session_state:
        st.session_state.user_id = None
    if 'user_name' not in st.session_state:
        st.session_state.user_name = None

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def login_user(email, password):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor(dictionary=True)
    print(f"DEBUG: Attempting login for email: {email}")
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        print(f"DEBUG: User found: {user['email']}, Hash starts with: {user['password_hash'][:10]}")
        is_valid = verify_password(password, user['password_hash'])
        print(f"DEBUG: Password valid: {is_valid}")
        
        if is_valid:
            st.session_state.logged_in = True
            st.session_state.user_role = user['role']
            st.session_state.user_id = user['id']
            st.session_state.user_name = user['full_name']
            return True, "Login successful"
    else:
        print("DEBUG: User not found in database")
    
    return False, "Invalid email or password"

def signup_user(full_name, email, password, role='employee'):
    conn = get_db_connection()
    if not conn:
        return False, "Database connection failed"
    
    cursor = conn.cursor()
    hashed = hash_password(password)
    
    try:
        cursor.execute(
            "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
            (full_name, email, hashed, role)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return True, "User registered successfully"
    except mysql.connector.Error as err:
        return False, f"Error: {err}"
