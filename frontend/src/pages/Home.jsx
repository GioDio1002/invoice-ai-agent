import UploadForm from '../components/UploadForm'

export default function Home() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold tracking-tight text-gray-900 sm:text-3xl">
          Dashboard
        </h1>
        <p className="mt-2 max-w-2xl text-gray-500">
          Upload an invoice (PDF or image). A LangGraph pipeline runs ingest → OCR →
          extract → validate before saving.
        </p>
      </div>
      <section className="rounded-2xl border border-gray-200 bg-white p-6 shadow-sm ring-1 ring-gray-100 sm:p-8">
        <h2 className="text-base font-semibold text-gray-900">Upload invoice</h2>
        <p className="mt-1 text-sm text-gray-500">
          Extraction uses your local Ollama or OpenAI (see backend env).
        </p>
        <div className="mt-6">
          <UploadForm />
        </div>
      </section>
      <p className="text-sm text-gray-500">
        Open <span className="font-medium text-gray-700">Invoices</span> for matching
        and tax assistance.
      </p>
    </div>
  )
}
