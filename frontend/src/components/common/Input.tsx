import { type InputHTMLAttributes, forwardRef } from 'react'
import clsx from 'clsx'

interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
  helperText?: string
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Input = forwardRef<HTMLInputElement, InputProps>(
  ({ label, error, helperText, leftIcon, rightIcon, className, id, ...props }, ref) => {
    const inputId = id || label?.toLowerCase().replace(/\s+/g, '-')

    return (
      <div className="flex flex-col gap-1.5">
        {label && (
          <label
            htmlFor={inputId}
            className="text-sm font-medium text-gray-300"
          >
            {label}
          </label>
        )}

        <div className="relative flex items-center">
          {leftIcon && (
            <div className="absolute left-3 flex items-center pointer-events-none text-gray-500">
              {leftIcon}
            </div>
          )}

          <input
            ref={ref}
            id={inputId}
            className={clsx(
              'w-full rounded-xl border bg-gray-900 text-white placeholder-gray-500',
              'py-2.5 text-sm transition-colors duration-150',
              'focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-transparent',
              leftIcon ? 'pl-10 pr-4' : 'px-4',
              rightIcon ? 'pr-10' : '',
              error
                ? 'border-red-500 focus:ring-red-500'
                : 'border-gray-700 hover:border-gray-600',
              'disabled:opacity-50 disabled:cursor-not-allowed',
              className
            )}
            {...props}
          />

          {rightIcon && (
            <div className="absolute right-3 flex items-center text-gray-500">
              {rightIcon}
            </div>
          )}
        </div>

        {error && (
          <p className="text-xs text-red-400 flex items-center gap-1">
            <svg className="w-3.5 h-3.5 flex-shrink-0" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7 4a1 1 0 11-2 0 1 1 0 012 0zm-1-9a1 1 0 00-1 1v4a1 1 0 102 0V6a1 1 0 00-1-1z"
                clipRule="evenodd"
              />
            </svg>
            {error}
          </p>
        )}

        {helperText && !error && (
          <p className="text-xs text-gray-500">{helperText}</p>
        )}
      </div>
    )
  }
)

Input.displayName = 'Input'

export default Input
