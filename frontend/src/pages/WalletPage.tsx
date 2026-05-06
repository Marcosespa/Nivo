import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import EndpointCard from '../components/console/EndpointCard'
import JsonPanel from '../components/console/JsonPanel'
import SessionSummaryCard from '../components/console/SessionSummaryCard'
import { useApiAction } from '../hooks/useApiAction'
import { usersService } from '../services/users.service'
import { topupService } from '../services/topup.service'
import { withdrawalService } from '../services/withdrawal.service'
import { useAuthStore } from '../store/authStore'

export default function WalletPage() {
  const { execute } = useApiAction()
  const { lastBankAccountId, lastVerificationAmount } = useAuthStore()
  const [loading, setLoading] = useState<string | null>(null)
  const [topupAmount, setTopupAmount] = useState('1000000')
  const [topupBankCode, setTopupBankCode] = useState('001')
  const [topupLimit, setTopupLimit] = useState('20')
  const [bankCode, setBankCode] = useState('001')
  const [accountType, setAccountType] = useState('savings')
  const [accountNumber, setAccountNumber] = useState('1234567890')
  const [accountHolder, setAccountHolder] = useState('Marcos Espana')
  const [verifyAccountId, setVerifyAccountId] = useState(lastBankAccountId)
  const [verifyAmount, setVerifyAmount] = useState(lastVerificationAmount)
  const [withdrawAccountId, setWithdrawAccountId] = useState(lastBankAccountId)
  const [withdrawAmount, setWithdrawAmount] = useState('200000')
  const [withdrawLimit, setWithdrawLimit] = useState('20')

  const run = async (key: string, job: () => Promise<unknown>) => {
    setLoading(key)
    try {
      await job()
      setVerifyAccountId(useAuthStore.getState().lastBankAccountId)
      setWithdrawAccountId(useAuthStore.getState().lastBankAccountId)
      setVerifyAmount(useAuthStore.getState().lastVerificationAmount)
    } finally {
      setLoading(null)
    }
  }

  return (
    <Layout>
      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <EndpointCard
              title="Perfil y wallet"
              endpoint="GET /api/v1/users/*"
              description="Consulta el perfil autenticado y el saldo visual actual."
            >
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'profile'}
                  onClick={() =>
                    run('profile', () =>
                      execute({
                        label: 'Perfil wallet',
                        method: 'GET',
                        path: '/api/v1/users/me',
                        request: () => usersService.me(),
                      })
                    )
                  }
                >
                  Perfil
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'wallet'}
                  onClick={() =>
                    run('wallet', () =>
                      execute({
                        label: 'Wallet visual',
                        method: 'GET',
                        path: '/api/v1/users/me/wallet',
                        request: () => usersService.wallet(),
                      })
                    )
                  }
                >
                  Wallet
                </Button>
              </div>
            </EndpointCard>

            <EndpointCard
              title="Topup"
              endpoint="POST/GET /api/v1/topup/*"
              description="Inicia recargas y consulta el historial ya procesado por el gateway."
            >
              <div className="grid gap-4 md:grid-cols-2">
                <Input
                  label="Amount COP"
                  type="number"
                  value={topupAmount}
                  onChange={(event) => setTopupAmount(event.target.value)}
                />
                <Input
                  label="Bank code"
                  value={topupBankCode}
                  onChange={(event) => setTopupBankCode(event.target.value)}
                />
              </div>
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'topup'}
                  onClick={() =>
                    run('topup', () =>
                      execute({
                        label: 'Topup iniciado',
                        method: 'POST',
                        path: '/api/v1/topup/initiate',
                        request: () =>
                          topupService.initiate({
                            amount_cop: Number(topupAmount),
                            bank_code: topupBankCode,
                          }),
                      })
                    )
                  }
                >
                  Iniciar topup
                </Button>
                <div className="flex gap-3">
                  <Input
                    label="Limit"
                    type="number"
                    value={topupLimit}
                    onChange={(event) => setTopupLimit(event.target.value)}
                  />
                  <Button
                    className="self-end"
                    variant="secondary"
                    loading={loading === 'topup-history'}
                    onClick={() =>
                      run('topup-history', () =>
                        execute({
                          label: 'Historial topup',
                          method: 'GET',
                          path: '/api/v1/topup/history',
                          request: () => topupService.history(Number(topupLimit)),
                        })
                      )
                    }
                  >
                    Historial
                  </Button>
                </div>
              </div>
            </EndpointCard>
          </div>

          <EndpointCard
            title="Registrar cuenta bancaria"
            endpoint="POST /api/v1/withdrawal/accounts"
            description="Crea una cuenta para retiros y devuelve el microdeposito de verificacion."
          >
            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
              <Input label="Bank code" value={bankCode} onChange={(event) => setBankCode(event.target.value)} />
              <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-300">
                Account type
                <select
                  className="h-[46px] rounded-xl border border-gray-700 bg-gray-900 px-4 text-sm text-white"
                  value={accountType}
                  onChange={(event) => setAccountType(event.target.value)}
                >
                  <option value="savings">savings</option>
                  <option value="checking">checking</option>
                </select>
              </label>
              <Input
                label="Account number"
                value={accountNumber}
                onChange={(event) => setAccountNumber(event.target.value)}
              />
              <Input
                label="Holder name"
                value={accountHolder}
                onChange={(event) => setAccountHolder(event.target.value)}
              />
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <Button
                loading={loading === 'register-account'}
                onClick={() =>
                  run('register-account', () =>
                    execute({
                      label: 'Cuenta bancaria registrada',
                      method: 'POST',
                      path: '/api/v1/withdrawal/accounts',
                      request: () =>
                        withdrawalService.registerAccount({
                          bank_code: bankCode,
                          account_type: accountType,
                          account_number: accountNumber,
                          account_holder_name: accountHolder,
                        }),
                    })
                  )
                }
              >
                Registrar cuenta
              </Button>
              <Button
                variant="secondary"
                loading={loading === 'list-accounts'}
                onClick={() =>
                  run('list-accounts', () =>
                    execute({
                      label: 'Cuentas bancarias listadas',
                      method: 'GET',
                      path: '/api/v1/withdrawal/accounts',
                      request: () => withdrawalService.listAccounts(),
                    })
                  )
                }
              >
                Listar cuentas
              </Button>
            </div>
          </EndpointCard>

          <div className="grid gap-6 md:grid-cols-2">
            <EndpointCard
              title="Verificar microdeposito"
              endpoint="POST /api/v1/withdrawal/accounts/{id}/verify"
              description="Confirma el microdeposito recibido para habilitar retiros."
            >
              <Input
                label="Account id"
                value={verifyAccountId}
                onChange={(event) => setVerifyAccountId(event.target.value)}
              />
              <Input
                label="Verification amount COP"
                value={verifyAmount}
                onChange={(event) => setVerifyAmount(event.target.value)}
              />
              <Button
                loading={loading === 'verify-account'}
                onClick={() =>
                  run('verify-account', () =>
                    execute({
                      label: 'Cuenta verificada',
                      method: 'POST',
                      path: `/api/v1/withdrawal/accounts/${verifyAccountId || useAuthStore.getState().lastBankAccountId}/verify`,
                      request: () =>
                        withdrawalService.verifyAccount(
                          verifyAccountId || useAuthStore.getState().lastBankAccountId,
                          Number(verifyAmount || useAuthStore.getState().lastVerificationAmount)
                        ),
                    })
                  )
                }
              >
                Verificar
              </Button>
            </EndpointCard>

            <EndpointCard
              title="Iniciar retiro"
              endpoint="POST /api/v1/withdrawal/initiate"
              description="Ejecuta el retiro sobre una cuenta ya verificada."
            >
              <Input
                label="Bank account id"
                value={withdrawAccountId}
                onChange={(event) => setWithdrawAccountId(event.target.value)}
              />
              <Input
                label="Amount COP"
                type="number"
                value={withdrawAmount}
                onChange={(event) => setWithdrawAmount(event.target.value)}
              />
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'withdraw'}
                  onClick={() =>
                    run('withdraw', () =>
                      execute({
                        label: 'Retiro iniciado',
                        method: 'POST',
                        path: '/api/v1/withdrawal/initiate',
                        request: () =>
                          withdrawalService.initiate({
                            bank_account_id:
                              withdrawAccountId || useAuthStore.getState().lastBankAccountId,
                            amount_cop: Number(withdrawAmount),
                          }),
                      })
                    )
                  }
                >
                  Iniciar retiro
                </Button>
                <div className="flex gap-3">
                  <Input
                    label="Limit"
                    type="number"
                    value={withdrawLimit}
                    onChange={(event) => setWithdrawLimit(event.target.value)}
                  />
                  <Button
                    className="self-end"
                    variant="secondary"
                    loading={loading === 'withdraw-history'}
                    onClick={() =>
                      run('withdraw-history', () =>
                        execute({
                          label: 'Historial de retiros',
                          method: 'GET',
                          path: '/api/v1/withdrawal/history',
                          request: () => withdrawalService.history(Number(withdrawLimit)),
                        })
                      )
                    }
                  >
                    Historial
                  </Button>
                </div>
              </div>
            </EndpointCard>
          </div>

          <JsonPanel />
        </div>

        <div className="space-y-6">
          <SessionSummaryCard />
        </div>
      </div>
    </Layout>
  )
}
