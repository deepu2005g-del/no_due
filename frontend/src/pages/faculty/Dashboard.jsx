/**
 * Faculty Dashboard - View assigned students, check attendance, approve/reject.
 */
import { useState, useEffect } from 'react'
import API from '../../api/axios'
import toast from 'react-hot-toast'
import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineUserGroup, HiOutlineBadgeCheck } from 'react-icons/hi'

export default function FacultyDashboard() {
  const [students, setStudents] = useState([])
  const [pendingRequests, setPendingRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionModal, setActionModal] = useState(null) // { requestId, action }
  const [remarks, setRemarks] = useState('')

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      const res = await API.get('/faculty/students')
      setStudents(res.data.students || [])
      setPendingRequests(res.data.pending_requests || [])
    } catch (err) {
      toast.error('Failed to load data')
    } finally {
      setLoading(false)
    }
  }

  const handleAction = async () => {
    if (!actionModal) return
    try {
      await API.post(`/faculty/approve/${actionModal.requestId}`, {
        action: actionModal.action,
        remarks
      })
      toast.success(`Request ${actionModal.action === 'approve' ? 'approved' : 'rejected'}!`)
      setActionModal(null)
      setRemarks('')
      fetchData()
    } catch (err) {
      toast.error(err.response?.data?.error || 'Action failed')
    }
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-6">
      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-primary-500/15 flex items-center justify-center">
              <HiOutlineUserGroup className="w-6 h-6 text-primary-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{students.length}</p>
              <p className="text-xs text-surface-400">Assigned Students</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-amber-500/15 flex items-center justify-center">
              <HiOutlineBadgeCheck className="w-6 h-6 text-amber-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{pendingRequests.length}</p>
              <p className="text-xs text-surface-400">Pending Reviews</p>
            </div>
          </div>
        </div>
        <div className="stat-card">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-xl bg-red-500/15 flex items-center justify-center">
              <HiOutlineXCircle className="w-6 h-6 text-red-400" />
            </div>
            <div>
              <p className="text-2xl font-bold text-white">{students.filter(s => parseFloat(s.attendance_pct) < 85).length}</p>
              <p className="text-xs text-surface-400">Below 85% Attendance</p>
            </div>
          </div>
        </div>
      </div>

      {/* Pending Requests */}
      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-surface-700/50">
          <h2 className="text-lg font-semibold text-white">Pending Requests</h2>
          <p className="text-sm text-surface-400">Review and approve student no-due requests</p>
        </div>
        {pendingRequests.length === 0 ? (
          <div className="p-10 text-center text-surface-400">
            <HiOutlineCheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500/50" />
            <p>No pending requests! All caught up.</p>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface-800/50">
                <tr>
                  <th className="table-header">Student</th>
                  <th className="table-header">Roll No</th>
                  <th className="table-header">Department</th>
                  <th className="table-header">Attendance</th>
                  <th className="table-header">Status</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/30">
                {pendingRequests.map((req) => {
                  const eligible = parseFloat(req.attendance_pct) >= 85
                  return (
                    <tr key={req.id} className="hover:bg-surface-800/30 transition-colors">
                      <td className="table-cell font-medium text-white">{req.student_name}</td>
                      <td className="table-cell text-surface-300">{req.roll_no}</td>
                      <td className="table-cell text-surface-300">{req.department}</td>
                      <td className="table-cell">
                        <span className={`font-semibold ${eligible ? 'text-emerald-400' : 'text-red-400'}`}>
                          {parseFloat(req.attendance_pct).toFixed(1)}%
                        </span>
                        {!eligible && <span className="text-xs text-red-400 ml-1">⚠</span>}
                      </td>
                      <td className="table-cell">
                        <span className="badge-pending">{req.status.replace(/_/g, ' ')}</span>
                      </td>
                      <td className="table-cell text-right">
                        <div className="flex items-center justify-end gap-2">
                          <button onClick={() => setActionModal({ requestId: req.id, action: 'approve' })}
                            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/25 transition-all"
                            disabled={!eligible}>
                            Approve
                          </button>
                          <button onClick={() => setActionModal({ requestId: req.id, action: 'reject' })}
                            className="px-3 py-1.5 text-xs font-medium rounded-lg bg-red-500/15 text-red-400 border border-red-500/30 hover:bg-red-500/25 transition-all">
                            Reject
                          </button>
                        </div>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* All Students */}
      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-surface-700/50">
          <h2 className="text-lg font-semibold text-white">All Assigned Students</h2>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-surface-800/50">
              <tr>
                <th className="table-header">Name</th>
                <th className="table-header">Roll No</th>
                <th className="table-header">Semester</th>
                <th className="table-header">Attendance</th>
                <th className="table-header">Eligible</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-surface-700/30">
              {students.map((s) => {
                const eligible = parseFloat(s.attendance_pct) >= 85
                return (
                  <tr key={s.id} className="hover:bg-surface-800/30 transition-colors">
                    <td className="table-cell font-medium text-white">{s.name}</td>
                    <td className="table-cell text-surface-300">{s.roll_no}</td>
                    <td className="table-cell text-surface-300">{s.semester}</td>
                    <td className="table-cell">
                      <div className="flex items-center gap-2">
                        <div className="w-20 h-2 bg-surface-700 rounded-full overflow-hidden">
                          <div className={`h-full rounded-full ${eligible ? 'bg-emerald-500' : 'bg-red-500'}`}
                            style={{ width: `${Math.min(parseFloat(s.attendance_pct), 100)}%` }} />
                        </div>
                        <span className={`text-xs font-semibold ${eligible ? 'text-emerald-400' : 'text-red-400'}`}>
                          {parseFloat(s.attendance_pct).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="table-cell">
                      {eligible ? <span className="badge-approved">Eligible</span> : <span className="badge-rejected">Ineligible</span>}
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Action Modal */}
      {actionModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setActionModal(null)}>
          <div className="glass-card p-6 w-full max-w-md mx-4 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-white mb-4">
              {actionModal.action === 'approve' ? '✅ Approve Request' : '❌ Reject Request'}
            </h3>
            <div>
              <label className="block text-sm text-surface-300 mb-2">Remarks (optional)</label>
              <textarea value={remarks} onChange={(e) => setRemarks(e.target.value)}
                className="input-field h-24 resize-none" placeholder="Add any remarks..." />
            </div>
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setActionModal(null)} className="btn-ghost">Cancel</button>
              <button onClick={handleAction}
                className={actionModal.action === 'approve' ? 'btn-success' : 'btn-danger'}>
                {actionModal.action === 'approve' ? 'Approve' : 'Reject'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
