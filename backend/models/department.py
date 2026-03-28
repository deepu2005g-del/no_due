"""
Department model - handles department operations.
"""
from models import query_db


def get_all_departments() -> list:
    """Get all departments."""
    return query_db("SELECT * FROM departments ORDER BY id")


def get_department_by_id(dept_id: int) -> dict:
    """Get a department by ID."""
    return query_db("SELECT * FROM departments WHERE id = %s", (dept_id,), one=True)


def get_department_by_name(name: str) -> dict:
    """Get a department by name."""
    return query_db("SELECT * FROM departments WHERE name = %s", (name,), one=True)
