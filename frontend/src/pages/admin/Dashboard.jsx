/**
 * Admin Dashboard - Manage department clearances.
 */
import { useState, useEffect } from 'react'
import API from '../../api/axios'
import toast from 'react-hot-toast'
import { HiOutlineCheckCircle, HiOutlineXCircle, HiOutlineChartBar } from 'react-icons/hi'

export default function AdminDashboard() {
  const [requests, setRequests] = useState([])
  const [departments, setDepartments] = useState([])
  const [loading, setLoading] = useState(true)
  const [actionModal, setActionModal] = useState(null)
  const [remarks, setRemarks] = useState('')

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      const [reqRes, deptRes] = await Promise.all([
        API.get('/admin/requests'),
        API.get('/admin/departments'),
      ])
      setRequests(reqRes.data.requests || [])
      setDepartments(deptRes.data.departments || [])
    } catch (err) { toast.error('Failed to load data') }
    finally { setLoading(false) }
  }

  const handleAction = async () => {
    if (!actionModal) return
    try {
      await API.post(`/admin/approve/${actionModal.requestId}`, {
        department_id: actionModal.departmentId, action: actionModal.action, remarks
      })
      toast.success(`Department ${actionModal.action === 'approve' ? 'cleared' : 'rejected'}!`)
      setActionModal(null); setRemarks(''); fetchData()
    } catch (err) { toast.error(err.response?.data?.error || 'Action failed') }
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="stat-card"><p className="text-2xl font-bold text-white">{requests.length}</p><p className="text-xs text-surface-400">Pending Clearances</p></div>
        {departments.filter(d => d.name !== 'Faculty').map(d => (
          <div key={d.id} className="stat-card"><p className="text-lg font-bold text-white">{d.name}</p><p className="text-xs text-surface-400">Department</p></div>
        ))}
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-surface-700/50">
          <h2 className="text-lg font-semibold text-white">Department Clearance Requests</h2>
        </div>
        {requests.length === 0 ? (
          <div className="p-10 text-center text-surface-400"><HiOutlineCheckCircle className="w-12 h-12 mx-auto mb-3 text-emerald-500/50" /><p>No pending clearances!</p></div>
        ) : (
          <div className="divide-y divide-surface-700/30">
            {requests.map((req) => (
              <div key={req.id} className="p-6 hover:bg-surface-800/30 transition-colors">
                <div className="flex items-center justify-between mb-4">
                  <div><h3 className="text-white font-semibold">{req.student_name}</h3><p className="text-xs text-surface-400">Roll: {req.roll_no} | Request #{req.id}</p></div>
                  <div className="text-right"><p className="text-xs text-surface-400">{req.approved_count}/{req.total_departments} cleared</p></div>
                </div>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {req.approvals?.filter(a => a.department_name !== 'Faculty').map((a) => (
                    <div key={a.id} className={`p-3 rounded-xl border ${a.status === 'approved' ? 'bg-emerald-500/10 border-emerald-500/30' : a.status === 'rejected' ? 'bg-red-500/10 border-red-500/30' : 'bg-surface-800/50 border-surface-700/30'}`}>
                      <span className="text-xs font-semibold text-surface-200 block mb-2">{a.department_name}</span>
                      {a.status === 'pending' ? (
                        <div className="flex gap-1">
                          <button onClick={() => setActionModal({ requestId: req.id, departmentId: a.department_id, action: 'approve' })} className="flex-1 px-2 py-1 text-xs rounded-lg bg-emerald-500/15 text-emerald-400 hover:bg-emerald-500/25">Clear</button>
                          <button onClick={() => setActionModal({ requestId: req.id, departmentId: a.department_id, action: 'reject' })} className="flex-1 px-2 py-1 text-xs rounded-lg bg-red-500/15 text-red-400 hover:bg-red-500/25">Reject</button>
                        </div>
                      ) : (
                        <span className={`text-xs ${a.status === 'approved' ? 'text-emerald-400' : 'text-red-400'}`}>{a.status}</span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {actionModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setActionModal(null)}>
          <div className="glass-card p-6 w-full max-w-md mx-4 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <h3 className="text-lg font-semibold text-white mb-4">{actionModal.action === 'approve' ? '✅ Clear Department' : '❌ Reject'}</h3>
            <textarea value={remarks} onChange={(e) => setRemarks(e.target.value)} className="input-field h-24 resize-none" placeholder="Remarks..." />
            <div className="flex justify-end gap-3 mt-4">
              <button onClick={() => setActionModal(null)} className="btn-ghost">Cancel</button>
              <button onClick={handleAction} className={actionModal.action === 'approve' ? 'btn-success' : 'btn-danger'}>{actionModal.action === 'approve' ? 'Clear' : 'Reject'}</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
