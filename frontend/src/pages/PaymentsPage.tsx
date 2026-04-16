import { useState, useEffect } from 'react'
import { RefreshCw, Send } from 'lucide-react'
import Layout from '../components/layout/Layout'
import Card from '../components/common/Card'
import SendPayment from '../components/payments/SendPayment'
import TransactionList from '../components/wallet/TransactionList'
import { paymentsService } from '../services/payments.service'
import type { Transaction } from '../types'

export default function PaymentsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchHistory = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await paymentsService.getHistory()
      setTransactions(data)
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Error al cargar historial')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchHistory()
  }, [])

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
        {/* Send payment form */}
        <div className="lg:col-span-2">
          <Card>
            <div className="flex items-center gap-2.5 mb-6">
              <div className="w-9 h-9 rounded-xl bg-indigo-500/15 flex items-center justify-center">
                <Send className="w-4 h-4 text-indigo-400" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-white">Enviar dinero</h2>
                <p className="text-xs text-gray-500">Transferencia instantánea</p>
              </div>
            </div>
            <SendPayment onSuccess={fetchHistory} />
          </Card>
        </div>

        {/* Payment history */}
        <div className="lg:col-span-3">
          <Card className="!p-0 overflow-hidden h-full">
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-800">
              <h2 className="text-sm font-semibold text-white">Historial de pagos</h2>
              <button
                onClick={fetchHistory}
                className="flex items-center gap-1.5 text-xs text-gray-500 hover:text-gray-300 transition-colors"
              >
                <RefreshCw className="w-3.5 h-3.5" />
                Actualizar
              </button>
            </div>

            {error && (
              <div className="mx-4 mt-4 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20">
                <p className="text-sm text-red-400">{error}</p>
              </div>
            )}

            <div className="px-2 py-2">
              <TransactionList
                transactions={transactions}
                loading={loading}
                emptyMessage="Sin pagos aún"
              />
            </div>
          </Card>
        </div>
      </div>
    </Layout>
  )
}
