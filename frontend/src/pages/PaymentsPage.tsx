import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import EndpointCard from '../components/console/EndpointCard'
import JsonPanel from '../components/console/JsonPanel'
import SessionSummaryCard from '../components/console/SessionSummaryCard'
import { useApiAction } from '../hooks/useApiAction'
import { paymentsService } from '../services/payments.service'
import { useAuthStore } from '../store/authStore'

export default function PaymentsPage() {
  const { execute } = useApiAction()
  const { lastOtp, lastTxId } = useAuthStore()
  const [loading, setLoading] = useState<string | null>(null)
  const [receiverPhone, setReceiverPhone] = useState('+573009876543')
  const [amountCop, setAmountCop] = useState('150000')
  const [message, setMessage] = useState('Pago de prueba desde el frontend React')
  const [confirmTxId, setConfirmTxId] = useState(lastTxId)
  const [confirmOtp, setConfirmOtp] = useState(lastOtp)
  const [detailTxId, setDetailTxId] = useState(lastTxId)
  const [page, setPage] = useState('1')
  const [pageSize, setPageSize] = useState('20')
  const [direction, setDirection] = useState('all')

  const run = async (key: string, job: () => Promise<unknown>) => {
    setLoading(key)
    try {
      await job()
      setConfirmTxId(useAuthStore.getState().lastTxId)
      setDetailTxId(useAuthStore.getState().lastTxId)
      setConfirmOtp(useAuthStore.getState().lastOtp)
    } finally {
      setLoading(null)
    }
  }

  return (
    <Layout>
      <div className="grid gap-6 xl:grid-cols-[1.3fr_0.7fr]">
        <div className="space-y-6">
          <EndpointCard
            title="Iniciar pago"
            endpoint="POST /api/v1/payments/initiate"
            description="Crea una transaccion pendiente y prepara el OTP de confirmacion."
          >
            <div className="grid gap-4 md:grid-cols-3">
              <Input
                label="Receiver phone"
                value={receiverPhone}
                onChange={(event) => setReceiverPhone(event.target.value)}
              />
              <Input
                label="Amount COP"
                type="number"
                value={amountCop}
                onChange={(event) => setAmountCop(event.target.value)}
              />
              <Input
                label="Message"
                value={message}
                onChange={(event) => setMessage(event.target.value)}
              />
            </div>
            <Button
              loading={loading === 'initiate'}
              onClick={() =>
                run('initiate', () =>
                  execute({
                    label: 'Pago iniciado',
                    method: 'POST',
                    path: '/api/v1/payments/initiate',
                    request: () =>
                      paymentsService.initiate({
                        receiver_phone: receiverPhone,
                        amount_cop: Number(amountCop),
                        message,
                      }),
                  })
                )
              }
            >
              Iniciar pago
            </Button>
          </EndpointCard>

          <div className="grid gap-6 md:grid-cols-2">
            <EndpointCard
              title="Confirmar pago"
              endpoint="POST /api/v1/payments/confirm"
              description="Usa el ultimo tx_id y OTP guardados o pegados manualmente."
            >
              <Input
                label="tx_id"
                value={confirmTxId}
                onChange={(event) => setConfirmTxId(event.target.value)}
              />
              <Input
                label="OTP"
                value={confirmOtp}
                onChange={(event) => setConfirmOtp(event.target.value)}
              />
              <Button
                loading={loading === 'confirm'}
                onClick={() =>
                  run('confirm', () =>
                    execute({
                      label: 'Pago confirmado',
                      method: 'POST',
                      path: '/api/v1/payments/confirm',
                      request: () =>
                        paymentsService.confirm({
                          tx_id: confirmTxId || useAuthStore.getState().lastTxId,
                          otp_code: confirmOtp || useAuthStore.getState().lastOtp,
                        }),
                    })
                  )
                }
              >
                Confirmar
              </Button>
            </EndpointCard>

            <EndpointCard
              title="Detalle de transaccion"
              endpoint="GET /api/v1/payments/{tx_id}"
              description="Trae el detalle de una transaccion individual."
            >
              <Input
                label="tx_id"
                value={detailTxId}
                onChange={(event) => setDetailTxId(event.target.value)}
              />
              <Button
                variant="secondary"
                loading={loading === 'detail'}
                onClick={() =>
                  run('detail', () =>
                    execute({
                      label: 'Detalle de transaccion',
                      method: 'GET',
                      path: `/api/v1/payments/${detailTxId || useAuthStore.getState().lastTxId}`,
                      request: () =>
                        paymentsService.detail(detailTxId || useAuthStore.getState().lastTxId),
                    })
                  )
                }
              >
                Consultar
              </Button>
            </EndpointCard>
          </div>

          <EndpointCard
            title="Historial"
            endpoint="GET /api/v1/payments/history"
            description="Consulta el historial por pagina, tamano y direccion del movimiento."
          >
            <div className="grid gap-4 md:grid-cols-3">
              <Input
                label="Page"
                type="number"
                value={page}
                onChange={(event) => setPage(event.target.value)}
              />
              <Input
                label="Page size"
                type="number"
                value={pageSize}
                onChange={(event) => setPageSize(event.target.value)}
              />
              <label className="flex flex-col gap-1.5 text-sm font-medium text-gray-300">
                Direction
                <select
                  className="h-[46px] rounded-xl border border-gray-700 bg-gray-900 px-4 text-sm text-white"
                  value={direction}
                  onChange={(event) => setDirection(event.target.value)}
                >
                  <option value="all">all</option>
                  <option value="sent">sent</option>
                  <option value="received">received</option>
                </select>
              </label>
            </div>
            <Button
              variant="secondary"
              loading={loading === 'history'}
              onClick={() =>
                run('history', () =>
                  execute({
                    label: 'Historial de pagos',
                    method: 'GET',
                    path: '/api/v1/payments/history',
                    request: () =>
                      paymentsService.history({
                        page: Number(page),
                        page_size: Number(pageSize),
                        direction,
                      }),
                  })
                )
              }
            >
              Traer historial
            </Button>
          </EndpointCard>

          <JsonPanel />
        </div>

        <div className="space-y-6">
          <SessionSummaryCard />
        </div>
      </div>
    </Layout>
  )
}
