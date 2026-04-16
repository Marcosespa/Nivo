import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Send, TrendingUp, TrendingDown, Wallet as WalletIcon, RefreshCw } from 'lucide-react'
import Layout from '../components/layout/Layout'
import WalletCard from '../components/wallet/WalletCard'
import TransactionList from '../components/wallet/TransactionList'
import Modal from '../components/common/Modal'
import SendPayment from '../components/payments/SendPayment'
import Card from '../components/common/Card'
import { useWallet } from '../hooks/useWallet'

function formatCOP(amount: number): string {
  return new Intl.NumberFormat('es-CO', {
    style: 'currency',
    currency: 'COP',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(amount)
}

export default function DashboardPage() {
  const { wallet, transactions, loading, error, refetch } = useWallet()
  const [sendModalOpen, setSendModalOpen] = useState(false)
  const navigate = useNavigate()

  // Calculate monthly stats
  const now = new Date()
  const monthTx = transactions.filter((tx) => {
    const d = new Date(tx.created_at)
    return d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear()
  })
  const monthlyReceived = monthTx
    .filter((tx) => tx.type === 'credit' && tx.status === 'completed')
    .reduce((sum, tx) => sum + tx.amount, 0)
  const monthlySpent = monthTx
    .filter((tx) => tx.type === 'debit' && tx.status === 'completed')
    .reduce((sum, tx) => sum + tx.amount, 0)

  const stats = [
    {
      label: 'Saldo total',
      value: wallet ? formatCOP(wallet.balance) : '—',
      icon: WalletIcon,
      color: 'text-indigo-400',
      bg: 'bg-indigo-500/10',
    },
    {
      label: 'Recibido este mes',
      value: formatCOP(monthlyReceived),
      icon: TrendingUp,
      color: 'text-emerald-400',
      bg: 'bg-emerald-500/10',
    },
    {
      label: 'Gastado este mes',
      value: formatCOP(monthlySpent),
      icon: TrendingDown,
      color: 'text-red-400',
      bg: 'bg-red-500/10',
    },
  ]

  return (
    <Layout>
      <div className="space-y-6">
        {/* Error state */}
        {error && !loading && (
          <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <p className="text-sm text-red-400">{error}</p>
            <button
              onClick={refetch}
              className="flex items-center gap-1.5 text-sm text-red-400 hover:text-red-300"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reintentar
            </button>
          </div>
        )}

        {/* Wallet card skeleton */}
        {loading ? (
          <div className="h-52 rounded-2xl bg-gray-800/50 animate-pulse" />
        ) : wallet ? (
          <WalletCard
            wallet={wallet}
            onTopUp={() => navigate('/wallet')}
            onWithdraw={() => navigate('/wallet')}
          />
        ) : null}

        {/* Stats row */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          {stats.map(({ label, value, icon: Icon, color, bg }) => (
            <Card key={label} className="!p-4">
              <div className="flex items-center gap-3">
                <div className={`w-10 h-10 rounded-xl ${bg} flex items-center justify-center flex-shrink-0`}>
                  <Icon className={`w-5 h-5 ${color}`} />
                </div>
                <div>
                  <p className="text-xs text-gray-500 font-medium">{label}</p>
                  <p className="text-base font-bold text-white mt-0.5">{value}</p>
                </div>
              </div>
            </Card>
          ))}
        </div>

        {/* Recent transactions + quick send */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Transactions */}
          <Card className="lg:col-span-2 !p-0 overflow-hidden">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
              <h2 className="text-sm font-semibold text-white">Movimientos recientes</h2>
              <button
                onClick={() => navigate('/wallet')}
                className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors font-medium"
              >
                Ver todos
              </button>
            </div>
            <div className="px-2 py-2">
              <TransactionList
                transactions={transactions}
                loading={loading}
                limit={5}
                emptyMessage="Sin movimientos aún"
              />
            </div>
          </Card>

          {/* Quick send */}
          <Card>
            <div className="flex items-center gap-2 mb-5">
              <div className="w-8 h-8 rounded-lg bg-indigo-500/15 flex items-center justify-center">
                <Send className="w-4 h-4 text-indigo-400" />
              </div>
              <h2 className="text-sm font-semibold text-white">Envío rápido</h2>
            </div>
            <SendPayment onSuccess={() => { setSendModalOpen(false); refetch() }} />
          </Card>
        </div>
      </div>

      {/* Send payment modal (unused here but kept for mobile quick-send if needed) */}
      <Modal
        isOpen={sendModalOpen}
        onClose={() => setSendModalOpen(false)}
        title="Enviar pago"
      >
        <SendPayment
          onSuccess={() => {
            setSendModalOpen(false)
            refetch()
          }}
        />
      </Modal>
    </Layout>
  )
}
