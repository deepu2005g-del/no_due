"""
Department Staff Routes
Handles hall ticket generation and download.
"""
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from models.request import get_approved_requests, get_request_by_id
from models.notification import create_notification
from models import query_db

staff_bp = Blueprint('staff', __name__)


@staff_bp.route('/approved', methods=['GET'])
@jwt_required()
def get_approved():
    """Get all HOD-approved requests ready for hall ticket issuance."""
    claims = get_jwt()
    if claims.get('role') != 'staff':
        return jsonify({'error': 'Staff access required'}), 403

    requests_list = get_approved_requests()
    return jsonify({'requests': requests_list}), 200


@staff_bp.route('/hallticket/<int:request_id>', methods=['POST'])
@jwt_required()
def generate_hallticket(request_id):
    """
    Generate a hall ticket for an approved request.
    Creates a unique ticket number and stores it.
    """
    claims = get_jwt()
    if claims.get('role') != 'staff':
        return jsonify({'error': 'Staff access required'}), 403

    staff_id = int(get_jwt_identity())

    req = get_request_by_id(request_id)
    if not req:
        return jsonify({'error': 'Request not found'}), 404

    if req['status'] != 'hod_approved':
        return jsonify({'error': 'Request must be HOD-approved to generate hall ticket'}), 400

    # Check if hall ticket already exists
    existing = query_db(
        "SELECT * FROM hall_tickets WHERE request_id = %s", (request_id,), one=True
    )
    if existing:
        return jsonify({
            'message': 'Hall ticket already generated',
            'hall_ticket': existing
        }), 200

    # Generate unique ticket number
    ticket_number = f"HT-{req['roll_no']}-{uuid.uuid4().hex[:8].upper()}"

    hall_ticket = query_db(
        """INSERT INTO hall_tickets (request_id, issued_by, ticket_number)
           VALUES (%s, %s, %s) RETURNING *""",
        (request_id, staff_id, ticket_number), one=True, commit=True
    )

    # Notify student
    student_user = query_db(
        "SELECT user_id FROM students WHERE id = %s", (req['student_id'],), one=True
    )
    if student_user:
        create_notification(
            student_user['user_id'],
            f'Your hall ticket has been generated! Ticket Number: {ticket_number}'
        )

    return jsonify({
        'message': 'Hall ticket generated successfully',
        'hall_ticket': hall_ticket
    }), 201


@staff_bp.route('/hallticket/<int:request_id>', methods=['GET'])
@jwt_required()
def get_hallticket(request_id):
    """
    Get hall ticket details for a request.
    Returns ticket info with student details for download/print.
    """
    user_id = int(get_jwt_identity())
    claims = get_jwt()

    hall_ticket = query_db(
        """SELECT ht.*, r.status as request_status, s.roll_no, s.department, s.semester,
           u.name as student_name, u.email as student_email,
           issuer.name as issued_by_name
           FROM hall_tickets ht
           JOIN requests r ON ht.request_id = r.id
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           JOIN users issuer ON ht.issued_by = issuer.id
           WHERE ht.request_id = %s""",
        (request_id,), one=True
    )

    if not hall_ticket:
        return jsonify({'error': 'Hall ticket not found'}), 404

    # Students can only see their own hall tickets
    if claims.get('role') == 'student':
        student = query_db("SELECT id FROM students WHERE user_id = %s", (user_id,), one=True)
        req = get_request_by_id(request_id)
        if not student or req['student_id'] != student['id']:
            return jsonify({'error': 'Unauthorized'}), 403

    return jsonify({'hall_ticket': hall_ticket}), 200
