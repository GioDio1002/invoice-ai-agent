import { NavLink } from 'react-router-dom'

const navClass = ({ isActive }) =>
  [
    'rounded-lg px-3 py-2 text-sm font-medium transition-colors',
    isActive
      ? 'bg-violet-50 text-violet-700 ring-1 ring-violet-200'
      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900',
  ].join(' ')

export default function Layout({ children }) {
  return (
    <div className="min-h-screen bg-gray-50">
      <header className="sticky top-0 z-40 border-b border-gray-200 bg-white/80 backdrop-blur-md">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4 px-4 py-3 sm:px-6">
          <NavLink
            to="/"
            className="text-lg font-semibold tracking-tight text-gray-900"
          >
            AI Finance Robot
          </NavLink>
          <nav className="flex flex-wrap items-center gap-1">
            <NavLink to="/" className={navClass} end>
              Dashboard
            </NavLink>
            <NavLink to="/invoices" className={navClass}>
              Invoices
            </NavLink>
            <NavLink to="/reports" className={navClass}>
              Reports
            </NavLink>
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-8 sm:px-6">{children}</main>
    </div>
  )
}
