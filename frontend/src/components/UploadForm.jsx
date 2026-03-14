import { useState } from 'react'
import { Button, TextField, Box, Alert, CircularProgress } from '@mui/material'
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
    <Box component="form" onSubmit={handleSubmit} sx={{ mt: 2 }}>
      <TextField
        type="file"
        inputProps={{ accept: 'application/pdf,image/*' }}
        onChange={(e) => setFile(e.target.files?.[0] || null)}
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained" disabled={!file || loading} sx={{ mt: 1 }}>
        {loading ? <CircularProgress size={24} /> : 'Upload & Extract Invoice'}
      </Button>
      {error && <Alert severity="error" sx={{ mt: 2 }}>{error}</Alert>}
      {result && (
        <Alert severity="success" sx={{ mt: 2 }}>
          Invoice saved (id: {result.id}). Vendor: {result.vendor ?? '—'}, Amount: {result.amount ?? '—'}
        </Alert>
      )}
    </Box>
  )
}
