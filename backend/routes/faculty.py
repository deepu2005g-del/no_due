"""
Faculty Routes
Handles viewing assigned students and approving/rejecting requests.
Enforces the 85% attendance rule.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.request import get_pending_faculty_requests, update_request_status, get_request_by_id
from models.approval import approve_department, reject_department
from models.notification import create_notification
from models.department import get_department_by_name
from models import query_db

faculty_bp = Blueprint('faculty', __name__)


@faculty_bp.route('/students', methods=['GET'])
@jwt_required()
def get_students():
    """
    Get all students assigned to this faculty advisor,
    along with their pending requests.
    """
    claims = get_jwt()
    if claims.get('role') != 'faculty':
        return jsonify({'error': 'Faculty access required'}), 403

    faculty_id = int(get_jwt_identity())

    # Get assigned students
    students = query_db(
        """SELECT s.*, u.name, u.email, 
           (SELECT COUNT(*) FROM requests r WHERE r.student_id = s.id AND r.status IN ('pending', 'resubmitted')) as pending_requests
           FROM students s
           JOIN users u ON s.user_id = u.id
           WHERE s.faculty_advisor_id = %s
           ORDER BY s.roll_no""",
        (faculty_id,)
    )

    # Get pending requests
    requests = get_pending_faculty_requests(faculty_id)

    return jsonify({
        'students': students,
        'pending_requests': requests
    }), 200


@faculty_bp.route('/approve/<int:request_id>', methods=['POST'])
@jwt_required()
def approve_request(request_id):
    """
    Approve or reject a student's no-due request.
    Body: { action: 'approve' | 'reject', remarks: '...' }
    
    Business rule: Attendance must be >= 85% for approval.
    """
    claims = get_jwt()
    if claims.get('role') != 'faculty':
        return jsonify({'error': 'Faculty access required'}), 403

    faculty_id = int(get_jwt_identity())
    data = request.get_json()
    action = data.get('action', '').lower()
    remarks = data.get('remarks', '')

    if action not in ('approve', 'reject'):
        return jsonify({'error': 'Action must be approve or reject'}), 400

    req = get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    if req['status'] not in ('pending', 'resubmitted'):
        return jsonify({'error': f'Cannot process request with status: {req["status"]}'}), 400

    # Get Faculty department
    faculty_dept = get_department_by_name('Faculty')

    if action == 'approve':
        # Enforce attendance rule
        if float(req['attendance_pct']) < 85:
            return jsonify({
                'error': f'Cannot approve: Student attendance is {req["attendance_pct"]}% (minimum 85% required)',
                'attendance': float(req['attendance_pct'])
            }), 400

        # Approve faculty department
        approve_department(request_id, faculty_dept['id'], faculty_id,
                           remarks or f'Attendance verified: {req["attendance_pct"]}%')

        # Update request status to faculty_approved
        update_request_status(request_id, 'faculty_approved', remarks)

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(
                student_user['user_id'],
                f'Your no-due request has been approved by Faculty. Now pending department clearance.'
            )

        # Notify admin
        admins = query_db("SELECT id FROM users WHERE role = 'admin'")
        for admin in admins:
            create_notification(
                admin['id'],
                f'Request #{request_id} from {req["student_name"]} needs department clearance.'
            )

        return jsonify({'message': 'Request approved by faculty', 'status': 'faculty_approved'}), 200

    else:
        # Reject
        reject_department(request_id, faculty_dept['id'], faculty_id, remarks)
        update_request_status(request_id, 'rejected', remarks or 'Rejected by faculty')

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(
                student_user['user_id'],
                f'Your no-due request has been rejected by Faculty. Reason: {remarks or "No reason provided"}'
            )

        return jsonify({'message': 'Request rejected by faculty', 'status': 'rejected'}), 200
