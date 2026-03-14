import { Typography } from '@mui/material'
import InvoiceList from '../components/InvoiceList'

export default function Invoices() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Invoices</Typography>
      <Typography color="text.secondary" sx={{ mb: 1 }}>
        List of processed invoices. Use Match for three-way matching and Tax for tax assistance.
      </Typography>
      <InvoiceList />
    </>
  )
}
