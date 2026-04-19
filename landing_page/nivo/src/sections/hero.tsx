import { HeroWithVideo } from '@/components/ui/hero-with-video';
import { mediaContent } from '@/data/media-content';

export const Hero = () => {
  return (
    <HeroWithVideo
      brandName="Nivo"
      heroSubtitle="Seguridad Post-Cuántica · NIST FIPS 203"
      heroDescription="La primera billetera digital colombiana con criptografía Post-Cuántica. Protegida hoy contra las amenazas que llegarán en 2045."
      emailPlaceholder="tu@email.com"
      backgroundImage={mediaContent.image.src}
      videoUrl={mediaContent.video.src}
    />
  );
  
};
