import { useState } from 'react'
import { Phone, DollarSign, FileText, CheckCircle, AlertCircle } from 'lucide-react'
import Input from '../common/Input'
import Button from '../common/Button'
import { paymentsService } from '../../services/payments.service'

interface SendPaymentProps {
  onSuccess?: () => void
}

function formatCOPDisplay(raw: string): string {
  const digits = raw.replace(/\D/g, '')
  if (!digits) return ''
  return new Intl.NumberFormat('es-CO').format(Number(digits))
}

type FormState = 'idle' | 'loading' | 'success' | 'error'

export default function SendPayment({ onSuccess }: SendPaymentProps) {
  const [recipientPhone, setRecipientPhone] = useState('')
  const [amountRaw, setAmountRaw] = useState('')
  const [description, setDescription] = useState('')
  const [formState, setFormState] = useState<FormState>('idle')
  const [errorMsg, setErrorMsg] = useState('')

  const [phoneError, setPhoneError] = useState('')
  const [amountError, setAmountError] = useState('')

  const amountValue = Number(amountRaw.replace(/\D/g, ''))

  const validate = (): boolean => {
    let valid = true
    setPhoneError('')
    setAmountError('')

    const cleanPhone = recipientPhone.replace(/\D/g, '')
    if (cleanPhone.length < 10) {
      setPhoneError('Ingresa un número válido (10 dígitos)')
      valid = false
    }
    if (amountValue <= 0) {
      setAmountError('Ingresa un monto mayor a $0')
      valid = false
    }
    if (amountValue < 1000) {
      setAmountError('El monto mínimo es $1.000 COP')
      valid = false
    }

    return valid
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!validate()) return

    const cleanPhone = recipientPhone.replace(/\D/g, '')
    const fullPhone = cleanPhone.startsWith('57') ? `+${cleanPhone}` : `+57${cleanPhone}`

    setFormState('loading')
    setErrorMsg('')

    try {
      await paymentsService.sendPayment(fullPhone, amountValue, description || undefined)
      setFormState('success')
      onSuccess?.()
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Error al enviar el pago'
      setErrorMsg(message)
      setFormState('error')
    }
  }

  const handleReset = () => {
    setRecipientPhone('')
    setAmountRaw('')
    setDescription('')
    setFormState('idle')
    setErrorMsg('')
    setPhoneError('')
    setAmountError('')
  }

  // Success state
  if (formState === 'success') {
    return (
      <div className="flex flex-col items-center justify-center py-10 text-center space-y-4 animate-fade-in">
        <div className="w-16 h-16 rounded-full bg-emerald-500/15 flex items-center justify-center">
          <CheckCircle className="w-8 h-8 text-emerald-400" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-white">¡Pago enviado!</h3>
          <p className="text-gray-400 text-sm mt-1">
            Enviaste{' '}
            <span className="text-white font-medium">
              {new Intl.NumberFormat('es-CO', {
                style: 'currency',
                currency: 'COP',
                minimumFractionDigits: 0,
              }).format(amountValue)}
            </span>{' '}
            a{' '}
            <span className="text-white font-medium">{recipientPhone}</span>
          </p>
        </div>
        <Button variant="secondary" onClick={handleReset}>
          Hacer otro pago
        </Button>
      </div>
    )
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* Error banner */}
      {formState === 'error' && errorMsg && (
        <div className="flex items-start gap-3 px-4 py-3 rounded-xl bg-red-500/10 border border-red-500/20 animate-fade-in">
          <AlertCircle className="w-4 h-4 text-red-400 flex-shrink-0 mt-0.5" />
          <p className="text-sm text-red-400">{errorMsg}</p>
        </div>
      )}

      <Input
        label="Número de celular del destinatario"
        type="tel"
        placeholder="+57 300 123 4567"
        value={recipientPhone}
        onChange={(e) => {
          setRecipientPhone(e.target.value)
          setPhoneError('')
          if (formState === 'error') setFormState('idle')
        }}
        leftIcon={<Phone className="w-4 h-4" />}
        error={phoneError}
        inputMode="tel"
        autoComplete="off"
      />

      <Input
        label="Monto (COP)"
        type="text"
        placeholder="0"
        value={amountRaw ? formatCOPDisplay(amountRaw) : ''}
        onChange={(e) => {
          setAmountRaw(e.target.value.replace(/\D/g, ''))
          setAmountError('')
          if (formState === 'error') setFormState('idle')
        }}
        leftIcon={<DollarSign className="w-4 h-4" />}
        error={amountError}
        inputMode="numeric"
        helperText="Mínimo $1.000 COP"
      />

      <Input
        label="Descripción (opcional)"
        type="text"
        placeholder="ej. Cena del viernes"
        value={description}
        onChange={(e) => setDescription(e.target.value)}
        leftIcon={<FileText className="w-4 h-4" />}
        maxLength={120}
      />

      <Button
        type="submit"
        fullWidth
        size="lg"
        loading={formState === 'loading'}
      >
        Enviar pago
      </Button>
    </form>
  )
}
