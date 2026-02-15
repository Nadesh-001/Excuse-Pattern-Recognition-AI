from database.connection import DatabaseConnection

if __name__ == "__main__":
    # First, initialize the database pool
    if DatabaseConnection.initialize_pool(min_conn=5, max_conn=30):
        print("✅ Database pool initialized")
        
        # Import app AFTER pool initialization
        from app import app
        
        # Run the Flask app
        app.run(host="0.0.0.0", port=5000, debug=True)
    else:
        print("❌ Failed to initialize database pool")
