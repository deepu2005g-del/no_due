"""
Approval model - handles per-department approval operations.
"""
from models import query_db


def create_approvals_for_request(request_id: int) -> list:
    """Create pending approval records for all departments for a request."""
    return query_db(
        """INSERT INTO approvals (request_id, department_id, status)
           SELECT %s, d.id, 'pending' FROM departments d
           RETURNING *""",
        (request_id,), commit=True
    )


def get_approvals_for_request(request_id: int) -> list:
    """Get all approvals with department names for a given request."""
    return query_db(
        """SELECT a.*, d.name as department_name, u.name as approver_name
           FROM approvals a
           JOIN departments d ON a.department_id = d.id
           LEFT JOIN users u ON a.approver_id = u.id
           WHERE a.request_id = %s
           ORDER BY d.id""",
        (request_id,)
    )


def update_approval(approval_id: int, status: str, approver_id: int, remarks: str = None) -> dict:
    """Approve or reject a specific department approval."""
    return query_db(
        """UPDATE approvals SET status = %s, approver_id = %s, remarks = %s, updated_at = NOW()
           WHERE id = %s RETURNING *""",
        (status, approver_id, remarks, approval_id), one=True, commit=True
    )


def approve_department(request_id: int, department_id: int, approver_id: int, remarks: str = None) -> dict:
    """Approve a specific department for a request."""
    return query_db(
        """UPDATE approvals SET status = 'approved', approver_id = %s, remarks = %s, updated_at = NOW()
           WHERE request_id = %s AND department_id = %s RETURNING *""",
        (approver_id, remarks, request_id, department_id), one=True, commit=True
    )


def reject_department(request_id: int, department_id: int, approver_id: int, remarks: str = '') -> dict:
    """Reject a specific department for a request."""
    return query_db(
        """UPDATE approvals SET status = 'rejected', approver_id = %s, remarks = %s, updated_at = NOW()
           WHERE request_id = %s AND department_id = %s RETURNING *""",
        (approver_id, remarks, request_id, department_id), one=True, commit=True
    )


def check_all_departments_cleared(request_id: int) -> bool:
    """Check if all departments have approved a request."""
    result = query_db(
        """SELECT 
           COUNT(*) as total,
           COUNT(*) FILTER (WHERE status = 'approved') as approved
           FROM approvals WHERE request_id = %s""",
        (request_id,), one=True
    )
    return result and result['total'] > 0 and result['total'] == result['approved']


def get_approvals_by_department(department_id: int) -> list:
    """Get all pending approvals for a specific department."""
    return query_db(
        """SELECT a.*, r.status as request_status, s.roll_no, u.name as student_name,
           s.department as acad_dept
           FROM approvals a
           JOIN requests r ON a.request_id = r.id
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE a.department_id = %s AND a.status = 'pending' AND r.status = 'faculty_approved'
           ORDER BY r.created_at ASC""",
        (department_id,)
    )


def reset_approvals_for_request(request_id: int):
    """Reset all approvals to pending (for resubmission)."""
    query_db(
        """UPDATE approvals SET status = 'pending', approver_id = NULL, remarks = NULL, updated_at = NOW()
           WHERE request_id = %s""",
        (request_id,), commit=True
    )
