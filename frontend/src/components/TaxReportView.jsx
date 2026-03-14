import { useState } from 'react'
import { getTaxReport } from '../api'

export default function TaxReportView({ invoiceId }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)

  const handleLoad = async () => {
    setLoading(true)
    setReport(null)
    try {
      const data = await getTaxReport(invoiceId)
      setReport(data)
    } catch (err) {
      setReport({
        summary: 'Error: ' + (err.response?.data?.detail || err.message),
      })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <button
        type="button"
        onClick={() => setOpen(true)}
        className="rounded-lg border border-violet-200 bg-violet-50 px-3 py-1.5 text-xs font-medium text-violet-800 hover:bg-violet-100"
      >
        Tax
      </button>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal
        >
          <div className="w-full max-w-lg rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
            <h2 className="text-lg font-semibold text-gray-900">
              Tax report · Invoice #{invoiceId}
            </h2>
            <button
              type="button"
              onClick={handleLoad}
              disabled={loading}
              className="mt-4 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
            >
              {loading ? 'Generating…' : 'Generate tax report'}
            </button>
            {report && (
              <div className="mt-4 space-y-2 rounded-lg bg-gray-50 p-3 text-sm text-gray-800">
                <p>{report.summary ?? '—'}</p>
                {report.vat_amount != null && (
                  <p className="tabular-nums">
                    VAT (10%): {Number(report.vat_amount).toFixed(2)}
                  </p>
                )}
                {report.deductions?.length > 0 && (
                  <p>Deductions: {report.deductions.join(', ')}</p>
                )}
              </div>
            )}
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="mt-6 w-full rounded-lg border border-gray-300 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  )
}
