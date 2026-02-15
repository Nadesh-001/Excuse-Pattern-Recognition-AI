from flask import render_template, request, redirect, url_for, session, flash
from app import app
from services.auth_service import register_user, authenticate_user, change_user_password
from services.user_service import service_delete_own_account
from services.permission_service import load_user_permissions
from utils.flask_auth import auth_required

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Sanitize inputs
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        try:
            user = authenticate_user(email, password)
            if user:
                # Prevent session fixation
                session.clear()
                
                session.permanent = True
                session['user_id'] = user['id']
                session['user_role'] = user['role']
                session['user_name'] = user['full_name']
                session['email'] = user.get('email', email)
                
                # Load permissions AFTER session is set
                load_user_permissions()
                
                flash("Login successful!", "success")
                return redirect(url_for('dashboard'))
            else:
                flash("Invalid credentials. Please try again.", "error")
        except Exception as e:
            app.logger.error(f"Login error: {e}")
            flash("An error occurred. Please try again.", "error")
    
    return render_template('login.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        # Sanitize email
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '').strip()
        role = request.form.get('role', 'employee')
        job_role = request.form.get('job_role', '').strip() or None
        
        try:
            success, message = register_user(full_name, email, password, role, job_role=job_role)
            if success:
                flash(message, "success")
                return redirect(url_for('login'))
            else:
                flash(message, "error")
        except Exception as e:
            current_app.logger.error(f"Registration error: {e}")
            flash("Registration failed. Please try again.", "error")
    
    return render_template('register.html')


@app.route('/change-password', methods=['GET', 'POST'])
@auth_required
def change_password():
    if request.method == 'POST':
        current_pw = request.form.get('current_password')
        new_pw = request.form.get('new_password')
        confirm_pw = request.form.get('confirm_password')
        
        try:
            success, message = change_user_password(
                session['user_id'], 
                current_pw, 
                new_pw, 
                confirm_pw
            )
            
            if success:
                flash(message, "success")
                return redirect(url_for('dashboard'))
            else:
                flash(message, "error")
        except Exception as e:
            current_app.logger.error(f"Error changing password: {e}")
            flash("An error occurred. Please try again.", "error")
            
    return render_template('change_password.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for('login'))

@app.route('/delete-account', methods=['POST'])
@auth_required
def delete_account():
    try:
        success, message = service_delete_own_account(session['user_id'])
        if success:
            session.clear()
            flash("Your account has been successfully deleted.", "success")
            return redirect(url_for('login'))
        else:
            flash(f"Error deleting account: {message}", "error")
            return redirect(url_for('profile')) # Assuming there's a profile route, need to check
    except Exception as e:
        current_app.logger.error(f"Error in delete_account route: {e}")
        flash("An unexpected error occurred.", "error")
        return redirect(url_for('dashboard'))

@app.route('/switch-account/<role>')
@auth_required
def switch_account(role):
    """Demo feature to quickly switch between roles."""
    if role not in ['admin', 'manager', 'employee']:
        flash("Invalid role for switching.", "error")
        return redirect(url_for('dashboard'))
        
    # Find a user with the requested role
    from repository.db import execute_query
    users = execute_query("SELECT id, full_name, email, role FROM users WHERE role = %s LIMIT 1", [role])
    
    if users:
        user = users[0]
        session['user_id'] = user['id']
        session['user_role'] = user['role']
        session['user_name'] = user['full_name']
        session['email'] = user['email']
        load_user_permissions()
        flash(f"Switched to {role.upper()} account: {user['full_name']}", "success")
    else:
        # Fallback if no user exists
        flash(f"No {role} account found in database.", "warning")
        
    return redirect(url_for('dashboard'))
