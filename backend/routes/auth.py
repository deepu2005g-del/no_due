"""
Authentication Routes
Handles login and registration with JWT token generation.
"""
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from models.user import create_user, get_user_by_email, get_user_by_id, check_password
from models import query_db

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Body: { email, password, name, role }
    - If role is 'student', also expects: roll_no, department, semester, attendance_pct
    """
    data = request.get_json()

    # Validate required fields
    required = ['email', 'password', 'name', 'role']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing field: {field}'}), 400

    # Check if email already exists
    if get_user_by_email(data['email']):
        return jsonify({'error': 'Email already registered'}), 409

    # Validate role
    valid_roles = ['student', 'faculty', 'admin', 'hod', 'staff']
    if data['role'] not in valid_roles:
        return jsonify({'error': f'Invalid role. Must be one of: {valid_roles}'}), 400

    # Create user
    user = create_user(data['email'], data['password'], data['name'], data['role'])

    # If student, create student record
    if data['role'] == 'student':
        student_fields = ['roll_no', 'department', 'semester']
        for field in student_fields:
            if field not in data:
                return jsonify({'error': f'Students must provide: {field}'}), 400

        attendance = data.get('attendance_pct', 0)
        faculty_id = data.get('faculty_advisor_id', None)

        query_db(
            """INSERT INTO students (user_id, roll_no, department, semester, attendance_pct, faculty_advisor_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user['id'], data['roll_no'], data['department'], data['semester'], attendance, faculty_id),
            commit=True
        )

    # Generate JWT token
    token = create_access_token(identity=str(user['id']),
                                additional_claims={'role': data['role'], 'name': user['name']})

    return jsonify({
        'message': 'Registration successful',
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': data['role']
        }
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    """
    Login with email and password.
    Returns JWT token and user info.
    """
    data = request.get_json()

    if not data or 'email' not in data or 'password' not in data:
        return jsonify({'error': 'Email and password are required'}), 400

    user = get_user_by_email(data['email'])
    if not user or not check_password(data['password'], user['password_hash']):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Generate JWT
    token = create_access_token(identity=str(user['id']),
                                additional_claims={'role': user['role'], 'name': user['name']})

    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'id': user['id'],
            'email': user['email'],
            'name': user['name'],
            'role': user['role']
        }
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def get_me():
    """Get the current authenticated user's info."""
    user_id = int(get_jwt_identity())
    user = get_user_by_id(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'user': user}), 200
