import type { HTMLAttributes } from 'react';
import { cn } from '@/lib/utils';

type SurfacePanelVariant = 'editorial' | 'data' | 'glow';

interface SurfacePanelProps extends HTMLAttributes<HTMLDivElement> {
  variant?: SurfacePanelVariant;
}

const variantClasses: Record<SurfacePanelVariant, string> = {
  editorial:
    'min-w-0 rounded-[28px] border border-nivo-line bg-nivo-paper shadow-card',
  data:
    'min-w-0 rounded-[24px] border border-nivo-line bg-nivo-cloud-soft shadow-subtle',
  glow:
    'min-w-0 rounded-[28px] border border-nivo-line bg-nivo-cloud-soft shadow-card',
};

export const SurfacePanel = ({
  className,
  variant = 'editorial',
  ...props
}: SurfacePanelProps) => {
  return <div className={cn(variantClasses[variant], className)} {...props} />;
};
