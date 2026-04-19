import { useEffect, useRef, useState } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import { ChevronDown } from 'lucide-react';
import { Link, useLocation } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { MenuToggleIcon } from '@/components/ui/menu-toggle-icon';
import { NivoLogo } from '@/components/ui/logo';
import { ThemeToggle } from '@/components/ui/theme-toggle';
import { useScroll } from '@/hooks/use-scroll';
import {
  isNavRouteActive,
  navProductLinks,
  navResourceLinks,
  navSecondaryLinks,
} from '@/data/navigation';
import { cn } from '@/lib/utils';

export const Navbar = () => {
  const [open, setOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const scrolled = useScroll(10);
  const location = useLocation();
  const desktopNavRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    document.body.style.overflow = open ? 'hidden' : '';
    return () => {
      document.body.style.overflow = '';
    };
  }, [open]);

  useEffect(() => {
    setOpen(false);
    setOpenDropdown(null);
    window.scrollTo({ top: 0, behavior: 'auto' });
  }, [location.pathname]);

  useEffect(() => {
    if (!openDropdown) return;
    const close = (e: MouseEvent) => {
      if (
        desktopNavRef.current &&
        !desktopNavRef.current.contains(e.target as Node)
      ) {
        setOpenDropdown(null);
      }
    };
    document.addEventListener('mousedown', close);
    return () => document.removeEventListener('mousedown', close);
  }, [openDropdown]);

  const toggleDropdown = (id: string) => {
    setOpenDropdown((prev) => (prev === id ? null : id));
  };

  const resourceTo = (hash: string) => ({
    pathname: '/',
    hash: `#${hash}`,
  });

  return (
    <header
      className={cn(
        'fixed inset-x-0 top-0 z-[70] w-full transition-all duration-300 ease-out',
        scrolled
          ? 'border-b border-nivo-line bg-nivo-paper/90 backdrop-blur-md'
          : 'border-b border-transparent bg-nivo-paper/60 backdrop-blur-sm'
      )}
    >
      <div className="mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8">
        <nav
          className={cn(
            'flex items-center justify-between',
            scrolled ? 'h-16' : 'h-20'
          )}
        >
          <Link to="/" className="text-nivo-ink">
            <NivoLogo />
          </Link>

          <div
            ref={desktopNavRef}
            className="hidden items-center gap-1 font-medium text-nivo-stone lg:flex"
          >
            <ul className="flex items-center space-x-1">
              <li className="relative">
                <button
                  type="button"
                  onClick={() => toggleDropdown('desktop-product')}
                  className="flex items-center rounded-lg px-3 py-2 text-sm transition-colors hover:text-nivo-ink"
                >
                  Producto
                  <ChevronDown
                    className={cn(
                      'ml-1 h-4 w-4 transition-transform',
                      openDropdown === 'desktop-product' && 'rotate-180'
                    )}
                  />
                </button>
                {openDropdown === 'desktop-product' ? (
                  <ul className="absolute left-0 top-full z-30 mt-2 w-52 rounded-xl border border-nivo-line bg-nivo-paper p-2 shadow-card">
                    {navProductLinks.map((item) => (
                      <li key={item.label}>
                        <Link
                          to={item.href}
                          onClick={() => setOpenDropdown(null)}
                          className={cn(
                            'block rounded-lg px-3 py-2 text-sm transition-colors',
                            isNavRouteActive(item.href, location.pathname)
                              ? 'bg-nivo-cloud text-nivo-ink'
                              : 'text-nivo-stone hover:bg-nivo-cloud-soft hover:text-nivo-ink'
                          )}
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </li>
              <li className="relative">
                <button
                  type="button"
                  onClick={() => toggleDropdown('desktop-resources')}
                  className="flex items-center rounded-lg px-3 py-2 text-sm transition-colors hover:text-nivo-ink"
                >
                  Recursos
                  <ChevronDown
                    className={cn(
                      'ml-1 h-4 w-4 transition-transform',
                      openDropdown === 'desktop-resources' && 'rotate-180'
                    )}
                  />
                </button>
                {openDropdown === 'desktop-resources' ? (
                  <ul className="absolute left-0 top-full z-30 mt-2 w-52 rounded-xl border border-nivo-line bg-nivo-paper p-2 shadow-card">
                    {navResourceLinks.map((item) => (
                      <li key={item.label}>
                        <Link
                          to={resourceTo(item.hash)}
                          onClick={() => setOpenDropdown(null)}
                          className="block rounded-lg px-3 py-2 text-sm text-nivo-stone transition-colors hover:bg-nivo-cloud-soft hover:text-nivo-ink"
                        >
                          {item.label}
                        </Link>
                      </li>
                    ))}
                  </ul>
                ) : null}
              </li>
              {navSecondaryLinks.map((link) => {
                const isDeveloper = link.href === '/developers';
                const isActive = isNavRouteActive(link.href, location.pathname);
                return (
                  <li key={link.href}>
                    <Link
                      to={link.href}
                      className={cn(
                        'rounded-lg px-3 py-2 text-sm transition-colors',
                        isDeveloper
                          ? 'text-nivo-forest hover:bg-nivo-forest/5'
                          : isActive
                            ? 'bg-nivo-cloud text-nivo-ink'
                            : 'hover:text-nivo-ink'
                      )}
                    >
                      {link.label}
                    </Link>
                  </li>
                );
              })}
            </ul>
          </div>

          <div className="hidden items-center gap-2 lg:flex">
            <ThemeToggle />
            <Button variant="ghost" size="sm" asChild>
              <Link to="/app">Entrar</Link>
            </Button>
            <a
              href="mailto:hola@nivo.money"
              className="inline-flex h-10 items-center justify-center rounded-full bg-nivo-forest px-5 text-[13px] font-medium text-white transition-colors hover:bg-nivo-forest-soft"
            >
              Registrarme
            </a>
          </div>

          <div className="flex items-center gap-2 lg:hidden">
            <ThemeToggle />
            <button
              type="button"
              onClick={() => setOpen(!open)}
              className="inline-flex h-10 w-10 items-center justify-center rounded-full border border-nivo-line text-nivo-ink"
              aria-label={open ? 'Cerrar navegación' : 'Abrir navegación'}
            >
              <MenuToggleIcon open={open} className="size-5" duration={300} />
            </button>
          </div>
        </nav>

        <AnimatePresence>
          {open ? (
            <>
              <motion.button
                type="button"
                aria-label="Cerrar menú"
                onClick={() => setOpen(false)}
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.2, ease: 'easeOut' }}
                className="fixed inset-0 z-40 bg-black/35 backdrop-blur-[2px] lg:hidden"
              />

              <motion.div
                initial={{ opacity: 0, y: -8 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.22, ease: [0.16, 1, 0.3, 1] }}
                className="absolute inset-x-0 top-full z-50 max-h-[min(85vh,calc(100dvh-5rem))] overflow-y-auto border-t border-nivo-line bg-nivo-paper lg:hidden"
              >
                <div className="mx-auto max-w-6xl px-4 py-6 sm:px-6">
                  <div className="grid gap-1">
                    <p className="px-4 pb-1 pt-2 font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                      Producto
                    </p>
                    {navProductLinks.map((link, index) => (
                      <motion.div
                        key={link.label}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 4 }}
                        transition={{
                          delay: 0.04 + index * 0.025,
                          duration: 0.2,
                        }}
                      >
                        <Link
                          to={link.href}
                          onClick={() => setOpen(false)}
                          className={cn(
                            'flex items-center justify-between rounded-lg px-4 py-3 text-[15px] font-medium transition-colors hover:bg-nivo-cloud-soft hover:text-nivo-ink',
                            isNavRouteActive(link.href, location.pathname)
                              ? 'bg-nivo-cloud text-nivo-ink'
                              : 'text-nivo-stone'
                          )}
                        >
                          <span>{link.label}</span>
                          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                            ↗
                          </span>
                        </Link>
                      </motion.div>
                    ))}

                    <p className="px-4 pb-1 pt-4 font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                      Recursos
                    </p>
                    {navResourceLinks.map((link, index) => (
                      <motion.div
                        key={link.label}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 4 }}
                        transition={{
                          delay:
                            0.06 + (navProductLinks.length + index) * 0.025,
                          duration: 0.2,
                        }}
                      >
                        <Link
                          to={resourceTo(link.hash)}
                          onClick={() => setOpen(false)}
                          className="flex items-center justify-between rounded-lg px-4 py-3 text-[15px] font-medium text-nivo-stone transition-colors hover:bg-nivo-cloud-soft hover:text-nivo-ink"
                        >
                          <span>{link.label}</span>
                          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                            ↗
                          </span>
                        </Link>
                      </motion.div>
                    ))}

                    {navSecondaryLinks.map((link, index) => (
                      <motion.div
                        key={link.href}
                        initial={{ opacity: 0, y: 6 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: 4 }}
                        transition={{
                          delay:
                            0.08 +
                            (navProductLinks.length +
                              navResourceLinks.length +
                              index) *
                              0.025,
                          duration: 0.2,
                        }}
                      >
                        <Link
                          to={link.href}
                          onClick={() => setOpen(false)}
                          className={cn(
                            'flex items-center justify-between rounded-lg px-4 py-3 text-[15px] font-medium transition-colors hover:bg-nivo-cloud-soft',
                            link.href === '/developers'
                              ? 'text-nivo-forest hover:bg-nivo-forest/5'
                              : isNavRouteActive(link.href, location.pathname)
                                ? 'bg-nivo-cloud text-nivo-ink'
                                : 'text-nivo-stone hover:text-nivo-ink'
                          )}
                        >
                          <span>{link.label}</span>
                          <span className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                            ↗
                          </span>
                        </Link>
                      </motion.div>
                    ))}
                  </div>

                  <div className="mt-6 flex flex-col gap-2 border-t border-nivo-line pt-6">
                    <Button variant="outline" size="default" className="w-full" asChild>
                      <Link to="/app" onClick={() => setOpen(false)}>
                        Entrar
                      </Link>
                    </Button>
                    <a
                      href="mailto:hola@nivo.money"
                      className="inline-flex h-11 w-full items-center justify-center rounded-full bg-nivo-forest px-5 text-[14px] font-medium text-white transition-colors hover:bg-nivo-forest-soft"
                    >
                      Registrarme gratis
                    </a>
                  </div>
                </div>
              </motion.div>
            </>
          ) : null}
        </AnimatePresence>
      </div>
    </header>
  );
};
