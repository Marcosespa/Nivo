import { motion } from 'framer-motion';
import { Badge } from '@/components/ui/badge';
import {
  socialImpactFootnote,
  socialImpactIntro,
  socialImpactLadder,
  socialImpactPillars,
  socialImpactStats,
} from '@/data/social-impact';

export const SocialImpact = () => {
  return (
    <section
      id="social-impact"
      className="relative border-t border-nivo-line bg-gradient-to-b from-nivo-cloud-soft/50 to-nivo-paper py-28 md:py-32"
    >
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-6 md:max-w-3xl">
          <Badge variant="outline">{socialImpactIntro.badge}</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[52px]">
            {socialImpactIntro.title}
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone">
            {socialImpactIntro.lead}
          </p>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45 }}
          className="mt-12 grid gap-4 sm:grid-cols-3"
        >
          {socialImpactStats.map((stat) => (
            <div
              key={stat.label}
              className="rounded-2xl border border-nivo-line bg-nivo-paper/80 px-6 py-5 shadow-subtle"
            >
              <p className="font-display text-3xl font-medium tracking-tightest text-nivo-forest md:text-[34px]">
                {stat.value}
              </p>
              <p className="mt-1 text-[13px] font-medium uppercase tracking-wider text-nivo-mist">
                {stat.label}
              </p>
            </div>
          ))}
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.45, delay: 0.08 }}
          className="mt-16 max-w-3xl"
        >
          <h3 className="font-display text-2xl font-medium tracking-tightest text-nivo-ink md:text-[28px]">
            {socialImpactLadder.title}
          </h3>
          <p className="mt-4 text-[15px] leading-7 text-nivo-stone md:text-base md:leading-8">
            {socialImpactLadder.body}
          </p>
        </motion.div>

        <div className="mt-14 grid gap-6 md:grid-cols-3">
          {socialImpactPillars.map((pillar, index) => (
            <motion.article
              key={pillar.title}
              initial={{ opacity: 0, y: 14 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ duration: 0.4, delay: index * 0.06 }}
              className="rounded-2xl border border-nivo-line bg-nivo-paper p-6 md:p-8"
            >
              <p className="font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-mist">
                {String(index + 1).padStart(2, '0')}
              </p>
              <h4 className="mt-4 font-display text-lg font-medium tracking-tightest text-nivo-ink">
                {pillar.title}
              </h4>
              <p className="mt-3 text-[15px] leading-7 text-nivo-stone">
                {pillar.description}
              </p>
            </motion.article>
          ))}
        </div>

        <p className="mx-auto mt-14 max-w-3xl text-center text-[13px] leading-6 text-nivo-mist">
          {socialImpactFootnote}
        </p>
      </div>
    </section>
  );
};
