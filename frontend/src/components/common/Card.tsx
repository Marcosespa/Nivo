import type { ReactNode } from 'react'
import clsx from 'clsx'

type Variant = 'default' | 'gradient'

interface CardProps {
  variant?: Variant
  className?: string
  children: ReactNode
  onClick?: () => void
}

const variantClasses: Record<Variant, string> = {
  default: [
    'bg-gray-900/80 border border-gray-800',
    'backdrop-blur-sm',
  ].join(' '),
  gradient: [
    'bg-gradient-to-br from-teal-950/95 via-teal-900/85 to-emerald-950/75',
    'border border-teal-700/40',
    'backdrop-blur-sm',
  ].join(' '),
}

export default function Card({
  variant = 'default',
  className,
  children,
  onClick,
}: CardProps) {
  return (
    <div
      role={onClick ? 'button' : undefined}
      tabIndex={onClick ? 0 : undefined}
      onClick={onClick}
      onKeyDown={
        onClick
          ? (e) => {
              if (e.key === 'Enter' || e.key === ' ') onClick()
            }
          : undefined
      }
      className={clsx(
        'rounded-2xl p-6',
        variantClasses[variant],
        onClick && 'cursor-pointer hover:border-teal-500/50 transition-colors duration-150',
        className
      )}
    >
      {children}
    </div>
  )
}
