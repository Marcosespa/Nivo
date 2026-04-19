import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const shieldSteps = [
  {
    step: '01',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 10.5V6.75a4.5 4.5 0 1 0-9 0v3.75m-.75 11.25h10.5a2.25 2.25 0 0 0 2.25-2.25v-6.75a2.25 2.25 0 0 0-2.25-2.25H6.75a2.25 2.25 0 0 0-2.25 2.25v6.75a2.25 2.25 0 0 0 2.25 2.25Z" />
      </svg>
    ),
    title: 'Identidad bajo doble candado',
    description:
      'Tus datos viajan protegidos por una llave que ni el computador más potente del mundo podrá romper en 20 años.',
    analogy: 'Como un buzón blindado al que solo tú tienes la combinación.',
  },
  {
    step: '02',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="M3.75 21h16.5M4.5 3h15M5.25 3v18m13.5-18v18M9 6.75h1.5m-1.5 3h1.5m-1.5 3h1.5m3-6H15m-1.5 3H15m-1.5 3H15M9 21v-3.375c0-.621.504-1.125 1.125-1.125h3.75c.621 0 1.125.504 1.125 1.125V21" />
      </svg>
    ),
    title: 'Bóveda con llave futura',
    description:
      'Usamos el mismo estándar de seguridad que gobiernos y banca suiza apenas empiezan a adoptar — aprobado por el NIST en 2024.',
    analogy: 'La cerradura que protege secretos de agencias de inteligencia.',
  },
  {
    step: '03',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="h-5 w-5" strokeWidth={1.5} stroke="currentColor">
        <path strokeLinecap="round" strokeLinejoin="round" d="m16.862 4.487 1.687-1.688a1.875 1.875 0 1 1 2.652 2.652L10.582 16.07a4.5 4.5 0 0 1-1.897 1.13L6 18l.8-2.685a4.5 4.5 0 0 1 1.13-1.897l8.932-8.931Zm0 0L19.5 7.125M18 14v4.75A2.25 2.25 0 0 1 15.75 21H5.25A2.25 2.25 0 0 1 3 18.75V8.25A2.25 2.25 0 0 1 5.25 6H10" />
      </svg>
    ),
    title: 'Cada pago, firmado y verificable',
    description:
      'Cada transacción lleva una firma digital única. Si alguien intenta alterar un recibo, Nivo lo detecta al instante.',
    analogy: 'Un sello notarial digital que viaja con cada peso que mueves.',
  },
];

export const QuantumShield = () => {
  return (
    <section
      id="quantum-shield"
      className="scroll-mt-24 relative bg-nivo-paper py-32 lg:scroll-mt-28"
    >
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">Seguridad del futuro, hoy</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[64px]">
            Tu dinero,
            <br />
            blindado para 2045.
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone md:text-xl md:leading-9">
            Hoy tu plata está segura. Nivo se asegura de que siga estándolo cuando los
            computadores cuánticos puedan romper la seguridad que usa el resto de la
            banca. Sin jerga técnica. Sin promesas vacías.
          </p>
        </div>

        <div className="mt-20 grid gap-6 md:grid-cols-3">
          {shieldSteps.map((step, index) => (
            <motion.div
              key={step.step}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.4 }}
              className="group flex flex-col rounded-2xl border border-nivo-line bg-nivo-cloud-soft p-8 transition-colors duration-300 hover:bg-nivo-cloud"
            >
              <div className="flex items-center justify-between">
                <span className="font-mono text-[10px] font-medium uppercase tracking-[0.32em] text-nivo-mist">
                  Paso {step.step}
                </span>
                <div className="flex h-10 w-10 items-center justify-center rounded-full bg-nivo-forest text-white">
                  {step.icon}
                </div>
              </div>

              <h3 className="mt-10 font-display text-[22px] font-medium leading-snug tracking-tightest text-nivo-ink">
                {step.title}
              </h3>
              <p className="mt-4 text-[15px] leading-7 text-nivo-stone">
                {step.description}
              </p>

              <div className="mt-8 border-t border-nivo-line pt-5">
                <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-stone-soft">
                  En palabras simples
                </p>
                <p className="mt-2 text-[14px] italic leading-6 text-nivo-ink">
                  "{step.analogy}"
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
