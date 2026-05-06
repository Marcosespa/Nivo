import { useState } from 'react'
import Layout from '../components/layout/Layout'
import Button from '../components/common/Button'
import Input from '../components/common/Input'
import Textarea from '../components/common/Textarea'
import EndpointCard from '../components/console/EndpointCard'
import JsonPanel from '../components/console/JsonPanel'
import SessionSummaryCard from '../components/console/SessionSummaryCard'
import { useApiAction } from '../hooks/useApiAction'
import { authService } from '../services/auth.service'
import { cryptoService } from '../services/crypto.service'
import { kycService } from '../services/kyc.service'
import { useAuthStore } from '../store/authStore'

export default function ProfilePage() {
  const { execute } = useApiAction()
  const { refreshToken, lastSignature, lastPublicKey, clearSession } = useAuthStore()
  const [loading, setLoading] = useState<string | null>(null)
  const [refreshValue, setRefreshValue] = useState(refreshToken)
  const [logoutValue, setLogoutValue] = useState(refreshToken)
  const [dataHex, setDataHex] = useState('486f6c61204e69766f')
  const [signatureHex, setSignatureHex] = useState(lastSignature)
  const [publicKeyHex, setPublicKeyHex] = useState(lastPublicKey)

  const run = async (key: string, job: () => Promise<unknown>) => {
    setLoading(key)
    try {
      await job()
      setRefreshValue(useAuthStore.getState().refreshToken)
      setLogoutValue(useAuthStore.getState().refreshToken)
      setSignatureHex(useAuthStore.getState().lastSignature)
      setPublicKeyHex(useAuthStore.getState().lastPublicKey)
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
              title="Refresh y logout"
              endpoint="POST /api/v1/auth/*"
              description="Mantiene o invalida la sesion actual usando el refresh token."
            >
              <Input
                label="Refresh token"
                value={refreshValue}
                onChange={(event) => setRefreshValue(event.target.value)}
              />
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'refresh'}
                  onClick={() =>
                    run('refresh', () =>
                      execute({
                        label: 'Refresh token ejecutado',
                        method: 'POST',
                        path: '/api/v1/auth/refresh',
                        request: () => authService.refresh(refreshValue || useAuthStore.getState().refreshToken),
                      })
                    )
                  }
                >
                  Refresh
                </Button>
                <Button
                  variant="danger"
                  loading={loading === 'logout'}
                  onClick={() =>
                    run('logout', async () => {
                      await execute({
                        label: 'Logout ejecutado',
                        method: 'POST',
                        path: '/api/v1/auth/logout',
                        request: () => authService.logout(logoutValue || useAuthStore.getState().refreshToken),
                      })
                      clearSession()
                    })
                  }
                >
                  Logout
                </Button>
              </div>
            </EndpointCard>

            <EndpointCard
              title="KYC"
              endpoint="POST/GET /api/v1/kyc/*"
              description="Inicia la verificacion con Truora y consulta el estado persistido."
            >
              <div className="grid gap-3 md:grid-cols-2">
                <Button
                  loading={loading === 'kyc-init'}
                  onClick={() =>
                    run('kyc-init', () =>
                      execute({
                        label: 'KYC iniciado',
                        method: 'POST',
                        path: '/api/v1/kyc/initiate',
                        request: () => kycService.initiate(),
                      })
                    )
                  }
                >
                  Iniciar KYC
                </Button>
                <Button
                  variant="secondary"
                  loading={loading === 'kyc-status'}
                  onClick={() =>
                    run('kyc-status', () =>
                      execute({
                        label: 'Estado KYC',
                        method: 'GET',
                        path: '/api/v1/kyc/status',
                        request: () => kycService.status(),
                      })
                    )
                  }
                >
                  Ver estado
                </Button>
              </div>
            </EndpointCard>
          </div>

          <EndpointCard
            title="Crypto"
            endpoint="GET/POST /api/v1/crypto/*"
            description="Prueba la API PQC: algoritmos, firma y verificacion con tu API key B2B."
          >
            <div className="grid gap-3 md:grid-cols-3">
              <Button
                variant="secondary"
                loading={loading === 'algorithms'}
                onClick={() =>
                  run('algorithms', () =>
                    execute({
                      label: 'Algoritmos PQC',
                      method: 'GET',
                      path: '/api/v1/crypto/algorithms',
                      request: () => cryptoService.algorithms(),
                    })
                  )
                }
              >
                Ver algoritmos
              </Button>
              <Button
                loading={loading === 'sign'}
                onClick={() =>
                  run('sign', () =>
                    execute({
                      label: 'Firma PQC generada',
                      method: 'POST',
                      path: '/api/v1/crypto/sign',
                      request: () => cryptoService.sign(dataHex),
                    })
                  )
                }
              >
                Firmar
              </Button>
              <Button
                variant="secondary"
                loading={loading === 'verify'}
                onClick={() =>
                  run('verify', () =>
                    execute({
                      label: 'Firma PQC verificada',
                      method: 'POST',
                      path: '/api/v1/crypto/verify',
                      request: () =>
                        cryptoService.verify({
                          data_hex: dataHex,
                          signature_hex: signatureHex || useAuthStore.getState().lastSignature,
                          public_key_hex: publicKeyHex || useAuthStore.getState().lastPublicKey,
                        }),
                    })
                  )
                }
              >
                Verificar
              </Button>
            </div>
            <Textarea
              label="Data hex"
              rows={3}
              value={dataHex}
              onChange={(event) => setDataHex(event.target.value)}
            />
            <Textarea
              label="Signature hex"
              rows={3}
              value={signatureHex}
              onChange={(event) => setSignatureHex(event.target.value)}
            />
            <Textarea
              label="Public key hex"
              rows={3}
              value={publicKeyHex}
              onChange={(event) => setPublicKeyHex(event.target.value)}
            />
          </EndpointCard>

          <JsonPanel />
        </div>

        <div className="space-y-6">
          <SessionSummaryCard />
          <div className="rounded-xl border border-gray-800 bg-gray-900/70 p-5">
            <h3 className="text-sm font-semibold text-white">Notas utiles</h3>
            <ul className="mt-3 space-y-2 text-sm text-gray-400">
              <li>La API key B2B se configura desde la pantalla de login.</li>
              <li>Las respuestas devuelven `dev_otp` cuando el backend esta en development.</li>
              <li>La firma y la llave publica quedan guardadas para reusar la verificacion.</li>
            </ul>
          </div>
        </div>
      </div>
    </Layout>
  )
}
