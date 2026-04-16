import { useNavigate } from 'react-router-dom'
import {
  User,
  Phone,
  Mail,
  Calendar,
  LogOut,
  CheckCircle,
  Clock,
  XCircle,
  Shield,
  Copy,
  Check,
} from 'lucide-react'
import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import Button from '../components/common/Button'
import { useAuthStore } from '../store/authStore'
import type { User as UserType } from '../types'
import clsx from 'clsx'

function KycBadge({ status }: { status: UserType['kyc_status'] }) {
  const config = {
    verified: {
      label: 'Verificado',
      icon: CheckCircle,
      className: 'bg-emerald-500/15 text-emerald-400 border-emerald-500/30',
    },
    pending: {
      label: 'Pendiente',
      icon: Clock,
      className: 'bg-yellow-500/15 text-yellow-400 border-yellow-500/30',
    },
    rejected: {
      label: 'Rechazado',
      icon: XCircle,
      className: 'bg-red-500/15 text-red-400 border-red-500/30',
    },
  }[status]

  const Icon = config.icon

  return (
    <span
      className={clsx(
        'inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-semibold border',
        config.className
      )}
    >
      <Icon className="w-3.5 h-3.5" />
      KYC {config.label}
    </span>
  )
}

function InfoRow({
  icon: Icon,
  label,
  value,
  copyable = false,
}: {
  icon: React.ElementType
  label: string
  value: string
  copyable?: boolean
}) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(value)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="flex items-center gap-4 py-3.5 border-b border-gray-800/60 last:border-0">
      <div className="w-9 h-9 rounded-xl bg-gray-800 flex items-center justify-center flex-shrink-0">
        <Icon className="w-4 h-4 text-gray-400" />
      </div>
      <div className="flex-1 min-w-0">
        <p className="text-xs text-gray-500 font-medium">{label}</p>
        <p className="text-sm text-white font-medium mt-0.5 truncate">{value}</p>
      </div>
      {copyable && (
        <button
          onClick={handleCopy}
          className="p-1.5 rounded-lg text-gray-500 hover:text-gray-300 hover:bg-gray-800 transition-colors"
          aria-label="Copiar"
        >
          {copied ? (
            <Check className="w-3.5 h-3.5 text-emerald-400" />
          ) : (
            <Copy className="w-3.5 h-3.5" />
          )}
        </button>
      )}
    </div>
  )
}

function UserAvatar({ name }: { name: string }) {
  const initials = name
    .split(' ')
    .map((n) => n[0])
    .slice(0, 2)
    .join('')
    .toUpperCase()

  return (
    <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center text-white text-2xl font-bold shadow-xl shadow-indigo-500/25">
      {initials}
    </div>
  )
}

function formatDate(dateStr: string): string {
  return new Intl.DateTimeFormat('es-CO', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  }).format(new Date(dateStr))
}

export default function ProfilePage() {
  const user = useAuthStore((s) => s.user)
  const logout = useAuthStore((s) => s.logout)
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  if (!user) return null

  return (
    <Layout>
      <div className="max-w-2xl space-y-6">
        {/* Profile header card */}
        <Card variant="gradient">
          <div className="flex items-center gap-5">
            <UserAvatar name={user.full_name} />
            <div className="flex-1 min-w-0">
              <h2 className="text-xl font-bold text-white truncate">{user.full_name}</h2>
              <p className="text-indigo-300 text-sm mt-0.5">{user.phone}</p>
              <div className="mt-3">
                <KycBadge status={user.kyc_status} />
              </div>
            </div>
          </div>
        </Card>

        {/* Account info */}
        <Card>
          <div className="flex items-center gap-2 mb-2">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/15 flex items-center justify-center">
              <User className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <h3 className="text-sm font-semibold text-white">Información de la cuenta</h3>
          </div>

          <div className="-mx-2">
            <InfoRow
              icon={User}
              label="Nombre completo"
              value={user.full_name}
            />
            <InfoRow
              icon={Phone}
              label="Número de celular"
              value={user.phone}
              copyable
            />
            {user.email && (
              <InfoRow
                icon={Mail}
                label="Correo electrónico"
                value={user.email}
              />
            )}
            <InfoRow
              icon={Calendar}
              label="Miembro desde"
              value={formatDate(user.created_at)}
            />
            <InfoRow
              icon={Shield}
              label="ID de usuario"
              value={user.id}
              copyable
            />
          </div>
        </Card>

        {/* KYC status detail */}
        <Card>
          <div className="flex items-center gap-2 mb-4">
            <div className="w-7 h-7 rounded-lg bg-indigo-500/15 flex items-center justify-center">
              <Shield className="w-3.5 h-3.5 text-indigo-400" />
            </div>
            <h3 className="text-sm font-semibold text-white">Estado KYC</h3>
          </div>

          <div className="flex items-start gap-4">
            <KycBadge status={user.kyc_status} />
            <div className="flex-1">
              {user.kyc_status === 'verified' && (
                <p className="text-sm text-gray-400">
                  Tu identidad ha sido verificada. Tienes acceso completo a todas las funciones de Nivo.
                </p>
              )}
              {user.kyc_status === 'pending' && (
                <p className="text-sm text-gray-400">
                  Tu verificación está en proceso. Esto puede tomar hasta 24 horas.
                </p>
              )}
              {user.kyc_status === 'rejected' && (
                <p className="text-sm text-gray-400">
                  Tu verificación fue rechazada. Contacta al soporte para más información.
                </p>
              )}
            </div>
          </div>
        </Card>

        {/* Logout */}
        <div className="pt-2">
          <Button
            variant="danger"
            onClick={handleLogout}
            fullWidth
            size="lg"
          >
            <LogOut className="w-4 h-4" />
            Cerrar sesión
          </Button>
        </div>
      </div>
    </Layout>
  )
}
