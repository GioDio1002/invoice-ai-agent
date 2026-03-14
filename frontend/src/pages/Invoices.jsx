import InvoiceList from '../components/InvoiceList'

export default function Invoices() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Invoices</h1>
        <p className="mt-1 text-gray-500">
          Processed invoices — Match (three-way) and Tax per row.
        </p>
      </div>
      <InvoiceList />
    </div>
  )
}
