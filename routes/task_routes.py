from flask import render_template, request, redirect, url_for, session, flash, current_app, abort

from app import app
from utils.flask_auth import auth_required, manager_required
from utils.task_enrichment import enrich_task
from services.task_service import (
    service_get_tasks,
    service_create_task,
    service_complete_task,
    service_submit_delay,
    service_delete_task,
    service_get_task_or_404,
)
from repository.resources_repo import get_resources_by_task
from services.user_service import get_users_list


# ---------------------------------------------------------------------------
# File upload policy — constants at module level, not per-request.
# ---------------------------------------------------------------------------

ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'doc', 'docx'}
MAX_FILE_SIZE      = 10 * 1024 * 1024  # 10 MB


def _validate_proof_file(proof_file) -> str | None:
    """
    Validate extension and size of an uploaded proof file.

    Returns an error message string, or None if the file is valid (or absent).
    """
    if not proof_file or not proof_file.filename:
        return None

    ext = proof_file.filename.rsplit('.', 1)[-1].lower() if '.' in proof_file.filename else ''
    if ext not in ALLOWED_EXTENSIONS:
        return f"Invalid file type. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS)).upper()}"

    # Seek/tell is acceptable here because Werkzeug has already buffered the
    # upload. We reset the position so the service layer reads from byte 0.
    proof_file.seek(0, 2)
    size = proof_file.tell()
    proof_file.seek(0)
    if size > MAX_FILE_SIZE:
        return "File too large. Maximum 10 MB allowed."

    return None


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route('/tasks')
@auth_required
def tasks():
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    role = session.get('user_role', 'employee')
    current_app.logger.debug("Tasks route — user: %s  role: %s", user_id, role)

    tasks_list = service_get_tasks(user_id, role)
    current_app.logger.debug("Service returned %d tasks", len(tasks_list))

    status_filter = request.args.get('status')
    if status_filter and status_filter != 'All':
        tasks_list = [t for t in tasks_list if t['status'] == status_filter]

    for task in tasks_list:
        enrich_task(task)

    return render_template('tasks.html', tasks=tasks_list, role=role)


@app.route('/tasks/new', methods=['GET', 'POST'])
@manager_required
def new_task():
    if request.method == 'POST':
        title       = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        assigned_to = request.form.get('assigned_to', '').strip()
        deadline    = request.form.get('deadline')
        priority    = request.form.get('priority', 'Medium')
        category    = request.form.get('category', 'General')

        try:
            est_hours   = int(request.form.get('est_hours')   or 0)
            est_minutes = int(request.form.get('est_minutes') or 0)
        except (ValueError, TypeError):
            flash("Invalid estimated time. Please enter valid numbers.", "error")
            return render_template('task_form.html', users=get_users_list(session['user_id']))

        if not (title and description and assigned_to):
            flash("Title, description, and assignee are required.", "warning")
            return render_template('task_form.html', users=get_users_list(session['user_id']))

        try:
            task_id = service_create_task(
                manager_id  = session['user_id'],
                title       = title,
                description = description,
                assigned_to = int(assigned_to),
                priority    = priority,
                deadline    = deadline,
                est_hours   = est_hours,
                est_minutes = est_minutes,
                category    = category,
            )
            current_app.logger.info("Task created — id: %s  manager: %s", task_id, session['user_id'])
            flash("Task created successfully!", "success")
            return redirect(url_for('tasks'))
        except (ValueError, TypeError) as e:
            flash(f"Invalid assignment or time data: {e}", "error")
        except Exception as e:
            current_app.logger.error("Task creation error: %s", e)
            flash("Error creating task. Please try again.", "error")

    return render_template('task_form.html', users=get_users_list(session['user_id']))


@app.route('/tasks/<int:task_id>')
@auth_required
def task_details(task_id):
    # Ownership / existence check is the service's responsibility.
    task = service_get_task_or_404(task_id)
    resources = get_resources_by_task(task_id)
    return render_template('task_details.html', task=task, resources=resources)


@app.route('/tasks/<int:task_id>/complete', methods=['POST'])
@auth_required
def complete_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)
    try:
        service_complete_task(user_id, task_id)
        flash("Task completed successfully!", "success")
    except LookupError:
        flash("Task not found.", "error")
        return redirect(url_for('tasks'))
    except PermissionError as e:
        flash(str(e), "error")
    except Exception as e:
        current_app.logger.error("Error completing task %s: %s", task_id, e)
        flash("Error completing task. Please try again.", "error")

    return redirect(url_for('task_details', task_id=task_id))


@app.route('/tasks/<int:task_id>/delay', methods=['POST'])
@auth_required
def submit_delay(task_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)

    reason     = request.form.get('reason', '').strip()
    proof_file = request.files.get('proof')

    if not reason:
        flash("A reason is required.", "warning")
        return redirect(url_for('task_details', task_id=task_id))

    file_error = _validate_proof_file(proof_file)
    if file_error:
        flash(file_error, "error")
        return redirect(url_for('task_details', task_id=task_id))

    try:
        result = service_submit_delay(
            user_id    = user_id,
            task_id    = task_id,
            reason     = reason,
            proof_file = proof_file,
        )
        flash("Excuse submitted successfully!", "success")
        flash(
            f"Score: {result.get('authenticity_score')}% — Risk: {result.get('risk_level')}",
            "info",
        )
        return redirect(url_for('task_details', task_id=task_id))

    except PermissionError as e:
        flash(str(e), "error")
    except LookupError:
        flash("Task not found.", "error")
        return redirect(url_for('tasks'))
    except Exception as e:
        current_app.logger.error("Error submitting delay for task %s: %s", task_id, e)
        flash(f"Error submitting delay: {e}", "error")

    return redirect(url_for('task_details', task_id=task_id))


@app.route('/tasks/<int:task_id>/delete', methods=['POST'])
@auth_required
def delete_task(task_id):
    user_id = session.get('user_id')
    if not user_id:
        abort(401)
    try:
        service_delete_task(user_id, task_id, session.get('user_role', 'employee'))
        flash("Task deleted successfully!", "success")
    except PermissionError as e:
        flash(str(e), "error")
    except LookupError:
        flash("Task not found.", "error")
    except Exception as e:
        current_app.logger.error("Error deleting task %s: %s", task_id, e)
        flash("Error deleting task. Please try again.", "error")

    return redirect(url_for('tasks'))
