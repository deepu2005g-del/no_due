-- No-Due Clearance Management System - Database Schema
-- PostgreSQL

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Enum types
CREATE TYPE user_role AS ENUM ('student', 'faculty', 'admin', 'hod', 'staff');
CREATE TYPE request_status AS ENUM ('pending', 'faculty_approved', 'departments_cleared', 'hod_approved', 'rejected', 'resubmitted');
CREATE TYPE approval_status AS ENUM ('pending', 'approved', 'rejected');

-- ============================================
-- USERS TABLE
-- ============================================
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(150) NOT NULL,
    role user_role NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- DEPARTMENTS TABLE
-- ============================================
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,       -- Library, Hostel, Accounts, Faculty
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- STUDENTS TABLE
-- ============================================
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    roll_no VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) NOT NULL,         -- Academic department (CSE, ECE, etc.)
    semester INTEGER NOT NULL CHECK (semester BETWEEN 1 AND 8),
    attendance_pct NUMERIC(5,2) DEFAULT 0.00 CHECK (attendance_pct BETWEEN 0 AND 100),
    faculty_advisor_id INTEGER REFERENCES users(id),  -- Assigned faculty
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- REQUESTS TABLE (No-Due Requests)
-- ============================================
CREATE TABLE requests (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    status request_status NOT NULL DEFAULT 'pending',
    remarks TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- APPROVALS TABLE (Per-Department Approval)
-- ============================================
CREATE TABLE approvals (
    id SERIAL PRIMARY KEY,
    request_id INTEGER NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    department_id INTEGER NOT NULL REFERENCES departments(id),
    approver_id INTEGER REFERENCES users(id),
    status approval_status NOT NULL DEFAULT 'pending',
    remarks TEXT,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(request_id, department_id)         -- One approval per department per request
);

-- ============================================
-- NOTIFICATIONS TABLE
-- ============================================
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    link VARCHAR(255),                        -- Optional deep-link
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- HALL TICKETS TABLE
-- ============================================
CREATE TABLE hall_tickets (
    id SERIAL PRIMARY KEY,
    request_id INTEGER UNIQUE NOT NULL REFERENCES requests(id) ON DELETE CASCADE,
    issued_by INTEGER NOT NULL REFERENCES users(id),
    ticket_number VARCHAR(50) UNIQUE NOT NULL,
    issued_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX idx_requests_student ON requests(student_id);
CREATE INDEX idx_requests_status ON requests(status);
CREATE INDEX idx_approvals_request ON approvals(request_id);
CREATE INDEX idx_approvals_status ON approvals(status);
CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_unread ON notifications(user_id, is_read) WHERE is_read = FALSE;
CREATE INDEX idx_students_faculty ON students(faculty_advisor_id);
