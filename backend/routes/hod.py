"""
HOD Routes
Handles final verification and approval.
Supports bulk approval of multiple requests.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.request import get_hod_pending_requests, update_request_status, get_request_by_id
from models.notification import create_notification
from models import query_db

hod_bp = Blueprint('hod', __name__)


@hod_bp.route('/requests', methods=['GET'])
@jwt_required()
def get_requests():
    """Get all requests with all departments cleared, awaiting HOD approval."""
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    requests_list = get_hod_pending_requests()
    return jsonify({'requests': requests_list}), 200


@hod_bp.route('/approve/<int:request_id>', methods=['POST'])
@jwt_required()
def approve_request(request_id):
    """
    Final approval by HOD.
    Body: { action: 'approve' | 'reject', remarks: '...' }
    """
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    data = request.get_json()
    action = data.get('action', '').lower()
    remarks = data.get('remarks', '')

    if action not in ('approve', 'reject'):
        return jsonify({'error': 'Action must be approve or reject'}), 400

    req = get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    if req['status'] != 'departments_cleared':
        return jsonify({'error': 'Request must have all departments cleared first'}), 400

    if action == 'approve':
        update_request_status(request_id, 'hod_approved', remarks)

        # Notify department staff to issue hall ticket
        staff_users = query_db("SELECT id FROM users WHERE role = 'staff'")
        for staff in staff_users:
            create_notification(
                staff['id'],
                f'Request #{request_id} from {req["student_name"]} approved by HOD. Issue hall ticket.'
            )

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(
                student_user['user_id'],
                'Congratulations! Your no-due request has been approved by HOD. Hall ticket will be issued soon.'
            )

        return jsonify({'message': 'Request approved by HOD', 'status': 'hod_approved'}), 200

    else:
        update_request_status(request_id, 'rejected', remarks or 'Rejected by HOD')

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(
                student_user['user_id'],
                f'Your no-due request was rejected by HOD. Reason: {remarks or "Not specified"}'
            )

        return jsonify({'message': 'Request rejected by HOD', 'status': 'rejected'}), 200


@hod_bp.route('/bulk-approve', methods=['POST'])
@jwt_required()
def bulk_approve():
    """
    Bulk approve multiple requests at once.
    Body: { request_ids: [1, 2, 3], remarks: '...' }
    """
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    data = request.get_json()
    request_ids = data.get('request_ids', [])
    remarks = data.get('remarks', 'Bulk approved by HOD')

    if not request_ids:
        return jsonify({'error': 'No request IDs provided'}), 400

    approved = []
    failed = []

    for rid in request_ids:
        req = get_request_by_id(rid)
        if not req or req['status'] != 'departments_cleared':
            failed.append({'id': rid, 'reason': 'Not found or not eligible'})
            continue

        update_request_status(rid, 'hod_approved', remarks)

        # Notify staff
        staff_users = query_db("SELECT id FROM users WHERE role = 'staff'")
        for staff in staff_users:
            create_notification(staff['id'],
                                f'Request #{rid} from {req["student_name"]} approved. Issue hall ticket.')

        # Notify student
        student_user = query_db(
            "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
        )
        if student_user:
            create_notification(student_user['user_id'],
                                'Your no-due request has been approved by HOD!')

        approved.append(rid)

    return jsonify({
        'message': f'{len(approved)} requests approved',
        'approved': approved,
        'failed': failed
    }), 200
