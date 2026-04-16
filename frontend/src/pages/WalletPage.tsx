import { useState } from 'react'
import { RefreshCw, AlertCircle } from 'lucide-react'
import Layout from '../components/layout/Layout'
import WalletCard from '../components/wallet/WalletCard'
import TransactionList from '../components/wallet/TransactionList'
import Modal from '../components/common/Modal'
import Card from '../components/common/Card'
import Input from '../components/common/Input'
import Button from '../components/common/Button'
import { useWallet } from '../hooks/useWallet'
import { walletService } from '../services/wallet.service'

function formatCOPDisplay(raw: string): string {
  const digits = raw.replace(/\D/g, '')
  if (!digits) return ''
  return new Intl.NumberFormat('es-CO').format(Number(digits))
}

export default function WalletPage() {
  const { wallet, transactions, loading, error, refetch } = useWallet()

  const [topUpOpen, setTopUpOpen] = useState(false)
  const [withdrawOpen, setWithdrawOpen] = useState(false)

  // Top-up state
  const [topUpAmountRaw, setTopUpAmountRaw] = useState('')
  const [topUpLoading, setTopUpLoading] = useState(false)
  const [topUpError, setTopUpError] = useState('')
  const [topUpSuccess, setTopUpSuccess] = useState(false)

  // Withdraw state
  const [withdrawAmountRaw, setWithdrawAmountRaw] = useState('')
  const [bankAccountId, setBankAccountId] = useState('')
  const [withdrawLoading, setWithdrawLoading] = useState(false)
  const [withdrawError, setWithdrawError] = useState('')
  const [withdrawSuccess, setWithdrawSuccess] = useState(false)

  const handleTopUp = async () => {
    const amount = Number(topUpAmountRaw.replace(/\D/g, ''))
    if (amount < 1000) {
      setTopUpError('El monto mínimo es $1.000 COP')
      return
    }
    setTopUpLoading(true)
    setTopUpError('')
    try {
      await walletService.topUp(amount)
      setTopUpSuccess(true)
      refetch()
    } catch (err: unknown) {
      setTopUpError(err instanceof Error ? err.message : 'Error al recargar')
    } finally {
      setTopUpLoading(false)
    }
  }

  const handleWithdraw = async () => {
    const amount = Number(withdrawAmountRaw.replace(/\D/g, ''))
    if (amount < 1000) {
      setWithdrawError('El monto mínimo es $1.000 COP')
      return
    }
    if (!bankAccountId.trim()) {
      setWithdrawError('Ingresa el ID de cuenta bancaria')
      return
    }
    setWithdrawLoading(true)
    setWithdrawError('')
    try {
      await walletService.withdraw(amount, bankAccountId)
      setWithdrawSuccess(true)
      refetch()
    } catch (err: unknown) {
      setWithdrawError(err instanceof Error ? err.message : 'Error al retirar')
    } finally {
      setWithdrawLoading(false)
    }
  }

  const resetTopUp = () => {
    setTopUpAmountRaw('')
    setTopUpError('')
    setTopUpSuccess(false)
    setTopUpOpen(false)
  }

  const resetWithdraw = () => {
    setWithdrawAmountRaw('')
    setBankAccountId('')
    setWithdrawError('')
    setWithdrawSuccess(false)
    setWithdrawOpen(false)
  }

  return (
    <Layout>
      <div className="space-y-6">
        {/* Error banner */}
        {error && !loading && (
          <div className="flex items-center justify-between px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
            <div className="flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-red-400" />
              <p className="text-sm text-red-400">{error}</p>
            </div>
            <button
              onClick={refetch}
              className="flex items-center gap-1.5 text-sm text-red-400 hover:text-red-300"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Reintentar
            </button>
          </div>
        )}

        {/* Wallet card */}
        {loading ? (
          <div className="h-52 rounded-2xl bg-gray-800/50 animate-pulse" />
        ) : wallet ? (
          <WalletCard
            wallet={wallet}
            onTopUp={() => { setTopUpSuccess(false); setTopUpOpen(true) }}
            onWithdraw={() => { setWithdrawSuccess(false); setWithdrawOpen(true) }}
          />
        ) : null}

        {/* Full transaction history */}
        <Card className="!p-0 overflow-hidden">
          <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
            <h2 className="text-sm font-semibold text-white">
              Historial de transacciones
            </h2>
            <button
              onClick={refetch}
              className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Actualizar
            </button>
          </div>
          <div className="px-2 py-2">
            <TransactionList
              transactions={transactions}
              loading={loading}
              emptyMessage="Sin transacciones aún"
            />
          </div>
        </Card>
      </div>

      {/* Top-up modal */}
      <Modal
        isOpen={topUpOpen}
        onClose={resetTopUp}
        title="Recargar saldo"
        size="sm"
      >
        {topUpSuccess ? (
          <div className="text-center py-4 space-y-3 animate-fade-in">
            <div className="w-12 h-12 rounded-full bg-emerald-500/15 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-white font-semibold">¡Recarga iniciada!</p>
            <p className="text-gray-400 text-sm">Tu saldo se actualizará en breve.</p>
            <Button variant="secondary" onClick={resetTopUp} fullWidth>
              Cerrar
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <Input
              label="Monto a recargar (COP)"
              type="text"
              placeholder="0"
              value={topUpAmountRaw ? formatCOPDisplay(topUpAmountRaw) : ''}
              onChange={(e) => {
                setTopUpAmountRaw(e.target.value.replace(/\D/g, ''))
                setTopUpError('')
              }}
              error={topUpError}
              inputMode="numeric"
              helperText="Mínimo $1.000 COP"
            />
            <Button
              fullWidth
              loading={topUpLoading}
              onClick={handleTopUp}
            >
              Recargar
            </Button>
          </div>
        )}
      </Modal>

      {/* Withdraw modal */}
      <Modal
        isOpen={withdrawOpen}
        onClose={resetWithdraw}
        title="Retirar fondos"
        size="sm"
      >
        {withdrawSuccess ? (
          <div className="text-center py-4 space-y-3 animate-fade-in">
            <div className="w-12 h-12 rounded-full bg-emerald-500/15 flex items-center justify-center mx-auto">
              <svg className="w-6 h-6 text-emerald-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <p className="text-white font-semibold">¡Retiro iniciado!</p>
            <p className="text-gray-400 text-sm">El dinero llegará a tu cuenta en 1-3 días hábiles.</p>
            <Button variant="secondary" onClick={resetWithdraw} fullWidth>
              Cerrar
            </Button>
          </div>
        ) : (
          <div className="space-y-4">
            <Input
              label="Monto a retirar (COP)"
              type="text"
              placeholder="0"
              value={withdrawAmountRaw ? formatCOPDisplay(withdrawAmountRaw) : ''}
              onChange={(e) => {
                setWithdrawAmountRaw(e.target.value.replace(/\D/g, ''))
                setWithdrawError('')
              }}
              inputMode="numeric"
              helperText="Mínimo $1.000 COP"
            />
            <Input
              label="ID de cuenta bancaria"
              type="text"
              placeholder="ej. acc_abc123"
              value={bankAccountId}
              onChange={(e) => {
                setBankAccountId(e.target.value)
                setWithdrawError('')
              }}
              error={withdrawError}
              helperText="Encuentra este ID en tu perfil o en las cuentas registradas"
            />
            <Button
              fullWidth
              loading={withdrawLoading}
              onClick={handleWithdraw}
            >
              Retirar
            </Button>
          </div>
        )}
      </Modal>
    </Layout>
  )
}
