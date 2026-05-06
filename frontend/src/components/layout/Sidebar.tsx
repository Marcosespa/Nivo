import { NavLink, useNavigate } from 'react-router-dom'
import {
  LayoutDashboard,
  Wallet,
  Send,
  ShieldCheck,
  LogOut,
  Shield,
  X,
} from 'lucide-react'
import { useAuthStore } from '../../store/authStore'
import clsx from 'clsx'

interface SidebarProps {
  mobileOpen: boolean
  onMobileClose: () => void
}

const navItems = [
  { to: '/dashboard', label: 'Consola', icon: LayoutDashboard },
  { to: '/wallet', label: 'Wallet y retiros', icon: Wallet },
  { to: '/payments', label: 'Pagos', icon: Send },
  { to: '/profile', label: 'Auth, KYC y Crypto', icon: ShieldCheck },
]

export default function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  const clearSession = useAuthStore((s) => s.clearSession)
  const navigate = useNavigate()

  const handleLogout = () => {
    clearSession()
    navigate('/login', { replace: true })
  }

  const sidebarContent = (
    <div className="flex flex-col h-full">
      {/* Logo */}
      <div className="flex items-center gap-3 px-6 py-6 border-b border-gray-800">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 flex items-center justify-center shadow-lg shadow-teal-500/20">
          <Shield className="w-5 h-5 text-white" />
        </div>
        <div>
          <span className="text-xl font-bold text-white tracking-tight">Nivo</span>
          <p className="text-xs text-gray-500">Backend console</p>
        </div>

        {/* Mobile close button */}
        <button
          onClick={onMobileClose}
          className="ml-auto p-1.5 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors lg:hidden"
          aria-label="Cerrar menú"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto">
        {navItems.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            onClick={onMobileClose}
            className={({ isActive }) =>
              clsx(
                'flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all duration-150',
                isActive
                  ? 'bg-teal-500/15 text-teal-300 border border-teal-500/30'
                  : 'text-gray-400 hover:text-white hover:bg-gray-800/70'
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  className={clsx(
                    'w-5 h-5 flex-shrink-0',
                    isActive ? 'text-teal-300' : 'text-gray-500'
                  )}
                />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      {/* Logout */}
      <div className="px-3 py-4 border-t border-gray-800">
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 w-full px-3 py-2.5 rounded-xl text-sm font-medium text-gray-400 hover:text-red-400 hover:bg-red-500/10 transition-all duration-150"
        >
          <LogOut className="w-5 h-5 flex-shrink-0" />
          Cerrar sesión
        </button>
      </div>
    </div>
  )

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="hidden lg:flex flex-col w-64 flex-shrink-0 bg-gray-900 border-r border-gray-800 h-screen sticky top-0">
        {sidebarContent}
      </aside>

      {/* Mobile overlay */}
      {mobileOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          {/* Backdrop */}
          <div
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onMobileClose}
          />
          {/* Drawer */}
          <aside className="absolute left-0 top-0 bottom-0 w-72 bg-gray-900 border-r border-gray-800 flex flex-col animate-slide-in">
            {sidebarContent}
          </aside>
        </div>
      )}
    </>
  )
}
