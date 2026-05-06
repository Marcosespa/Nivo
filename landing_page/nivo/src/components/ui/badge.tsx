import type { HTMLAttributes } from 'react';

type BadgeVariant = 'default' | 'outline' | 'muted' | 'forest';

interface BadgeProps extends HTMLAttributes<HTMLDivElement> {
  variant?: BadgeVariant;
}

const variantClasses: Record<BadgeVariant, string> = {
  default: 'border border-nivo-line bg-nivo-paper text-nivo-ink',
  outline: 'border border-nivo-line bg-transparent text-nivo-stone',
  muted: 'border border-transparent bg-nivo-cloud text-nivo-stone',
  forest: 'border border-nivo-forest/15 bg-nivo-forest/5 text-nivo-forest',
};

export const Badge = ({
  className = '',
  variant = 'default',
  ...props
}: BadgeProps) => {
  return (
    <div
      className={`inline-flex items-center gap-2 rounded-full px-3 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.24em] ${variantClasses[variant]} ${className}`.trim()}
      {...props}
    />
  );
};
