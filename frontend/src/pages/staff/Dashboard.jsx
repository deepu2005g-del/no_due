/**
 * Staff Dashboard - Generate hall tickets for HOD-approved students.
 */
import { useState, useEffect } from 'react'
import API from '../../api/axios'
import toast from 'react-hot-toast'
import { HiOutlineTicket, HiOutlineDownload, HiOutlinePrinter } from 'react-icons/hi'

export default function StaffDashboard() {
  const [requests, setRequests] = useState([])
  const [loading, setLoading] = useState(true)
  const [hallTicket, setHallTicket] = useState(null)

  useEffect(() => { fetchData() }, [])

  const fetchData = async () => {
    try {
      const res = await API.get('/staff/approved')
      setRequests(res.data.requests || [])
    } catch (err) { toast.error('Failed to load') }
    finally { setLoading(false) }
  }

  const generateTicket = async (reqId) => {
    try {
      const res = await API.post(`/staff/hallticket/${reqId}`)
      toast.success(res.data.message)
      fetchData()
      viewTicket(reqId)
    } catch (err) { toast.error(err.response?.data?.error || 'Failed') }
  }

  const viewTicket = async (reqId) => {
    try {
      const res = await API.get(`/staff/hallticket/${reqId}`)
      setHallTicket(res.data.hall_ticket)
    } catch (err) { toast.error('Ticket not found') }
  }

  const printTicket = () => {
    const printWindow = window.open('', '_blank')
    printWindow.document.write(`<!DOCTYPE html><html><head><title>Hall Ticket</title>
      <style>body{font-family:Arial;padding:40px;max-width:700px;margin:0 auto}
      .header{text-align:center;border-bottom:3px solid #333;padding-bottom:20px;margin-bottom:20px}
      .header h1{font-size:24px;margin-bottom:5px}.header p{color:#666}
      .info{display:grid;grid-template-columns:1fr 1fr;gap:15px;margin:20px 0}
      .info div{padding:10px;background:#f5f5f5;border-radius:8px}
      .info label{font-size:12px;color:#666;display:block}.info span{font-weight:bold;font-size:14px}
      .ticket-no{text-align:center;font-size:20px;font-weight:bold;margin:30px 0;padding:15px;background:#e8f5e9;border-radius:8px;color:#2e7d32}
      .footer{margin-top:40px;text-align:center;color:#666;font-size:12px;border-top:1px solid #ddd;padding-top:15px}</style>
    </head><body>
      <div class="header"><h1>🎓 No-Due Clearance Hall Ticket</h1><p>Official Document</p></div>
      <div class="ticket-no">Ticket: ${hallTicket.ticket_number}</div>
      <div class="info">
        <div><label>Student Name</label><span>${hallTicket.student_name}</span></div>
        <div><label>Roll Number</label><span>${hallTicket.roll_no}</span></div>
        <div><label>Department</label><span>${hallTicket.department}</span></div>
        <div><label>Semester</label><span>${hallTicket.semester}</span></div>
        <div><label>Email</label><span>${hallTicket.student_email}</span></div>
        <div><label>Issued By</label><span>${hallTicket.issued_by_name}</span></div>
        <div><label>Issued Date</label><span>${new Date(hallTicket.issued_at).toLocaleDateString()}</span></div>
        <div><label>Status</label><span>✅ All Dues Cleared</span></div>
      </div>
      <div class="footer"><p>This is a computer-generated document.</p><p>Generated on ${new Date().toLocaleString()}</p></div>
    </body></html>`)
    printWindow.document.close()
    printWindow.print()
  }

  if (loading) return <div className="flex items-center justify-center h-64"><div className="w-10 h-10 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" /></div>

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="stat-card"><p className="text-2xl font-bold text-white">{requests.length}</p><p className="text-xs text-surface-400">Approved Students</p></div>
        <div className="stat-card"><p className="text-2xl font-bold text-white">{requests.filter(r => r.ticket_number).length}</p><p className="text-xs text-surface-400">Tickets Issued</p></div>
      </div>

      <div className="glass-card overflow-hidden">
        <div className="p-6 border-b border-surface-700/50">
          <h2 className="text-lg font-semibold text-white">Hall Ticket Management</h2>
          <p className="text-sm text-surface-400">Generate and print hall tickets for approved students</p>
        </div>

        {requests.length === 0 ? (
          <div className="p-10 text-center text-surface-400"><HiOutlineTicket className="w-12 h-12 mx-auto mb-3 text-surface-500" /><p>No approved students yet</p></div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-surface-800/50">
                <tr>
                  <th className="table-header">Student</th>
                  <th className="table-header">Roll No</th>
                  <th className="table-header">Department</th>
                  <th className="table-header">Ticket</th>
                  <th className="table-header text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-700/30">
                {requests.map((req) => (
                  <tr key={req.id} className="hover:bg-surface-800/30 transition-colors">
                    <td className="table-cell font-medium text-white">{req.student_name}</td>
                    <td className="table-cell text-surface-300">{req.roll_no}</td>
                    <td className="table-cell text-surface-300">{req.department}</td>
                    <td className="table-cell">{req.ticket_number ? <span className="badge-approved">{req.ticket_number}</span> : <span className="badge-pending">Not Generated</span>}</td>
                    <td className="table-cell text-right">
                      {req.ticket_number ? (
                        <button onClick={() => viewTicket(req.id)} className="px-3 py-1.5 text-xs font-medium rounded-lg bg-primary-500/15 text-primary-400 border border-primary-500/30 hover:bg-primary-500/25 flex items-center gap-1 ml-auto">
                          <HiOutlineDownload className="w-3.5 h-3.5" /> View
                        </button>
                      ) : (
                        <button onClick={() => generateTicket(req.id)} className="btn-success text-xs py-1.5 flex items-center gap-1 ml-auto">
                          <HiOutlineTicket className="w-3.5 h-3.5" /> Generate
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Hall Ticket Preview Modal */}
      {hallTicket && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50" onClick={() => setHallTicket(null)}>
          <div className="glass-card p-6 w-full max-w-lg mx-4 animate-slide-up" onClick={(e) => e.stopPropagation()}>
            <div className="text-center mb-6">
              <h2 className="text-xl font-bold text-white">🎓 Hall Ticket</h2>
              <p className="text-primary-400 font-mono text-lg mt-1">{hallTicket.ticket_number}</p>
            </div>
            <div className="grid grid-cols-2 gap-4 mb-6">
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Name</p><p className="text-sm font-semibold text-white">{hallTicket.student_name}</p></div>
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Roll No</p><p className="text-sm font-semibold text-white">{hallTicket.roll_no}</p></div>
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Department</p><p className="text-sm font-semibold text-white">{hallTicket.department}</p></div>
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Semester</p><p className="text-sm font-semibold text-white">{hallTicket.semester}</p></div>
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Issued By</p><p className="text-sm font-semibold text-white">{hallTicket.issued_by_name}</p></div>
              <div className="p-3 rounded-xl bg-surface-800/50"><p className="text-xs text-surface-400">Date</p><p className="text-sm font-semibold text-white">{new Date(hallTicket.issued_at).toLocaleDateString()}</p></div>
            </div>
            <div className="flex gap-3">
              <button onClick={printTicket} className="btn-primary flex-1 flex items-center justify-center gap-2"><HiOutlinePrinter className="w-4 h-4" /> Print</button>
              <button onClick={() => setHallTicket(null)} className="btn-ghost flex-1">Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
