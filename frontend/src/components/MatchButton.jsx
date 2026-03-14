import { useState } from 'react'
import { runMatch } from '../api'

export default function MatchButton({ invoiceId }) {
  const [open, setOpen] = useState(false)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState(null)

  const handleRun = async () => {
    setLoading(true)
    setResult(null)
    try {
      const data = await runMatch({
        invoice_id: invoiceId,
        po_id: null,
        receipt_id: null,
      })
      setResult(data)
    } catch (err) {
      setResult({
        matched: false,
        message: err.response?.data?.detail || err.message,
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
        className="rounded-lg border border-gray-300 bg-white px-3 py-1.5 text-xs font-medium text-gray-700 shadow-sm hover:bg-gray-50"
      >
        Match
      </button>
      {open && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center bg-gray-900/40 p-4 backdrop-blur-sm"
          role="dialog"
          aria-modal
          aria-labelledby="match-title"
        >
          <div className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-2xl border border-gray-200 bg-white p-6 shadow-xl">
            <h2 id="match-title" className="text-lg font-semibold text-gray-900">
              Three-way match · Invoice #{invoiceId}
            </h2>
            <p className="mt-1 text-sm text-gray-500">
              Compare invoice vs PO / receipt (agents on backend).
            </p>
            <button
              type="button"
              onClick={handleRun}
              disabled={loading}
              className="mt-4 rounded-lg bg-violet-600 px-4 py-2 text-sm font-semibold text-white hover:bg-violet-700 disabled:opacity-50"
            >
              {loading ? 'Running…' : 'Run match'}
            </button>
            {result && (
              <div className="mt-4 rounded-lg bg-gray-50 p-3 text-sm">
                <p className="font-medium text-gray-900">
                  {result.matched ? 'Matched' : 'Mismatch'}: {result.message}
                </p>
                {result.details && (
                  <pre className="mt-2 max-h-40 overflow-auto rounded border border-gray-200 bg-white p-2 text-xs">
                    {JSON.stringify(result.details, null, 2)}
                  </pre>
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
