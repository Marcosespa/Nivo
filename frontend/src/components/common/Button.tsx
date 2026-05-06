import { type ButtonHTMLAttributes, type ReactNode } from 'react'
import clsx from 'clsx'

type Variant = 'primary' | 'secondary' | 'danger' | 'ghost'
type Size = 'sm' | 'md' | 'lg'

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  fullWidth?: boolean
  children: ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary: [
    'bg-gradient-to-r from-teal-500 to-emerald-500',
    'hover:from-teal-400 hover:to-emerald-400',
    'text-gray-950 font-semibold',
    'shadow-lg shadow-teal-500/20',
    'disabled:from-teal-900 disabled:to-emerald-900 disabled:shadow-none disabled:text-white',
  ].join(' '),
  secondary: [
    'bg-gray-800 hover:bg-gray-700',
    'text-gray-200 font-medium',
    'border border-gray-700 hover:border-gray-600',
    'disabled:bg-gray-900 disabled:text-gray-600',
  ].join(' '),
  danger: [
    'bg-gradient-to-r from-red-600 to-red-500',
    'hover:from-red-500 hover:to-red-400',
    'text-white font-semibold',
    'shadow-lg shadow-red-500/25',
    'disabled:from-red-900 disabled:to-red-800 disabled:shadow-none',
  ].join(' '),
  ghost: [
    'bg-transparent hover:bg-gray-800/60',
    'text-gray-300 hover:text-white font-medium',
    'disabled:text-gray-600',
  ].join(' '),
}

const sizeClasses: Record<Size, string> = {
  sm: 'px-3 py-1.5 text-sm rounded-lg',
  md: 'px-4 py-2.5 text-sm rounded-xl',
  lg: 'px-6 py-3 text-base rounded-xl',
}

function Spinner() {
  return (
    <svg
      className="animate-spin h-4 w-4"
      xmlns="http://www.w3.org/2000/svg"
      fill="none"
      viewBox="0 0 24 24"
    >
      <circle
        className="opacity-25"
        cx="12"
        cy="12"
        r="10"
        stroke="currentColor"
        strokeWidth="4"
      />
      <path
        className="opacity-75"
        fill="currentColor"
        d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
      />
    </svg>
  )
}

export default function Button({
  variant = 'primary',
  size = 'md',
  loading = false,
  fullWidth = false,
  disabled,
  className,
  children,
  ...props
}: ButtonProps) {
  return (
    <button
      disabled={disabled || loading}
      className={clsx(
        'inline-flex items-center justify-center gap-2',
        'transition-all duration-150 cursor-pointer',
        'disabled:cursor-not-allowed disabled:opacity-60',
        variantClasses[variant],
        sizeClasses[size],
        fullWidth && 'w-full',
        className
      )}
      {...props}
    >
      {loading && <Spinner />}
      {children}
    </button>
  )
}
