import Card from '../common/Card'
import { useAuthStore } from '../../store/authStore'

const Row = ({ label, value }: { label: string; value: string }) => (
  <div className="flex items-start justify-between gap-4 border-b border-gray-800 py-3 last:border-0">
    <span className="text-xs uppercase tracking-wide text-gray-500">{label}</span>
    <span className="max-w-[70%] break-words text-right text-sm text-white">{value || '—'}</span>
  </div>
)

export default function SessionSummaryCard() {
  const {
    baseUrl,
    environment,
    accessToken,
    refreshToken,
    apiKey,
    lastOtp,
    lastTxId,
    lastBankAccountId,
    lastVerificationAmount,
    lastPublicKey,
  } = useAuthStore()

  return (
    <Card className="!rounded-xl">
      <div className="mb-3">
        <h3 className="text-sm font-semibold text-white">Estado de sesion</h3>
        <p className="text-xs text-gray-500">Valores reutilizados por los formularios</p>
      </div>
      <div>
        <Row label="Base URL" value={baseUrl} />
        <Row label="Entorno" value={environment} />
        <Row label="Access" value={accessToken ? `${accessToken.slice(0, 20)}...` : ''} />
        <Row label="Refresh" value={refreshToken ? `${refreshToken.slice(0, 20)}...` : ''} />
        <Row label="API key" value={apiKey ? `${apiKey.slice(0, 12)}...` : ''} />
        <Row label="Ultimo OTP" value={lastOtp} />
        <Row label="Ultimo tx_id" value={lastTxId} />
        <Row label="Cuenta bancaria" value={lastBankAccountId} />
        <Row label="Microdeposito" value={lastVerificationAmount} />
        <Row label="Public key" value={lastPublicKey ? `${lastPublicKey.slice(0, 20)}...` : ''} />
      </div>
    </Card>
  )
}
