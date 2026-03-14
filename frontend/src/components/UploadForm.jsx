import { useState } from 'react'
import { uploadInvoice } from '../api'

export default function UploadForm({ onUploaded }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!file) return
    setError(null)
    setResult(null)
    setLoading(true)
    try {
      const data = await uploadInvoice(file)
      setResult(data)
      onUploaded?.(data)
    } catch (err) {
      setError(err.response?.data?.detail || err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label className="mb-2 block text-sm font-medium text-gray-700">
          File
        </label>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <label className="inline-flex cursor-pointer items-center justify-center rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50">
            <input
              type="file"
              accept="application/pdf,image/*"
              className="sr-only"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
            />
            Choose PDF or image
          </label>
          <span className="truncate text-sm text-gray-500">
            {file ? file.name : 'No file selected'}
          </span>
        </div>
      </div>
      <button
        type="submit"
        disabled={!file || loading}
        className="inline-flex items-center justify-center rounded-lg bg-violet-600 px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-violet-700 disabled:pointer-events-none disabled:opacity-50"
      >
        {loading ? (
          <span className="flex items-center gap-2">
            <svg
              className="h-4 w-4 animate-spin"
              viewBox="0 0 24 24"
              aria-hidden
            >
              <circle
                className="opacity-25"
                cx="12"
                cy="12"
                r="10"
                stroke="currentColor"
                strokeWidth="4"
                fill="none"
              />
              <path
                className="opacity-75"
                fill="currentColor"
                d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
              />
            </svg>
            Running workflow…
          </span>
        ) : (
          'Upload & extract'
        )}
      </button>
      {error && (
        <div
          className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800"
          role="alert"
        >
          {error}
        </div>
      )}
      {result && (
        <div className="space-y-3 rounded-lg border border-emerald-200 bg-emerald-50/80 px-4 py-3 text-sm text-emerald-900">
          <p className="font-medium">
            Invoice saved (id {result.id}) · {result.vendor ?? '—'} ·{' '}
            {result.amount != null ? Number(result.amount).toFixed(2) : '—'}
          </p>
          {result.workflow_steps?.length > 0 && (
            <div>
              <p className="mb-1 text-xs font-semibold uppercase tracking-wide text-emerald-800">
                LangGraph steps
              </p>
              <ol className="list-inside list-decimal space-y-0.5 text-xs text-emerald-900/90">
                {result.workflow_steps.map((s, i) => (
                  <li key={i}>{s}</li>
                ))}
              </ol>
            </div>
          )}
        </div>
      )}
    </form>
  )
}
