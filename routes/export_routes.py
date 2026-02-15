from flask import session, request, flash, redirect, url_for
from app import app
from utils.flask_auth import auth_required
from services.export_service import generate_csv_report, generate_word_report, generate_pdf_report

@app.route('/export')
@auth_required
def export_report():
    """Generic endpoint for downloading reports in various formats."""
    user_id = session.get('user_id')
    role = session.get('user_role', 'employee')
    
    # Parameters
    report_type = request.args.get('type', 'tasks') # 'tasks' or 'delays'
    fmt = request.args.get('format', 'csv').lower() # 'csv', 'docx', 'pdf'
    
    try:
        if fmt == 'csv':
            return generate_csv_report(user_id=user_id, role=role, type=report_type)
        elif fmt == 'docx' or fmt == 'word':
            return generate_word_report(user_id=user_id, role=role, type=report_type)
        elif fmt == 'pdf':
            return generate_pdf_report(user_id=user_id, role=role, type=report_type)
        else:
            flash(f"Unsupported format: {fmt}", "error")
            return redirect(url_for('dashboard'))
    except Exception as e:
        app.logger.error(f"Export error: {e}")
        flash(f"Failed to generate {fmt.upper()} report", "error")
        return redirect(url_for('dashboard'))

# Legacy route for backward compatibility if needed
@app.route('/export/csv')
@auth_required
def export_csv():
    return redirect(url_for('export_report', format='csv', type=request.args.get('type', 'tasks')))
