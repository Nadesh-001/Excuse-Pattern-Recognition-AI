import mysql.connector
from mysql.connector import pooling
import streamlit as st
import os

# Create a connection pool
# We use a function to get the config to ensure it works even if loaded before secrets are ready (though usually secrets are ready)
def get_db_config():
    return {
        "host": st.secrets.get("DB_HOST") or os.getenv("DB_HOST", "localhost"),
        "user": st.secrets.get("DB_USER") or os.getenv("DB_USER", "root"),
        "password": st.secrets.get("DB_PASSWORD") or os.getenv("DB_PASSWORD", ""),
        "database": st.secrets.get("DB_NAME") or os.getenv("DB_NAME", "test"),
        "port": int(st.secrets.get("DB_PORT") or os.getenv("DB_PORT", 4000)),
        "ssl_ca": os.path.join(os.path.dirname(os.path.dirname(__file__)), "isrgrootx1.pem"),
        "ssl_disabled": False
    }

# Use st.cache_resource to persist the pool across reruns
@st.cache_resource
def get_pool():
    config = get_db_config()
    
    # Ensure ssl_ca exists, if not, might need to adjust path or disable ssl if local
    if not os.path.exists(config["ssl_ca"]):
            # Fallback for local dev if pem missing, but production usually needs it for TiDB
            print(f"Warning: SSL Cert not found at {config['ssl_ca']}")
            
    try:
        pool = pooling.MySQLConnectionPool(
            pool_name="app_pool",
            pool_size=5,
            **config
        )
        return pool
    except mysql.connector.Error as err:
        print(f"Error creating connection pool: {err}")
        raise err

def get_conn():
    """Get a connection from the pool."""
    try:
        connection = get_pool().get_connection()
        return connection
    except mysql.connector.Error as err:
        print(f"Error getting connection: {err}")
        raise err
