"""
Request model - handles no-due request operations.
"""
from models import query_db


def create_request(student_id: int) -> dict:
    """Create a new no-due request for a student."""
    return query_db(
        """INSERT INTO requests (student_id, status)
           VALUES (%s, 'pending')
           RETURNING *""",
        (student_id,), one=True, commit=True
    )


def get_request_by_id(request_id: int) -> dict:
    """Get a single request by ID with student info."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, s.attendance_pct, u.name as student_name
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE r.id = %s""",
        (request_id,), one=True
    )


def get_requests_by_student(student_id: int) -> list:
    """Get all requests for a student."""
    return query_db(
        """SELECT r.*, 
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id AND a.status = 'approved') as approved_count,
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id) as total_departments
           FROM requests r WHERE r.student_id = %s
           ORDER BY r.created_at DESC""",
        (student_id,)
    )


def get_requests_by_status(status: str) -> list:
    """Get all requests with a specific status."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, s.attendance_pct, u.name as student_name
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE r.status = %s
           ORDER BY r.created_at DESC""",
        (status,)
    )


def get_all_requests() -> list:
    """Get all requests with student info."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, s.attendance_pct, u.name as student_name,
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id AND a.status = 'approved') as approved_count,
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id) as total_departments
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           ORDER BY r.created_at DESC"""
    )


def update_request_status(request_id: int, status: str, remarks: str = None) -> dict:
    """Update the status of a request."""
    return query_db(
        """UPDATE requests SET status = %s, remarks = %s, updated_at = NOW()
           WHERE id = %s RETURNING *""",
        (status, remarks, request_id), one=True, commit=True
    )


def get_pending_faculty_requests(faculty_id: int) -> list:
    """Get pending requests for students assigned to a faculty member."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, s.attendance_pct, s.semester, u.name as student_name
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE s.faculty_advisor_id = %s AND r.status IN ('pending', 'resubmitted')
           ORDER BY r.created_at DESC""",
        (faculty_id,)
    )


def get_department_pending_requests() -> list:
    """Get requests that are faculty_approved and need department clearance."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department as acad_dept, s.attendance_pct, u.name as student_name,
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id AND a.status = 'approved') as approved_count,
           (SELECT COUNT(*) FROM approvals a WHERE a.request_id = r.id) as total_departments
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE r.status = 'faculty_approved'
           ORDER BY r.created_at ASC"""
    )


def get_hod_pending_requests() -> list:
    """Get requests where all departments have cleared."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, s.attendance_pct, u.name as student_name
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           WHERE r.status = 'departments_cleared'
           ORDER BY r.created_at ASC"""
    )


def get_approved_requests() -> list:
    """Get HOD-approved requests (ready for hall ticket)."""
    return query_db(
        """SELECT r.*, s.roll_no, s.department, u.name as student_name,
           ht.ticket_number, ht.issued_at
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           LEFT JOIN hall_tickets ht ON ht.request_id = r.id
           WHERE r.status = 'hod_approved'
           ORDER BY r.updated_at DESC"""
    )
