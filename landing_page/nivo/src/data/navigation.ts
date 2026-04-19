export interface NavLink {
  label: string;
  href: string;
}

/** Enlaces bajo el menú «Producto». */
export const navProductLinks: NavLink[] = [
  { label: 'App', href: '/app' },
  { label: 'Monedas', href: '/monedas' },
  { label: 'Invertir', href: '/invertir' },
  { label: 'Seguridad', href: '/seguridad' },
];

/** Anclas en la página de inicio (sección por `id`). */
export interface NavResourceLink {
  label: string;
  hash: string;
}

export const navResourceLinks: NavResourceLink[] = [
  { label: 'Cómo funciona', hash: 'quantum-shield' },
  { label: 'Confianza', hash: 'trust' },
  { label: 'Arquitectura', hash: 'architecture' },
];

export const navSecondaryLinks: NavLink[] = [
  { label: 'Empresas', href: '/empresas' },
  { label: 'API PQC', href: '/developers' },
];
