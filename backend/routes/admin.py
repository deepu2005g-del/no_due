"""
Admin Routes
Handles department clearance (Library, Hostel, Accounts).
Admin can approve/reject per-department for each request.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.request import get_department_pending_requests, get_request_by_id, update_request_status, get_all_requests
from models.approval import (approve_department, reject_department,
                              check_all_departments_cleared, get_approvals_for_request,
                              get_approvals_by_department)
from models.notification import create_notification
from models.department import get_all_departments
from models import query_db

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    """
    Get all requests that need department clearance.
    Optionally filter by department_id query parameter.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    dept_id = request.args.get('department_id', type=int)

    if dept_id:
        # Get pending approvals for a specific department
        approvals = get_approvals_by_department(dept_id)
        return jsonify({'approvals': approvals}), 200
    else:
        # Get all faculty-approved requests needing department clearance
        requests_list = get_department_pending_requests()
        # Enrich with approval details
        result = []
        for req in requests_list:
            approvals = get_approvals_for_request(req['id'])
            result.append({**req, 'approvals': approvals})
        return jsonify({'requests': result}), 200


@admin_bp.route('/all-requests', methods=['GET'])
@jwt_required()
def get_all():
    """Get all requests regardless of status (for monitoring)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    all_reqs = get_all_requests()
    result = []
    for req in all_reqs:
        approvals = get_approvals_for_request(req['id'])
        result.append({**req, 'approvals': approvals})
    return jsonify({'requests': result}), 200


@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
def get_departments():
    """Get all departments."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    departments = get_all_departments()
    return jsonify({'departments': departments}), 200


@admin_bp.route('/approve/<int:request_id>', methods=['POST'])
@jwt_required()
def approve_request(request_id):
    """
    Approve or reject a department clearance.
    Body: { department_id, action: 'approve' | 'reject', remarks: '...' }
    
    If all departments are cleared after this approval, auto-updates request status.
    """
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403

    admin_id = int(get_jwt_identity())
    data = request.get_json()

    department_id = data.get('department_id')
    action = data.get('action', '').lower()
    remarks = data.get('remarks', '')

    if not department_id:
        return jsonify({'error': 'department_id is required'}), 400
    if action not in ('approve', 'reject'):
        return jsonify({'error': 'Action must be approve or reject'}), 400

    req = get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    if req['status'] != 'faculty_approved':
        return jsonify({'error': f'Request is not in faculty_approved status'}), 400

    if action == 'approve':
        approve_department(request_id, department_id, admin_id, remarks)

        # Check if ALL departments are now cleared
        if check_all_departments_cleared(request_id):
            update_request_status(request_id, 'departments_cleared')

            # Notify HOD
            hods = query_db("SELECT id FROM users WHERE role = 'hod'")
            for hod in hods:
                create_notification(
                    hod['id'],
                    f'All departments cleared for request #{request_id} from {req["student_name"]}. Ready for final approval.'
                )

            # Notify student
            student_user = query_db(
                "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
            )
            if student_user:
                create_notification(
                    student_user['user_id'],
                    'All departments have cleared your no-due request. Awaiting HOD approval.'
                )

        return jsonify({
            'message': 'Department clearance approved',
            'all_cleared': check_all_departments_cleared(request_id)
        }), 200

    else:
        reject_department(request_id, department_id, admin_id, remarks)
        update_request_status(request_id, 'rejected', f'Rejected by department. {remarks}')

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(
                student_user['user_id'],
                f'Your no-due request was rejected. Reason: {remarks or "Pending dues"}'
            )

        return jsonify({'message': 'Department clearance rejected'}), 200


@admin_bp.route('/users', methods=['GET'])
@jwt_required()
def get_users():
    """Get all users (Admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    users = query_db("SELECT id, name, email, role, is_active, created_at FROM users ORDER BY created_at DESC")
    return jsonify({'users': users}), 200


@admin_bp.route('/users/<int:user_id>', methods=['DELETE'])
@jwt_required()
def delete_user(user_id):
    """Delete a user (Admin only)."""
    claims = get_jwt()
    if claims.get('role') != 'admin':
        return jsonify({'error': 'Admin access required'}), 403
    
    # Don't delete self
    current_user_id = int(get_jwt_identity())
    if user_id == current_user_id:
        return jsonify({'error': 'Cannot delete your own admin account'}), 400
    
    query_db("DELETE FROM users WHERE id = %s", (user_id,), commit=True)
    return jsonify({'message': 'User deleted successfully'}), 200
