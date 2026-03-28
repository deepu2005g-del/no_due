"""
Notification model - handles notification CRUD.
"""
from models import query_db


def create_notification(user_id: int, message: str, link: str = None) -> dict:
    """Create a notification for a user."""
    return query_db(
        """INSERT INTO notifications (user_id, message, link)
           VALUES (%s, %s, %s)
           RETURNING *""",
        (user_id, message, link), one=True, commit=True
    )


def get_notifications(user_id: int, unread_only: bool = False) -> list:
    """Get notifications for a user, optionally only unread."""
    if unread_only:
        return query_db(
            """SELECT * FROM notifications
               WHERE user_id = %s AND is_read = FALSE
               ORDER BY created_at DESC""",
            (user_id,)
        )
    return query_db(
        """SELECT * FROM notifications
           WHERE user_id = %s
           ORDER BY created_at DESC
           LIMIT 50""",
        (user_id,)
    )


def mark_as_read(notification_id: int, user_id: int) -> dict:
    """Mark a notification as read."""
    return query_db(
        """UPDATE notifications SET is_read = TRUE
           WHERE id = %s AND user_id = %s RETURNING *""",
        (notification_id, user_id), one=True, commit=True
    )


def mark_all_read(user_id: int):
    """Mark all notifications as read for a user."""
    query_db(
        "UPDATE notifications SET is_read = TRUE WHERE user_id = %s AND is_read = FALSE",
        (user_id,), commit=True
    )


def get_unread_count(user_id: int) -> int:
    """Get count of unread notifications."""
    result = query_db(
        "SELECT COUNT(*) as count FROM notifications WHERE user_id = %s AND is_read = FALSE",
        (user_id,), one=True
    )
    return result['count'] if result else 0
