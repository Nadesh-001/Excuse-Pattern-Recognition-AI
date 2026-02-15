from flask import render_template, request, redirect, url_for, flash, session, current_app
from app import app
from utils.flask_auth import admin_required
from services.user_service import get_users_list, manage_create_user, manage_update_user
from repository.users_repo import soft_delete_user
from repository.db import test_connection


@app.route('/admin')
@admin_required
def admin_panel():
    try:
        user_id = session.get('user_id')
        users = get_users_list(user_id)
        
        # Filter for active only for the primary display
        active_users = [u for u in users if u.get('active_status', True)]
        
        # Mock Risk Scores for "Risk Alert" Feature (Demo Only)
        import random
        for u in active_users:
            u['risk_warning'] = random.choice([True, False, False, False]) if 'admin' not in u['role'] else False

        # Mock Logs for Demo
        logs = [
            {"timestamp": "2 mins ago", "email": "nadesh@example.com", "action": "LOGIN", "details": "User logged in successfully"},
            {"timestamp": "15 mins ago", "email": "admin@example.com", "action": "UPDATE_USER", "details": "Updated role for user: sarah.j"},
            {"timestamp": "1 hour ago", "email": "system", "action": "BACKUP", "details": "Daily database backup completed"},
            {"timestamp": "2 hours ago", "email": "mike.t@example.com", "action": "TASK_Create", "details": "Created new task: Q4 Report"},
            {"timestamp": "5 hours ago", "email": "nadesh@example.com", "action": "LOGOUT", "details": "User logged out"},
        ]

        diagnostics = test_connection()

        return render_template('admin.html', users=active_users, logs=logs, diagnostics=diagnostics)
    except PermissionError as e:
        flash(str(e), "error")
        return redirect(url_for('dashboard'))
    except Exception as e:
        current_app.logger.error(f"Admin panel error: {e}")
        flash("Error loading admin panel. Please try again.", "error")
        return redirect(url_for('dashboard'))


@app.route('/admin/users/add', methods=['POST'])
@admin_required
def admin_add_user():
    try:
        actor_id    = session.get('user_id')
        full_name   = request.form.get('name')
        email       = request.form.get('email')
        password    = request.form.get('password')
        role        = request.form.get('role', 'employee')
        
        success, message = manage_create_user(actor_id, full_name, email, password, role)
        
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            
    except Exception as e:
        flash("Error creating user. Please check logs.", "error")
        current_app.logger.error(f"Admin add user error: {e}")
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    try:
        # In this implementation, delete is just a soft-delete (deactivate)
        soft_delete_user(user_id)
        flash("User deactivated successfully!", "success")
    except Exception as e:
        flash(f"Error deleting user: {str(e)}", "error")
        current_app.logger.error(f"Admin delete user error: {e}")
    
    return redirect(url_for('admin_panel'))


@app.route('/admin/users/edit', methods=['POST'])
@admin_required
def admin_edit_user():
    try:
        actor_id       = session.get('user_id')
        target_user_id = int(request.form.get('user_id'))
        full_name      = request.form.get('name')
        email          = request.form.get('email')
        role           = request.form.get('role')
        active_status  = request.form.get('active_status', 'true').lower() == 'true'
        
        success, message = manage_update_user(
            actor_id, target_user_id, full_name, email, role, active_status
        )
        
        if success:
            flash(message, "success")
        else:
            flash(message, "error")
            
    except (ValueError, TypeError):
        flash("Invalid request data.", "error")
    except Exception as e:
        flash("Error updating user. Please check logs.", "error")
        current_app.logger.error(f"Admin edit user error: {e}")
    
    return redirect(url_for('admin_panel'))
