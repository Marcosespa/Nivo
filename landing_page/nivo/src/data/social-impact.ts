/** Contenido alineado con AMBITO_SOCIAL.md (raíz del repo). */

export const socialImpactIntro = {
  badge: 'Impacto social',
  title: 'Formalidad progresiva para quien el sistema dejó atrás',
  lead:
    'En Colombia, más de la mitad de la población trabaja en la informalidad, con barreras a la formación, al crédito formal y a mejorar el bienestar. Cerca del 80 % de los trabajadores informales gana menos del salario mínimo; la pobreza monetaria afecta al 31,5 % del país. Ese contexto pide soluciones que no castiguen la vulnerabilidad, sino que abran puertas.',
};

export const socialImpactStats = [
  { value: '>50%', label: 'trabajo informal' },
  { value: '~80%', label: 'informales bajo el mínimo' },
  { value: '31,5%', label: 'pobreza monetaria' },
] as const;

export const socialImpactLadder = {
  title: 'Escalera de la formalidad progresiva',
  body:
    'Pasos graduales y acompañados —no un salto binario entre formal e informal— que acerquen a las personas al sistema financiero y a mejores condiciones de vida, con apoyo sin persecución.',
};

export const socialImpactPillars = [
  {
    title: 'Billeteras con historia crediticia',
    description:
      'Dotar a trabajadores informales y vendedores ambulantes de billeteras digitales que permitan construir una historia crediticia real: trazabilidad de flujos y comportamiento cuando el marco y los aliados lo permitan.',
  },
  {
    title: 'Más allá del “gota a gota”',
    description:
      'Contribuir a que el crédito informal deje paso a productos formales y a créditos garantizados por el Estado cuando existan programas, regulación y partnerships institucionales verificables.',
  },
  {
    title: 'Apoyo sin persecución',
    description:
      'El producto y el trato al usuario evitan lógicas punitivas hacia quien opera en informalidad: la meta es facilitar inclusión y formalización, no exponer ni castigar.',
  },
] as const;

export const socialImpactFootnote =
  'Cifras de contexto: referencia general; en materiales oficiales conviene citar fuente (p. ej. DANE). Este ámbito orienta narrativa y roadmap futuro sin sustituir prioridades técnicas ni regulatorias del MVP.';

/** Props para la página dedicada `/impacto`. */
export const socialImpactPageProps = {
  badge: socialImpactIntro.badge,
  title: socialImpactIntro.title,
  description: `${socialImpactIntro.lead} ${socialImpactLadder.body}`,
  proof: 'Historia crediticia · productos formales · apoyo sin persecución',
  stats: [...socialImpactStats],
  cards: socialImpactPillars.map((p) => ({
    title: p.title,
    description: p.description,
  })),
  calloutTitle: 'Impacto que se construye con el producto',
  calloutDescription: socialImpactFootnote,
};
