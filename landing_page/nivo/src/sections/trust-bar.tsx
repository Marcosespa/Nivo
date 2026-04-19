import { motion } from 'framer-motion';

const trustPoints = [
  { label: 'Ruta regulatoria Colombia', sub: 'Infraestructura y aliados compatibles con operación local' },
  { label: 'NIST FIPS 203 / 204', sub: 'Estándares aprobados en agosto de 2024' },
  { label: 'Wompi · ACH · PSE', sub: 'Infraestructura de pagos en Colombia' },
  { label: 'ISO 27001 · SOC 2', sub: 'Controles auditables y trazabilidad operativa' },
];

export const TrustBar = () => {
  return (
    <section
      id="trust"
      className="scroll-mt-24 relative border-y border-nivo-line bg-nivo-paper py-12 lg:scroll-mt-28"
    >
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <p className="text-center font-mono text-[10px] font-medium uppercase tracking-[0.32em] text-nivo-mist">
          Confianza respaldada, no prometida
        </p>

        <div className="mt-10 grid gap-10 md:grid-cols-4">
          {trustPoints.map((point, index) => (
            <motion.div
              key={point.label}
              initial={{ opacity: 0, y: 8 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.06, duration: 0.35 }}
              className="group text-center md:text-left"
            >
              <p className="font-display text-lg font-medium tracking-tightest text-nivo-ink">
                {point.label}
              </p>
              <p className="mt-1 text-[13px] leading-6 text-nivo-stone-soft">
                {point.sub}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
