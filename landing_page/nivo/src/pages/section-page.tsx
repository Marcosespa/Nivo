import { Link } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { SurfacePanel } from '@/components/ui/surface-panel';
import { PageHeader } from '@/components/layout/page-header';
import { PageShell } from '@/components/layout/page-shell';
import { PageCallout } from '@/components/layout/page-callout';

interface SectionPageStat {
  value: string;
  label: string;
}

interface SectionPageCard {
  title: string;
  description: string;
}

export interface SectionPageProps {
  badge: string;
  title: string;
  description: string;
  proof: string;
  stats: SectionPageStat[];
  cards: SectionPageCard[];
  calloutTitle: string;
  calloutDescription: string;
}

export const SectionPage = ({
  badge,
  title,
  description,
  proof,
  stats,
  cards,
  calloutTitle,
  calloutDescription,
}: SectionPageProps) => {
  return (
    <PageShell>
      <PageHeader
        badge={badge}
        title={title}
        description={description}
        proof={proof}
        stats={stats}
        actions={
          <>
            <Button variant="forest" size="lg" asChild>
              <a href="mailto:hola@nivo.money">Unirme a la beta</a>
            </Button>
            <Link to="/">
              <Button variant="outline" size="lg">
                Volver al inicio
              </Button>
            </Link>
          </>
        }
      />

      <div className="mt-16 grid gap-6 md:grid-cols-3">
        {cards.map((card) => (
          <SurfacePanel key={card.title} variant="editorial" className="p-6 md:p-8">
            <Badge variant="muted">{badge}</Badge>
            <h2 className="mt-5 font-display text-xl font-medium tracking-tightest text-nivo-ink">
              {card.title}
            </h2>
            <p className="mt-4 text-[15px] leading-7 text-nivo-stone">{card.description}</p>
          </SurfacePanel>
        ))}
      </div>

      <PageCallout
        badge="Siguiente paso"
        title={calloutTitle}
        description={calloutDescription}
        className="max-w-4xl"
      >
        <Button variant="forest" size="lg" asChild>
          <a href="mailto:hola@nivo.money">Hablar con Nivo</a>
        </Button>
      </PageCallout>
    </PageShell>
  );
};
