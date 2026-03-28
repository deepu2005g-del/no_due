/**
 * Student Dashboard - Submit requests, view status pipeline, resubmit.
 */
import { useState, useEffect } from 'react'
import API from '../../api/axios'
import StatusTracker from '../../components/StatusTracker'
import toast from 'react-hot-toast'
import { HiOutlinePaperAirplane, HiOutlineRefresh, HiOutlineClock, HiOutlineCheckCircle, HiOutlineXCircle } from 'react-icons/hi'

export default function StudentDashboard() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [submitting, setSubmitting] = useState(false)

  useEffect(() => { fetchStatus() }, [])

  const fetchStatus = async () => {
    try {
      const res = await API.get('/student/status')
      setRequests(res.data.requests || [])
    } catch (err) {
      toast.error('Failed to load status')
    } finally {
      setLoading(false)
    }
  }

  const submitRequest = async () => {
    setSubmitting(true)
    try {
      const res = await API.post('/student/request')
      toast.success(res.data.message)
      if (res.data.warning) toast(res.data.warning, { icon: '⚠️', duration: 6000 })
      fetchStatus()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to submit')
    } finally {
      setSubmitting(false)
    }
  }

  const resubmit = async (id) => {
    try {
      await API.post(`/student/resubmit/${id}`)
      toast.success('Request resubmitted!')
      fetchStatus()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to resubmit')
    }
  }

  const hasActiveRequest = requests.some(r => !['rejected', 'hod_approved'].includes(r.status))

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header with submit button */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">My No-Due Requests</h1>
          <p className="text-surface-400 text-sm mt-1">Track your clearance progress</p>
        </div>
        {!hasActiveRequest && (
          <button onClick={submitRequest} disabled={submitting}
            className="btn-primary flex items-center gap-2">
            {submitting ? <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <HiOutlinePaperAirplane className="w-5 h-5" />}
            Submit New Request
          </button>
        )}
      </div>

      {/* Student Info Card */}
      {requests[0]?.student && (
        <div className="glass-card p-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-xs text-surface-400">Roll No</p>
              <p className="text-sm font-semibold text-white">{requests[0].student.roll_no}</p>
            </div>
            <div>
              <p className="text-xs text-surface-400">Department</p>
              <p className="text-sm font-semibold text-white">{requests[0].student.department}</p>
            </div>
            <div>
              <p className="text-xs text-surface-400">Semester</p>
              <p className="text-sm font-semibold text-white">{requests[0].student.semester}</p>
            </div>
            <div>
              <p className="text-xs text-surface-400">Attendance</p>
              <p className={`text-sm font-semibold ${requests[0].student.attendance_pct >= 85 ? 'text-emerald-400' : 'text-red-400'}`}>
                {requests[0].student.attendance_pct}%
                {requests[0].student.attendance_pct < 85 && <span className="text-xs ml-1">(Below 85%)</span>}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* No requests state */}
      {requests.length === 0 && (
        <div className="glass-card p-12 text-center">
          <HiOutlineClock className="w-16 h-16 text-surface-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold text-white mb-2">No Requests Yet</h2>
          <p className="text-surface-400 mb-6">Submit your first no-due clearance request to get started.</p>
          <button onClick={submitRequest} disabled={submitting} className="btn-primary">
            Submit Request
          </button>
        </div>
      )}

      {/* Requests List */}
      {requests.map((req) => (
        <div key={req.id} className="glass-card p-6 animate-slide-up">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <h3 className="text-lg font-semibold text-white">Request #{req.id}</h3>
              <span className={`badge ${
                req.status === 'hod_approved' ? 'badge-approved' :
                req.status === 'rejected' ? 'badge-rejected' : 'badge-pending'
              }`}>
                {req.status.replace(/_/g, ' ').toUpperCase()}
              </span>
            </div>
            <span className="text-xs text-surface-500">{new Date(req.created_at).toLocaleDateString()}</span>
          </div>

          {/* Status Pipeline */}
          <StatusTracker status={req.status} />

          {/* Department Approvals */}
          {req.approvals && req.approvals.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-semibold text-surface-300 mb-3">Department Clearances</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                {req.approvals.map((a) => (
                  <div key={a.id} className={`p-3 rounded-xl border transition-all
                    ${a.status === 'approved' ? 'bg-emerald-500/10 border-emerald-500/30' :
                      a.status === 'rejected' ? 'bg-red-500/10 border-red-500/30' :
                      'bg-surface-800/50 border-surface-700/30'}`}>
                    <div className="flex items-center gap-2 mb-1">
                      {a.status === 'approved' ? <HiOutlineCheckCircle className="w-4 h-4 text-emerald-400" /> :
                       a.status === 'rejected' ? <HiOutlineXCircle className="w-4 h-4 text-red-400" /> :
                       <HiOutlineClock className="w-4 h-4 text-amber-400" />}
                      <span className="text-xs font-semibold text-surface-200">{a.department_name}</span>
                    </div>
                    <span className={`text-xs ${
                      a.status === 'approved' ? 'text-emerald-400' :
                      a.status === 'rejected' ? 'text-red-400' : 'text-amber-400'
                    }`}>{a.status}</span>
                    {a.remarks && <p className="text-xs text-surface-400 mt-1 truncate">{a.remarks}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Reject reason & resubmit */}
          {req.status === 'rejected' && (
            <div className="mt-4 flex items-center justify-between p-3 rounded-xl bg-red-500/10 border border-red-500/20">
              <div>
                <p className="text-sm text-red-400 font-medium">Reason: {req.remarks || 'No reason provided'}</p>
              </div>
              <button onClick={() => resubmit(req.id)} className="btn-ghost text-sm flex items-center gap-1">
                <HiOutlineRefresh className="w-4 h-4" /> Resubmit
              </button>
            </div>
          )}
        </div>
      ))}
    </div>
  )
}
