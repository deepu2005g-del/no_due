"""
Student Routes
Handles no-due request submission, status tracking, and resubmission.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.request import create_request, get_requests_by_student, get_request_by_id, update_request_status
from models.approval import create_approvals_for_request, get_approvals_for_request, reset_approvals_for_request
from models.notification import create_notification
from models import query_db

student_bp = Blueprint('student', __name__)


def get_student_record(user_id: int):
    """Helper: get the student record for a user."""
    return query_db(
        "SELECT * FROM students WHERE user_id = %s", (user_id,), one=True
    )


@student_bp.route('/request', methods=['POST'])
@jwt_required()
def submit_request():
    """
    Submit a new no-due clearance request.
    Auto-creates pending approvals for all departments.
    Auto-flags students with attendance < 85%.
    """
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({'error': 'Only students can submit requests'}), 403

    user_id = int(get_jwt_identity())
    student = get_student_record(user_id)
    if not student:
        return jsonify({'error': 'Student record not found'}), 404

    # Check for existing active request
    existing = query_db(
        """SELECT id FROM requests WHERE student_id = %s 
           AND status NOT IN ('rejected', 'hod_approved')""",
        (student['id'],), one=True
    )
    if existing:
        return jsonify({'error': 'You already have an active request', 'request_id': existing['id']}), 409

    # Create request
    req = create_request(student['id'])

    # Create approval entries for all departments
    create_approvals_for_request(req['id'])

    # Auto-flag if attendance < 85%
    warning = None
    if student['attendance_pct'] < 85:
        warning = f"Warning: Your attendance is {student['attendance_pct']}% (below 85% threshold). Faculty may reject your request."

    # Notify assigned faculty
    if student.get('faculty_advisor_id'):
        create_notification(
            student['faculty_advisor_id'],
            f"New no-due request from {claims.get('name', 'Student')} (Roll: {student['roll_no']})"
        )

    return jsonify({
        'message': 'No-due request submitted successfully',
        'request': req,
        'warning': warning
    }), 201


@student_bp.route('/status', methods=['GET'])
@jwt_required()
def get_status():
    """
    Get all requests and their per-department approval status.
    Returns a pipeline view of the clearance workflow.
    """
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({'error': 'Only students can view their status'}), 403

    user_id = int(get_jwt_identity())
    student = get_student_record(user_id)
    if not student:
        return jsonify({'error': 'Student record not found'}), 404

    requests = get_requests_by_student(student['id'])

    # Enrich each request with approval details
    result = []
    for req in requests:
        approvals = get_approvals_for_request(req['id'])
        result.append({
            **req,
            'approvals': approvals,
            'student': {
                'roll_no': student['roll_no'],
                'department': student['department'],
                'semester': student['semester'],
                'attendance_pct': float(student['attendance_pct'])
            }
        })

    return jsonify({'requests': result}), 200


@student_bp.route('/resubmit/<int:request_id>', methods=['POST'])
@jwt_required()
def resubmit(request_id):
    """
    Resubmit a rejected request.
    Resets all approvals back to pending.
    """
    claims = get_jwt()
    if claims.get('role') != 'student':
        return jsonify({'error': 'Only students can resubmit'}), 403

    user_id = int(get_jwt_identity())
    student = get_student_record(user_id)

    req = get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    # Verify ownership
    if req['student_id'] != student['id']:
        return jsonify({'error': 'Unauthorized'}), 403

    if req['status'] != 'rejected':
        return jsonify({'error': 'Only rejected requests can be resubmitted'}), 400

    # Reset approvals and update status
    reset_approvals_for_request(request_id)
    updated = update_request_status(request_id, 'resubmitted')

    # Notify faculty
    if student.get('faculty_advisor_id'):
        create_notification(
            student['faculty_advisor_id'],
            f"Resubmitted no-due request from {claims.get('name', 'Student')} (Roll: {student['roll_no']})"
        )

    return jsonify({
        'message': 'Request resubmitted successfully',
        'request': updated
    }), 200
