import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const layers = [
  {
    label: 'Tu App Nivo',
    sublabel: 'iOS · Android · Web',
    accent: false,
  },
  {
    label: 'Capa Nivo',
    sublabel: 'UX · Recibos verificables · KYC · Antifraude · PQC híbrido',
    accent: true,
  },
  {
    label: 'Aliados responsables',
    sublabel: 'PSE · ACH · Emisor de tarjeta · FX · Broker · Exchange',
    accent: false,
  },
];

const integrationModes = [
  {
    title: 'Cuenta diaria',
    description:
      'Paga, recibe, usa tarjeta virtual y administra tus movimientos en pesos colombianos con onboarding rápido y soporte local.',
    tag: 'Para ti',
  },
  {
    title: 'Monedas globales',
    description:
      'Cambia entre COP, USD y EUR con precio claro, historial por moneda y ejecución a través de aliados habilitados.',
    tag: 'Para viajar y cobrar',
  },
  {
    title: 'Inversión modular',
    description:
      'Activa crypto, acciones o ETFs con partners separados, límites visibles y disclosures antes de confirmar.',
    tag: 'Para crecer',
  },
  {
    title: 'Seguridad post-cuántica',
    description:
      'Protege llaves, recibos y órdenes sensibles con ML-KEM, ML-DSA y modo híbrido para mantener compatibilidad.',
    tag: 'Para durar',
  },
];

export const Architecture = () => {
  return (
    <section
      id="architecture"
      className="scroll-mt-24 relative bg-nivo-paper py-32 lg:scroll-mt-28"
    >
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">Arquitectura</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
            Nivo no tiene que ser banco
            <br />
            para darte una experiencia completa.
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone">
            La app concentra la experiencia, la seguridad y los recibos. Los aliados
            responsables ejecutan pagos, divisas, tarjetas, crypto y acciones según
            corresponda.
          </p>
        </div>

        <div className="mx-auto mt-20 flex max-w-2xl flex-col items-center gap-0">
          {layers.map((layer, index) => (
            <div key={layer.label} className="flex w-full flex-col items-center">
              <motion.div
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.12, duration: 0.4 }}
                className={`relative w-full rounded-2xl border px-6 py-6 text-center ${
                  layer.accent
                    ? 'border-nivo-forest bg-nivo-forest text-nivo-paper'
                    : 'border-nivo-line bg-nivo-cloud-soft text-nivo-ink'
                }`}
              >
                <p
                  className={`font-mono text-[10px] font-medium uppercase tracking-[0.32em] ${
                    layer.accent ? 'text-nivo-paper/70' : 'text-nivo-stone'
                  }`}
                >
                  {layer.label}
                </p>
                <p
                  className={`mt-2 font-display text-[17px] ${
                    layer.accent ? 'text-nivo-paper' : 'text-nivo-ink'
                  }`}
                >
                  {layer.sublabel}
                </p>
              </motion.div>

              {index < layers.length - 1 && (
                <div className="h-10 w-px bg-nivo-line" />
              )}
            </div>
          ))}
        </div>

        <div className="mt-24 grid gap-4 md:grid-cols-2 lg:grid-cols-4">
          {integrationModes.map((mode, index) => (
            <motion.div
              key={mode.title}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.4 }}
              className="flex flex-col rounded-2xl border border-nivo-line bg-nivo-paper p-7 transition-colors hover:bg-nivo-cloud-soft"
            >
              <Badge variant="muted">{mode.tag}</Badge>
              <h3 className="mt-6 font-display text-xl font-medium tracking-tightest text-nivo-ink">
                {mode.title}
              </h3>
              <p className="mt-3 text-[14px] leading-7 text-nivo-stone">
                {mode.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
