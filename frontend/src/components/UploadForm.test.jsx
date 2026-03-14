import { render, screen } from '@testing-library/react'
import UploadForm from './UploadForm'

test('renders upload invoice button', () => {
  render(<UploadForm />)
  expect(screen.getByText(/Upload & extract/i)).toBeInTheDocument()
})
