/**
 * StatusTracker - Visual pipeline showing request progress.
 * Displays each step in the workflow with animated transitions.
 */

const steps = [
  { key: 'submitted', label: 'Submitted' },
  { key: 'faculty', label: 'Faculty Review' },
  { key: 'departments', label: 'Dept. Clearance' },
  { key: 'hod', label: 'HOD Approval' },
  { key: 'hallticket', label: 'Hall Ticket' },
]

// Map request status to step index
const statusToStep = {
  pending: 0,
  resubmitted: 0,
  faculty_approved: 1,
  departments_cleared: 2,
  hod_approved: 3,
  rejected: -1,
}

export default function StatusTracker({ status }) {
  const currentStep = statusToStep[status] ?? 0
  const isRejected = status === 'rejected'

  return (
    <div className="py-4">
      <div className="flex items-center justify-between">
        {steps.map((step, index) => {
          const isCompleted = !isRejected && currentStep >= index
          const isCurrent = !isRejected && currentStep === index
          const isLast = index === steps.length - 1

          return (
            <div key={step.key} className="flex items-center flex-1 last:flex-none">
              {/* Step circle */}
              <div className="flex flex-col items-center">
                <div
                  className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-sm transition-all duration-500
                    ${isRejected ? 'bg-red-500/20 border-2 border-red-500 text-red-400' :
                      isCompleted ? 'bg-gradient-to-br from-emerald-400 to-emerald-600 text-white shadow-lg shadow-emerald-500/30' :
                      isCurrent ? 'bg-primary-500/20 border-2 border-primary-500 text-primary-400 animate-pulse-slow' :
                      'bg-surface-700 border-2 border-surface-600 text-surface-400'}`}
                >
                  {isRejected ? '✕' : isCompleted && currentStep > index ? '✓' : index + 1}
                </div>
                <span className={`text-xs mt-2 font-medium text-center
                  ${isCompleted ? 'text-emerald-400' : isCurrent ? 'text-primary-400' : 'text-surface-500'}`}>
                  {step.label}
                </span>
              </div>

              {/* Connector line */}
              {!isLast && (
                <div className="flex-1 mx-2 h-0.5 rounded-full overflow-hidden bg-surface-700">
                  <div
                    className={`h-full transition-all duration-700 ease-out rounded-full
                      ${isCompleted && currentStep > index ? 'bg-gradient-to-r from-emerald-400 to-emerald-500 w-full' : 'w-0'}`}
                  />
                </div>
              )}
            </div>
          )
        })}
      </div>
      {isRejected && (
        <div className="mt-3 text-center">
          <span className="badge-rejected text-sm">Request Rejected</span>
        </div>
      )}
    </div>
  )
}
