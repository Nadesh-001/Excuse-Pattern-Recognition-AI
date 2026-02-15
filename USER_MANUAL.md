# Excuse Pattern Recognition AI - User Manual

## Table of Contents
1. [Overview](#overview)
2. [Getting Started](#getting-started)
3. [User Roles](#user-roles)
4. [Features by Role](#features-by-role)
5. [Detailed Feature Guide](#detailed-feature-guide)
6. [Dark Mode](#dark-mode)
7. [FAQ](#faq)

---

## Overview

*Excuse Pattern Recognition AI* is an intelligent task management and delay analysis system powered by AI. The system helps organizations:

- ✅ Assign and track tasks efficiently
- 🤖 Analyze delay reasons using AI
- 📊 Monitor team performance and patterns
- ⏱️ Track time spent on tasks
- 🎯 Identify genuine vs suspicious delay patterns

### Key Technologies
- *Web Framework*: Flask (Python web framework)
- *AI Analysis*: Groq AI for intelligent delay pattern recognition
- *Data Storage*: TiDB (MySQL) Database
- *Authentication*: Session-based with RBAC decorators
- *Multi-role Access*: Employee, Manager, and Admin roles

---

## Getting Started

### First Time Login

1. *Access the Application*
   - Open your browser and navigate to: http://localhost:5000
   - You'll see the login page

2. *Default Admin Credentials*
   - Email: admin@example.com
   - Password: admin123
   - ⚠️ *Important*: Change the password after first login

3. *Navigation*
   - Use the navigation bar to access different sections
   - Dashboard, Tasks, Analytics, Chatbot, and more
   - Admin panel for administrators

---

## User Roles

The system has three distinct roles with different permissions:

### 👤 Employee
*Access Level*: Basic
- View assigned tasks
- Submit delay reports
- Chat with AI for excuse validation
- View personal analytics
- Export personal reports

### 👔 Manager
*Access Level*: Team Management
- All Employee features
- Create and assign tasks to employees
- View team analytics
- Monitor employee performance
- Track task timers
- View employee profiles
- Export team reports

### 👑 Admin
*Access Level*: Full System Control
- All Manager features
- Create and manage users (Employees, Managers, Admins)
- View system-wide analytics
- Access all tasks and delays
- View activity logs
- Full data export capabilities

---

## Features by Role

### 👤 Employee Dashboard

#### 1. *My Tasks*
View all tasks assigned to you with:
- Task title and description
- Priority level (High/Medium/Low)
- Deadline and overdue warnings
- Status tracking

#### 2. *Submit Delay*
When a task is delayed:
1. Click "⏰ Submit Delay" on the task
2. Provide detailed reason
3. AI analyzes authenticity (0-100%)
4. Categorizes delay type
5. Assigns risk level
6. Provides recommendations

*AI Analysis Includes:*
- *Authenticity Score*: Composite score (0-100%) based on text quality, history, context, proof, and timing.
- *Risk Level*: Low (>=75%), Medium (>=45%), or High (<45%).
- *Signal Breakdown*: Individual scores for excuse quality, delay history, task priority, and submission timing.
- *AI Neural Sync*: Optional AI-powered verification signal merged into the final score.
- *Pattern Recognition*: Detection of repeated excuses and avoidance behaviors.

#### 3. *Chat with AI*
Real-time AI assistant to:
- Validate excuses before submission
- Get feedback on delay reasons
- Receive suggestions for better explanations

#### 4. *My Analytics*
Personal performance metrics:
- Total tasks assigned
- Completion rate
- Delay submissions
- Average authenticity score
- Pattern analysis

---

### 👔 Manager Dashboard

#### 1. *Team Analytics*
Comprehensive team overview:
- Total tasks created
- Delayed tasks count
- Team average authenticity score
- Risk distribution charts
- Category analysis
- Employee performance comparison
- Timeline trends

#### 2. *All Team Tasks*
View and filter all tasks:
- *Filters*: Status, Priority, Search
- *Timer Tracking*: See time estimates and elapsed time
- *Task Details*: Full information for each task

*⏱️ Timer Features*:
Each task with estimated time shows:
- *Estimated Time*: Allocated duration (e.g., 2h 30m)
- *Elapsed Time*: Time since creation (e.g., 1h 45m)
- *Status Indicator*:
  - ⏳ *X remaining* (Blue) - On track
  - 🔴 *Over by X* (Red) - Running late
  - ✅ *Completed on time* (Green) - Finished successfully
  - ⚠️ *Completed over time* (Yellow) - Done but late

#### 3. *Employee Profiles*
View detailed employee information:
- Active/Inactive status
- Tasks assigned
- Delay submissions
- Performance metrics
- Recent activity
- Risk levels
- *Task Management*: Delete employee tasks

#### 4. *Create Task*
Assign new tasks with:
- Task title and description
- Employee assignment (employees only, not other managers)
- Priority level
- Deadline
- *⏱️ Estimated Time*: Set hours and minutes
- *📎 Resources*: Attach Google Docs, Sheets, Forms, or external links

*Time Estimation*:
- Set completion time estimate
- Helps track if tasks finish on time
- Provides accountability

#### 5. *Export Reports*
Download data as CSV:
- All tasks report
- All delays report
- Combined comprehensive report

---

### 👑 Admin Panel

#### 1. *User Management*
Complete user control:
- Create new users (Employee/Manager/Admin)
- Edit user details
- Activate/Deactivate accounts
- View all users with filters
- Search functionality

*Create User Process*:
1. Click "Add New User"
2. Enter name, email, password
3. Select role
4. Set active status
5. User receives credentials

#### 2. *System Analytics*
Full system overview:
- Total users by role
- Active users count
- Total tasks
- Total delays
- System-wide patterns

#### 3. *System Diagnosis*
Run health checks on critical components:
- *Database*: Verifies connection pool and query health
- *AI Services*: Checks API key validity for Groq/Gemini
- *Filesystem*: Verifies upload directory permissions
- *Environment*: Shows current OS and Python environment details


#### 3. *All Tasks & Delays*
Access to all data:
- View all tasks across organization
- Monitor all delay submissions
- Filter and search capabilities

#### 4. *Recent Activity Logs*
Audit trail showing:
- User actions
- Timestamps
- Activity types
- Last 20 activities

---

## Detailed Feature Guide

### AI Delay Analysis

#### Scoring Signals (Weights)
- **Excuse Text Quality (30%)**: Analyzes length, detail, and usage of generic phrases.
- **Delay History (20%)**: Higher penalties for frequent prior delays.
- **Task Context (20%)**: Higher urgency for high-priority tasks near deadlines.
- **Proof Attachment (15%)**: Bonus score for providing supporting evidence.
- **Timing (15%)**: Penalty for submissions made after the official deadline.

#### Risk Classifications
- 🟢 *Low (75-100%)*: Genuine, acceptable delay.
- 🟡 *Medium (45-74%)*: Requires managerial attention.
- 🔴 *High (0-44%)*: Suspicious pattern, needs investigation.

---

### Task Timer System

*For Managers*: Track task progress in real-time

#### How It Works:
1. *Create Task*: Set estimated time (e.g., 2h 30m)
2. *Timer Starts*: Begins counting from creation
3. *Monitor Progress*: View in "All Team Tasks"
4. *Track Completion*: See if task finished on time

#### Timer Display:

⏱️ Estimated    ⏰ Elapsed    📊 Status
   2h 30m         1h 45m      ⏳ 45m remaining


#### Status Types:
- *On Track*: Time remaining shown
- *Overtime*: How much over estimate
- *Completed on Time*: Finished within estimate
- *Completed Over Time*: Finished but exceeded estimate

---

### Dark Mode

Toggle between light and dark themes:

*Activation*:
1. Look for theme toggle in sidebar
2. Click "🌙 Dark Mode" or "☀️ Light Mode"
3. Entire interface switches instantly

*Features*:
- Auto-adjusts all colors
- High contrast for readability
- Preserves role-specific colors
- Reduces eye strain

*Areas Covered*:
- Login page
- Dashboards
- Forms
- Tables
- Charts
- Task cards
- Modals

---

### Resource Attachment

Attach helpful resources to tasks:

*Supported Types*:
- 📄 Google Docs
- 📊 Google Sheets
- 📋 Google Forms
- 📄 Microsoft Word (external links)
- 📊 Microsoft Excel (external links)
- 🔗 Any external link

*How to Attach*:
1. When creating a task, find "📎 Attach Resources"
2. Paste URL
3. Add optional custom title
4. Resource appears in task details

---

### Export Functionality

Download data for offline analysis:

*Available Reports*:
1. *Tasks Report*: All task data
2. *Delays Report*: All delay submissions with AI analysis
3. *Combined Report*: Tasks + Delays merged

*Format*: CSV (Excel compatible)

*Data Included*:
- All relevant fields
- Timestamps
- AI analysis results
- User information

---

## Common Workflows

### As an Employee

#### Workflow 1: Complete a Task
1. Login to Employee Dashboard
2. View "My Tasks"
3. Click "View Details" on task
4. Complete the work
5. If delayed, click "Submit Delay"

#### Workflow 2: Submit Delay
1. Find overdue task
2. Click "⏰ Submit Delay"
3. Write detailed reason
4. Submit for AI analysis
5. Review AI feedback
6. Adjust behavior based on recommendations

---

### As a Manager

#### Workflow 1: Create a Task
1. Go to "Create Task" tab
2. Fill task details
3. Set estimated time
4. Assign to employee
5. Attach resources if needed
6. Submit

#### Workflow 2: Monitor Team
1. Check "Team Analytics" for overview
2. View "All Team Tasks" for details
3. Monitor timer status
4. Check "Employee Profiles" for individual performance
5. Export reports for presentations

#### Workflow 3: Track Task Progress
1. Go to "All Team Tasks"
2. Look at timer section
3. Identify overdue tasks (🔴 red status)
4. Identify on-track tasks (⏳ blue status)
5. Take action on concerning patterns

---

### As an Admin

#### Workflow 1: Create New User
1. Go to "User Management"
2. Click "Add New User"
3. Enter details
4. Select appropriate role
5. Activate user
6. Share credentials

#### Workflow 2: Monitor System
1. Check "System Analytics"
2. Review "Recent Activity Logs"
3. Investigate suspicious patterns
4. View all tasks and delays
5. Export comprehensive reports

---

## Dark Mode

### Enabling Dark Mode
- Located in sidebar: Click "🌙 Dark Mode"
- Toggle anytime during session
- Preference saved per session

### Dark Mode Features
- All UI elements adapt
- High contrast text
- Reduced eye strain
- Maintains color schemes for priorities, statuses
- Works across all pages and roles

---

## FAQ

### General Questions

*Q: How do I reset my password?*
A: Contact your admin for password reset.

*Q: Can I see tasks assigned to other employees?*
A: Only if you're a Manager or Admin.

*Q: How accurate is the AI analysis?*
A: The AI uses advanced language models with 85%+ accuracy.

### For Employees

*Q: Will my manager see my delay reasons?*
A: Yes, managers can view all delay submissions.

*Q: Can I delete a delay submission?*
A: No, all submissions are permanent for audit purposes.

*Q: What if I disagree with the AI authenticity score?*
A: Discuss with your manager; the score is a guide, not final judgment.

### For Managers

*Q: Can I assign tasks to other managers?*
A: No, you can only assign to employees.

*Q: How is elapsed time calculated?*
A: From task creation timestamp to current time.

*Q: Can I edit a task after creation?*
A: Currently, no. Delete and recreate if needed.

*Q: What if an employee consistently has low authenticity scores?*
A: This indicates a pattern. Have a discussion about expectations.

### For Admins

*Q: Can I bulk import users?*
A: Not currently. Add users individually.

*Q: How do I back up data?*
A: Data is stored in the cloud database. Regular exports are recommended.

*Q: Can I deactivate an admin account?*
A: Yes, but ensure at least one admin remains active.

---

## Best Practices

### For Employees
1. ✅ Submit delays as soon as you know
2. ✅ Be honest and detailed in reasons
3. ✅ Use AI chat for validation before submission
4. ✅ Learn from AI feedback
5. ✅ Maintain good authenticity scores

### For Managers
1. ✅ Set realistic time estimates
2. ✅ Monitor timer status regularly
3. ✅ Address overdue patterns quickly
4. ✅ Review employee profiles weekly
5. ✅ Use analytics for team improvements
6. ✅ Attach resources to complex tasks

### For Admins
1. ✅ Review activity logs regularly
2. ✅ Monitor system-wide patterns
3. ✅ Maintain user accounts actively
4. ✅ Export reports for backups
5. ✅ Investigate high-risk patterns

---

## Support

For technical issues or questions:
- Check this manual first
- Review AI_MODELS_GUIDE.md for AI configuration
- Contact your system administrator
- Report bugs with screenshots and error messages

---
Feature Documentation - Excuse Pattern Recognition AI

## Document Overview
This document provides technical and functional details of all features in the Excuse Pattern Recognition AI system.

---

## Table of Contents
1. [System Architecture](#system-architecture)
2. [Authentication & Security](#authentication--security)
3. [Role-Based Access Control](#role-based-access-control)
4. [Core Features](#core-features)
5. [AI Integration](#ai-integration)
6. [Timer & Time Tracking](#timer--time-tracking)
7. [UI/UX Features](#uiux-features)
8. [Data Management](#data-management)
9. [Reporting & Analytics](#reporting--analytics)

---

## System Architecture

### Technology Stack
- *Web Framework*: Flask (Python micro-framework)
- *Backend*: Python 3.8+
- *Database*: MySQL / TiDB Cloud
- *AI Engine*: Groq API (llama-70b model)
- *Authentication*: Flask session-based with decorator guards
- *Templates*: Jinja2 (Flask's templating engine)
- *Charts*: Plotly for interactive visualizations

### Data Flow

```
User Request → Flask Routes → Python Services → MySQL Database
                 ↓
           AI Analysis (Groq)
                 ↓
        Flask Templates (Jinja2)
                 ↓
           HTML Response
```


### Database Structure (Tables)
1. *Users*: User accounts and credentials
2. *Tasks*: Task assignments and tracking
3. *Delays*: Delay submissions and AI analysis
4. *Resources*: Attached files and links
5. *ActivityLogs*: System activity audit trail

---

## Authentication & Security

### Feature: User Login
*Purpose*: Secure access to the system

*Functionality*:
- Email and password authentication
- Password hashing using industry-standard algorithms
- Session management via Streamlit session state
- Role-based redirection after login

*Security Measures*:
- Passwords stored as hashes in Database
- CSRF protection enabled
- Session timeout on browser close
- Role validation on every page load

### Feature: User Session Management
*State Management*:
- User data stored in st.session_state.user
- Includes: name, email, role, active status
- Persists across page refreshes
- Cleared on logout

---

## Role-Based Access Control (RBAC)

### Overview

The system implements a **three-tier role-based access control system** with Flask decorator-based authorization:
- **Employee** - Basic user with task viewing and delay submission
- **Manager** - Team lead with task creation and team monitoring
- **Admin** - Full system administrator with user management

### RBAC Implementation Architecture

#### 1. Session-Based Authentication
- User credentials validated during login via bcrypt password verification.
- User role stored in Flask `session['user_role']`.
- Session persists until explicit logout or browser close.
- Role membership is defined centrally in `utils/flask_auth.py` via `_MANAGER_ROLES` and `_ADMIN_ROLES` sets.

**Session Data:**
- `session['user_id']` - Persistent User ID
- `session['user_role']` - Role (employee/manager/admin)
- `session['user_name']` - Full name
- `session['email']` - User email

#### 2. Decorator-Based Authorization

The system uses two primary decorators from `utils/flask_auth.py`:

**@auth_required**
Checks if `user_id` exists in the session. Redirects to login with a `next` URL parameter to preserve the user's destination.

**@manager_required**
Allows users in `_MANAGER_ROLES` (Managers and Admins). Others are redirected to the dashboard with an error.

**@admin_required**
Allows users in `_ADMIN_ROLES` (Admins only). Others are redirected to the dashboard with an error.

#### 3. Manual Role Validation

For complex permissions, role is checked within route logic:

```python
@app.route('/tasks/new', methods=['GET', 'POST'])
@auth_required
def new_task():
    if session.get('user_role') not in ['manager', 'admin']:
        flash("Unauthorized - Manager privileges required", "error")
        return redirect(url_for('tasks'))
    # Only managers and admins can create tasks
```

#### 4. Data Scope Filtering

Routes filter data based on role:

```python
# Employee sees only own tasks
if user_role == 'employee':
    tasks = get_tasks_by_user(user_id)
else:
    # Manager/Admin sees all tasks
    tasks = get_all_tasks()
```

---

### Complete Permission Matrix

Comprehensive table of all features and role access:

| Feature Category | Feature | Employee | Manager | Admin | Implementation |
|-----------------|---------|----------|---------|-------|----------------|
| **Authentication** | | | | | |
| | Login | ✅ | ✅ | ✅ | Public route |
| | Register | ✅ | ✅ | ✅ | Public route |
| | Logout | ✅ | ✅ | ✅ | @auth_required |
| **Dashboard** | | | | | |
| | View own dashboard | ✅ | ✅ | ✅ | @auth_required |
| | View statistics | ✅ | ✅ | ✅ | @auth_required + role filter |
| **Tasks** | | | | | |
| | View own tasks | ✅ | ✅ | ✅ | @auth_required + scope filter |
| | View all tasks | ❌ | ✅ | ✅ | @auth_required + role check |
| | Create task | ❌ | ✅ | ✅ | @auth_required + role check |
| | Assign task to employee | ❌ | ✅ | ✅ | @auth_required + role check |
| | View task details | ✅ | ✅ | ✅ | @auth_required + ownership check |
| | Complete task | ✅ | ✅ | ✅ | @auth_required + ownership check |
| | Submit delay reason | ✅ | ✅ | ✅ | @auth_required |
| | Attach resources | ❌ | ✅ | ✅ | @auth_required + role check |
| **Analytics** | | | | | |
| | View personal analytics | ✅ | ✅ | ✅ | @auth_required |
| | View team analytics | ❌ | ✅ | ✅ | @auth_required + role filter |
| | View system analytics | ❌ | ❌ | ✅ | @auth_required + role filter |
| | View risk insights | ❌ | ✅ | ✅ | @auth_required + role filter |
| | Export reports | ❌ | ✅ | ✅ | @auth_required + role check |
| **AI Features** | | | | | |
| | Use chatbot | ✅ | ✅ | ✅ | @auth_required |
| | AI delay analysis | ✅ | ✅ | ✅ | @auth_required (automatic) |
| | View AI feedback | ✅ | ✅ | ✅ | @auth_required |
| **User Management** | | | | | |
| | View own profile | ✅ | ✅ | ✅ | @auth_required |
| | Edit own profile | ✅ | ✅ | ✅ | @auth_required |
| | View all users | ❌ | ❌ | ✅ | @admin_required |
| | Create new user | ❌ | ❌ | ✅ | @admin_required |
| | Edit any user | ❌ | ❌ | ✅ | @admin_required |
| | Delete user | ❌ | ❌ | ✅ | @admin_required |
| | Activate/Deactivate user | ❌ | ❌ | ✅ | @admin_required |
| **System** | | | | | |
| | View audit logs | ❌ | ❌ | ✅ | @admin_required |
| | Run system diagnostics | ❌ | ❌ | ✅ | @admin_required |
| | View activity logs | ❌ | ❌ | ✅ | @admin_required (last 50) |
| **Search** | | | | | |
| | Search own tasks/delays | ✅ | ✅ | ✅ | @auth_required + scope filter |
| | Search all data | ❌ | ❌ | ✅ | @auth_required + scope filter |

---

### Flask Route Access Control

Complete list of all routes and their authorization:

| Route | Method | Access Level | Decorator(s) | Role Check | Description |
|-------|--------|-------------|--------------|------------|-------------|
| `/` | GET | Public | - | - | Redirects to login or dashboard |
| `/login` | GET, POST | Public | - | - | User authentication |
| `/register` | GET, POST | Public | - | - | New user registration |
| `/logout` | GET | Authenticated | - | - | Session termination |
| `/dashboard` | GET | Authenticated | @auth_required | - | User dashboard with statistics |
| `/tasks` | GET | Authenticated | @auth_required | Scope filtering | View tasks list |
| `/tasks/new` | GET, POST | Manager+ | @auth_required | Manual check | Create new task |
| `/tasks/<id>` | GET | Authenticated | @auth_required | Ownership | Task details view |
| `/tasks/<id>/complete` | POST | Authenticated | @auth_required | Ownership | Mark task complete |
| `/tasks/<id>/delay` | POST | Authenticated | @auth_required | Ownership | Submit delay reason |
| `/analytics` | GET | Authenticated | @auth_required | Role filtering | Analytics dashboard |
| `/chatbot` | GET | Authenticated | @auth_required | - | AI chatbot interface |
| `/chatbot/api` | POST | Authenticated | Session check | - | AI chat API endpoint |
| `/admin` | GET | Admin only | @admin_required | - | Admin control panel |
| `/admin/users/add` | POST | Admin only | @admin_required | - | Create new user |
| `/admin/users/edit` | POST | Admin only | @admin_required | - | Edit user details |
| `/admin/users/delete/<id>` | POST | Admin only | @admin_required | - | Delete user account |
| `/search` | GET | Authenticated | @auth_required | Scope filtering | Search functionality |

---

### Security Implementation

#### 1. Password Security
```python
# Password Hashing (bcrypt)
from utils.hashing import hash_password, verify_password

# During registration
hashed = hash_password(plain_password)
# Store hashed in database

# During login
if verify_password(plain_password, stored_hash):
    # Authentication successful
```

**Features:**
- Bcrypt algorithm with salt
- Adaptive hashing (cost factor)
- Never store plain text passwords
- One-way hash (cannot be reversed)

#### 2. Session Security
```python
# Flask session configuration
app.secret_key = os.getenv("FLASK_SECRET_KEY")
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True  # HTTPS only
```

**Features:**
- Cryptographically signed cookies
- HTTP-only cookies (no JavaScript access)
- Secure flag for HTTPS
- Server-side session storage

#### 3. Authorization Checks

**Three-Layer Protection:**

1. **Route Level** - Decorators prevent unauthorized access
2. **Logic Level** - Manual role checks in complex scenarios
3. **Data Level** - Database queries filtered by user/role

#### 4. Input Validation
- Email format validation (regex)
- Role validation (enum check)
- SQL injection prevention (parameterized queries)
- XSS protection (Jinja2 auto-escaping)

#### 5. Audit Trail
```python
# Logging security events
from services.activity_service import log_activity

log_activity(user_id, "LOGIN", "User logged in successfully")
log_activity(admin_id, "CREATE_USER", f"Created user {new_email}")
log_activity(admin_id, "DELETE_USER", f"Deleted user {target_email}")
```

All security-relevant actions are logged to `audit_logs` table.

---

### Permission Enforcement Examples

#### Example 1: Employee Viewing Tasks
```python
@app.route('/tasks')
@auth_required
def tasks():
    user_id = session['user_id']
    role = session.get('user_role', 'employee')
    
    # Employee sees only assigned tasks
    if role == 'employee':
        tasks_list = get_tasks_by_user(user_id)
    else:
        # Manager/Admin sees all tasks
        tasks_list = get_all_tasks()
    
    return render_template('tasks.html', tasks=tasks_list, role=role)
```

#### Example 2: Manager Creating Task
```python
@app.route('/tasks/new', methods=['GET', 'POST'])
@auth_required
def new_task():
    # Manual role check
    if session.get('user_role') not in ['manager', 'admin']:
        flash("Unauthorized - Manager privileges required", "error")
        return redirect(url_for('tasks'))
    
    if request.method == 'POST':
        # Only employees can be assigned tasks
        users = get_users_by_role('employee')
        # Create task logic...
    
    return render_template('task_form.html', users=users)
```

#### Example 3: Admin Deleting User
```python
@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    # Prevent self-deletion
    if user_id == session['user_id']:
        flash("Cannot delete yourself", "error")
        return redirect(url_for('admin_panel'))
    
    # Admin-only operation (already checked by decorator)
    # Delete user and cascade related data
    # Log the action
    log_activity(session['user_id'], "DELETE_USER", f"Deleted user ID {user_id}")
    
    return redirect(url_for('admin_panel'))
```

---

### Best Practices

#### For Developers
1. ✅ **Always use decorators** - Never rely solely on client-side checks
2. ✅ **Validate ownership** - Check if user owns the resource
3. ✅ **Filter by role** - Apply scope filtering in queries
4. ✅ **Log security events** - Audit trail for accountability
5. ✅ **Never trust input** - Validate and sanitize all user input
6. ✅ **Use parameterized queries** - Prevent SQL injection
7. ✅ **Check both authentication and authorization** - Auth != Authz

#### For Administrators
1. ✅ **Review audit logs regularly** - Monitor for suspicious activity
2. ✅ **Use strong passwords** - Enforce password policies
3. ✅ **Deactivate unused accounts** - Reduce attack surface
4. ✅ **Limit admin accounts** - Principle of least privilege
5. ✅ **Monitor failed logins** - Detect brute force attempts
6. ✅ **Regular security audits** - Review user access patterns

#### For End Users
1. ✅ **Never share credentials** - Each user should have unique account
2. ✅ **Log out on shared devices** - Prevent session hijacking
3. ✅ **Report suspicious activity** - Inform admin immediately
4. ✅ **Use unique passwords** - Don't reuse across systems
5. ✅ **Verify URLs** - Ensure you're on the correct domain

---

### Troubleshooting RBAC Issues

**Problem:** "Please login to access this page"
- **Cause:** Session expired or not authenticated
- **Solution:** Log in again

**Problem:** "Admin privileges required"
- **Cause:** Trying to access admin route with non-admin account
- **Solution:** Contact admin for role upgrade (if justified)

**Problem:** "Cannot see other users' tasks"
- **Cause:** Employee role has limited scope
- **Solution:** This is intentional - only managers/admins see all tasks

**Problem:** "Task creation option not available"
- **Cause:** Employee role cannot create tasks
- **Solution:** Only managers and admins can create tasks

---

## Core Features

### 1. Task Management

#### Feature: Create Task (Manager/Admin)
*Location*: Manager/Admin Dashboard → Create Task tab

*Form Fields*:
- *Task Title** (required): Short description
- *Description*: Detailed task information
- *Assign To** (required): Employee email dropdown
  - Only shows active employees
  - Excluded: Managers and Admins
- *Priority** (required): Low/Medium/High
- *Deadline** (required): Date picker
- *Estimated Time*: Hours and Minutes
  - Hours: 0-999
  - Minutes: 0-59 (in 15-min increments)
- *Resource URL* (optional): External link
- *Resource Title* (optional): Custom name for resource

*Validation*:
- All required fields checked
- URL validation for resources
- Employee availability check
- Unique task ID generation

*Storage*:
Added to Tasks table with:
- Unique ID
- Creation timestamp
- Status: "Pending" (default)
- Assigned by: Current user email

*Time Estimation Format*:
Stored in description or dedicated column.

#### Feature: View Tasks
*Employee View*:
- Filters tasks by assigned_to_email == user.email
- Shows only own tasks

*Manager View*:
- Shows all tasks in organization
- Filterable by:
  - Status (All/Pending/Completed/Delayed)
  - Priority (All/High/Medium/Low)
  - Search text (title or email)

*Display Components*:
- Task card with colored border (priority-based)
- Title and status badge
- Description preview (150 chars)
- Priority, Deadline, Assigned to
- Timer section (if estimated time exists)
- Action buttons (View Details, Submit Delay)

#### Feature: Task Timer (Manager Only)
*Calculation*:
python
elapsed_time = current_time - task_creation_time
remaining_time = estimated_time - elapsed_time


*Display*:
Three boxes showing:
1. *Estimated Time*: From task creation
2. *Elapsed Time*: Auto-calculated
3. *Status*: Dynamic based on comparison

*Status Logic*:
- Task Pending + Elapsed < Estimated = "⏳ X remaining" (Blue)
- Task Pending + Elapsed > Estimated = "🔴 Over by X" (Red)
- Task Completed + Elapsed ≤ Estimated = "✅ Completed on time" (Green)
- Task Completed + Elapsed > Estimated = "⚠️ Completed over time" (Yellow)

*Time Formatting*:
- Minutes only: "45m"
- Hours + Minutes: "2h 30m"
- Days + Hours + Minutes: "3d 5h 20m"

---

### 2. Delay Management

#### Feature: Submit Delay (Employee)
*Trigger*: Task is overdue (deadline < current date) and status ≠ Completed

*Process*:
1. Click "⏰ Submit Delay" on task card
2. Modal/Form opens
3. Enter detailed reason (text area)
4. Submit for AI analysis
5. AI processes in real-time
6. Results displayed immediately

*AI Analysis Pipeline*:

Reason Text → Groq AI API → JSON Response
    ↓
Parse: authenticity, category, risk, avoidance
    ↓
Store in Delays table
    ↓
Display results to user


*Stored Data*:
- Delay ID (unique)
- Task ID (reference)
- User email
- Reason text
- AI analysis results:
  - Authenticity score (0-100)
  - Category
  - Risk level
  - Avoidance score
  - Recommendations
- Creation timestamp

#### Feature: AI Chat (Employee)
*Purpose*: Pre-validate excuses before submission

*Functionality*:
- Real-time chat interface
- Same AI model as delay analysis
- Provides feedback without storing
- Helps employees improve their explanations

*Use Cases*:
- "Is this reason acceptable?"
- "How can I explain this better?"
- "What category does this fall under?"

---

### 3. User Management (Admin Only)

#### Feature: Create User
*Location*: Admin Panel → User Management → Add New User

*Form Fields*:
- *Name** (required)
- *Email** (required, unique)
- *Password** (required, auto-hashed)
- *Role** (required): Employee/Manager/Admin
- *Active Status*: Checkbox (default: True)

*Validation*:
- Email uniqueness check
- Password strength (minimum 6 characters)
- Role selection validation
- Format validation for email

*Process*:
- SQL UPDATE/INSERT operations
- Check email doesn't exist
- Hash password
- Add to Users table with timestamp
- Log activity

*Post-Creation*:
- User can immediately login
- Appears in user list
- Included in role-specific filters

#### Feature: Edit User
*Editable Fields*:
- Name
- Email (if unique)
- Role
- Active status
- Password (optional)

*Restrictions*:
- Cannot delete own admin account
- Cannot delete the *only* remaining Administrator (Safety Lock)

*Active Status*:
- Toggle users as Active/Inactive
- Inactive users are immediate blocked from logging in
- Useful for offboarding employees without deleting data

#### Feature: View Users
*Display*:
- Filterable by role
- Searchable by name/email
- Shows status (active/inactive)
- Displays last login
- Expandable for details

---

### 4. Analytics & Reporting

#### Feature: Employee Analytics
*Metrics*:
- Total tasks assigned
- Tasks by status (Pending/Completed/Delayed)
- Total delay submissions
- Average authenticity score
- Risk distribution
- Category breakdown

*Visualizations*:
- Pie charts for risk levels
- Bar charts for categories
- Timeline of delays
- Performance trends

#### Feature: Team Analytics (Manager)
*Metrics*:
- Team-wide task count
- Delayed tasks percentage
- Team average authenticity
- Employee comparison
- Pattern identification

*Charts*:
- Risk distribution pie chart
- Category bar chart
- Employee performance comparison
- Timeline trend analysis

#### Feature: System Analytics (Admin)
*Metrics*:
- Total users by role
- Active vs inactive users
- Total tasks across system
- Total delays
- System-wide patterns

*Insights*:
- High-risk users
- Frequent delay categories
- Team performance comparison
- Usage statistics

---

## AI Integration

### AI Model Configuration

*Provider*: Groq
*Model*: openai/gpt-oss-20b
*Settings*:
- Temperature: 0.7 (balanced creativity vs consistency)
- Max Tokens: 2048
- Response Format: JSON

### Feature: Delay Analysis AI

#### Input Processing
python
prompt = f"""
Analyze this delay reason: "{reason_text}"
Task: {task_title}
User: {user_email}

Provide:
1. Authenticity score (0-100)
2. Category
3. Risk level
4. Avoidance score
5. Recommendations
"""


#### Output Format (JSON)
json
{
  "authenticity_score": 75,
  "category": "Technical",
  "risk_level": "Medium",
  "avoidance_score": 35,
  "recommendations": "Verify technical details..."
}


#### Analysis Criteria

*Authenticity Score*:
- Language specificity (vague vs detailed)
- Emotional tone
- Responsibility taking
- Previous submission patterns
- Timing consistency

*Categories*:
1. *Health*: Medical conditions, illness
2. *Personal*: Family, personal emergencies
3. *Technical*: Software, hardware, network issues
4. *External*: Weather, transportation, infrastructure
5. *Workload*: Too many tasks, complexity
6. *Communication*: Requirements unclear, miscommunication
7. *Other*: Doesn't fit above categories

*Risk Levels*:
- *Low*: Authenticity > 70%, taking responsibility
- *Medium*: Authenticity 40-70%, some concerns
- *High*: Authenticity < 40%, suspicious patterns

*Avoidance Score*:
- Measures responsibility avoidance
- Based on language patterns
- High score = external blame, no ownership
- Low score = internal attribution, accountability

---

## Timer & Time Tracking

### Feature: Task Time Estimation

#### Creation
*When*: Task creation by Manager/Admin
*Interface*: Number inputs for hours and minutes

*Storage*:
Embedded in task description or separate column.

*Parsing*:
Regex extraction:
python
time_match = re.search(r'⏱️ Estimated Time:\s*(.+)', description)
hours = re.search(r'(\d+)h', time_str)
minutes = re.search(r'(\d+)m', time_str)


### Feature: Elapsed Time Calculation

#### Real-time Calculation
python
created_at = datetime.strptime(task['created_at'], "%Y-%m-%d %H:%M:%S")
elapsed = datetime.now() - created_at
elapsed_minutes = int(elapsed.total_seconds() / 60)


#### Display Formatting
python
if elapsed_days > 0:
    display = f"{days}d {hours}h {mins}m"
elif elapsed_hours > 0:
    display = f"{hours}h {mins}m"
else:
    display = f"{mins}m"


### Feature: Time Status Indicator

#### Status Determination
python
if status == 'Completed':
    if elapsed <= estimated:
        status = "✅ Completed on time"
    else:
        status = "⚠️ Completed over time"
elif elapsed > estimated:
    overtime = elapsed - estimated
    status = f"🔴 Over by {format_time(overtime)}"
else:
    remaining = estimated - elapsed
    status = f"⏳ {format_time(remaining)} remaining"


#### Color Coding
- *Blue* (#3b82f6): On track, time remaining
- *Red* (#ef4444): Overtime, concerning
- *Green* (#10b981): Completed on time, success
- *Yellow* (#f59e0b): Completed over time, warning

---

## UI/UX Features

### Feature: Dark Mode

#### Toggle Mechanism
*Location*: Sidebar
*State*: Session-based (resets on logout)

*Implementation*:
python
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

if st.button("🌙 Dark Mode" if not st.session_state.dark_mode else "☀️ Light Mode"):
    st.session_state.dark_mode = not st.session_state.dark_mode
    st.rerun()


#### CSS Injection
Conditional stylesheet:
python
if st.session_state.dark_mode:
    st.markdown(dark_mode_css, unsafe_allow_html=True)


#### Styled Elements
- Background colors
- Text colors
- Form elements
- Cards and containers
- Charts and graphs
- Modals and popups
- Sidebar and header
- Tables and data displays

#### Color Scheme
*Dark Mode*:
- Background: #1a1d24
- Cards: #1e222a
- Text: #fafafa
- Borders: #2d3139

*Preserved Colors*:
- Priority indicators (High/Medium/Low)
- Status badges (Pending/Completed/Delayed)
- Risk levels (High/Medium/Low)
- Role theme colors

### Feature: Role-Specific Theming

#### Color Schemes
*Employee* (Blue):
- Primary: #3b82f6
- Background: #dbeafe
- Icon: 👤

*Manager* (Purple):
- Primary: #8b5cf6
- Background: #f5f3ff
- Icon: 👔

*Admin* (Orange):
- Primary: #f59e0b
- Background: #fef3c7
- Icon: 👑

#### Application
- Header gradient
- Sidebar profile card
- Navigation cards
- Metric cards
- Status indicators

### Feature: Responsive Task Cards

#### Structure
html
<div style="border-left: 4px solid {priority_color}">
  Title + Status Badge
  Description Preview
  Priority | Deadline | Assigned To
  Timer Section (if applicable)
  Action Buttons
</div>


#### Interactive Elements
- Expandable details
- Clickable action buttons
- Hover effects
- Status badges
- Priority indicators

---

## Data Management

### Feature: Database Integration

#### Connection
- MySQL / TiDB Cloud
- Credentials from `.env` or `secrets.toml`
- Secure TLS connection

#### Database Operations
*Read*:
python
cursor.execute("SELECT * FROM ...")


*Write*:
python
cursor.execute("INSERT INTO ...")


*Update*:
python
cursor.execute("UPDATE ...")


*Delete*:
python
cursor.execute("DELETE FROM ...")


#### Data Synchronization
- Real-time read on page load
- Immediate write on form submission
- Transaction support (commit/rollback)

### Feature: Activity Logging

#### Logged Actions
- User login/logout
- Task creation
- Task deletion
- Delay submission
- User creation/edit
- Role changes

#### Log Structure

ID | User Email | Action Type | Description | Timestamp
1  | manager@ex | create_task | Created: Review | 2026-01-28 12:00


#### Retention
- Last 50 activities shown
- All activities stored permanently
- Admin-only access

---

## Reporting & Analytics

### Feature: Data Export

#### Export Types
1. *Tasks Report*
   - All task fields
   - Assignment details
   - Time tracking data
   - Resources attached

2. *Delays Report*
   - Delay reasons
   - AI analysis results
   - User information
   - Timestamps

3. *Combined Report*
   - Tasks + Delays merged
   - Full relationship data
   - Comprehensive analysis

#### Format
- CSV (Comma-Separated Values)
- Excel-compatible
- UTF-8 encoding
- Headers included

#### Access Control
- Employee: Own data only
- Manager: Team data
- Admin: All data

---

## Security Features

### 1. Password Security
- Hashing algorithm: Industry-standard
- Salted hashes
- No plaintext storage
- Secure comparison

### 2. Session Security
- Session tokens
- CSRF protection
- XSS prevention
- Secure cookies

### 3. Data Privacy
- Role-based data filtering
- Query-level security
- Audit trail
- Activity logging

### 4. Input Validation
- SQL injection prevention
- XSS filtering
- URL validation
- Email format validation
- Length restrictions

---

## Performance Features

### Optimization Techniques
1. *Lazy Loading*: Load data only when tab is accessed
2. *Caching*: Streamlit's built-in caching (@st.cache_data)
3. *Pagination*: Limit results to recent entries
4. *Efficient Queries*: Filter data at source
5. *Asynchronous AI*: Non-blocking AI calls

### Scalability
- TiDB: Cloud scale SQL
- Streamlit: Handles concurrent users
- AI API: Rate limits via Groq account

---

## Error Handling

### User-Facing Errors
- Clear error messages
- Helpful suggestions
- Retry mechanisms
- Fallback options

### Technical Errors
- Try-catch blocks
- Error logging
- Graceful degradation
- User notification

---

## Future Enhancements

### Planned Features
1. Email notifications
2. WebSocket real-time updates
3. Advanced analytics dashboard
4. Bulk task creation
5. Custom AI training
6. Mobile app
7. Slack/Teams integration
8. Calendar sync
9. Automated task assignment
10. Performance reviews

---

## Technical Requirements

### Minimum Requirements
- Python 3.8+
- Internet connection
- Modern web browser
- Database Connection (TiDB/MySQL)
- Groq API key

### Recommended
- Python 3.10+
- Chrome/Edge browser
- Stable internet (for AI)

---

## API Documentation

### Groq AI API

*Endpoint*: https://api.groq.com/v1/chat/completions

*Headers*:
json
{
  "Authorization": "Bearer {GROQ_API_KEY}",
  "Content-Type": "application/json"
}


*Request*:
json
{
  "model": "openai/gpt-oss-20b",
  "messages": [...],
  "temperature": 0.7,
  "max_tokens": 2048
}


*Response*:
json
{
  "choices": [{
    "message": {
      "content": "{JSON analysis}"
    }
  }]
}


### Database

*Service*: TiDB / MySQL
*Auth*: User/Password/Host/Port/SSL

---


---

## Best Practices: Task Management Checklist

This practical checklist helps you maximize the Excuse Pattern Recognition AI system and minimize delay patterns.

### 10-Step Task Management Framework

| Step | Action | Benefits & App Integration |
|------|--------|---------------------------|
| **1. Capture Everything** | Create a single, searchable task list in the app | Eliminates "lost tasks" excuses. The app surfaces tasks that were added but never opened or completed. |
| **2. Prioritize Clearly** | Use Eisenhower (urgent vs. important) or ABC method (A=must, B=should, C=nice-to-have) | Reduces "didn't know which to tackle first" excuses. The app tags tasks by priority and reminds you of overdue high-priority items. |
| **3. Break Down Big Jobs** | Divide each task into sub-tasks with mini-deadlines | Prevents "too many steps" excuses. The app shows number of sub-tasks left, making next steps obvious. |
| **4. Set Realistic Time Windows** | Estimate effort for each sub-task; add 10-15% buffer | Avoids "ran out of time" excuses. The app tracks actual vs. estimated time, highlighting chronic over-estimation. |
| **5. Automate Reminders** | Use calendar invites, recurring notifications, or app's auto-reminder feature | Stops "I forgot" excuses. The app logs when reminders were triggered and whether tasks were acted on. |
| **6. Review Daily/Weekly** | End of day: tick off completed tasks. End of week: audit why tasks lagged | Turns excuses into data. The app generates "Delay Pattern" reports, highlighting recurring excuse types. |
| **7. Delegate Wisely** | Assign tasks to others with clear ownership and due dates | Removes "couldn't complete it" excuses by sharing responsibility. The app flags unassigned or stuck tasks. |
| **8. Use Excuse Log** | When tasks delay, add brief notes: "Technical hiccup", "Awaiting feedback", etc. | Turns vague excuses into actionable insights. The app aggregates notes, showing most common barriers. |
| **9. Celebrate Small Wins** | Add quick "celebrate" tick or emoji when sub-tasks complete | Positive reinforcement reduces procrastination. The app tracks streaks and completion rates for motivation. |
| **10. Leverage Data** | After 30 days, review app reports: Which excuses appear most? Which tasks are always overdue? | Fine-tunes your workflow. Adjust priorities, deadlines, or processes based on evidence, not assumptions. |

### How the App Supports Each Step

#### Capture (Step 1)
- **Feature**: Centralized task dashboard
- **Benefit**: All tasks visible in one place
- **Excuse Prevention**: No more "I didn't see it" or "It wasn't assigned to me"

#### Prioritize (Step 2)
- **Feature**: Priority tags (High/Medium/Low) with color coding
- **Benefit**: Visual priority hierarchy
- **Excuse Prevention**: Eliminates confusion about task importance

#### Break Down (Step 3)
- **Feature**: Task descriptions with detailed requirements
- **Benefit**: Clear action items and sub-steps
- **Excuse Prevention**: Reduces "task was too complex" excuses

#### Time Windows (Step 4)
- **Feature**: Estimated time tracking with timer display
- **Benefit**: Real-time progress monitoring
- **Excuse Prevention**: Catches time overruns early

#### Reminders (Step 5)
- **Feature**: Deadline tracking with visual indicators
- **Benefit**: Proactive deadline awareness
- **Excuse Prevention**: Eliminates "forgot the deadline" excuses

#### Review (Step 6)
- **Feature**: Analytics dashboard with delay patterns
- **Benefit**: Data-driven insights into performance
- **Excuse Prevention**: Identifies recurring excuse patterns

#### Delegate (Step 7)
- **Feature**: Task assignment with clear ownership
- **Benefit**: Accountability tracking
- **Excuse Prevention**: No ambiguity about responsibility

#### Excuse Log (Step 8)
- **Feature**: AI-powered delay analysis with categorization
- **Benefit**: Structured excuse documentation
- **Excuse Prevention**: Patterns become visible over time

#### Celebrate (Step 9)
- **Feature**: Completion tracking and status updates
- **Benefit**: Visible progress and achievements
- **Excuse Prevention**: Builds momentum and motivation

#### Leverage Data (Step 10)
- **Feature**: Comprehensive reports and export functionality
- **Benefit**: Evidence-based process improvement
- **Excuse Prevention**: Continuous system refinement

### Quick Action Plan for Today

1. **Open the app** and create a new "Backlog" task
2. **Add your current top 3 tasks** with priorities
3. **Set realistic deadlines** (add 15% buffer to your estimates)
4. **Assign each task** a priority (A/B/C or High/Medium/Low)
5. **When you complete a task**, mark it done immediately
6. **At day's end**, use the app's "Weekly Snapshot" to see what tasks lagged and why

### 30-Day Challenge

**Week 1**: Capture all tasks in the app  
**Week 2**: Add time estimates to every task  
**Week 3**: Review delay patterns in Analytics  
**Week 4**: Adjust your workflow based on data

Give it a try and see how the data-feedback loop changes your approach to task management. Happy task-tackling!

---

## Changelog

### Version 1.0 (January 2026)
- Initial release
- Core task management
- AI delay analysis
- Multi-role system
- Dark mode
- Timer tracking
- Export functionality
- User management

### Version 2.0 (February 2026)
- **Production Architecture**: Complete refactoring to N-Tier Design (Services/Repository)
- **System Diagnosis**: Built-in health check tools for Admin
- **Advanced Admin Controls**: User activation/deactivation, Last Admin protection
- **Performance**: Connection pooling and optimized query handling

