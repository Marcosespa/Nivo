import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

const flywheelSteps = [
  {
    label: 'Usuarios activan Nivo',
    detail:
      'Empiezan con pagos, tarjeta y recibos claros. La confianza nace en movimientos cotidianos, no en promesas técnicas.',
  },
  {
    label: 'Freelancers cambian monedas',
    detail:
      'Quienes cobran afuera mueven COP, USD y EUR sin perder visibilidad de tasa, fee y comprobante.',
  },
  {
    label: 'Llegan crypto y acciones',
    detail:
      'Los módulos de inversión se activan por partner, con límites, riesgos y costos antes de confirmar.',
  },
  {
    label: 'Se protege lo que debe durar',
    detail:
      'Identidad, recibos y órdenes sensibles suman firmas verificables, llaves híbridas y trazabilidad de auditoría.',
  },
  {
    label: 'Empresas integran Nivo',
    detail:
      'Pymes digitales y fintechs usan recibos verificables, onboarding, antifraude y PQC híbrido como infraestructura.',
  },
];

export const Flywheel = () => {
  return (
    <section id="flywheel" className="relative bg-nivo-paper py-32">
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">Cómo empieza</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
            La ruta simple: pagar, cambiar, invertir y escalar.
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone">
            Nivo arranca con el dolor más frecuente: mover plata. Desde ahí abre monedas,
            inversión, seguridad post-cuántica y servicios para empresas sin romper la experiencia.
          </p>
        </div>

        <div className="mx-auto mt-20 grid max-w-3xl gap-0">
          {flywheelSteps.map((step, index) => (
            <div key={step.label} className="flex items-start gap-6">
              <div className="flex flex-col items-center">
                <motion.div
                  initial={{ opacity: 0, scale: 0.8 }}
                  whileInView={{ opacity: 1, scale: 1 }}
                  viewport={{ once: true }}
                  transition={{ delay: index * 0.1, duration: 0.3 }}
                  className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full border border-nivo-line bg-nivo-paper font-mono text-[11px] font-medium text-nivo-ink"
                >
                  {String(index + 1).padStart(2, '0')}
                </motion.div>
                {index < flywheelSteps.length - 1 && (
                  <div className="h-20 w-px bg-nivo-line" />
                )}
              </div>
              <motion.div
                initial={{ opacity: 0, x: -8 }}
                whileInView={{ opacity: 1, x: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.1 + 0.08, duration: 0.3 }}
                className="pb-12"
              >
                <p className="font-display text-[19px] font-medium tracking-tightest text-nivo-ink">
                  {step.label}
                </p>
                <p className="mt-2 text-[15px] leading-7 text-nivo-stone">{step.detail}</p>
              </motion.div>
            </div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="mx-auto mt-16 flex max-w-3xl flex-col items-center gap-6 rounded-2xl border border-nivo-line bg-nivo-cloud-soft p-12 text-center md:p-16"
        >
          <Badge variant="outline">Beta abierta</Badge>
          <h3 className="font-display text-3xl font-medium tracking-tightest text-nivo-ink md:text-[40px]">
            Entra a la beta de Nivo.
          </h3>
          <p className="max-w-xl text-[15px] leading-8 text-nivo-stone md:text-base">
            Pagos, cambio de monedas, crypto, acciones y comprobantes protegidos desde
            el primer movimiento.
          </p>
          <div className="mt-2 flex flex-wrap items-center justify-center gap-3">
            <Button variant="forest" size="lg" asChild>
              <a href="mailto:hola@nivo.money">Registrarme gratis</a>
            </Button>
            <Button variant="outline" size="lg" asChild>
              <Link to="/developers">Soy empresa</Link>
            </Button>
          </div>
        </motion.div>
      </div>
    </section>
  );
};
