import InvoiceList from '../components/InvoiceList'

export default function Reports() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Reports</h1>
        <p className="mt-1 text-gray-500">
          Generate tax reports from invoice rows (Tax on each row).
        </p>
      </div>
      <InvoiceList />
    </div>
  )
}
