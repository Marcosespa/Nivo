import { useLocation } from 'react-router-dom'
import { Bell, Menu } from 'lucide-react'
import { useAuthStore } from '../../store/authStore'

interface HeaderProps {
  onMobileMenuOpen: () => void
}

const pageTitles: Record<string, string> = {
  '/dashboard': 'Dashboard',
  '/wallet': 'Mi Wallet',
  '/payments': 'Pagos',
  '/profile': 'Perfil',
}

function UserAvatar({ name }: { name: string }) {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-sm font-semibold shadow-lg flex-shrink-0">
      {initials}
    </div>
  )
}

export default function Header({ onMobileMenuOpen }: HeaderProps) {
  const location = useLocation()
  const user = useAuthStore((s) => s.user)

  const pageTitle = pageTitles[location.pathname] || 'Nivo'

  return (
    <header className="flex items-center justify-between px-4 sm:px-6 py-4 bg-gray-950/80 backdrop-blur-sm border-b border-gray-800 sticky top-0 z-30">
      {/* Left: mobile menu + title */}
      <div className="flex items-center gap-3">
        <button
          onClick={onMobileMenuOpen}
          className="p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors lg:hidden"
          aria-label="Abrir menú"
        >
          <Menu className="w-5 h-5" />
        </button>
        <h1 className="text-lg font-semibold text-white">{pageTitle}</h1>
      </div>

      {/* Right: notification bell + avatar */}
      <div className="flex items-center gap-3">
        <button
          className="relative p-2 rounded-lg text-gray-400 hover:text-white hover:bg-gray-800 transition-colors"
          aria-label="Notificaciones"
        >
          <Bell className="w-5 h-5" />
          {/* Notification dot */}
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-indigo-500 rounded-full" />
        </button>

        {user && (
          <div className="flex items-center gap-2.5">
            <UserAvatar name={user.full_name} />
            <div className="hidden sm:flex flex-col">
              <span className="text-sm font-medium text-white leading-tight">
                {user.full_name}
              </span>
              <span className="text-xs text-gray-500 leading-tight">{user.phone}</span>
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
