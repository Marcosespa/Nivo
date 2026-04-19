import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';

const pillars = [
  {
    kicker: 'Qué es, sin física',
    title: 'Una computadora distinta',
    body:
      'La computación cuántica aprovecha propiedades de partículas muy pequeñas para resolver algunos problemas mucho más rápido que un PC convencional. En la calle casi no la notas; en criptografía sí, porque buena parte de los candados digitales actuales asumían que nadie podría ensayar tantas combinaciones en un tiempo razonable.',
  },
  {
    kicker: 'Por qué te importa',
    title: 'Guardar hoy, leer mañana',
    body:
      'El riesgo real no es que mañana desaparezca tu saldo. Es que alguien capture datos cifrados hoy —identidad, claves, recibos— y los conserve años hasta que una máquina cuántica pueda descifrarlos. En el sector se habla de “cosechar ahora, descifrar después”. Lo que firmas o archivas hoy puede seguir siendo sensible dentro de una década.',
  },
  {
    kicker: 'Qué ganas con Nivo',
    title: 'Misma app, candado del futuro',
    body:
      'Nivo incorpora criptografía post-cuántica alineada con el NIST (el mismo marco que usan gobiernos y grandes bancos) donde más duele si falla: identidad, recibos y acuerdos de largo plazo. Tú sigues pagando y cobrando igual; nosotros endurecemos la capa invisible para que no dependas de migraciones apresuradas cuando el riesgo deje de ser teoría.',
  },
];

export const WhyQuantum = () => {
  return (
    <section
      id="why-quantum"
      className="scroll-mt-24 relative border-y border-nivo-line bg-nivo-cloud-soft py-28 lg:scroll-mt-28"
    >
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">Por qué la cuántica importa</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
            ¿Qué es lo &quot;cuántico&quot;
            <br />
            y por qué elegir Nivo?
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone md:text-xl md:leading-9">
            No hace falta entender la física. Sí conviene saber que la siguiente generación
            de máquinas puede dejar cortos algunos métodos de protección que hoy dan por
            cerrados bancos y apps. Nivo integra desde el diseño estándares
            post-cuánticos para que tu cuenta no quede rezagada cuando eso pase.
          </p>
        </div>

        <div className="mt-16 grid gap-5 md:grid-cols-3">
          {pillars.map((item, index) => (
            <motion.article
              key={item.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.07, duration: 0.4 }}
              className="flex flex-col rounded-2xl border border-nivo-line bg-nivo-paper p-7 shadow-subtle"
            >
              <p className="font-mono text-[10px] font-medium uppercase tracking-[0.28em] text-nivo-forest">
                {item.kicker}
              </p>
              <h3 className="mt-5 font-display text-[22px] font-medium leading-snug tracking-tightest text-nivo-ink">
                {item.title}
              </h3>
              <p className="mt-4 text-[15px] leading-7 text-nivo-stone">{item.body}</p>
            </motion.article>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 10 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.35 }}
          className="mt-14 rounded-2xl border border-nivo-line bg-nivo-paper px-8 py-8 md:px-10 md:py-9"
        >
          <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
            En una frase
          </p>
          <p className="mt-4 max-w-3xl text-[17px] leading-8 text-nivo-ink md:text-lg md:leading-9">
            Una cuenta que ya contempla lo que firmas hoy frente a lo que alguien podría
            atacar dentro de años. La post-cuántica no sustituye sentido común ni
            antifraude; los refuerza. Respuesta corta:{' '}
            <span className="font-medium text-nivo-forest">
              menos riesgo de que identidad y comprobantes envejezcan mal protegidos.
            </span>
          </p>
        </motion.div>
      </div>
    </section>
  );
};
