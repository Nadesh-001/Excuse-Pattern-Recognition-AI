import mysql.connector
import os
from dotenv import load_dotenv
from passlib.context import CryptContext

load_dotenv()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

import streamlit as st

def get_db_connection():
    try:
        # Check Streamlit secrets first, then environment variables
        host = st.secrets.get("DB_HOST") or os.getenv("DB_HOST")
        user = st.secrets.get("DB_USER") or os.getenv("DB_USER")
        password = st.secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD")
        database = st.secrets.get("DB_NAME") or os.getenv("DB_NAME")
        port = st.secrets.get("DB_PORT") or os.getenv("DB_PORT", 4000)

        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
            port=int(port),
            ssl_ca=os.path.join(os.path.dirname(__file__), "isrgrootx1.pem"),
            ssl_disabled=False,
        )
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def init_db():
    conn = get_db_connection()
    if conn:
        cursor = conn.cursor()
        try:
            with open('database/schema.sql', 'r') as f:
                # Split by ; for multiple statements
                statements = f.read().split(';')
                for stmt in statements:
                    if stmt.strip():
                        cursor.execute(stmt)
            
            # Create Default Admin
            cursor.execute("SELECT * FROM users WHERE email = %s", ('admin@example.com',))
            if not cursor.fetchone():
                hashed_pw = pwd_context.hash("admin123")
                cursor.execute(
                    "INSERT INTO users (full_name, email, password_hash, role) VALUES (%s, %s, %s, %s)",
                    ('System Admin', 'admin@example.com', hashed_pw, 'admin')
                )
                print("Default Admin created.")
            
            conn.commit()
            print("Database initialized successfully!")
        except Exception as e:
            print(f"Init Error: {e}")
        finally:
            cursor.close()
            conn.close()

if __name__ == "__main__":
    init_db()
