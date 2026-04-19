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
      <div className="rounded-xl border border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.03),rgba(255,255,255,0.01))] p-5">
        <div className="flex items-center gap-2 border-b border-white/8 pb-3">
          <span className="h-2.5 w-2.5 rounded-full bg-[#ff5f57]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#febc2e]" />
          <span className="h-2.5 w-2.5 rounded-full bg-[#28c840]" />
          <span className="ml-3 font-mono text-[11px] uppercase tracking-[0.25em] text-slate-500">
            {title}
          </span>
        </div>
        {children}
      </div>
    </SurfacePanel>
  );
};
