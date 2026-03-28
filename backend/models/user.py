"""
User model - handles user CRUD and password operations.
"""
import bcrypt
from models import query_db


def hash_password(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def check_password(password: str, hashed: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_user(email: str, password: str, name: str, role: str = 'student') -> dict:
    """Insert a new user and return the created user record."""
    pw_hash = hash_password(password)
    return query_db(
        """INSERT INTO users (email, password_hash, name, role)
           VALUES (%s, %s, %s, %s)
           RETURNING id, email, name, role, created_at""",
        (email, pw_hash, name, role),
        one=True, commit=True
    )


def get_user_by_email(email: str) -> dict:
    """Fetch a user by email address."""
    return query_db(
        "SELECT * FROM users WHERE email = %s AND is_active = TRUE",
        (email,), one=True
    )


def get_user_by_id(user_id: int) -> dict:
    """Fetch a user by their ID."""
    return query_db(
        "SELECT id, email, name, role, created_at FROM users WHERE id = %s",
        (user_id,), one=True
    )
