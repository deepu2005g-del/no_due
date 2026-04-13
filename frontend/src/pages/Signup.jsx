/**
 * Signup Page - Registration form with role selection and student fields.
 * Students can pick a faculty advisor from the live list fetched from the backend.
 */
import { useState, useEffect } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import axios from 'axios'
import { HiOutlineShieldCheck, HiOutlineUser, HiOutlineEnvelope, HiOutlineLockClosed } from 'react-icons/hi2'

/* Get API URL from env or default to localhost:5000 */
const API = import.meta.env.VITE_API_URL

export default function Signup() {
  const [form, setForm] = useState({
    name: '', email: '', password: '', role: 'student',
    roll_no: '', department: '', semester: '8', attendance_pct: '90',
    faculty_advisor_id: ''
  })
  const [loading, setLoading] = useState(false)
  const [facultyList, setFacultyList] = useState([])
  const { signup } = useAuth()
  const navigate = useNavigate()

  /* Fetch all active faculty members for the advisor selection dropdown */
  useEffect(() => {
    axios.get(`${API}/auth/faculty-list`)
      .then(res => setFacultyList(res.data.faculty || []))
      .catch(err => {
        console.error('Failed to fetch faculty list:', err)
        /* Silent fallback: if backend is down, dropdown will remain empty or show raw input */
      })
  }, [])

  const handleChange = (e) => {
    setForm({ ...form, [e.target.name]: e.target.value })
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    /* Basic Validation */
    if (!form.name || !form.email || !form.password) 
      return toast.error('Fill in all required fields')

    if (form.role === 'student') {
      if (!form.roll_no) return toast.error('Roll number is required for students')
      if (!form.department) return toast.error('Department is required for students')
      if (!form.faculty_advisor_id) return toast.error('Please select your faculty advisor')
    }

    setLoading(true)
    try {
      const payload = { 
        ...form, 
        semester: parseInt(form.semester), 
        attendance_pct: parseFloat(form.attendance_pct),
        faculty_advisor_id: form.faculty_advisor_id ? parseInt(form.faculty_advisor_id) : null
      }
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
      {/* Background decoration */}
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
                <HiOutlineEnvelope className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
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
                <p className="text-xs font-semibold text-primary-400 mb-2">Academic Information</p>
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

                {/* Faculty Advisor selection - CRITICAL for dynamic linkage */}
                <div className="mt-4">
                  <label className="block text-xs text-surface-400 mb-1">Faculty Advisor <span className="text-red-400">*</span></label>
                  {facultyList.length > 0 ? (
                    <select 
                      name="faculty_advisor_id" 
                      value={form.faculty_advisor_id} 
                      onChange={handleChange} 
                      className="input-field text-sm"
                    >
                      <option value="">-- Select your advisor --</option>
                      {facultyList.map(f => (
                        <option key={f.id} value={f.id}>{f.name} ({f.email})</option>
                      ))}
                    </select>
                  ) : (
                    <div className="p-2 text-xs text-surface-500 bg-surface-900/50 rounded-lg border border-dashed border-surface-700">
                      No faculty advisors registered yet.
                    </div>
                  )}
                  <p className="text-[10px] text-surface-500 mt-1">This links your clearance request to the correct faculty advisor.</p>
                </div>
              </div>
            )}

            <button type="submit" disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3 mt-2">
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Create Account'
              )}
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
