import { useEffect, useState } from 'react'
import { getInvoices } from '../api'
import MatchButton from './MatchButton'
import TaxReportView from './TaxReportView'

export default function InvoiceList() {
  const [invoices, setInvoices] = useState([])
  const [loading, setLoading] = useState(true)

  const refresh = async () => {
    setLoading(true)
    try {
      const data = await getInvoices()
      setInvoices(data)
    } catch {
      setInvoices([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  if (loading) {
    return (
      <p className="text-sm text-gray-500">Loading invoices…</p>
    )
  }
  if (!invoices.length) {
    return (
      <div className="rounded-2xl border border-dashed border-gray-300 bg-white p-12 text-center">
        <p className="text-gray-500">No invoices yet.</p>
        <p className="mt-1 text-sm text-gray-400">Upload from Dashboard.</p>
      </div>
    )
  }

  return (
    <div className="overflow-hidden rounded-2xl border border-gray-200 bg-white shadow-sm ring-1 ring-gray-100">
      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-4 py-3 font-semibold text-gray-700">ID</th>
              <th className="px-4 py-3 font-semibold text-gray-700">Date</th>
              <th className="px-4 py-3 font-semibold text-gray-700">Vendor</th>
              <th className="px-4 py-3 font-semibold text-gray-700">Amount</th>
              <th className="px-4 py-3 font-semibold text-gray-700">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {invoices.map((inv) => (
              <tr key={inv.id} className="hover:bg-gray-25">
                <td className="whitespace-nowrap px-4 py-3 font-mono text-gray-600">
                  {inv.id}
                </td>
                <td className="whitespace-nowrap px-4 py-3 text-gray-700">
                  {inv.date ?? '—'}
                </td>
                <td className="max-w-[200px] truncate px-4 py-3 text-gray-900">
                  {inv.vendor ?? '—'}
                </td>
                <td className="whitespace-nowrap px-4 py-3 tabular-nums text-gray-700">
                  {inv.amount != null ? Number(inv.amount).toFixed(2) : '—'}
                </td>
                <td className="whitespace-nowrap px-4 py-3">
                  <div className="flex flex-wrap gap-2">
                    <MatchButton invoiceId={inv.id} />
                    <TaxReportView invoiceId={inv.id} />
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
