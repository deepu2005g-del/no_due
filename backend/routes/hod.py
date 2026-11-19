"""
HOD Routes
Handles final verification and approval.
Supports bulk approval of multiple requests.
"""
from flask import Blueprint, request, jsonify, Response
import csv
import io
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


@hod_bp.route('/all-status', methods=['GET'])
@jwt_required()
def get_all_status():
    """Get all requests in the HOD's department for monitoring."""
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    # For now, get all requests since we're in a demo/flat structure
    # In a real app, this would filter by HOD's department
    from models.request import get_all_requests
    all_reqs = get_all_requests()
    return jsonify({'requests': all_reqs}), 200


@hod_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_stats():
    """Get high-level stats for the HOD dashboard."""
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    # Total requests
    totals = query_db("SELECT COUNT(*) as total FROM requests", one=True)
    # Status counts
    status_counts = query_db("SELECT status, COUNT(*) as count FROM requests GROUP BY status")
    # Department clearance activity
    dept_stats = query_db("""
        SELECT d.name as department, COUNT(a.id) as approvals
        FROM departments d
        LEFT JOIN approvals a ON d.id = a.department_id AND a.status = 'approved'
        GROUP BY d.name
    """)
    
    return jsonify({
        'totals': totals,
        'status_counts': status_counts,
        'department_stats': dept_stats,
        'avg_processing_hours': 12 # Placeholder for demo
    }), 200


@hod_bp.route('/report.csv', methods=['GET'])
@jwt_required()
def report_csv():
    """Generate a CSV report of department clearance data."""
    claims = get_jwt()
    if claims.get('role') != 'hod':
        return jsonify({'error': 'HOD access required'}), 403

    rows = query_db(
        """SELECT r.id, u.name as student_name, s.roll_no, s.department, s.semester,
                  s.attendance_pct, r.status, r.created_at, r.updated_at,
                  ht.ticket_number
           FROM requests r
           JOIN students s ON r.student_id = s.id
           JOIN users u ON s.user_id = u.id
           LEFT JOIN hall_tickets ht ON ht.request_id = r.id
           ORDER BY r.created_at DESC"""
    )
    approvals = query_db(
        """SELECT a.request_id, a.department_id, d.name as department_name,
                  a.status, a.remarks, a.updated_at
           FROM approvals a
           JOIN departments d ON a.department_id = d.id"""
    )
    by_request = {}
    for a in approvals:
        by_request.setdefault(a['request_id'], {})[a['department_name']] = a

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Request ID', 'Student', 'Roll No', 'Department', 'Semester', 'Attendance %',
        'Request Status', 'Faculty Status', 'Faculty Updated', 'Library Status',
        'Library Updated', 'Hostel Status', 'Hostel Updated', 'Accounts Status',
        'Accounts Updated', 'Hall Ticket', 'Created At', 'Updated At',
    ])

    for r in rows:
        deps = by_request.get(r['id'], {})
        def cell(name, field='status'):
            return deps.get(name, {}).get(field) or ''
        writer.writerow([
            r['id'], r['student_name'], r['roll_no'], r['department'], r['semester'],
            r['attendance_pct'], r['status'],
            cell('Faculty'), cell('Faculty', 'updated_at'),
            cell('Library'), cell('Library', 'updated_at'),
            cell('Hostel'), cell('Hostel', 'updated_at'),
            cell('Accounts'), cell('Accounts', 'updated_at'),
            r['ticket_number'] or '', r['created_at'], r['updated_at'],
        ])

    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=department_clearance_report.csv'}
    )


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
