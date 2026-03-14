import { useState } from 'react'
import { Button, Dialog, DialogTitle, DialogContent, Typography } from '@mui/material'
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
      setReport({ summary: 'Error: ' + (err.response?.data?.detail || err.message) })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button size="small" variant="outlined" color="secondary" onClick={() => setOpen(true)}>
        Tax
      </Button>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Tax report (Invoice #{invoiceId})</DialogTitle>
        <DialogContent>
          <Button variant="contained" color="secondary" onClick={handleLoad} disabled={loading} sx={{ mb: 2 }}>
            {loading ? 'Generating…' : 'Generate tax report'}
          </Button>
          {report && (
            <>
              <Typography variant="body2">{report.summary ?? '—'}</Typography>
              {report.vat_amount != null && (
                <Typography variant="body2" sx={{ mt: 1 }}>VAT (10%): {Number(report.vat_amount).toFixed(2)}</Typography>
              )}
              {report.deductions && report.deductions.length > 0 && (
                <Typography variant="body2" sx={{ mt: 1 }}>
                  Deductions: {report.deductions.join(', ')}
                </Typography>
              )}
            </>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
