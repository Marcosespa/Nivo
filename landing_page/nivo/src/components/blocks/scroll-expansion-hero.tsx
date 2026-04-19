import { useEffect, useMemo, useRef, useState, type ReactNode } from 'react';
import { motion } from 'framer-motion';

interface ScrollExpandMediaProps {
  mediaType?: 'video' | 'image';
  mediaSrc: string;
  posterSrc?: string;
  bgImageSrc: string;
  title?: string;
  date?: string;
  scrollToExpand?: string;
  textBlend?: boolean;
  children?: ReactNode;
}

const clamp = (value: number, min: number, max: number) =>
  Math.min(Math.max(value, min), max);

const interpolate = (start: number, end: number, progress: number) =>
  start + (end - start) * progress;

const buildYouTubeEmbedUrl = (url: string) => {
  if (url.includes('embed/')) {
    return `${url}${url.includes('?') ? '&' : '?'}autoplay=1&mute=1&loop=1&controls=0&rel=0&playsinline=1`;
  }

  const videoId = url.split('v=')[1]?.split('&')[0];

  if (!videoId) {
    return url;
  }

  return `https://www.youtube.com/embed/${videoId}?autoplay=1&mute=1&loop=1&controls=0&rel=0&playsinline=1&playlist=${videoId}`;
};

