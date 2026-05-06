import { Monitor, Moon, Sun } from 'lucide-react';
import { useTheme } from '@/hooks/use-theme';
import { cn } from '@/lib/utils';

type ThemeOption = 'system' | 'light' | 'dark';

const themeOptions: {
  value: ThemeOption;
  label: string;
  icon: typeof Monitor;
}[] = [
  { value: 'system', label: 'Seguir sistema', icon: Monitor },
  { value: 'light', label: 'Modo claro', icon: Sun },
  { value: 'dark', label: 'Modo oscuro', icon: Moon },
];

interface ThemeToggleProps {
  className?: string;
}

export const ThemeToggle = ({ className }: ThemeToggleProps) => {
  const { preference, resolvedTheme, setTheme } = useTheme();

  return (
    <div
      className={cn(
        'inline-flex items-center rounded-full border border-nivo-line bg-nivo-paper/90 p-1 shadow-subtle backdrop-blur-sm',
        className
      )}
      role="group"
      aria-label="Selector de tema"
    >
      {themeOptions.map(({ value, label, icon: Icon }) => {
        const isActive = preference === value;

        return (
          <button
            key={value}
            type="button"
            onClick={() => setTheme(value)}
            className={cn(
              'inline-flex h-8 w-8 items-center justify-center rounded-full transition-colors',
              isActive
                ? 'bg-nivo-ink text-nivo-paper shadow-subtle'
                : 'text-nivo-stone hover:bg-nivo-cloud-soft hover:text-nivo-ink'
            )}
            aria-label={label}
            aria-pressed={isActive}
            title={
              value === 'system'
                ? `Seguir el sistema (${resolvedTheme === 'dark' ? 'oscuro' : 'claro'})`
                : label
            }
          >
            <Icon className="h-4 w-4" />
          </button>
        );
      })}
    </div>
  );
};
