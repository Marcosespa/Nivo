import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const standardBlocks = [
  {
    label: 'ML-KEM · FIPS 203',
    title: 'Intercambio de llaves resistente a cuántica',
    description:
      'Los secretos compartidos nunca viajan en claro. Protege la negociación de canal cifrado contra ataques futuros.',
  },
  {
    label: 'ML-DSA · FIPS 204',
    title: 'Firmas verificables para órdenes',
    description:
      'Firmas digitales que comprueban que una instrucción no fue alterada después de aceptarse.',
  },
  {
    label: 'SLH-DSA · FIPS 205',
    title: 'Respaldo para larga duración',
    description:
      'Firma basada en hash para casos donde conviene diversidad criptográfica y conservación prolongada.',
  },
];

const readinessPoints = [
  {
    title: 'Riesgo "guardar hoy, descifrar mañana"',
    description:
      'Identidad, recibos y contratos viven años. Nivo prioriza PQC en la información que seguiría siendo sensible si alguien la captura hoy.',
  },
  {
    title: 'Modo híbrido durante la transición',
    description:
      'PQC se combina con criptografía clásica (X25519) mientras bancos, pasarelas, dispositivos y proveedores terminan su migración.',
  },
  {
    title: 'Criptoagilidad sin promesas mágicas',
    description:
      'PQC cubre un riesgo específico. La defensa real también necesita KYC, antifraude, límites, monitoreo y rotación de llaves.',
  },
];

export const QuantumSecurity = () => {
  return (
    <section id="quantum-security" className="relative bg-nivo-cloud-soft py-32">
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="grid gap-14 lg:grid-cols-[0.9fr_1.1fr] lg:items-start">
          <div>
            <Badge variant="outline">Arquitectura técnica · para devs y auditores</Badge>
            <h2 className="mt-6 max-w-3xl font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
              Protección pensada para datos que no pueden caducar.
            </h2>
            <p className="mt-6 max-w-2xl text-lg leading-8 text-nivo-stone">
              La amenaza cuántica no significa que el dinero deje de moverse mañana. El
              riesgo real es que datos cifrados hoy sean útiles para un atacante cuando
              existan computadoras cuánticas criptográficamente relevantes.
            </p>
            <p className="mt-5 max-w-2xl text-[15px] leading-8 text-nivo-stone-soft">
              Nivo usa una estrategia gradual: aplicar PQC donde aporta más valor,
              mantener compatibilidad con sistemas actuales y versionar algoritmos para
              poder migrar sin rehacer toda la plataforma.
            </p>
          </div>

          <div className="grid gap-3">
            {readinessPoints.map((point, index) => (
              <motion.div
                key={point.title}
                initial={{ opacity: 0, y: 12 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.08, duration: 0.35 }}
                className="rounded-2xl border border-nivo-line bg-nivo-paper p-6"
              >
                <h3 className="font-display text-lg font-medium tracking-tightest text-nivo-ink">
                  {point.title}
                </h3>
                <p className="mt-3 text-[14px] leading-7 text-nivo-stone">
                  {point.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>

        <div className="mt-16 grid gap-3 md:grid-cols-3">
          {standardBlocks.map((block, index) => (
            <motion.div
              key={block.label}
              initial={{ opacity: 0, y: 12 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.08, duration: 0.35 }}
              className="rounded-2xl border border-nivo-ink bg-nivo-ink p-7 text-nivo-paper"
            >
              <p className="font-mono text-[10px] font-medium uppercase tracking-[0.28em] text-nivo-paper/70">
                {block.label}
              </p>
              <h3 className="mt-5 font-display text-lg font-medium tracking-tightest text-nivo-paper">
                {block.title}
              </h3>
              <p className="mt-3 text-[14px] leading-7 text-nivo-cloud">
                {block.description}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};
