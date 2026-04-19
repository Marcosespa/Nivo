import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const comparisons = [
  {
    fear: 'Me da miedo que me vacíen la cuenta por un link falso.',
    answer:
      'Cada recibo tiene firma digital verificable. Si alguien intenta suplantar un pago o alterar un comprobante, Nivo lo detecta antes de ejecutarse.',
    badge: 'Antifraude activo',
  },
  {
    fear: '¿Y si la app desaparece con mi plata como ha pasado antes?',
    answer:
      'Nivo no custodia tu dinero directamente. Los fondos viven en infraestructura bancaria regulada, segregada de la operación de la empresa.',
    badge: 'Custodia segregada',
  },
  {
    fear: 'El KYC me parece invasivo y no sé quién ve mis datos.',
    answer:
      'Tu identidad se cifra con criptografía post-cuántica. Solo se comparte con las entidades que lo exige la ley, con acceso auditado en bitácora inmutable.',
    badge: 'Privacidad trazable',
  },
  {
    fear: 'Otras apps me han cobrado comisiones que no entendía.',
    answer:
      'Precio antes de confirmar, sin excepciones. Tasa, comisión y destino visibles en la misma pantalla. Si el costo cambia, se cancela automáticamente.',
    badge: 'Precio transparente',
  },
];

export const SafetyPromise = () => {
  return (
    <section id="safety" className="relative bg-nivo-cloud-soft py-32">
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="grid gap-16 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div className="lg:sticky lg:top-32">
            <Badge variant="outline">Hablemos claro</Badge>
            <h2 className="mt-6 font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
              En Colombia, confiar en una app financiera cuesta.
            </h2>
            <p className="mt-6 max-w-lg text-lg leading-8 text-nivo-stone">
              Entendemos el miedo. Estafas por WhatsApp, apps que desaparecen,
              cobros escondidos, datos que se filtran. Por eso Nivo se diseñó al revés:
              primero la seguridad, después la experiencia.
            </p>

            <div className="mt-10 border-l-2 border-nivo-forest pl-6">
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-forest">
                Compromiso Nivo
              </p>
              <p className="mt-3 text-[15px] leading-7 text-nivo-ink">
                Si Nivo detecta un movimiento sospechoso, tu cuenta se pausa
                automáticamente hasta que tú lo confirmes. Sin esperar a que llames.
              </p>
            </div>
          </div>

          <div className="grid gap-4">
            {comparisons.map((item, index) => (
              <motion.div
                key={item.fear}
                initial={{ opacity: 0, x: 12 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08, duration: 0.4 }}
                className="group rounded-2xl border border-nivo-line bg-nivo-paper p-7 transition-shadow duration-300 hover:shadow-card"
              >
                <div className="flex items-start gap-5">
                  <div className="mt-1 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-nivo-ink font-mono text-[11px] font-medium text-nivo-paper">
                    {String(index + 1).padStart(2, '0')}
                  </div>
                  <div className="flex-1">
                    <p className="text-[15px] italic leading-7 text-nivo-stone-soft">
                      "{item.fear}"
                    </p>
                    <div className="mt-5 border-t border-nivo-line pt-5">
                      <span className="inline-flex items-center rounded-full border border-nivo-forest/20 bg-nivo-forest/5 px-2.5 py-1 font-mono text-[10px] font-medium uppercase tracking-[0.24em] text-nivo-forest">
                        {item.badge}
                      </span>
                      <p className="mt-4 text-[15px] leading-7 text-nivo-ink">
                        {item.answer}
                      </p>
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
};
