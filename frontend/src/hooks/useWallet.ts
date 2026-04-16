import { useState, useEffect, useCallback } from 'react'
import { walletService } from '../services/wallet.service'
import type { Wallet, Transaction } from '../types'

export function useWallet() {
  const [wallet, setWallet] = useState<Wallet | null>(null)
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchWallet = useCallback(async () => {
    try {
      setLoading(true)
      setError(null)
      const [walletData, txData] = await Promise.all([
        walletService.getWallet(),
        walletService.getTransactions(),
      ])
      setWallet(walletData)
      setTransactions(txData)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al cargar wallet'
      setError(message)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchWallet()
  }, [fetchWallet])

  return {
    wallet,
    transactions,
    loading,
    error,
    refetch: fetchWallet,
  }
}
