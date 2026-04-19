import type { ReactNode } from 'react';
import { cn } from '@/lib/utils';

interface PageShellProps {
  children: ReactNode;
  variant?: 'default' | 'orbital';
  className?: string;
  containerClassName?: string;
}

export const PageShell = ({
  children,
  variant = 'orbital',
  className,
  containerClassName,
}: PageShellProps) => {
  return (
    <div className={cn('relative overflow-hidden bg-nivo-paper pt-32 pb-24', className)}>
      {variant === 'orbital' ? (
        <div className="pointer-events-none absolute inset-x-0 top-0 overflow-hidden">
          <div className="absolute inset-x-0 top-0 h-[420px] bg-nivo-grid-fine bg-grid-fine opacity-50" />
          <div className="absolute inset-x-0 top-40 h-px bg-gradient-to-r from-transparent via-nivo-line to-transparent" />
        </div>
      ) : null}

      <div className={cn('relative z-10 mx-auto w-full max-w-6xl px-6 lg:px-10', containerClassName)}>
        {children}
      </div>
    </div>
  );
};
