import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { nivoFeatureTabs, type FeatureSectionData } from '@/data/feature-tabs';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';

interface FeaturePillarsTabsProps {
  data?: FeatureSectionData;
}

export const FeaturePillarsTabs = ({
  data = nivoFeatureTabs,
}: FeaturePillarsTabsProps) => {
  const [activeTab, setActiveTab] = useState(data.tabs[0]?.value ?? '');
  const currentTab =
    data.tabs.find((tab) => tab.value === activeTab) ?? data.tabs[0];

  if (!currentTab) {
    return null;
  }

  return (
    <section className="relative bg-nivo-cloud-soft py-32">
      <div className="mx-auto w-full max-w-6xl px-6 lg:px-10">
        <div className="flex flex-col gap-5 md:max-w-3xl">
          <Badge variant="outline">{data.badge}</Badge>
          <h2 className="font-display text-[40px] font-medium leading-[1.05] tracking-tightest text-nivo-ink md:text-[56px]">
            {data.heading}
          </h2>
          <p className="max-w-2xl text-lg leading-8 text-nivo-stone">
            {data.description}
          </p>
        </div>

        <div className="mt-12 flex flex-wrap items-center gap-2">
          {data.tabs.map((tab) => {
            const isActive = tab.value === currentTab.value;
            return (
              <button
                key={tab.value}
                type="button"
                onClick={() => setActiveTab(tab.value)}
                className={`inline-flex items-center gap-2 rounded-full px-4 py-2.5 text-[13px] font-medium transition-colors ${
                  isActive
                    ? 'bg-nivo-ink text-nivo-paper'
                    : 'border border-nivo-line bg-nivo-paper text-nivo-stone hover:border-nivo-ink hover:text-nivo-ink'
                }`}
              >
                <span className="text-current">{tab.icon}</span>
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        <div className="mt-8 rounded-3xl border border-nivo-line bg-nivo-paper p-8 lg:p-14">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentTab.value}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -8 }}
              transition={{ duration: 0.25, ease: 'easeOut' }}
              className="grid gap-12 lg:grid-cols-[0.95fr_1.05fr] lg:gap-12"
            >
              <div className="flex flex-col gap-5">
                <Badge variant="forest" className="w-fit">
                  {currentTab.content.badge}
                </Badge>
                <h3 className="font-display text-[32px] font-medium leading-tight tracking-tightest text-nivo-ink lg:text-[44px]">
                  {currentTab.content.title}
                </h3>
                <p className="max-w-2xl text-[15px] leading-8 text-nivo-stone lg:text-base">
                  {currentTab.content.description}
                </p>

                <div className="mt-2 grid gap-2">
                  {currentTab.content.stats.map((stat) => (
                    <div
                      key={stat}
                      className="flex items-center gap-3 rounded-xl border border-nivo-line bg-nivo-cloud-soft px-4 py-3 text-[14px] text-nivo-ink"
                    >
                      <span className="h-1.5 w-1.5 rounded-full bg-nivo-forest" />
                      <span>{stat}</span>
                    </div>
                  ))}
                </div>

                <div className="pt-3">
                  <Button variant="forest" size="default">
                    {currentTab.content.buttonText}
                  </Button>
                </div>
              </div>

              <div className="w-full rounded-2xl border border-nivo-line bg-nivo-ink p-6 text-nivo-paper lg:p-8">
                <div className="flex items-center gap-2 border-b border-nivo-stone/40 pb-4">
                  <span className="h-2.5 w-2.5 rounded-full bg-nivo-stone-soft" />
                  <span className="h-2.5 w-2.5 rounded-full bg-nivo-stone-soft" />
                  <span className="h-2.5 w-2.5 rounded-full bg-nivo-forest" />
                  <span className="ml-3 font-mono text-[10px] uppercase tracking-[0.28em] text-nivo-cloud">
                    {currentTab.content.visualTitle}
                  </span>
                </div>

                <div className="mt-6 space-y-3 font-mono text-[13px] leading-7">
                  {currentTab.content.visualLines.map((line, index) => (
                    <motion.div
                      key={line}
                      initial={{ opacity: 0, x: -8 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.06, duration: 0.22 }}
                      className="rounded-lg border border-nivo-stone/30 bg-nivo-ink px-4 py-3"
                    >
                      <span className="mr-3 text-nivo-forest">
                        {String(index + 1).padStart(2, '0')}
                      </span>
                      <span className="text-nivo-cloud">{line}</span>
                    </motion.div>
                  ))}
                </div>

                <div className="mt-6 grid gap-3 sm:grid-cols-2">
                  <div className="rounded-lg border border-nivo-stone/30 p-4">
                    <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-nivo-cloud">
                      Estado
                    </p>
                    <p className="mt-2 font-display text-sm font-medium text-nivo-forest">
                      Operación lista
                    </p>
                  </div>
                  <div className="rounded-lg border border-nivo-stone/30 p-4">
                    <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-nivo-cloud">
                      Control
                    </p>
                    <p className="mt-2 font-display text-sm font-medium text-nivo-paper">
                      Confirmación visible
                    </p>
                  </div>
                </div>
              </div>
            </motion.div>
          </AnimatePresence>
        </div>
      </div>
    </section>
  );
};
