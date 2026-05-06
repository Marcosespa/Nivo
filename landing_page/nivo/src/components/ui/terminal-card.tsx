import type { ReactNode } from 'react';
import { SurfacePanel } from '@/components/ui/surface-panel';

interface TerminalCardProps {
  title: string;
  children: ReactNode;
  className?: string;
}

export const TerminalCard = ({
  title,
  children,
  className = '',
}: TerminalCardProps) => {
  return (
    <SurfacePanel variant="data" className={`p-5 ${className}`.trim()}>
      <div className="rounded-xl border border-nivo-line/80 bg-gradient-to-b from-nivo-ink/[0.04] to-transparent p-5 dark:from-white/[0.06] dark:to-transparent">
        <div className="flex items-center gap-2 border-b border-nivo-line/80 pb-3">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-3 font-mono text-[11px] uppercase tracking-[0.25em] text-nivo-mist">
            {title}
          </span>
        </div>
        {children}
      </div>
    </SurfacePanel>
  );
};
