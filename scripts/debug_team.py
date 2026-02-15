
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from repository.db import get_db_connection

def debug_team_structure():
    conn = get_db_connection()
    cur = conn.cursor()
    
    print("\n🔍 Debugging Team Structure...\n")
    
    # Check "nadeshgracious001@gmail.com" (ID 4)
    target_email = "nadeshgracious001@gmail.com"
    cur.execute("SELECT id, username, email, role FROM users WHERE email = %s", (target_email,))
    user = cur.fetchone()
    
    if not user:
        print(f"❌ User {target_email} not found!")
        return

    user_id, username, email, role = user
    print(f"👤 User: {username} (ID: {user_id})")
    print(f"📧 Email: {email}")
    print(f"👑 Role: {role}")
    
    if role not in ['manager', 'admin']:
        print("⚠️ User is not a manager/admin. Team Analytics will be empty.")
        return

    # Check for subordinates
    cur.execute("""
        SELECT id, username, email, role 
        FROM users 
        WHERE manager_id = %s
    """, (user_id,))
    
    team = cur.fetchall()
    
    if not team:
        print(f"⚠️ No users report to {username} (manager_id={user_id}).")
        print("   This explains why Team Analytics is empty.")
    else:
        print(f"✅ Found {len(team)} team members:")
        for member in team:
            print(f"   - {member[1]} ({member[2]}) [ID: {member[0]}]")

    conn.close()

if __name__ == "__main__":
    debug_team_structure()
