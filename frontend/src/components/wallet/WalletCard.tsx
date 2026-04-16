import { useState } from 'react'
import { Eye, EyeOff, ArrowDownToLine, ArrowUpFromLine } from 'lucide-react'
import type { Wallet } from '../../types'

interface WalletCardProps {
  wallet: Wallet
  onTopUp: () => void
  onWithdraw: () => void
}

function formatCOP(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function maskAccount(account: string): string {
  if (account.length <= 4) return account
  return `••••  ••••  ••••  ${account.slice(-4)}`
}

export default function WalletCard({ wallet, onTopUp, onWithdraw }: WalletCardProps) {
  const [balanceVisible, setBalanceVisible] = useState(true)

  return (
    <div className="relative rounded-2xl overflow-hidden">
      {/* Gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-indigo-700 via-indigo-800 to-purple-900" />

      {/* Decorative circles */}
      <div className="absolute -top-12 -right-12 w-48 h-48 rounded-full bg-white/5" />
      <div className="absolute -bottom-10 -left-10 w-36 h-36 rounded-full bg-white/5" />
      <div className="absolute top-1/2 right-8 w-24 h-24 rounded-full bg-indigo-500/20" />

      {/* Card content */}
      <div className="relative px-6 py-7 space-y-6">
        {/* Top row */}
        <div className="flex items-start justify-between">
          <div>
            <p className="text-indigo-200 text-xs font-medium uppercase tracking-widest mb-1">
              Saldo disponible
            </p>
            <div className="flex items-center gap-3">
              <span className="text-3xl font-bold text-white tracking-tight">
                {balanceVisible ? formatCOP(wallet.balance) : '$ ••••••'}
              </span>
              <button
                onClick={() => setBalanceVisible((v) => !v)}
                className="p-1.5 rounded-lg text-indigo-300 hover:text-white hover:bg-white/10 transition-colors"
                aria-label={balanceVisible ? 'Ocultar saldo' : 'Mostrar saldo'}
              >
                {balanceVisible ? (
                  <EyeOff className="w-4 h-4" />
                ) : (
                  <Eye className="w-4 h-4" />
                )}
              </button>
            </div>
          </div>

          {/* Currency badge */}
          <span className="px-2.5 py-1 rounded-lg bg-white/10 text-indigo-200 text-xs font-semibold">
            {wallet.currency}
          </span>
        </div>

        {/* Account number */}
        <div>
          <p className="text-indigo-300/70 text-xs mb-1">Número de cuenta</p>
          <p className="text-indigo-100 font-mono text-sm tracking-widest">
            {maskAccount(wallet.account_number)}
          </p>
        </div>

        {/* Action buttons */}
        <div className="flex gap-3">
          <button
            onClick={onTopUp}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors border border-white/10"
          >
            <ArrowDownToLine className="w-4 h-4" />
            Recargar
          </button>
          <button
            onClick={onWithdraw}
            className="flex-1 flex items-center justify-center gap-2 py-2.5 rounded-xl bg-white/10 hover:bg-white/20 text-white text-sm font-medium transition-colors border border-white/10"
          >
            <ArrowUpFromLine className="w-4 h-4" />
            Retirar
          </button>
        </div>
      </div>
    </div>
  )
}
