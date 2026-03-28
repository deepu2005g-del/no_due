"""
Analytics Routes
Provides statistics and insights for the analytics dashboard.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt
from models import query_db

analytics_bp = Blueprint('analytics', __name__)


@analytics_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """
    Get system-wide analytics:
    - Total requests by status
    - Average processing time
    - Department-wise approval stats
    - Recent activity
    """
    claims = get_jwt()
    if claims.get('role') not in ('admin', 'hod'):
        return jsonify({'error': 'Admin or HOD access required'}), 403

    # Request counts by status
    status_counts = query_db(
        """SELECT status, COUNT(*) as count
           FROM requests GROUP BY status ORDER BY count DESC"""
    )

    # Total counts
    totals = query_db(
        """SELECT 
           COUNT(*) as total_requests,
           COUNT(*) FILTER (WHERE status = 'hod_approved') as approved,
           COUNT(*) FILTER (WHERE status = 'rejected') as rejected,
           COUNT(*) FILTER (WHERE status NOT IN ('hod_approved', 'rejected')) as in_progress
           FROM requests""",
        one=True
    )

    # Average processing time (from creation to HOD approval)
    avg_time = query_db(
        """SELECT AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 3600) as avg_hours
           FROM requests WHERE status = 'hod_approved'""",
        one=True
    )

    # Department-wise approval stats
    dept_stats = query_db(
        """SELECT d.name as department, 
           COUNT(*) as total,
           COUNT(*) FILTER (WHERE a.status = 'approved') as approved,
           COUNT(*) FILTER (WHERE a.status = 'rejected') as rejected,
           COUNT(*) FILTER (WHERE a.status = 'pending') as pending
           FROM approvals a
           JOIN departments d ON a.department_id = d.id
           GROUP BY d.name ORDER BY d.name"""
    )

    # Recent activity (last 10 status changes)
    recent = query_db(
        """SELECT r.id, r.status, r.updated_at, u.name as student_name, s.roll_no
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           ORDER BY r.updated_at DESC LIMIT 10"""
    )

    # Students with low attendance
    flagged_students = query_db(
        """SELECT s.roll_no, u.name, s.department, s.attendance_pct
           FROM students s JOIN users u ON s.user_id = u.id
           WHERE s.attendance_pct < 85
           ORDER BY s.attendance_pct ASC"""
    )

    return jsonify({
        'status_counts': status_counts,
        'totals': totals,
        'avg_processing_hours': round(avg_time['avg_hours'], 1) if avg_time and avg_time['avg_hours'] else 0,
        'department_stats': dept_stats,
        'recent_activity': recent,
        'flagged_students': flagged_students
    }), 200
