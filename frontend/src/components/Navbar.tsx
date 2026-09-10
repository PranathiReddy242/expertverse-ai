import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../contexts/AuthContext'

export default function Navbar() {
  const navigate = useNavigate()
  const { token, user, logout } = useAuth()
  const isAuthenticated = !!token
  const [menuOpen, setMenuOpen] = useState(false)

  const handleLogout = () => {
    logout()
    navigate('/login')
    setMenuOpen(false)
  }

  const navLinkClass = ({ isActive }: { isActive: boolean }) =>
    `rounded-full px-4 py-2 text-sm transition ${
      isActive ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
    }`

  const closeMenu = () => setMenuOpen(false)

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="text-xl font-semibold text-slate-900">ExpertVerse AI</div>

        {/* Mobile hamburger button */}
        <button
          onClick={() => setMenuOpen(!menuOpen)}
          className="flex flex-col gap-1.5 md:hidden"
          aria-label="Toggle menu"
        >
          <span className={`block h-0.5 w-6 bg-slate-700 transition-transform ${menuOpen ? 'translate-y-2 rotate-45' : ''}`} />
          <span className={`block h-0.5 w-6 bg-slate-700 transition-opacity ${menuOpen ? 'opacity-0' : ''}`} />
          <span className={`block h-0.5 w-6 bg-slate-700 transition-transform ${menuOpen ? '-translate-y-2 -rotate-45' : ''}`} />
        </button>

        {/* Desktop nav */}
        <div className="hidden items-center gap-4 md:flex">
          <NavLink to="/" className={navLinkClass}>Home</NavLink>
          <NavLink to="/experts" className={navLinkClass}>Experts</NavLink>
          <NavLink to="/chat" className={navLinkClass}>Chat</NavLink>
          <NavLink to="/book" className={navLinkClass}>Book</NavLink>
          {isAuthenticated ? (
            <>
              <NavLink to="/dashboard" className={navLinkClass}>Dashboard</NavLink>
              <NavLink to="/profile" className={navLinkClass}>Profile</NavLink>
              {user?.is_admin && (
                <NavLink to="/admin" className={navLinkClass}>Admin</NavLink>
              )}
              <button
                onClick={handleLogout}
                className="rounded-full bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
              >
                Logout
              </button>
            </>
          ) : (
            <>
              <NavLink to="/login" className={navLinkClass}>Login</NavLink>
              <NavLink to="/register" className={navLinkClass}>Register</NavLink>
            </>
          )}
        </div>
      </nav>

      {/* Mobile nav dropdown */}
      {menuOpen && (
        <div className="border-t border-slate-200 bg-white px-6 py-4 md:hidden">
          <div className="flex flex-col gap-2">
            <NavLink to="/" className={navLinkClass} onClick={closeMenu}>Home</NavLink>
            <NavLink to="/experts" className={navLinkClass} onClick={closeMenu}>Experts</NavLink>
            <NavLink to="/chat" className={navLinkClass} onClick={closeMenu}>Chat</NavLink>
            <NavLink to="/book" className={navLinkClass} onClick={closeMenu}>Book</NavLink>
            {isAuthenticated ? (
              <>
                <NavLink to="/dashboard" className={navLinkClass} onClick={closeMenu}>Dashboard</NavLink>
                <NavLink to="/profile" className={navLinkClass} onClick={closeMenu}>Profile</NavLink>
                {user?.is_admin && (
                  <NavLink to="/admin" className={navLinkClass} onClick={closeMenu}>Admin</NavLink>
                )}
                <button
                  onClick={handleLogout}
                  className="rounded-full bg-red-600 px-4 py-2 text-sm text-white hover:bg-red-700"
                >
                  Logout
                </button>
              </>
            ) : (
              <>
                <NavLink to="/login" className={navLinkClass} onClick={closeMenu}>Login</NavLink>
                <NavLink to="/register" className={navLinkClass} onClick={closeMenu}>Register</NavLink>
              </>
            )}
          </div>
        </div>
      )}
    </header>
  )
}
