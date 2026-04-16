import { useState, useEffect, useRef, useCallback } from 'react'
import { ArrowLeft, RefreshCw } from 'lucide-react'
import Button from '../common/Button'
import { authService } from '../../services/auth.service'
import { useAuthStore } from '../../store/authStore'

const OTP_LENGTH = 6
const RESEND_COOLDOWN = 120 // seconds

interface OtpVerificationProps {
  phone: string
  onBack: () => void
  onSuccess: () => void
}

export default function OtpVerification({
  phone,
  onBack,
  onSuccess,
}: OtpVerificationProps) {
  const [digits, setDigits] = useState<string[]>(Array(OTP_LENGTH).fill(''))
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [countdown, setCountdown] = useState(RESEND_COOLDOWN)
  const [resending, setResending] = useState(false)

  const inputRefs = useRef<(HTMLInputElement | null)[]>([])
  const login = useAuthStore((s) => s.login)

  // Countdown timer
  useEffect(() => {
    if (countdown <= 0) return
    const timer = setInterval(() => setCountdown((c) => c - 1), 1000)
    return () => clearInterval(timer)
  }, [countdown])

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60)
    const s = secs % 60
    return `${m}:${s.toString().padStart(2, '0')}`
  }

  const handleVerify = useCallback(
    async (otpCode: string) => {
      setError('')
      setLoading(true)
      try {
        const { access_token, user } = await authService.verifyOtp(phone, otpCode)
        login(access_token, user)
        onSuccess()
      } catch (err: unknown) {
        const message = err instanceof Error ? err.message : 'Código incorrecto'
        setError(message)
        // Clear digits on error
        setDigits(Array(OTP_LENGTH).fill(''))
        inputRefs.current[0]?.focus()
      } finally {
        setLoading(false)
      }
    },
    [phone, login, onSuccess]
  )

  // Auto-submit when all 6 digits are filled
  useEffect(() => {
    const code = digits.join('')
    if (code.length === OTP_LENGTH && !digits.includes('')) {
      handleVerify(code)
    }
  }, [digits, handleVerify])

  const handleDigitChange = (index: number, value: string) => {
    // Handle paste
    if (value.length > 1) {
      const pasted = value.replace(/\D/g, '').slice(0, OTP_LENGTH)
      const newDigits = [...Array(OTP_LENGTH).fill('')]
      pasted.split('').forEach((char, i) => {
        newDigits[i] = char
      })
      setDigits(newDigits)
      const nextIndex = Math.min(pasted.length, OTP_LENGTH - 1)
      inputRefs.current[nextIndex]?.focus()
      return
    }

    const digit = value.replace(/\D/g, '')
    const newDigits = [...digits]
    newDigits[index] = digit
    setDigits(newDigits)

    // Advance to next input
    if (digit && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleKeyDown = (index: number, e: React.KeyboardEvent) => {
    if (e.key === 'Backspace') {
      if (digits[index]) {
        const newDigits = [...digits]
        newDigits[index] = ''
        setDigits(newDigits)
      } else if (index > 0) {
        inputRefs.current[index - 1]?.focus()
      }
    }
    if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus()
    }
    if (e.key === 'ArrowRight' && index < OTP_LENGTH - 1) {
      inputRefs.current[index + 1]?.focus()
    }
  }

  const handleResend = async () => {
    setResending(true)
    setError('')
    try {
      await authService.requestOtp(phone)
      setCountdown(RESEND_COOLDOWN)
      setDigits(Array(OTP_LENGTH).fill(''))
      inputRefs.current[0]?.focus()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al reenviar'
      setError(message)
    } finally {
      setResending(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* Back button */}
      <button
        onClick={onBack}
        className="flex items-center gap-1.5 text-sm text-gray-400 hover:text-white transition-colors"
      >
        <ArrowLeft className="w-4 h-4" />
        Cambiar número
      </button>

      <div className="space-y-2">
        <h2 className="text-2xl font-bold text-white">Ingresa el código</h2>
        <p className="text-gray-400 text-sm">
          Enviamos un código de 6 dígitos a{' '}
          <span className="text-white font-medium">{phone}</span>
        </p>
      </div>

      {/* OTP digit boxes */}
      <div className="flex gap-2 justify-center">
        {digits.map((digit, i) => (
          <input
            key={i}
            ref={(el) => {
              inputRefs.current[i] = el
            }}
            type="text"
            inputMode="numeric"
            maxLength={6}
            value={digit}
            onChange={(e) => handleDigitChange(i, e.target.value)}
            onKeyDown={(e) => handleKeyDown(i, e)}
            onFocus={(e) => e.target.select()}
            autoFocus={i === 0}
            className={[
              'w-12 h-14 text-center text-xl font-bold rounded-xl',
              'bg-gray-900 border-2 text-white',
              'focus:outline-none focus:border-indigo-500',
              'transition-colors duration-150',
              error ? 'border-red-500' : digit ? 'border-indigo-500/60' : 'border-gray-700',
            ].join(' ')}
          />
        ))}
      </div>

      {/* Error message */}
      {error && (
        <p className="text-center text-sm text-red-400">{error}</p>
      )}

      {/* Manual verify button (fallback if auto-submit doesn't fire) */}
      <Button
        fullWidth
        size="lg"
        loading={loading}
        onClick={() => handleVerify(digits.join(''))}
        disabled={digits.join('').length < OTP_LENGTH}
      >
        Verificar código
      </Button>

      {/* Countdown / resend */}
      <div className="text-center">
        {countdown > 0 ? (
          <p className="text-sm text-gray-500">
            Reenviar código en{' '}
            <span className="text-gray-300 font-medium tabular-nums">
              {formatTime(countdown)}
            </span>
          </p>
        ) : (
          <button
            onClick={handleResend}
            disabled={resending}
            className="flex items-center gap-1.5 mx-auto text-sm text-indigo-400 hover:text-indigo-300 disabled:opacity-50 transition-colors"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${resending ? 'animate-spin' : ''}`} />
            Reenviar código
          </button>
        )}
      </div>
    </div>
  )
}
