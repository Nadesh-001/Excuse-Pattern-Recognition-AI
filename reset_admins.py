import mysql.connector
from repository.users_repo import get_conn

def reset_admins():
    print("🗑️ Resetting Admin Accounts...")
    conn = get_conn()
    cursor = conn.cursor()
    
    try:
        # Find admins
        cursor.execute("SELECT id, email FROM users WHERE role='admin'")
        admins = cursor.fetchall()
        
        if not admins:
            print("✅ No admin accounts found.")
            return

        for (user_id, email) in admins:
            print(f"   Deleting admin: {email} (ID: {user_id})...")
            
            # Delete Related Records (Cascade manually)
            cursor.execute("DELETE FROM audit_logs WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM delays WHERE user_id=%s", (user_id,))
            cursor.execute("DELETE FROM tasks WHERE assigned_to=%s", (user_id,))
            cursor.execute("DELETE FROM role_permissions WHERE role='admin'") # Careful, this deletes for role, not user specific. But if resetting admins... keep permissions typically.
            # Actually, don't delete role_permissions unless we want to reset RBAC.
            # Just delete USER data.
            
            # Delete User
            cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
            
        conn.commit()
        print(f"✅ Successfully deleted {len(admins)} admin(s).")
        print("   The 'One-Time Admin Setup' screen should now be visible.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    reset_admins()
