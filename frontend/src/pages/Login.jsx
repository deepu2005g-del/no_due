/**
 * Login Page - Modern glassmorphism design with gradient background.
 */
import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import toast from 'react-hot-toast'
import { HiOutlineShieldCheck, HiOutlineMail, HiOutlineLockClosed, HiOutlineEye, HiOutlineEyeOff } from 'react-icons/hi'

export default function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [showPw, setShowPw] = useState(false)
  const { login } = useAuth()
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!email || !password) return toast.error('Please fill in all fields')
    setLoading(true)
    try {
      const user = await login(email, password)
      toast.success(`Welcome back, ${user.name}!`)
      navigate(`/${user.role}`)
    } catch (err) {
      toast.error(err.response?.data?.error || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center relative overflow-hidden">
      {/* Animated background */}
      <div className="absolute inset-0 bg-gradient-to-br from-surface-950 via-primary-950/50 to-surface-950">
        <div className="absolute top-1/4 -left-20 w-72 h-72 bg-primary-500/20 rounded-full blur-3xl animate-pulse-slow" />
        <div className="absolute bottom-1/4 -right-20 w-96 h-96 bg-purple-500/15 rounded-full blur-3xl animate-pulse-slow" style={{animationDelay: '1s'}} />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary-600/5 rounded-full blur-3xl" />
      </div>

      <div className="relative z-10 w-full max-w-md px-4">
        {/* Logo */}
        <div className="text-center mb-8 animate-fade-in">
          <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center shadow-2xl shadow-primary-500/30">
            <HiOutlineShieldCheck className="w-9 h-9 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white">No-Due Clearance</h1>
          <p className="text-surface-400 mt-1">Sign in to your account</p>
        </div>

        {/* Login Card */}
        <div className="glass-card p-8 animate-slide-up">
          <form onSubmit={handleSubmit} className="space-y-5">
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-2">Email</label>
              <div className="relative">
                <HiOutlineMail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input
                  id="login-email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-field pl-10"
                  placeholder="you@college.edu"
                />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-surface-300 mb-2">Password</label>
              <div className="relative">
                <HiOutlineLockClosed className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-surface-400" />
                <input
                  id="login-password"
                  type={showPw ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="input-field pl-10 pr-10"
                  placeholder="••••••••"
                />
                <button type="button" onClick={() => setShowPw(!showPw)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-surface-400 hover:text-white">
                  {showPw ? <HiOutlineEyeOff className="w-5 h-5" /> : <HiOutlineEye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            <button id="login-submit" type="submit" disabled={loading}
              className="btn-primary w-full flex items-center justify-center gap-2 py-3">
              {loading ? (
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              ) : (
                'Sign In'
              )}
            </button>
          </form>

          <p className="text-center text-sm text-surface-400 mt-6">
            Don't have an account?{' '}
            <Link to="/signup" className="text-primary-400 hover:text-primary-300 font-medium">
              Sign Up
            </Link>
          </p>

          {/* Demo Credentials */}
          <div className="mt-6 p-4 rounded-xl bg-surface-800/50 border border-surface-700/30">
            <p className="text-xs font-semibold text-surface-400 mb-2">Demo Credentials (password: password123)</p>
            <div className="grid grid-cols-2 gap-1 text-xs text-surface-400">
              <span>Student:</span><span className="text-surface-300">student1@college.edu</span>
              <span>Faculty:</span><span className="text-surface-300">faculty@college.edu</span>
              <span>Admin:</span><span className="text-surface-300">admin@college.edu</span>
              <span>HOD:</span><span className="text-surface-300">hod@college.edu</span>
              <span>Staff:</span><span className="text-surface-300">staff@college.edu</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
