import { Routes, Route } from 'react-router-dom'
import { ThemeProvider, createTheme, CssBaseline } from '@mui/material'
import Layout from './components/Layout'
import Home from './pages/Home'
import Invoices from './pages/Invoices'
import Reports from './pages/Reports'

const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' },
    secondary: { main: '#2e7d32' },
  },
})

function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Layout>
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/invoices" element={<Invoices />} />
          <Route path="/reports" element={<Reports />} />
        </Routes>
      </Layout>
    </ThemeProvider>
  )
}

export default App
