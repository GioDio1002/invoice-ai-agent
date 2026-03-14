import { useState } from 'react'
import { Button, Dialog, DialogTitle, DialogContent, Typography } from '@mui/material'
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
      setResult({ matched: false, message: err.response?.data?.detail || err.message })
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <Button size="small" variant="outlined" onClick={() => setOpen(true)} sx={{ mr: 1 }}>
        Match
      </Button>
      <Dialog open={open} onClose={() => setOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Three-way match (Invoice #{invoiceId})</DialogTitle>
        <DialogContent>
          <Button variant="contained" onClick={handleRun} disabled={loading} sx={{ mb: 2 }}>
            {loading ? 'Running…' : 'Run match'}
          </Button>
          {result && (
            <Typography variant="body2">
              {result.matched ? '✓ Matched' : '✗ Mismatch'}: {result.message}
              {result.details && (
                <pre style={{ fontSize: 12, overflow: 'auto' }}>
                  {JSON.stringify(result.details, null, 2)}
                </pre>
              )}
            </Typography>
          )}
        </DialogContent>
      </Dialog>
    </>
  )
}
