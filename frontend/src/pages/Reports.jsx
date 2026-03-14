import { Typography } from '@mui/material'
import InvoiceList from '../components/InvoiceList'

export default function Reports() {
  return (
    <>
      <Typography variant="h4" gutterBottom>Reports</Typography>
      <Typography color="text.secondary" sx={{ mb: 1 }}>
        Generate tax reports from the Invoices table (Tax button per row). Match and tax data appear in dialogs.
      </Typography>
      <InvoiceList />
    </>
  )
}
