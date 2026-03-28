/**
 * App.jsx - Main application with routing.
 * Routes are protected by role-based access control.
 */
import { Routes, Route, Navigate } from 'react-router-dom'
import { useAuth } from './context/AuthContext'
import Layout from './components/Layout'
import Login from './pages/Login'
import Signup from './pages/Signup'
import StudentDashboard from './pages/student/Dashboard'
import FacultyDashboard from './pages/faculty/Dashboard'
import AdminDashboard from './pages/admin/Dashboard'
import HodDashboard from './pages/hod/Dashboard'
import StaffDashboard from './pages/staff/Dashboard'

// Protected route wrapper - checks auth + role
function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth()

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-surface-950">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-500"></div>
      </div>
    )
  }

  if (!user) return <Navigate to="/login" replace />
  if (allowedRoles && !allowedRoles.includes(user.role)) {
    return <Navigate to={`/${user.role}`} replace />
  }

  return <Layout>{children}</Layout>
}

// Redirect to role-based dashboard after login
function RoleRedirect() {
  const { user, loading } = useAuth()
  if (loading) return null
  if (!user) return <Navigate to="/login" replace />
  return <Navigate to={`/${user.role}`} replace />
}

export default function App() {
  return (
    <Routes>
      {/* Public routes */}
      <Route path="/login" element={<Login />} />
      <Route path="/signup" element={<Signup />} />

      {/* Role-based dashboards */}
      <Route path="/student" element={
        <ProtectedRoute allowedRoles={['student']}>
          <StudentDashboard />
        </ProtectedRoute>
      } />
      <Route path="/faculty" element={
        <ProtectedRoute allowedRoles={['faculty']}>
          <FacultyDashboard />
        </ProtectedRoute>
      } />
      <Route path="/admin" element={
        <ProtectedRoute allowedRoles={['admin']}>
          <AdminDashboard />
        </ProtectedRoute>
      } />
      <Route path="/hod" element={
        <ProtectedRoute allowedRoles={['hod']}>
          <HodDashboard />
        </ProtectedRoute>
      } />
      <Route path="/staff" element={
        <ProtectedRoute allowedRoles={['staff']}>
          <StaffDashboard />
        </ProtectedRoute>
      } />

      {/* Root redirect */}
      <Route path="/" element={<RoleRedirect />} />
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  )
}
