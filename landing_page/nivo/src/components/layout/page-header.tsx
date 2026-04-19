import type { ReactNode } from 'react';
import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import { SurfacePanel } from '@/components/ui/surface-panel';
import { cn } from '@/lib/utils';

interface PageHeaderStat {
  value: string;
  label: string;
}

interface PageHeaderProps {
  badge: string;
  title: string;
  description: string;
  proof?: string;
  stats?: PageHeaderStat[];
  actions?: ReactNode;
  visual?: ReactNode;
  className?: string;
}

export const PageHeader = ({
  badge,
  title,
  description,
  proof,
  stats,
  actions,
  visual,
  className,
}: PageHeaderProps) => {
  if (!visual) {
    return (
      <div className={cn('flex flex-col gap-5 md:max-w-4xl', className)}>
        <Badge variant="outline">{badge}</Badge>
        <h1 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[64px]">
          {title}
        </h1>
        <p className="max-w-3xl text-lg leading-8 text-nivo-stone md:text-xl">
          {description}
        </p>
        {proof ? (
          <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
            {proof}
          </p>
        ) : null}
        {stats?.length ? (
          <div className="grid gap-3 sm:grid-cols-3">
            {stats.map((stat) => (
              <div
                key={`${stat.label}-${stat.value}`}
                className="rounded-2xl border border-nivo-line bg-nivo-cloud-soft px-5 py-4"
              >
                <p className="font-display text-xl font-medium tracking-tightest text-nivo-ink">
                  {stat.value}
                </p>
                <p className="mt-1 font-mono text-[10px] uppercase tracking-[0.24em] text-nivo-mist">
                  {stat.label}
                </p>
              </div>
            ))}
          </div>
        ) : null}
        {actions ? <div className="flex flex-wrap items-center gap-3 pt-2">{actions}</div> : null}
      </div>
    );
  }

  return (
    <SurfacePanel
      variant="glow"
      className={cn('relative overflow-hidden p-6 md:p-8 lg:p-10', className)}
    >
      <div className="absolute inset-x-0 top-0 h-48 bg-nivo-grid-fine bg-grid-fine opacity-40" />
      <div className="absolute left-10 right-10 top-0 h-px bg-gradient-to-r from-transparent via-nivo-line to-transparent" />

      <div className="relative z-10 grid items-center gap-10 lg:grid-cols-[0.92fr_1.08fr] lg:gap-14">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.45, ease: [0.16, 1, 0.3, 1] }}
          className="min-w-0 max-w-xl"
        >
          <Badge variant="outline">
            {badge}
          </Badge>
          <h1 className="mt-6 max-w-4xl font-display text-[40px] font-medium leading-[1.02] tracking-tightest text-nivo-ink md:text-[64px]">
            {title}
          </h1>
          <p className="mt-6 max-w-3xl text-lg leading-8 text-nivo-stone md:text-xl">
            {description}
          </p>

          {proof ? (
            <p className="mt-6 break-words font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
              {proof}
            </p>
          ) : null}

          {stats?.length ? (
            <div className="mt-8 grid gap-3 md:grid-cols-3">
              {stats.map((stat, index) => (
                <motion.div
                  key={`${stat.label}-${stat.value}`}
                  initial={{ opacity: 0, y: 12 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{
                    delay: 0.12 + index * 0.05,
                    duration: 0.3,
                    ease: [0.16, 1, 0.3, 1],
                  }}
                  className="min-w-0 rounded-2xl border border-nivo-line bg-nivo-paper px-4 py-4"
                >
                  <p className="break-words font-display text-lg font-medium tracking-tightest text-nivo-ink md:text-xl">
                    {stat.value}
                  </p>
                  <p className="mt-1 break-words font-mono text-[10px] uppercase tracking-[0.2em] text-nivo-mist">
                    {stat.label}
                  </p>
                </motion.div>
              ))}
            </div>
          ) : null}

          {actions ? (
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.22, duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
              className="mt-8 flex flex-wrap items-center gap-3"
            >
              {actions}
            </motion.div>
          ) : null}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, x: 24, scale: 0.985 }}
          animate={{ opacity: 1, x: 0, scale: 1 }}
          transition={{ delay: 0.08, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
          className="relative z-10 min-w-0"
        >
          {visual}
        </motion.div>
      </div>
    </SurfacePanel>
  );
};
