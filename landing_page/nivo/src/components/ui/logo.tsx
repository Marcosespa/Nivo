import { cn } from '@/lib/utils';

type LogoMarkProps = {
  className?: string;
};

export const NivoMark = ({ className }: LogoMarkProps) => (
  <svg
    viewBox="0 0 64 64"
    role="img"
    aria-label="Nivo"
    className={cn('h-5 w-5', className)}
  >
    <rect width="64" height="64" rx="12" fill="currentColor" />
    <g stroke="#FFFFFF" strokeLinecap="square" strokeLinejoin="miter" fill="none">
      <path d="M18 48 L18 16 L46 48 L46 16" strokeWidth="3" />
      <path d="M24 42 L24 24 L40 42 L40 24" strokeWidth="1.2" opacity="0.55" />
      <path d="M28 38 L28 30 L36 38 L36 30" strokeWidth="0.7" opacity="0.3" />
    </g>
  </svg>
);

interface NivoLogoProps {
  showWordmark?: boolean;
  showTagline?: boolean;
  className?: string;
  tone?: 'ink' | 'paper';
}

export const NivoLogo = ({
  showWordmark = true,
  showTagline = false,
  className,
  tone = 'ink',
}: NivoLogoProps) => {
  const isDark = tone === 'ink';
  return (
    <span className={cn('flex items-center gap-2.5', className)}>
      <span className={cn('flex h-8 w-8 items-center justify-center', isDark ? 'text-nivo-ink' : 'text-nivo-paper')}>
        <NivoMark className="h-full w-full" />
      </span>

      {showWordmark && (
        <span className="flex flex-col justify-center">
          <span
            className={cn(
              'font-display text-[20px] font-medium leading-none tracking-tightest',
              isDark ? 'text-nivo-ink' : 'text-nivo-paper'
            )}
          >
            Nivo
          </span>

          {showTagline && (
            <span
              className={cn(
                'mt-1 block font-mono text-[10px] font-normal uppercase tracking-[0.24em]',
                isDark ? 'text-nivo-stone' : 'text-nivo-cloud'
              )}
            >
              Post-Quantum Banking
            </span>
          )}
        </span>
      )}
    </span>
  );
};
