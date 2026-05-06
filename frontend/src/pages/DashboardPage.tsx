import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import EndpointCard from '../components/console/EndpointCard'
import JsonPanel from '../components/console/JsonPanel'
import RequestLogPanel from '../components/console/RequestLogPanel'
import SessionSummaryCard from '../components/console/SessionSummaryCard'
import { useApiAction } from '../hooks/useApiAction'
import { healthService } from '../services/health.service'
import { usersService } from '../services/users.service'
import { devService } from '../services/dev.service'

export default function DashboardPage() {
  const { execute } = useApiAction()
  const [loading, setLoading] = useState<string | null>(null)
  const [senderPhone, setSenderPhone] = useState('+573001234567')
  const [receiverPhone, setReceiverPhone] = useState('+573009876543')
  const [seedBalance, setSeedBalance] = useState('50000000')

  const run = async (key: string, job: () => Promise<unknown>) => {
    setLoading(key)
    try {
      await job()
    } finally {
      setLoading(null)
    }
  }

  return (
    <Layout>
      <div className="grid gap-6 xl:grid-cols-[1.45fr_0.55fr]">
        <div className="space-y-6">
          <div className="grid gap-6 md:grid-cols-2">
            <EndpointCard
              title="Health checks"
              endpoint="GET /health*"
              description="Valida disponibilidad del backend y del modulo PQC."
            >
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'health'}
                  onClick={() =>
                    run('health', () =>
                      execute({
                        label: 'Health general',
                        method: 'GET',
                        path: '/health',
                        request: () => healthService.health(),
                      })
                    )
                  }
                >
                  GET /health
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'pqc'}
                  onClick={() =>
                    run('pqc', () =>
                      execute({
                        label: 'Health PQC',
                        method: 'GET',
                        path: '/health/pqc',
                        request: () => healthService.pqc(),
                      })
                    )
                  }
                >
                  GET /health/pqc
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'ready'}
                  onClick={() =>
                    run('ready', () =>
                      execute({
                        label: 'Readiness',
                        method: 'GET',
                        path: '/health/ready',
                        request: () => healthService.ready(),
                      })
                    )
                  }
                >
                  GET /health/ready
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'live'}
                  onClick={() =>
                    run('live', () =>
                      execute({
                        label: 'Liveness',
                        method: 'GET',
                        path: '/health/live',
                        request: () => healthService.live(),
                      })
                    )
                  }
                >
                  GET /health/live
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'root'}
                  onClick={() =>
                    run('root', () =>
                      execute({
                        label: 'Root endpoint',
                        method: 'GET',
                        path: '/',
                        request: () => healthService.root(),
                      })
                    )
                  }
                >
                  GET /
                </Button>
              </div>
            </EndpointCard>

            <EndpointCard
              title="Sesion actual"
              endpoint="GET /api/v1/users/*"
              description="Consulta el perfil autenticado y el estado visual de la wallet."
            >
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'me'}
                  onClick={() =>
                    run('me', () =>
                      execute({
                        label: 'Perfil actual',
                        method: 'GET',
                        path: '/api/v1/users/me',
                        request: () => usersService.me(),
                      })
                    )
                  }
                >
                  GET /users/me
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'wallet'}
                  onClick={() =>
                    run('wallet', () =>
                      execute({
                        label: 'Wallet actual',
                        method: 'GET',
                        path: '/api/v1/users/me/wallet',
                        request: () => usersService.wallet(),
                      })
                    )
                  }
                >
                  GET /users/me/wallet
                </Button>
              </div>
            </EndpointCard>
          </div>

          <EndpointCard
            title="Dev seed"
            endpoint="POST/DELETE /api/v1/dev/seed"
            description="Reinicia sender y receiver de prueba sin salir del frontend."
          >
            <div className="grid gap-4 md:grid-cols-3">
              <Input
                label="Sender phone"
                value={senderPhone}
                onChange={(event) => setSenderPhone(event.target.value)}
              />
              <Input
                label="Receiver phone"
                value={receiverPhone}
                onChange={(event) => setReceiverPhone(event.target.value)}
              />
              <Input
                label="Seed balance COP"
                type="number"
                value={seedBalance}
                onChange={(event) => setSeedBalance(event.target.value)}
              />
            </div>
            <div className="grid gap-3 md:grid-cols-2">
              <Button
                loading={loading === 'seed'}
                onClick={() =>
                  run('seed', () =>
                    execute({
                      label: 'Seed regenerado',
                      method: 'POST',
                      path: '/api/v1/dev/seed',
                      request: () =>
                        devService.seed({
                          sender_phone: senderPhone,
                          receiver_phone: receiverPhone,
                          seed_balance_cop: Number(seedBalance),
                        }),
                    })
                  )
                }
              >
                POST /dev/seed
              </Button>
              <Button
                variant="danger"
                loading={loading === 'seed-clear'}
                onClick={() =>
                  run('seed-clear', () =>
                    execute({
                      label: 'Seed limpiado',
                      method: 'DELETE',
                      path: '/api/v1/dev/seed',
                      request: () =>
                        devService.clearSeed({
                          sender_phone: senderPhone,
                          receiver_phone: receiverPhone,
                          seed_balance_cop: Number(seedBalance),
                        }),
                    })
                  )
                }
              >
                DELETE /dev/seed
              </Button>
            </div>
          </EndpointCard>

          <JsonPanel />
          <RequestLogPanel />
        </div>

        <div className="space-y-6">
          <SessionSummaryCard />
        </div>
      </div>
    </Layout>
  )
}
