/**
 * Signup Page - Registration form with role selection and student fields.
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { HiOutlineShieldCheck, HiOutlineUser, HiOutlineMail, HiOutlineLockClosed } from 'react-icons/hi'

export default function Signup() {
  const [form, setForm] = useState({
    name: '', email: '', password: '', role: 'student',
    roll_no: '', department: '', semester: '8', attendance_pct: '0'
  })
  const [loading, setLoading] = useState(false)
  const { signup } = useAuth()
  const navigate = useNavigate()

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!form.name || !form.email || !form.password) return toast.error('Fill in all required fields')
    setLoading(true)
    try {
      const payload = { ...form, semester: parseInt(form.semester), attendance_pct: parseFloat(form.attendance_pct) }
      const user = await signup(payload)
      toast.success(`Welcome, ${user.name}!`)
      navigate(`/${user.role}`)
    } catch (err) {
      toast.error(err.response?.data?.error || 'Registration failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      <div className="absolute inset-0 bg-gradient-to-br from-surface-950 via-primary-950/50 to-surface-950">
        <div className="absolute top-1/3 -right-20 w-72 h-72 bg-primary-500/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/3 -left-20 w-96 h-96 bg-purple-500/15 rounded-full blur-3xl animate-pulse-slow" />
      </div>

      <div className="relative z-10 w-full max-w-lg px-4 my-8">
        <div className="text-center mb-8 animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-primary-500/30">
            <HiOutlineShieldCheck className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">Create Account</h1>
          <p className="text-surface-400 mt-1">Join the No-Due Clearance System</p>
        </div>

        <div className="glass-card p-8 animate-slide-up">
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">Full Name</label>
              <div className="relative">
                <HiOutlineUser className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input name="name" value={form.name} onChange={handleChange}
                  className="input-field pl-10" placeholder="John Doe" />
              </div>
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">Email</label>
              <div className="relative">
                <HiOutlineMail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input name="email" type="email" value={form.email} onChange={handleChange}
                  className="input-field pl-10" placeholder="you@college.edu" />
              </div>
            </div>

            {/* Password */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">Password</label>
              <div className="relative">
                <HiOutlineLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input name="password" type="password" value={form.password} onChange={handleChange}
                  className="input-field pl-10" placeholder="••••••••" />
              </div>
            </div>

            {/* Role */}
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-1.5">Role</label>
              <select name="role" value={form.role} onChange={handleChange} className="input-field">
                <option value="student">Student</option>
                <option value="faculty">Faculty</option>
                <option value="admin">Admin</option>
                <option value="hod">HOD</option>
                <option value="staff">Department Staff</option>
              </select>
            </div>

            {/* Student-specific fields */}
            {form.role === 'student' && (
              <div className="space-y-4 p-4 rounded-xl bg-surface-800/30 border border-surface-700/30">
                <p className="text-xs font-semibold text-primary-400">Student Details</p>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-surface-400 mb-1">Roll Number</label>
                    <input name="roll_no" value={form.roll_no} onChange={handleChange}
                      className="input-field text-sm" placeholder="CS2024001" />
                  </div>
                  <div>
                    <label className="block text-xs text-surface-400 mb-1">Department</label>
                    <input name="department" value={form.department} onChange={handleChange}
                      className="input-field text-sm" placeholder="Computer Science" />
                  </div>
                  <div>
                    <label className="block text-xs text-surface-400 mb-1">Semester</label>
                    <select name="semester" value={form.semester} onChange={handleChange} className="input-field text-sm">
                      {[1,2,3,4,5,6,7,8].map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                  <div>
                    <label className="block text-xs text-surface-400 mb-1">Attendance %</label>
                    <input name="attendance_pct" type="number" step="0.1" min="0" max="100"
                      value={form.attendance_pct} onChange={handleChange} className="input-field text-sm" />
                  </div>
                </div>
              </div>
            )}

            <button type="submit" disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2">
              {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-surface-400 mt-6">
            Already have an account? <Link to="/login" className="text-primary-400 hover:text-primary-300 font-medium">Sign In</Link>
          </p>
        </div>
      </div>
    </div>
  )
}
