import { useMemo, useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { DatabaseZap, LockKeyhole, Shield, TestTube2 } from 'lucide-react'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import Textarea from '../components/common/Textarea'
import { useAuthStore } from '../store/authStore'
import { useApiAction } from '../hooks/useApiAction'
import { authService } from '../services/auth.service'
import { devService } from '../services/dev.service'
import { usersService } from '../services/users.service'

export default function LoginPage() {
  const navigate = useNavigate()
  const {
    baseUrl,
    apiKey,
    isAuthenticated,
    lastOtp,
    setBaseUrl,
    setApiKey,
    setProfile,
    accessToken,
  } = useAuthStore()
  const { execute } = useApiAction()

  const [configUrl, setConfigUrl] = useState(baseUrl)
  const [configApiKey, setConfigApiKey] = useState(apiKey)
  const [phone, setPhone] = useState('+573001234567')
  const [otpCode, setOtpCode] = useState(lastOtp)
  const [deviceId, setDeviceId] = useState('nivo-react-console')
  const [senderPhone, setSenderPhone] = useState('+573001234567')
  const [receiverPhone, setReceiverPhone] = useState('+573009876543')
  const [seedBalance, setSeedBalance] = useState('50000000')
  const [loading, setLoading] = useState<string | null>(null)

  const subtitle = useMemo(
    () =>
      'Conecta el frontend al backend local, siembra usuarios de prueba y autentica la sesion real con OTP o dev seed.',
    []
  )

  if (isAuthenticated && accessToken) {
    return <Navigate to="/dashboard" replace />
  }

  const syncProfile = async () => {
    const profile = await execute({
      label: 'Perfil sincronizado',
      method: 'GET',
      path: '/api/v1/users/me',
      request: () => usersService.me(),
    })
    setProfile(profile as import('../types').UserProfile)
  }

  const handleSaveConfig = () => {
    setBaseUrl(configUrl)
    setApiKey(configApiKey)
  }

  const handleRequestOtp = async () => {
    setLoading('otp-request')
    try {
      await execute({
        label: 'OTP solicitado',
        method: 'POST',
        path: '/api/v1/auth/request-otp',
        request: () => authService.requestOtp(phone),
      })
    } finally {
      setLoading(null)
    }
  }

  const handleVerifyOtp = async () => {
    setLoading('otp-verify')
    try {
      await execute({
        label: 'OTP verificado',
        method: 'POST',
        path: '/api/v1/auth/verify-otp',
        request: () =>
          authService.verifyOtp({
            phone_number: phone,
            otp_code: otpCode || useAuthStore.getState().lastOtp,
            device_id: deviceId,
          }),
      })
      await syncProfile()
      navigate('/dashboard', { replace: true })
    } finally {
      setLoading(null)
    }
  }

  const handleSeed = async () => {
    setLoading('seed')
    try {
      await execute({
        label: 'Usuarios demo sembrados',
        method: 'POST',
        path: '/api/v1/dev/seed',
        request: () =>
          devService.seed({
            sender_phone: senderPhone,
            receiver_phone: receiverPhone,
            seed_balance_cop: Number(seedBalance),
          }),
      })
      await syncProfile()
      navigate('/dashboard', { replace: true })
    } finally {
      setLoading(null)
    }
  }

  return (
    <div className="min-h-screen bg-gray-950">
      <div className="mx-auto grid min-h-screen max-w-7xl grid-cols-1 gap-0 lg:grid-cols-[1.15fr_0.85fr]">
        <section className="flex flex-col justify-between border-b border-gray-800 px-6 py-10 lg:border-b-0 lg:border-r lg:px-12">
          <div className="space-y-8">
            <div className="flex items-center gap-3">
              <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-teal-500/15">
                <Shield className="h-5 w-5 text-teal-300" />
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.24em] text-teal-300">Nivo</p>
                <h1 className="text-3xl font-bold text-white">Frontend para probar el backend</h1>
              </div>
            </div>
            <p className="max-w-2xl text-base leading-7 text-gray-400">{subtitle}</p>

            <div className="grid gap-4 md:grid-cols-3">
              {[
                {
                  icon: DatabaseZap,
                  title: 'Base URL editable',
                  body: 'Apunta la consola al backend local, Docker o cualquier ambiente de pruebas.',
                },
                {
                  icon: LockKeyhole,
                  title: 'Sesion persistente',
                  body: 'Guarda access token, refresh token, OTPs, tx_id y llaves para seguir el flujo.',
                },
                {
                  icon: TestTube2,
                  title: 'Cobertura real',
                  body: 'Dashboard, pagos, wallet, KYC, crypto, topups y retiros en una sola app.',
                },
              ].map(({ icon: Icon, title, body }) => (
                <div key={title} className="rounded-xl border border-gray-800 bg-gray-900/70 p-5">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-lg bg-teal-500/10">
                    <Icon className="h-5 w-5 text-teal-300" />
                  </div>
                  <h2 className="text-sm font-semibold text-white">{title}</h2>
                  <p className="mt-2 text-sm text-gray-400">{body}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="mt-10 rounded-xl border border-gray-800 bg-gray-900/70 p-5">
            <h2 className="text-sm font-semibold text-white">Configuracion</h2>
            <div className="mt-4 grid gap-4">
              <Input
                label="Base URL del backend"
                value={configUrl}
                onChange={(event) => setConfigUrl(event.target.value)}
                placeholder="http://localhost:8001"
              />
              <Textarea
                label="API key B2B"
                rows={3}
                value={configApiKey}
                onChange={(event) => setConfigApiKey(event.target.value)}
                placeholder="Opcional para crypto si quieres una llave propia"
              />
              <Button onClick={handleSaveConfig}>Guardar configuracion</Button>
            </div>
          </div>
        </section>

        <section className="flex items-center px-6 py-10 lg:px-10">
          <div className="grid w-full gap-6">
            <div className="rounded-xl border border-gray-800 bg-gray-900/70 p-6">
              <h2 className="text-lg font-semibold text-white">Login por OTP</h2>
              <p className="mt-2 text-sm text-gray-400">Usa el flujo real del backend de autenticacion.</p>
              <div className="mt-5 grid gap-4">
                <Input
                  label="Celular"
                  value={phone}
                  onChange={(event) => setPhone(event.target.value)}
                />
                <div className="grid gap-4 md:grid-cols-2">
                  <Input
                    label="OTP"
                    value={otpCode}
                    onChange={(event) => setOtpCode(event.target.value)}
                    helperText="Si el backend responde dev_otp, se reutiliza aqui."
                  />
                  <Input
                    label="Device ID"
                    value={deviceId}
                    onChange={(event) => setDeviceId(event.target.value)}
                  />
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <Button loading={loading === 'otp-request'} onClick={handleRequestOtp}>
                    Solicitar OTP
                  </Button>
                  <Button
                    variant="secondary"
                    loading={loading === 'otp-verify'}
                    onClick={handleVerifyOtp}
                  >
                    Verificar OTP
                  </Button>
                </div>
              </div>
            </div>

            <div className="rounded-xl border border-gray-800 bg-gray-900/70 p-6">
              <h2 className="text-lg font-semibold text-white">Dev seed</h2>
              <p className="mt-2 text-sm text-gray-400">
                Crea sender y receiver de prueba, carga saldo y entra directo con el token del sender.
              </p>
              <div className="mt-5 grid gap-4">
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
                <Button loading={loading === 'seed'} onClick={handleSeed}>
                  Sembrar y entrar
                </Button>
              </div>
            </div>
          </div>
        </section>
      </div>
    </div>
  )
}
