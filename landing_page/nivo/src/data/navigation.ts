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

/**
 * Rutas alias en `App.tsx` que deben resaltar el mismo ítem del nav
 * (canonical = `href` en navProductLinks / navSecondaryLinks).
 */
export const navPathAliases: Record<string, readonly string[]> = {
  '/app': ['/app', '/plataforma', '/platform'],
  '/seguridad': ['/seguridad', '/trustlayer', '/trust-layer'],
  '/empresas': ['/empresas', '/architecture', '/arquitectura'],
};

export function isNavRouteActive(canonicalHref: string, pathname: string): boolean {
  const group = navPathAliases[canonicalHref];
  if (group) return group.includes(pathname);
  return pathname === canonicalHref;
}
