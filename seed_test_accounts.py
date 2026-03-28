import os
import psycopg2
import bcrypt
from dotenv import load_dotenv

load_dotenv('./backend/.env')

def seed_test_accounts():
    conn = psycopg2.connect(os.getenv('DATABASE_URL'))
    cur = conn.cursor()

    test_users = [
        ('student@test.com', '123456', 'Test Student', 'student'),
        ('faculty@test.com', '123456', 'Test Faculty', 'faculty'),
        ('hod@test.com', '123456', 'Test HOD', 'hod'),
        ('admin@test.com', '123456', 'Test Admin', 'admin'),
        ('staff@test.com', '123456', 'Test Staff', 'staff')
    ]

    print("Seeding test accounts...")
    
    for email, password, name, role in test_users:
        # Check if user exists
        cur.execute("SELECT id FROM users WHERE email = %s", (email,))
        user_exists = cur.fetchone()
        
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        if user_exists:
            print(f"Updating user: {email} ({role})")
            cur.execute(
                "UPDATE users SET password_hash = %s, name = %s, role = %s WHERE email = %s RETURNING id",
                (password_hash, name, role, email)
            )
            user_id = cur.fetchone()[0]
        else:
            print(f"Creating user: {email} ({role})")
            cur.execute(
                "INSERT INTO users (email, password_hash, name, role) VALUES (%s, %s, %s, %s) RETURNING id",
                (email, password_hash, name, role)
            )
            user_id = cur.fetchone()[0]

        # If student, ensure students table entry exists
        if role == 'student':
            cur.execute("SELECT id FROM students WHERE user_id = %s", (user_id,))
            if not cur.fetchone():
                print(f"Creating student record for {email}")
                cur.execute(
                    "INSERT INTO students (user_id, roll_no, department, semester, attendance_pct) VALUES (%s, %s, %s, %s, %s)",
                    (user_id, 'TEST2024001', 'Computer Science', 8, 88.5)
                )

    conn.commit()
    cur.close()
    conn.close()
    print("Seeding complete!")

if __name__ == "__main__":
    seed_test_accounts()
