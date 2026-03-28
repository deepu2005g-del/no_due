"""
No-Due Clearance Management System - Flask Application
Main entry point that sets up the Flask app, registers blueprints,
and configures JWT authentication and CORS.
"""
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from config import get_config


def create_app():
    """Application factory pattern."""
    app = Flask(__name__)
    cfg = get_config()

    # Core config
    app.config['SECRET_KEY'] = cfg.SECRET_KEY
    app.config['JWT_SECRET_KEY'] = cfg.JWT_SECRET_KEY
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = cfg.JWT_ACCESS_TOKEN_EXPIRES

    # Initialize extensions
    CORS(app, origins=cfg.CORS_ORIGINS, supports_credentials=True)
    jwt = JWTManager(app)

    # JWT error handlers
    @jwt.expired_token_loader
    def expired_token(jwt_header, jwt_payload):
        return jsonify({'error': 'Token has expired', 'code': 'token_expired'}), 401

    @jwt.invalid_token_loader
    def invalid_token(error):
        return jsonify({'error': 'Invalid token', 'code': 'invalid_token'}), 401

    @jwt.unauthorized_loader
    def missing_token(error):
        return jsonify({'error': 'Authorization required', 'code': 'missing_token'}), 401

    # Register blueprints (all API routes)
    from routes.auth import auth_bp
    from routes.student import student_bp
    from routes.faculty import faculty_bp
    from routes.admin import admin_bp
    from routes.hod import hod_bp
    from routes.staff import staff_bp
    from routes.notifications import notifications_bp
    from routes.analytics import analytics_bp

    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(student_bp, url_prefix='/api/student')
    app.register_blueprint(faculty_bp, url_prefix='/api/faculty')
    app.register_blueprint(admin_bp, url_prefix='/api/admin')
    app.register_blueprint(hod_bp, url_prefix='/api/hod')
    app.register_blueprint(staff_bp, url_prefix='/api/staff')
    app.register_blueprint(notifications_bp, url_prefix='/api/notifications')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health():
        return jsonify({'status': 'ok', 'message': 'No-Due Clearance System API'}), 200

    return app


if __name__ == '__main__':
    app = create_app()
    print("=" * 50)
    print("  No-Due Clearance System API")
    print("  Running on http://localhost:5000")
    print("=" * 50)
    app.run(host='0.0.0.0', port=5000, debug=True)
