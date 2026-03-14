import axios from 'axios'

const baseURL = import.meta.env.VITE_API_URL || '/api'
export const api = axios.create({ baseURL })

export async function uploadFile(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/upload-file', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function uploadInvoice(file) {
  const form = new FormData()
  form.append('file', file)
  const { data } = await api.post('/upload-invoice', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getInvoices() {
  const { data } = await api.get('/invoices')
  return data
}

export async function runMatch(body) {
  const { data } = await api.post('/match', body)
  return data
}

export async function getTaxReport(invoiceId) {
  const { data } = await api.post('/tax-assist', { invoice_id: invoiceId })
  return data
}
