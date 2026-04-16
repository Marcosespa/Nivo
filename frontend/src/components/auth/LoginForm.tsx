import { useState } from 'react'
import { Phone } from 'lucide-react'
import Input from '../common/Input'
import Button from '../common/Button'
import { authService } from '../../services/auth.service'

interface LoginFormProps {
  onOtpSent: (phone: string) => void
}

export default function LoginForm({ onOtpSent }: LoginFormProps) {
  const [phone, setPhone] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const formatPhone = (value: string) => {
    // Strip everything except digits
    return value.replace(/\D/g, '').slice(0, 10)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (phone.length < 10) {
      setError('Ingresa un número de celular válido (10 dígitos)')
      return
    }

    const fullPhone = `+57${phone}`

    try {
      setLoading(true)
      await authService.requestOtp(fullPhone)
      onOtpSent(fullPhone)
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al enviar el código'
      setError(message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white">Inicia sesión</h2>
        <p className="text-gray-400 text-sm">
          Te enviaremos un código de verificación a tu celular.
        </p>
      </div>

      <div className="space-y-4">
        <div className="flex gap-2">
          {/* Country prefix */}
          <div className="flex items-center gap-2 px-3 py-2.5 bg-gray-800 border border-gray-700 rounded-xl text-sm text-gray-300 flex-shrink-0">
            <span className="text-base">🇨🇴</span>
            <span className="font-medium">+57</span>
          </div>

          {/* Phone input */}
          <div className="flex-1">
            <Input
              type="tel"
              placeholder="300 123 4567"
              value={phone}
              onChange={(e) => {
                setPhone(formatPhone(e.target.value))
                setError('')
              }}
              leftIcon={<Phone className="w-4 h-4" />}
              error={error}
              inputMode="numeric"
              autoComplete="tel-national"
              autoFocus
            />
          </div>
        </div>
      </div>

      <Button type="submit" loading={loading} fullWidth size="lg">
        Enviar código
      </Button>

      <p className="text-center text-xs text-gray-600">
        Al continuar aceptas nuestros{' '}
        <span className="text-indigo-400 cursor-pointer hover:underline">
          Términos y Condiciones
        </span>
      </p>
    </form>
  )
}
