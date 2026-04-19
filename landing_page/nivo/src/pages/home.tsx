import { Hero } from '@/sections/hero';
import { TrustBar } from '@/sections/trust-bar';
import { QuantumShield } from '@/sections/quantum-shield';
import { SafetyPromise } from '@/sections/safety-promise';
import { FeaturePillarsTabs } from '@/components/blocks/feature-pillars-tabs';
import { Architecture } from '@/sections/architecture';
import { QuantumSecurity } from '@/sections/quantum-security';
import { CategoryFraming } from '@/sections/category-framing';
import { Flywheel } from '@/sections/flywheel';

export const HomePage = () => {
  return (
    <>
      <Hero />

      <TrustBar />

      <QuantumShield />

      <SafetyPromise />

      <section id="pillars">
        <FeaturePillarsTabs />
      </section>

      <Architecture />

      <QuantumSecurity />

      <CategoryFraming />

      <Flywheel />
    </>
  );
};
