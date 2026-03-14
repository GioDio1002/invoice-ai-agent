import { Link as RouterLink } from 'react-router-dom'
import { AppBar, Toolbar, Typography, Link, Container } from '@mui/material'

export default function Layout({ children }) {
  return (
    <>
      <AppBar position="static">
        <Toolbar>
          <Typography variant="h6" sx={{ flexGrow: 1 }}>
            <Link component={RouterLink} to="/" color="inherit" underline="none">
              AI Finance Robot
            </Link>
          </Typography>
          <Link component={RouterLink} to="/" color="inherit" sx={{ mx: 1 }}>Dashboard</Link>
          <Link component={RouterLink} to="/invoices" color="inherit" sx={{ mx: 1 }}>Invoices</Link>
          <Link component={RouterLink} to="/reports" color="inherit" sx={{ mx: 1 }}>Reports</Link>
        </Toolbar>
      </AppBar>
      <Container maxWidth="lg" sx={{ py: 3 }}>
        {children}
      </Container>
    </>
  )
}
