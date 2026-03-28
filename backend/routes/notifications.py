"""
Notification Routes
Handles fetching and marking notifications.
"""
from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.notification import get_notifications, mark_as_read, mark_all_read, get_unread_count

notifications_bp = Blueprint('notifications', __name__)


@notifications_bp.route('/', methods=['GET'])
@jwt_required()
def get_all():
    """Get all notifications for the current user."""
    user_id = int(get_jwt_identity())
    notifs = get_notifications(user_id)
    unread = get_unread_count(user_id)
    return jsonify({'notifications': notifs, 'unread_count': unread}), 200


@notifications_bp.route('/unread', methods=['GET'])
@jwt_required()
def get_unread():
    """Get only unread notifications."""
    user_id = int(get_jwt_identity())
    notifs = get_notifications(user_id, unread_only=True)
    return jsonify({'notifications': notifs, 'unread_count': len(notifs)}), 200


@notifications_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required()
def read_notification(notification_id):
    """Mark a single notification as read."""
    user_id = int(get_jwt_identity())
    result = mark_as_read(notification_id, user_id)
    if not result:
        return jsonify({'error': 'Notification not found'}), 404
    return jsonify({'message': 'Marked as read'}), 200


@notifications_bp.route('/read-all', methods=['PUT'])
@jwt_required()
def read_all():
    """Mark all notifications as read."""
    user_id = int(get_jwt_identity())
    mark_all_read(user_id)
    return jsonify({'message': 'All notifications marked as read'}), 200
