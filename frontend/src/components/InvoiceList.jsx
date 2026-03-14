import { useEffect, useState } from 'react'
import { Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper, Typography } from '@mui/material'
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
    } catch (err) {
      setInvoices([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    refresh()
  }, [])

  if (loading) return <Typography>Loading invoices…</Typography>
  if (!invoices.length) return <Typography>No invoices yet. Upload one from the Dashboard.</Typography>

  return (
    <TableContainer component={Paper} sx={{ mt: 2 }}>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>ID</TableCell>
            <TableCell>Date</TableCell>
            <TableCell>Vendor</TableCell>
            <TableCell>Amount</TableCell>
            <TableCell>Actions</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {invoices.map((inv) => (
            <TableRow key={inv.id}>
              <TableCell>{inv.id}</TableCell>
              <TableCell>{inv.date ?? '—'}</TableCell>
              <TableCell>{inv.vendor ?? '—'}</TableCell>
              <TableCell>{inv.amount != null ? Number(inv.amount).toFixed(2) : '—'}</TableCell>
              <TableCell>
                <MatchButton invoiceId={inv.id} />
                <TaxReportView invoiceId={inv.id} />
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  )
}
