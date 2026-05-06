import { Link } from 'react-router-dom';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

export const NotFoundPage = () => {
  return (
    <div className="bg-nivo-paper pt-32 pb-20">
      <div className="mx-auto w-full max-w-5xl px-6 text-center lg:px-10">
        <div className="rounded-[28px] border border-nivo-line bg-nivo-cloud-soft px-6 py-16 shadow-card md:px-12">
          <Badge variant="outline">404</Badge>
          <h1 className="mt-6 font-display text-4xl font-medium tracking-tightest text-nivo-ink md:text-6xl">
            Esta ruta no existe en Nivo
          </h1>
          <p className="mx-auto mt-6 max-w-2xl text-base leading-8 text-nivo-stone md:text-lg">
            Vuelve al inicio o explora los módulos principales: pagos, monedas, inversión y seguridad.
          </p>
          <div className="mt-8 flex flex-wrap items-center justify-center gap-3">
            <Link to="/">
              <Button variant="forest" size="lg">Volver al inicio</Button>
            </Link>
            <Link to="/app">
              <Button variant="outline" size="lg">Abrir la app</Button>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
