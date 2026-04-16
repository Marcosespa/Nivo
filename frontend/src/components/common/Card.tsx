import clsx from 'clsx'

type Variant = 'default' | 'gradient'

interface CardProps {
  variant?: Variant
  className?: string
  children: React.ReactNode
  onClick?: () => void
}

const variantClasses: Record<Variant, string> = {
  default: [
    'bg-gray-900/80 border border-gray-800',
    'backdrop-blur-sm',
  ].join(' '),
  gradient: [
    'bg-gradient-to-br from-indigo-900/90 via-indigo-800/80 to-purple-900/70',
    'border border-indigo-700/50',
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
        onClick && 'cursor-pointer hover:border-indigo-600/60 transition-colors duration-150',
        className
      )}
    >
      {children}
    </div>
  )
}
