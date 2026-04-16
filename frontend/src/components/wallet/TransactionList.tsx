import { ArrowDownLeft, ArrowUpRight, Clock, CheckCircle, XCircle } from 'lucide-react'
import clsx from 'clsx'
import type { Transaction } from '../../types'

interface TransactionListProps {
  transactions: Transaction[]
  loading?: boolean
  limit?: number
  emptyMessage?: string
}

function formatCOP(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return new Intl.DateTimeFormat('es-CO', {
    day: '2-digit',
    month: 'short',
    hour: '2-digit',
    minute: '2-digit',
  }).format(date)
}

function StatusIcon({ status }: { status: Transaction['status'] }) {
  if (status === 'completed') return <CheckCircle className="w-3.5 h-3.5 text-emerald-400" />
  if (status === 'failed') return <XCircle className="w-3.5 h-3.5 text-red-400" />
  return <Clock className="w-3.5 h-3.5 text-yellow-400" />
}

// Loading skeleton row
function SkeletonRow() {
  return (
    <div className="flex items-center gap-4 py-3.5 px-4 animate-pulse">
      <div className="w-10 h-10 rounded-full bg-gray-800 flex-shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="h-3.5 bg-gray-800 rounded w-36" />
        <div className="h-3 bg-gray-800 rounded w-24" />
      </div>
      <div className="h-4 bg-gray-800 rounded w-20" />
    </div>
  )
}

function EmptyState({ message }: { message: string }) {
  return (
    <div className="flex flex-col items-center justify-center py-12 text-center">
      <div className="w-14 h-14 rounded-2xl bg-gray-800/60 flex items-center justify-center mb-3">
        <ArrowDownLeft className="w-7 h-7 text-gray-600" />
      </div>
      <p className="text-gray-400 text-sm font-medium">{message}</p>
      <p className="text-gray-600 text-xs mt-1">Tus movimientos aparecerán aquí</p>
    </div>
  )
}

export default function TransactionList({
  transactions,
  loading = false,
  limit,
  emptyMessage = 'Sin transacciones aún',
}: TransactionListProps) {
  const displayed = limit ? transactions.slice(0, limit) : transactions

  if (loading) {
    return (
      <div className="divide-y divide-gray-800">
        {Array.from({ length: 4 }).map((_, i) => (
          <SkeletonRow key={i} />
        ))}
      </div>
    )
  }

  if (displayed.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <div className="divide-y divide-gray-800/60">
      {displayed.map((tx) => {
        const isCredit = tx.type === 'credit'

        return (
          <div
            key={tx.id}
            className="flex items-center gap-4 py-3.5 px-4 hover:bg-gray-800/30 transition-colors rounded-xl -mx-4"
          >
            {/* Icon */}
            <div
              className={clsx(
                'w-10 h-10 rounded-full flex items-center justify-center flex-shrink-0',
                isCredit
                  ? 'bg-emerald-500/15 text-emerald-400'
                  : 'bg-red-500/15 text-red-400'
              )}
            >
              {isCredit ? (
                <ArrowDownLeft className="w-5 h-5" />
              ) : (
                <ArrowUpRight className="w-5 h-5" />
              )}
            </div>

            {/* Info */}
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {tx.description || (isCredit ? 'Pago recibido' : 'Pago enviado')}
              </p>
              <div className="flex items-center gap-2 mt-0.5">
                {tx.counterpart_name && (
                  <span className="text-xs text-gray-500 truncate">
                    {tx.counterpart_name}
                  </span>
                )}
                <span className="text-xs text-gray-600">
                  {formatDate(tx.created_at)}
                </span>
                <StatusIcon status={tx.status} />
              </div>
            </div>

            {/* Amount */}
            <div
              className={clsx(
                'text-sm font-semibold tabular-nums flex-shrink-0',
                isCredit ? 'text-emerald-400' : 'text-red-400'
              )}
            >
              {isCredit ? '+' : '-'}
              {formatCOP(tx.amount)}
            </div>
          </div>
        )
      })}
    </div>
  )
}
