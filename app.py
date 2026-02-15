from flask import Flask, render_template, redirect, url_for, session
from dotenv import load_dotenv
import os
from datetime import timedelta
from flask_wtf.csrf import CSRFProtect

# Load environment variables
load_dotenv()

# Create Flask app
app = Flask(__name__)

# --- Configuration ---
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_key_4192_secure_for_demo_only")
if os.getenv("FLASK_ENV") == "production" and app.secret_key == "dev_key_4192_secure_for_demo_only":
    raise RuntimeError("Production environment detected but FLASK_SECRET_KEY is not set securely.")
app.permanent_session_lifetime = timedelta(days=7)

# CSRF Protection
csrf = CSRFProtect(app)

# Secure Cookie Configuration
is_production = os.getenv('FLASK_ENV') == 'production'

app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SECURE=is_production,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=50 * 1024 * 1024
)

# --- Root Route ---
@app.route('/')
def index():
    return render_template('landing.html')

# --- Error Handlers ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"Server Error: {e}")
    return render_template('base.html', error="A serious error occurred. Please try again later."), 500

# Import all route modules (this registers the routes)
import routes.auth_routes
import routes.task_routes
import routes.admin_routes
import routes.analytics_routes
import routes.chatbot_routes
import routes.common_routes
import routes.dashboard_routes
import routes.debug_routes
import routes.team_routes
import routes.export_routes
import routes.sample_data_routes  # Sample data generator for testing AI features

# --- Run Server ---
if __name__ == '__main__':
    print("🚀 Starting Flask server...")
    print("📍 Server will be available at: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
