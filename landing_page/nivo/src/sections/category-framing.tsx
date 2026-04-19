import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const comparisons = [
  {
    technology: 'Billeteras locales',
    problem: 'Pago rápido en COP',
    infrastructure: 'Nequi / Daviplata',
  },
  {
    technology: 'Apps globales',
    problem: 'Monedas y viajes',
    infrastructure: 'Revolut',
  },
  {
    technology: 'Inversión móvil',
    problem: 'Crypto, acciones y ETFs',
    infrastructure: 'Binance / Robinhood',
  },
  {
    technology: 'LATAM global',
    problem: 'Todo junto, claro y trazable',
    infrastructure: 'Nivo',
    highlight: true,
  },
];

const expansionLayers = [
  {
    title: 'Cuenta y tarjeta',
    description:
      'Pagos P2P, links de cobro, tarjeta virtual y movimientos claros para el día a día en Colombia.',
  },
  {
    title: 'Cambio entre monedas',
    description:
      'COP, USD y EUR con tasa visible antes de confirmar, historial por moneda y alertas de precio.',
  },
  {
    title: 'Crypto y acciones',
    description:
      'Módulos separados por partner para criptoactivos, acciones y ETFs con riesgos, costos y custodia visibles.',
  },
  {
    title: 'Seguridad y API para empresas',
    description:
      'Recibos verificables, onboarding, antifraude y PQC híbrido para fintechs, pymes digitales y comercios exportadores.',
  },
];

export const CategoryFraming = () => {
  return (
    <section id="category" className="relative bg-nivo-paper py-32">
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">Por qué ahora</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
            LATAM ya usa billeteras.
            <br />
            Ahora necesita una cuenta global simple.
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone">
            Nivo toma lo que la gente ya entiende de Nequi y lo combina con cambio de
            monedas, inversión, trazabilidad y protección post-cuántica para una vida
            financiera más internacional.
          </p>
        </div>

        <div className="mx-auto mt-16 max-w-4xl overflow-hidden rounded-2xl border border-nivo-line bg-nivo-paper">
          <div className="grid grid-cols-3 border-b border-nivo-line px-6 py-4">
            <p className="font-mono text-[10px] font-medium uppercase tracking-[0.28em] text-nivo-mist">
              Era
            </p>
            <p className="font-mono text-[10px] font-medium uppercase tracking-[0.28em] text-nivo-mist">
              Problema
            </p>
            <p className="font-mono text-[10px] font-medium uppercase tracking-[0.28em] text-nivo-mist">
              Solución
            </p>
          </div>
          {comparisons.map((row, index) => (
            <motion.div
              key={row.technology}
              initial={{ opacity: 0, x: -8 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.35 }}
              className={`grid grid-cols-3 border-b border-nivo-line px-6 py-5 last:border-b-0 ${
                row.highlight ? 'bg-nivo-forest text-nivo-paper' : ''
              }`}
            >
              <p
                className={`text-[15px] ${
                  row.highlight ? 'text-nivo-paper/80' : 'text-nivo-stone'
                }`}
              >
                {row.technology}
              </p>
              <p
                className={`text-[15px] ${
                  row.highlight ? 'text-nivo-paper/80' : 'text-nivo-stone'
                }`}
              >
                {row.problem}
              </p>
              <p
                className={`font-display text-[15px] font-medium ${
                  row.highlight ? 'text-nivo-paper' : 'text-nivo-ink'
                }`}
              >
                {row.infrastructure}
              </p>
            </motion.div>
          ))}
        </div>

        <div className="mt-24 flex flex-col gap-4 md:max-w-3xl">
          <Badge variant="outline">Qué crece dentro de Nivo</Badge>
          <h3 className="font-display text-3xl font-medium leading-tight tracking-tightest text-nivo-ink md:text-[40px]">
            Primero pagos. Luego monedas, inversión y servicios para empresas.
          </h3>
        </div>

        <div className="mt-12 grid gap-3 sm:grid-cols-2">
          {expansionLayers.map((layer, index) => (
            <motion.div
              key={layer.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.35 }}
              className="rounded-2xl border border-nivo-line bg-nivo-cloud-soft p-7"
            >
              <h4 className="font-display text-lg font-medium tracking-tightest text-nivo-ink">
                {layer.title}
              </h4>
              <p className="mt-3 text-[14px] leading-7 text-nivo-stone">
                {layer.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
