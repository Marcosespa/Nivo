import { Badge } from '@/components/ui/badge';

interface SectionHeaderProps {
  badge: string;
  title: string;
  description?: string;
  className?: string;
  align?: 'center' | 'left';
}

export const SectionHeader = ({
  badge,
  title,
  description,
  className = '',
  align = 'center',
}: SectionHeaderProps) => {
  return (
    <div
      className={`flex flex-col gap-4 ${
        align === 'left' ? 'items-start text-left' : 'items-center text-center'
      } ${className}`.trim()}
    >
      <Badge variant="outline">{badge}</Badge>
      <h2 className="max-w-3xl font-display text-3xl font-medium leading-tight tracking-tightest text-nivo-ink md:text-5xl">
        {title}
      </h2>
      {description ? (
        <p className="max-w-3xl text-base leading-8 text-nivo-stone md:text-lg">
          {description}
        </p>
      ) : null}
    </div>
  );
};
