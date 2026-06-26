import { NavLink } from 'react-router-dom'

const links = [
  { label: 'Home', path: '/' },
  { label: 'Experts', path: '/experts' },
  { label: 'Chat', path: '/chat' },
  { label: 'Dashboard', path: '/dashboard' },
]

export default function Navbar() {
  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur">
      <nav className="mx-auto flex max-w-6xl items-center justify-between px-6 py-4">
        <div className="text-xl font-semibold text-slate-900">ExpertVerse AI</div>
        <div className="flex items-center gap-4">
          {links.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `rounded-full px-4 py-2 text-sm transition ${
                  isActive ? 'bg-indigo-600 text-white' : 'text-slate-700 hover:bg-slate-100'
                }`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </div>
      </nav>
    </header>
  )
}
