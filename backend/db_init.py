"""
Automatic MySQL schema initialization.
Creates the database (if missing) and required tables/indexes on startup.
Safe to run repeatedly: uses CREATE ... IF NOT EXISTS only.
"""
import pymysql
import pymysql.cursors
from config import get_config

config = get_config()

TABLES = [
    """
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) UNIQUE NOT NULL,
        password_hash VARCHAR(255) NOT NULL,
        name VARCHAR(150) NOT NULL,
        role ENUM('student','faculty','admin','hod','staff') NOT NULL DEFAULT 'student',
        is_active BOOLEAN DEFAULT TRUE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS departments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(100) UNIQUE NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS students (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT UNIQUE NOT NULL,
        roll_no VARCHAR(50) UNIQUE NOT NULL,
        department VARCHAR(100) NOT NULL,
        semester INT NOT NULL,
        attendance_pct DECIMAL(5,2) DEFAULT 0.00,
        faculty_advisor_id INT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_students_faculty (faculty_advisor_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        FOREIGN KEY (faculty_advisor_id) REFERENCES users(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS requests (
        id INT AUTO_INCREMENT PRIMARY KEY,
        student_id INT NOT NULL,
        status ENUM('pending','faculty_approved','departments_cleared','hod_approved','rejected','resubmitted') NOT NULL DEFAULT 'pending',
        remarks TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        INDEX idx_requests_student (student_id),
        INDEX idx_requests_status (status),
        FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS approvals (
        id INT AUTO_INCREMENT PRIMARY KEY,
        request_id INT NOT NULL,
        department_id INT NOT NULL,
        approver_id INT,
        status ENUM('pending','approved','rejected') NOT NULL DEFAULT 'pending',
        remarks TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        UNIQUE KEY uq_request_department (request_id, department_id),
        INDEX idx_approvals_request (request_id),
        INDEX idx_approvals_status (status),
        FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
        FOREIGN KEY (department_id) REFERENCES departments(id),
        FOREIGN KEY (approver_id) REFERENCES users(id)
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS notifications (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        message TEXT NOT NULL,
        is_read BOOLEAN DEFAULT FALSE,
        link VARCHAR(255),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        INDEX idx_notifications_user (user_id),
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    ) ENGINE=InnoDB
    """,
    """
    CREATE TABLE IF NOT EXISTS hall_tickets (
        id INT AUTO_INCREMENT PRIMARY KEY,
        request_id INT UNIQUE NOT NULL,
        issued_by INT NOT NULL,
        ticket_number VARCHAR(50) UNIQUE NOT NULL,
        issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (request_id) REFERENCES requests(id) ON DELETE CASCADE,
        FOREIGN KEY (issued_by) REFERENCES users(id)
    ) ENGINE=InnoDB
    """,
]

DEPARTMENTS = ['Library', 'Hostel', 'Accounts', 'Faculty']


def initialize_database():
    kwargs = {}
    if getattr(config, 'DB_SSL', False):
        kwargs['ssl'] = {'ssl': {}}

    server = pymysql.connect(
        host=config.DB_HOST, port=int(config.DB_PORT),
        user=config.DB_USER, password=config.DB_PASSWORD,
        autocommit=True, cursorclass=pymysql.cursors.DictCursor, **kwargs
    )
    try:
        with server.cursor() as cur:
            cur.execute(
                f"CREATE DATABASE IF NOT EXISTS `{config.DB_NAME}` "
                "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
            )
        server.select_db(config.DB_NAME)
        with server.cursor() as cur:
            for table in TABLES:
                cur.execute(table)
            for name in DEPARTMENTS:
                cur.execute(
                    "INSERT IGNORE INTO departments (name, description) VALUES (%s, %s)",
                    (name, ''),
                )
    finally:
        server.close()
