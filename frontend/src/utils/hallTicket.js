export function printHallTicket(hallTicket) {
  const printWindow = window.open('', '_blank')
  if (!printWindow) return
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
    </body></html>`)
  printWindow.document.close()
  printWindow.print()
}
