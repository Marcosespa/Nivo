import { useEffect, useMemo, useRef, useState } from 'react';
import { LayoutGroup, motion } from 'framer-motion';
import { ArrowRight, Mail, Pause, Play } from 'lucide-react';
import { TextRotate } from '@/components/ui/text-rotate';
import { cn } from '@/lib/utils';

const DEFAULT_HERO_ROTATING_PHRASES = [
  'el futuro.',
  'la era cuántica.',
  'lo que viene.',
  'el estándar NIST.',
  'cualquier vector.',
] as const;

interface HeroWithVideoProps {
  brandName?: string;
  /** Parte fija del titular; la frase animada se añade después (con espacio). */
  heroTitleLead?: string;
  /** Textos que rotan al final del titular. */
  heroRotatingPhrases?: readonly string[];
  heroSubtitle?: string;
  heroDescription?: string;
  backgroundImage?: string;
  videoUrl?: string;
  emailPlaceholder?: string;
}

export const HeroWithVideo = ({
  brandName = 'Nivo',
  heroTitleLead = 'Tu dinero, blindado contra',
  heroRotatingPhrases = DEFAULT_HERO_ROTATING_PHRASES,
  heroSubtitle = 'Seguridad Post-Cuántica · NIST FIPS 203',
  heroDescription = 'La primera billetera digital colombiana con criptografía Post-Cuántica. Protegida hoy contra las amenazas que llegarán en 2045.',
  backgroundImage = 'https://images.unsplash.com/photo-1451187580459-43490279c0fa?ixlib=rb-4.0.3&auto=format&fit=crop&w=2072&q=80',
  videoUrl,
  emailPlaceholder = 'tu@email.com',
}: HeroWithVideoProps) => {
  const [email, setEmail] = useState('');
  const [isVideoPlaying, setIsVideoPlaying] = useState(false);
  const [isVideoPaused, setIsVideoPaused] = useState(false);
  const [isMounted, setIsMounted] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    setIsMounted(true);
  }, []);

  const handleEmailSubmit = () => {
    const safeEmail = email.trim();
    const body = safeEmail
      ? `Hola Nivo,%0D%0A%0D%0AMe interesa entrar a la beta.%0D%0AMi email: ${encodeURIComponent(safeEmail)}`
      : 'Hola Nivo,%0D%0A%0D%0AMe interesa entrar a la beta.';
    window.location.href = `mailto:hola@nivo.money?subject=Beta%20Nivo&body=${body}`;
  };

  const handlePlayVideo = async () => {
    if (!videoRef.current) return;

    try {
      await videoRef.current.play();
      setIsVideoPlaying(true);
      setIsVideoPaused(false);
    } catch {
      setIsVideoPlaying(false);
      setIsVideoPaused(false);
    }
  };

  const handlePauseVideo = () => {
    if (!videoRef.current) return;
    videoRef.current.pause();
    setIsVideoPaused(true);
  };

  const handleResumeVideo = async () => {
    if (!videoRef.current) return;
    try {
      await videoRef.current.play();
      setIsVideoPaused(false);
    } catch {
      setIsVideoPaused(true);
    }
  };

  const handleVideoEnded = () => {
    setIsVideoPlaying(false);
    setIsVideoPaused(false);
  };

  const ctaLabel = useMemo(
    () => (email.trim() ? 'Unirme con este email' : 'Registrarme gratis'),
    [email]
  );

  return (
    <section className="relative overflow-hidden bg-nivo-paper pb-12 pt-24 sm:pb-16 sm:pt-28">
      <div className="pointer-events-none absolute inset-0 bg-nivo-grid-fine bg-grid-fine opacity-40" />

      <div className="relative mx-auto w-full max-w-6xl px-4 sm:px-6 lg:px-8">
        <div className="pb-10 pt-2 text-center sm:pb-12 sm:pt-4">
          <div className="mx-auto max-w-2xl">
            <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
              {heroSubtitle}
            </p>
            <h1 className="mt-6 font-display text-4xl font-medium tracking-tightest text-nivo-ink sm:text-5xl md:text-6xl">
              <LayoutGroup>
                <motion.span
                  className="flex flex-wrap items-baseline justify-center gap-x-1 sm:gap-x-1.5"
                  layout
                >
                  <motion.span
                    className="min-w-0 pt-0.5 sm:pt-1 md:pt-1.5"
                    layout
                    transition={{
                      type: 'spring',
                      damping: 30,
                      stiffness: 400,
                    }}
                  >
                    {heroTitleLead}
                    {' '}
                  </motion.span>
                  <TextRotate
                    texts={[...heroRotatingPhrases]}
                    mainClassName="inline-flex max-w-[min(100%,22rem)] text-white px-2 sm:px-2.5 md:px-3 bg-nivo-forest overflow-hidden py-0.5 sm:py-1 md:py-1.5 justify-center rounded-lg align-baseline sm:max-w-none"
                    staggerFrom="last"
                    initial={{ y: '100%' }}
                    animate={{ y: 0 }}
                    exit={{ y: '-120%' }}
                    staggerDuration={0.025}
                    splitLevelClassName="overflow-hidden pb-0.5 sm:pb-1 md:pb-1"
                    transition={{
                      type: 'spring',
                      damping: 30,
                      stiffness: 400,
                    }}
                    rotationInterval={2200}
                  />
                </motion.span>
              </LayoutGroup>
            </h1>
            <p className="mt-6 text-lg leading-8 text-nivo-stone">
              {heroDescription}
            </p>

            <div className="mt-8 flex flex-wrap items-center justify-center gap-3 sm:gap-4">
              <div className="relative w-full max-w-xs">
                <Mail className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-nivo-mist" />
                <input
                  type="email"
                  placeholder={emailPlaceholder}
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full rounded-full border border-nivo-line bg-nivo-cloud-soft py-3 pl-11 pr-4 text-sm text-nivo-ink outline-none transition focus:border-nivo-forest"
                />
              </div>
              <button
                onClick={handleEmailSubmit}
                className="flex items-center gap-2 rounded-full bg-nivo-forest px-6 py-3 text-sm font-medium text-white transition-colors hover:bg-nivo-forest-soft"
              >
                {ctaLabel}
                <ArrowRight className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>

        <header className="relative w-full overflow-hidden rounded-[28px] border border-nivo-line shadow-card">
          <div className="relative aspect-video bg-nivo-ink">
            <img
              src={backgroundImage}
              alt="Tierra vista desde el espacio"
              className={cn(
                'absolute inset-0 h-full w-full object-cover transition-opacity duration-500',
                isVideoPlaying ? 'opacity-0' : 'opacity-100'
              )}
            />
            {videoUrl ? (
              <video
                ref={videoRef}
                src={videoUrl}
                className={cn(
                  'absolute inset-0 h-full w-full object-cover transition-opacity duration-500',
                  isVideoPlaying ? 'opacity-100' : 'opacity-0'
                )}
                onEnded={handleVideoEnded}
                playsInline
                muted
                loop
                preload="metadata"
                poster={backgroundImage}
              />
            ) : null}
            <div className="absolute inset-0 bg-gradient-to-t from-black/55 via-black/5 to-black/35" />

            <div className="absolute bottom-5 left-5 right-5 z-10 flex items-end justify-between gap-4 sm:bottom-8 sm:left-8 sm:right-8">
              <div>
                <p className="font-mono text-[10px] uppercase tracking-[0.3em] text-white/75">
                  {brandName} · Seguridad del futuro
                </p>
                <p className="mt-2 max-w-xl font-display text-lg font-medium tracking-tightest text-white sm:text-2xl">
                  La misma experiencia simple. Una infraestructura mucho más difícil de romper.
                </p>
              </div>

              {isMounted && videoUrl ? (
                <button
                  onClick={
                    !isVideoPlaying
                      ? handlePlayVideo
                      : isVideoPaused
                        ? handleResumeVideo
                        : handlePauseVideo
                  }
                  className="flex h-14 w-14 shrink-0 items-center justify-center rounded-full border border-white/25 bg-white/15 text-white shadow-lg backdrop-blur-md transition hover:bg-white/25"
                  aria-label={!isVideoPlaying || isVideoPaused ? 'Reproducir video' : 'Pausar video'}
                >
                  {!isVideoPlaying || isVideoPaused ? (
                    <Play className="ml-0.5 h-6 w-6 fill-current" />
                  ) : (
                    <Pause className="h-6 w-6 fill-current" />
                  )}
                </button>
              ) : null}
            </div>
          </div>
        </header>
      </div>
    </section>
  );
};
