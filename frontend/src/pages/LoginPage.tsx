import { useState } from 'react'
import { Navigate, useNavigate } from 'react-router-dom'
import { Shield, Zap, Lock, Globe } from 'lucide-react'
import { useAuthStore } from '../store/authStore'
import LoginForm from '../components/auth/LoginForm'
import OtpVerification from '../components/auth/OtpVerification'

type Step = 'phone' | 'otp'

const features = [
  { icon: Zap, text: 'Pagos instantáneos entre usuarios' },
  { icon: Lock, text: 'Seguridad de nivel bancario' },
  { icon: Globe, text: 'Disponible las 24 horas, 7 días' },
]

export default function LoginPage() {
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated)
  const navigate = useNavigate()
  const [step, setStep] = useState<Step>('phone')
  const [phone, setPhone] = useState('')

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const handleOtpSent = (sentPhone: string) => {
    setPhone(sentPhone)
    setStep('otp')
  }

  const handleAuthSuccess = () => {
    navigate('/dashboard', { replace: true })
  }

  return (
    <div className="min-h-screen flex bg-gray-950">
      {/* Left panel — branding / hero */}
      <div className="hidden lg:flex flex-col justify-between w-1/2 bg-gradient-to-br from-indigo-950 via-indigo-900 to-purple-950 p-12 relative overflow-hidden">
        {/* Background decorations */}
        <div className="absolute top-0 left-0 w-full h-full">
          <div className="absolute top-1/4 -left-20 w-72 h-72 rounded-full bg-indigo-700/20 blur-3xl" />
          <div className="absolute bottom-1/4 right-0 w-64 h-64 rounded-full bg-purple-700/20 blur-3xl" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-96 h-96 rounded-full bg-indigo-800/10 blur-3xl" />
        </div>

        <div className="relative z-10">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-white/10 flex items-center justify-center border border-white/20">
              <Shield className="w-5 h-5 text-white" />
            </div>
            <span className="text-2xl font-bold text-white tracking-tight">Nivo</span>
          </div>
        </div>

        {/* Hero text */}
        <div className="relative z-10 space-y-6">
          <div className="space-y-3">
            <h1 className="text-4xl font-bold text-white leading-tight">
              Tu plata,<br />
              <span className="text-indigo-300">en otro nivel.</span>
            </h1>
            <p className="text-indigo-200/80 text-lg leading-relaxed max-w-sm">
              La cuenta digital que te da el control total de tu dinero. Simple, seguro y sin complicaciones.
            </p>
          </div>

          {/* Feature list */}
          <ul className="space-y-3">
            {features.map(({ icon: Icon, text }) => (
              <li key={text} className="flex items-center gap-3 text-indigo-200/70 text-sm">
                <div className="w-7 h-7 rounded-lg bg-white/10 flex items-center justify-center flex-shrink-0">
                  <Icon className="w-3.5 h-3.5 text-indigo-300" />
                </div>
                {text}
              </li>
            ))}
          </ul>
        </div>

        {/* Bottom tagline */}
        <div className="relative z-10">
          <p className="text-indigo-300/50 text-xs">
            © 2025 Nivo Technologies SAS · Colombia
          </p>
        </div>
      </div>

      {/* Right panel — auth form */}
      <div className="flex-1 flex flex-col items-center justify-center px-6 sm:px-12 py-12">
        {/* Mobile logo */}
        <div className="flex items-center gap-2.5 mb-10 lg:hidden">
          <div className="w-9 h-9 rounded-xl bg-indigo-600 flex items-center justify-center">
            <Shield className="w-5 h-5 text-white" />
          </div>
          <span className="text-xl font-bold text-white">Nivo</span>
        </div>

        {/* Form container */}
        <div className="w-full max-w-sm">
          {step === 'phone' ? (
            <div className="animate-fade-in">
              <LoginForm onOtpSent={handleOtpSent} />
            </div>
          ) : (
            <div className="animate-fade-in">
              <OtpVerification
                phone={phone}
                onBack={() => setStep('phone')}
                onSuccess={handleAuthSuccess}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
