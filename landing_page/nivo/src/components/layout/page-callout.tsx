import type { ReactNode } from 'react';
import { SurfacePanel } from '@/components/ui/surface-panel';
import { cn } from '@/lib/utils';

interface PageCalloutProps {
  badge: string;
  title: string;
  description: string;
  children?: ReactNode;
  className?: string;
}

export const PageCallout = ({
  badge,
  title,
  description,
  children,
  className,
}: PageCalloutProps) => {
  return (
    <SurfacePanel
      variant="editorial"
      className={cn('mx-auto mt-28 flex max-w-3xl flex-col items-center gap-6 p-8 text-center md:p-12', className)}
    >
      <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
        {badge}
      </p>
      <h3 className="font-display text-2xl font-medium tracking-tightest text-nivo-ink md:text-4xl">
        {title}
      </h3>
      <p className="text-base leading-8 text-nivo-stone">
        {description}
      </p>
      {children ? <div className="mt-2 flex flex-wrap items-center justify-center gap-3">{children}</div> : null}
    </SurfacePanel>
  );
};
