import { cloneElement, isValidElement, type ButtonHTMLAttributes, type ReactNode } from 'react';
import { cn } from '@/lib/utils';

type ButtonVariant = 'forest' | 'ink' | 'outline' | 'ghost' | 'link';
type ButtonSize = 'default' | 'lg' | 'sm' | 'icon';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  asChild?: boolean;
  variant?: ButtonVariant;
  size?: ButtonSize;
  children?: ReactNode;
}

const variantClasses: Record<ButtonVariant, string> = {
  forest:
    'bg-nivo-forest text-white hover:bg-nivo-forest-soft shadow-forest',
  ink:
    'bg-nivo-ink text-nivo-paper hover:bg-nivo-stone',
  outline:
    'border border-nivo-ink bg-transparent text-nivo-ink hover:bg-nivo-ink hover:text-nivo-paper',
  ghost:
    'bg-transparent text-nivo-stone hover:bg-nivo-cloud-soft hover:text-nivo-ink',
  link:
    'bg-transparent text-nivo-ink hover:text-nivo-forest underline-offset-4 hover:underline px-0',
};

const sizeClasses: Record<ButtonSize, string> = {
  sm: 'h-9 px-4 text-xs',
  default: 'h-11 px-5 text-sm',
  lg: 'h-12 px-7 text-[15px]',
  icon: 'h-11 w-11 text-sm',
};

export const Button = ({
  className = '',
  variant = 'forest',
  size = 'default',
  asChild = false,
  type = 'button',
  children,
  ...props
}: ButtonProps) => {
  const classes = cn(
    'inline-flex items-center justify-center rounded-full font-medium tracking-[-0.01em] transition-colors duration-200 ease-out',
    variantClasses[variant],
    sizeClasses[size],
    className
  );

  if (asChild && isValidElement<{ className?: string }>(children)) {
    return cloneElement(children, {
      className: cn(classes, children.props.className),
    });
  }

  return (
    <button type={type} className={classes} {...props}>
      {children}
    </button>
  );
};
