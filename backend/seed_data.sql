-- Seed Data for No-Due Clearance System
-- All passwords are hashed version of 'password123'
-- bcrypt hash: $2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK

-- ============================================
-- INSERT DEPARTMENTS
-- ============================================
INSERT INTO departments (name, description) VALUES
    ('Library', 'Central Library - Book returns and fine clearance'),
    ('Hostel', 'Hostel Administration - Room clearance and dues'),
    ('Accounts', 'Accounts Department - Fee payment verification'),
    ('Faculty', 'Faculty Advisor - Attendance and academic clearance');

-- ============================================
-- INSERT USERS (one per role)
-- ============================================
INSERT INTO users (email, password_hash, name, role) VALUES
    ('student1@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Rahul Sharma', 'student'),
    ('student2@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Priya Patel', 'student'),
    ('student3@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Amit Kumar', 'student'),
    ('faculty@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Dr. Sunita Verma', 'faculty'),
    ('admin@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Rajesh Admin', 'admin'),
    ('hod@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Prof. Anil Gupta', 'hod'),
    ('staff@college.edu', '$2b$12$LJ3m4ys3Lz0QGmMfKzOhPeDKN.OkgOE4gKDS3dGGMb3eJPqnXSFaK', 'Meena Staff', 'staff');

-- ============================================
-- INSERT STUDENTS (varying attendance)
-- ============================================
INSERT INTO students (user_id, roll_no, department, semester, attendance_pct, faculty_advisor_id) VALUES
    (1, 'CS2024001', 'Computer Science', 8, 92.50, 4),
    (2, 'CS2024002', 'Computer Science', 8, 78.30, 4),   -- Below 85% - ineligible
    (3, 'EC2024001', 'Electronics', 8, 88.00, 4);

-- ============================================
-- SAMPLE REQUESTS
-- ============================================
-- Rahul has a request in progress (faculty approved)
INSERT INTO requests (student_id, status, created_at) VALUES
    (1, 'faculty_approved', NOW() - INTERVAL '3 days');

-- Priya has a rejected request 
INSERT INTO requests (student_id, status, remarks, created_at) VALUES
    (2, 'rejected', 'Attendance below 85%', NOW() - INTERVAL '5 days');

-- Amit has a fresh pending request
INSERT INTO requests (student_id, status, created_at) VALUES
    (3, 'pending', NOW() - INTERVAL '1 day');

-- ============================================
-- SAMPLE APPROVALS for Rahul's request (id=1)
-- ============================================
INSERT INTO approvals (request_id, department_id, approver_id, status, remarks) VALUES
    (1, 4, 4, 'approved', 'Attendance verified: 92.5%'),     -- Faculty approved
    (1, 1, NULL, 'pending', NULL),                             -- Library pending
    (1, 2, NULL, 'pending', NULL),                             -- Hostel pending
    (1, 3, NULL, 'pending', NULL);                             -- Accounts pending

-- Approvals for Amit's request (id=3) - all pending
INSERT INTO approvals (request_id, department_id, status) VALUES
    (3, 4, 'pending'),
    (3, 1, 'pending'),
    (3, 2, 'pending'),
    (3, 3, 'pending');

-- ============================================
-- SAMPLE NOTIFICATIONS
-- ============================================
INSERT INTO notifications (user_id, message, is_read) VALUES
    (1, 'Your no-due request has been approved by Faculty Advisor.', TRUE),
    (1, 'Your request is pending clearance from Library department.', FALSE),
    (4, 'New no-due request submitted by Amit Kumar (EC2024001).', FALSE),
    (5, 'Request #1 from Rahul Sharma is awaiting department clearance.', FALSE),
    (2, 'Your no-due request has been rejected. Reason: Attendance below 85%.', FALSE);
