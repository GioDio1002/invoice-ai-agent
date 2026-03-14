import { Typography, Paper, Box } from '@mui/material'
import UploadForm from '../components/UploadForm'

export default function Home() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>Dashboard</Typography>
      <Typography color="text.secondary" sx={{ mb: 2 }}>
        Upload an invoice (PDF or image) to extract data and create a voucher.
      </Typography>
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6">Upload invoice</Typography>
        <UploadForm />
      </Paper>
      <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
        Go to Invoices to view all extracted invoices, run three-way matching, or generate tax reports.
      </Typography>
    </Box>
  )
}
