import re
import logging

from repository.users_repo import (
    get_all_users,
    update_user,
    get_user_by_id,
    get_user_by_email,
    create_user,
    soft_delete_user,
)
from utils.hashing import hash_password
from services.activity_service import log_activity

logger = logging.getLogger(__name__)

_EMAIL_RE      = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
_MIN_PW_LENGTH = 8
_VALID_ROLES   = {'admin', 'manager', 'employee'}


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------

def _get_actor_or_raise(actor_id: int) -> dict:
    """Return the actor dict if they are active, else raise PermissionError."""
    actor = get_user_by_id(actor_id)
    if not actor or not actor.get('active_status', True):
        raise PermissionError("Account inactive or not found")
    return actor


def _require_admin(actor_id: int) -> None:
    """Raise PermissionError if the actor is not an active admin."""
    actor = _get_actor_or_raise(actor_id)
    if actor.get('role') != 'admin':
        raise PermissionError("Admin privileges required")


def _require_manager(actor_id: int) -> None:
    """Raise PermissionError if the actor is not a manager or admin."""
    actor = _get_actor_or_raise(actor_id)
    if actor.get('role') not in ('admin', 'manager'):
        raise PermissionError("Manager/Admin privileges required")


def _validate_user_fields(
    full_name: str,
    email: str,
    role: str,
    password: str | None = None,
) -> list[str]:
    """Return a list of validation error messages (empty if all valid)."""
    errors = []

    if not full_name or not full_name.strip():
        errors.append("Full name is required")

    if not email or not _EMAIL_RE.match(email.strip()):
        errors.append("A valid email address is required")

    if role not in _VALID_ROLES:
        errors.append(f"Role must be one of: {', '.join(sorted(_VALID_ROLES))}")

    if password is not None and len(password) < _MIN_PW_LENGTH:
        errors.append(f"Password must be at least {_MIN_PW_LENGTH} characters")

    return errors


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def get_users_list(actor_id: int) -> list[dict]:
    """
    Return all users. Requires the actor to be an admin or manager.
    Note: Managers need this list to assign tasks.
    """
    _require_manager(actor_id)
    return get_all_users()


def manage_create_user(
    actor_id: int,
    full_name: str,
    email: str,
    password: str,
    role: str,
) -> tuple[bool, str]:
    """Create a new user. Actor must be an admin."""
    try:
        _require_admin(actor_id)
    except PermissionError as e:
        return False, str(e)

    email = email.strip()
    errors = _validate_user_fields(full_name, email, role, password)
    if errors:
        return False, "; ".join(errors)

    if get_user_by_email(email):
        return False, "An account with this email already exists"

    try:
        create_user(full_name.strip(), email, hash_password(password), role)
        log_activity(actor_id, "CREATE_USER", f"Created user {email} role={role}")
        return True, "User created successfully"
    except Exception as e:
        logger.error("manage_create_user failed for email=%s: %s", email, e)
        return False, "User creation failed. Please try again."


def manage_update_user(
    actor_id: int,
    target_user_id: int,
    full_name: str,
    email: str,
    role: str,
    active_status: bool,
) -> tuple[bool, str]:
    """Update an existing user's details. Actor must be an admin."""
    try:
        _require_admin(actor_id)
    except PermissionError as e:
        return False, str(e)

    email = email.strip()
    errors = _validate_user_fields(full_name, email, role)
    if errors:
        return False, "; ".join(errors)

    existing = get_user_by_email(email)
    if existing and existing['id'] != target_user_id:
        return False, "Email is already in use by another account"

    try:
        update_user(target_user_id, full_name.strip(), email, role, active_status)
        log_activity(
            actor_id, "UPDATE_USER",
            f"Updated user_id={target_user_id} email={email} role={role} active={active_status}"
        )
        return True, "User updated successfully"
    except Exception as e:
        logger.error("manage_update_user failed for user_id=%s: %s", target_user_id, e)
        return False, "User update failed. Please try again."


def service_delete_own_account(user_id: int) -> tuple[bool, str]:
    """Soft-delete the requesting user's own account."""
    try:
        soft_delete_user(user_id)
        log_activity(user_id, "DELETE_ACCOUNT", "User deleted their own account")
        return True, "Account deleted successfully"
    except LookupError:
        return False, "Account not found"
    except Exception as e:
        logger.error("service_delete_own_account failed for user_id=%s: %s", user_id, e)
        return False, "Account deletion failed. Please try again."