const ScrollExpandMedia = ({
  mediaType = 'video',
  mediaSrc,
  posterSrc,
  bgImageSrc,
  title,
  date,
  scrollToExpand,
  textBlend = false,
  children,
}: ScrollExpandMediaProps) => {
  const [scrollProgress, setScrollProgress] = useState(0);
  const [showContent, setShowContent] = useState(false);
  const [mediaFullyExpanded, setMediaFullyExpanded] = useState(false);
  const [isMobile, setIsMobile] = useState(false);
  const [viewport, setViewport] = useState({ width: 1440, height: 900 });

  const touchStartYRef = useRef(0);

  useEffect(() => {
    const resetSection = () => {
      setScrollProgress(0);
      setShowContent(false);
      setMediaFullyExpanded(false);
      touchStartYRef.current = 0;
      window.scrollTo({ top: 0, behavior: 'auto' });
    };

    resetSection();
    window.addEventListener('resetSection', resetSection);

    return () => window.removeEventListener('resetSection', resetSection);
  }, [mediaType]);

  useEffect(() => {
    const syncViewport = () => {
      setIsMobile(window.innerWidth < 768);
      setViewport({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    syncViewport();
    window.addEventListener('resize', syncViewport);

    return () => window.removeEventListener('resize', syncViewport);
  }, []);

  useEffect(() => {
    const updateProgress = (delta: number) => {
      setScrollProgress((current) => {
        const next = clamp(current + delta, 0, 1);

        if (next >= 1) {
          setMediaFullyExpanded(true);
          setShowContent(true);
        } else if (next < 0.75) {
          setShowContent(false);
          setMediaFullyExpanded(false);
        }

        return next;
      });
    };

    const handleWheel = (event: globalThis.WheelEvent) => {
      if (mediaFullyExpanded && event.deltaY < 0 && window.scrollY <= 5) {
        setMediaFullyExpanded(false);
        setShowContent(false);
        updateProgress(-0.12);
        event.preventDefault();
        return;
      }

      if (!mediaFullyExpanded) {
        event.preventDefault();
        updateProgress(event.deltaY * 0.0009);
      }
    };

    const handleTouchStart = (event: globalThis.TouchEvent) => {
      touchStartYRef.current = event.touches[0]?.clientY ?? 0;
    };

    const handleTouchMove = (event: globalThis.TouchEvent) => {
      if (!touchStartYRef.current) {
        return;
      }

      const touchY = event.touches[0]?.clientY ?? 0;
      const deltaY = touchStartYRef.current - touchY;

      if (mediaFullyExpanded && deltaY < -20 && window.scrollY <= 5) {
        setMediaFullyExpanded(false);
        setShowContent(false);
        updateProgress(-0.14);
        event.preventDefault();
      } else if (!mediaFullyExpanded) {
        const factor = deltaY < 0 ? 0.008 : 0.005;
        updateProgress(deltaY * factor);
        event.preventDefault();
      }

      touchStartYRef.current = touchY;
    };

    const handleTouchEnd = () => {
      touchStartYRef.current = 0;
    };

    const handleScroll = () => {
      if (!mediaFullyExpanded) {
        window.scrollTo({ top: 0, behavior: 'auto' });
      }
    };

    window.addEventListener('wheel', handleWheel, { passive: false });
    window.addEventListener('scroll', handleScroll, { passive: true });
    window.addEventListener('touchstart', handleTouchStart, { passive: false });
    window.addEventListener('touchmove', handleTouchMove, { passive: false });
    window.addEventListener('touchend', handleTouchEnd, { passive: true });

    return () => {
      window.removeEventListener('wheel', handleWheel);
      window.removeEventListener('scroll', handleScroll);
      window.removeEventListener('touchstart', handleTouchStart);
      window.removeEventListener('touchmove', handleTouchMove);
      window.removeEventListener('touchend', handleTouchEnd);
    };
  }, [mediaFullyExpanded]);

  const collapsedWidth = Math.min(
    viewport.width - (isMobile ? 32 : 160),
    isMobile ? 320 : 380
  );
  const collapsedHeight = isMobile ? 420 : 460;
  const expandedWidth = viewport.width;
  const expandedHeight = viewport.height * (isMobile ? 0.62 : 0.9);
  const mediaWidth = interpolate(collapsedWidth, expandedWidth, scrollProgress);
  const mediaHeight = interpolate(collapsedHeight, expandedHeight, scrollProgress);
  const mediaRadius = interpolate(28, isMobile ? 20 : 10, scrollProgress);
  const textTranslateX = scrollProgress * (isMobile ? 18 : 15);

  const { firstWord, remainingTitle } = useMemo(() => {
    if (!title) {
      return { firstWord: '', remainingTitle: '' };
    }

    const words = title.split(' ');

    return {
      firstWord: words[0] ?? '',
      remainingTitle: words.slice(1).join(' '),
    };
  }, [title]);

  const backgroundOpacity = 1 - scrollProgress;
  const overlayOpacity = mediaType === 'video' ? 0.5 - scrollProgress * 0.3 : 0.7 - scrollProgress * 0.3;

  return (
    <div className="overflow-x-hidden transition-colors duration-700 ease-in-out">
      <section className="relative flex min-h-screen flex-col items-center justify-start">
        <div className="relative flex min-h-screen w-full flex-col items-center">
          <motion.div
            className="absolute inset-0 z-0 h-full"
            initial={{ opacity: 0 }}
            animate={{ opacity: backgroundOpacity }}
            transition={{ duration: 0.1 }}
          >
            <img
              src={bgImageSrc}
              alt="Background"
              className="h-screen w-screen scale-[1.03] object-cover object-center"
            />
            <div className="absolute inset-0 bg-black/45" />
          </motion.div>

          <div className="relative z-10 mx-auto flex w-full max-w-7xl flex-col items-center px-4 sm:px-6 lg:px-10">
            <div className="relative flex h-screen w-full flex-col items-center justify-center">
              <div
                className="absolute left-1/2 top-1/2 z-0 -translate-x-1/2 -translate-y-1/2 rounded-[28px] transition-none"
                style={{
                  width: `${mediaWidth}px`,
                  height: `${mediaHeight}px`,
                  maxWidth: '100vw',
                  maxHeight: '92vh',
                  borderRadius: `${mediaRadius}px`,
                  boxShadow: '0 30px 80px rgba(2, 8, 23, 0.45)',
                }}
              >
                {mediaType === 'video' ? (
                  mediaSrc.includes('youtube.com') || mediaSrc.includes('youtu.be') ? (
                    <div
                      className="relative h-full w-full overflow-hidden"
                      style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                    >
                      <iframe
                        title={title ?? 'Embedded video'}
                        src={buildYouTubeEmbedUrl(mediaSrc)}
                        className="h-full w-full"
                        frameBorder="0"
                        allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                        allowFullScreen
                      />
                      <motion.div
                        className="absolute inset-0 bg-black/40"
                        style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                        animate={{ opacity: overlayOpacity }}
                        transition={{ duration: 0.2 }}
                      />
                    </div>
                  ) : (
                    <div
                      className="relative h-full w-full overflow-hidden"
                      style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                    >
                      <video
                        src={mediaSrc}
                        poster={posterSrc}
                        autoPlay
                        muted
                        loop
                        playsInline
                        preload="auto"
                        className="h-full w-full object-cover"
                        style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                      />
                      <motion.div
                        className="absolute inset-0 bg-black/40"
                        style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                        animate={{ opacity: overlayOpacity }}
                        transition={{ duration: 0.2 }}
                      />
                    </div>
                  )
                ) : (
                  <div
                    className="relative h-full w-full overflow-hidden"
                    style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                  >
                    <img
                      src={mediaSrc}
                      alt={title || 'Media content'}
                      className="h-full w-full object-cover"
                      style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                    />
                    <motion.div
                      className="absolute inset-0 bg-black/50"
                      style={{ borderRadius: `${Math.max(mediaRadius - 4, 8)}px` }}
                      animate={{ opacity: overlayOpacity }}
                      transition={{ duration: 0.2 }}
                    />
                  </div>
                )}

                <div className="relative z-10 mt-4 flex flex-col items-center text-center text-nivo-paper">
                  {date ? (
                    <p
                      className="text-lg font-medium tracking-[0.35em] uppercase text-nivo-quantum md:text-2xl"
                      style={{ transform: `translateX(-${textTranslateX}vw)` }}
                    >
                      {date}
                    </p>
                  ) : null}
                  {scrollToExpand ? (
                    <p
                      className="mt-2 text-xs font-semibold uppercase tracking-[0.45em] text-nivo-mist md:text-sm"
                      style={{ transform: `translateX(${textTranslateX}vw)` }}
                    >
                      {scrollToExpand}
                    </p>
                  ) : null}
                </div>
              </div>

              <div
                className={`relative z-10 flex w-full flex-col items-center justify-center gap-2 text-center transition-none ${
                  textBlend ? 'mix-blend-screen' : 'mix-blend-normal'
                }`}
              >
                <motion.h2
                  className="text-4xl font-semibold uppercase tracking-[0.2em] text-nivo-paper md:text-6xl lg:text-7xl"
                  style={{ transform: `translateX(-${textTranslateX}vw)` }}
                >
                  {firstWord}
                </motion.h2>
                <motion.h2
                  className="text-4xl font-semibold uppercase tracking-[0.16em] text-nivo-mist md:text-6xl lg:text-7xl"
                  style={{ transform: `translateX(${textTranslateX}vw)` }}
                >
                  {remainingTitle}
                </motion.h2>
              </div>
            </div>

            <motion.section
              className="w-full px-2 py-12 md:px-8 md:py-20"
              initial={{ opacity: 0 }}
              animate={{ opacity: showContent ? 1 : 0 }}
              transition={{ duration: 0.7 }}
            >
              {children}
            </motion.section>
          </div>
        </div>
      </section>
    </div>
  );
};

export default ScrollExpandMedia;
