import os
import sys
import mysql.connector
import toml
from pathlib import Path

def print_status(message, status):
    icon = "✅" if status else "❌"
    print(f"{icon} {message}")

def check_files():
    print("\n--- 1. File Integrity Check ---")
    files = [
        ".env",
        ".streamlit/secrets.toml",
        "app.py",
        "components/styling.py",
        "utils/session.py",
        "assets/logo_light.png"
    ]
    all_exist = True
    for f in files:
        if os.path.exists(f):
            print_status(f"Found {f}", True)
        else:
            print_status(f"Missing {f}", False)
            all_exist = False
    return all_exist

def check_env_vars():
    print("\n--- 2. Environment Variables ---")
    # Check .env
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    all_set = True
    for var in required_vars:
        if os.getenv(var):
             print_status(f"ENV: {var} is set", True)
        else:
             print_status(f"ENV: {var} is missing", False)
             all_set = False
    return all_set

def check_db_connection():
    print("\n--- 3. Database Connection (TiDB) ---")
    try:
        # Try finding secrets first
        config = {}
        if os.path.exists(".streamlit/secrets.toml"):
            secrets = toml.load(".streamlit/secrets.toml")
            # Check for flat structure or [tidb] section
            if "tidb" in secrets:
                config = secrets["tidb"]
                print("   Using .streamlit/secrets.toml [tidb] section")
            elif "DB_HOST" in secrets:
                print("   Using .streamlit/secrets.toml (flat structure)")
                config = {
                    "host": secrets.get("DB_HOST"),
                    "port": secrets.get("DB_PORT", 4000),
                    "user": secrets.get("DB_USER"),
                    "password": secrets.get("DB_PASSWORD"),
                    "database": secrets.get("DB_NAME"),
                    "ssl_ca": os.path.abspath("isrgrootx1.pem"),
                    "ssl_verify_cert": True,
                    "ssl_verify_identity": True
                }

        # Fallback to env if config is still empty
        if not config:
             print("   Using .env config")
             config = {
                "host": os.getenv("DB_HOST"),
                "port": os.getenv("DB_PORT", 4000),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME")
             }
        
        # Adjust for mysql-connector arguments
        if 'port' in config:
            config['port'] = int(config['port'])
            
        print(f"   Connecting to {config.get('host')}...")
        conn = mysql.connector.connect(**config)
        if conn.is_connected():
            print_status("Connection successful", True)
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            ver = cursor.fetchone()
            print(f"   DB Version: {ver[0]}")
            
            # Check Tables
            cursor.execute("SHOW TABLES")
            tables = [x[0] for x in cursor.fetchall()]
            print(f"   Tables found: {', '.join(tables)}")
            
            conn.close()
            return True
    except Exception as e:
        print_status(f"Connection failed: {e}", False)
        return False

def check_imports():
    print("\n--- 4. Import / Syntax Check ---")
    modules = ["services.auth_service", "utils.session", "components.styling"]
    all_good = True
    for mod in modules:
        try:
            __import__(mod)
            print_status(f"Imported {mod}", True)
        except ImportError as e:
            print_status(f"Failed to import {mod}: {e}", False)
            all_good = False
        except Exception as e:
            print_status(f"Error importing {mod}: {e}", False)
            all_good = False
    return all_good

def main():
    print("==========================================")
    print("   EXCUSE PATTERN AI - DIAGNOSTICS TOOL   ")
    print("==========================================")
    
    files_ok = check_files()
    env_ok = check_env_vars()
    imports_ok = check_imports()
    db_ok = check_db_connection()
    
    print("\n==========================================")
    if files_ok and env_ok and imports_ok and db_ok:
        print("✅ SYSTEM READY. NO ISSUES DETECTED.")
    else:
        print("⚠️ ISSUES DETECTED. REVIEW LOGS ABOVE.")
    print("==========================================")

if __name__ == "__main__":
    main()
