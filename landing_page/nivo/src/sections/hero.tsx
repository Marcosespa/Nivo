import { HeroWithVideo } from '@/components/ui/hero-with-video';
import { mediaContent } from '@/data/media-content';

export const Hero = () => {
  return (
    <HeroWithVideo
      brandName="Nivo"
      heroSubtitle="Seguridad post-cuántica · alineada con NIST FIPS 203"
      heroDescription="Billetera digital colombiana con criptografía post-cuántica integrada desde el diseño: protege hoy lo que seguirá siendo sensible cuando madure el riesgo cuántico."
      emailPlaceholder="tu@email.com"
      backgroundImage={mediaContent.image.src}
      videoUrl={mediaContent.video.src}
    />
  );
};
