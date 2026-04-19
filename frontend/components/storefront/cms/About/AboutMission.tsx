import { cn } from '@/lib/utils';

interface AboutMissionProps {
  className?: string;
}

export function AboutMission({ className }: AboutMissionProps) {
  return (
    <section className={cn('py-12', className)}>
      <h2 className="text-3xl font-bold tracking-tight mb-8 text-center">
        Our Mission
      </h2>
      <div className="bg-primary/5 border border-primary/20 rounded-lg p-8 text-center max-w-3xl mx-auto">
        <p className="text-lg md:text-xl leading-relaxed">
          To empower Sri Lankan businesses with an affordable, intuitive, and
          feature-rich commerce platform that bridges local market needs with
          global e-commerce standards — enabling every merchant to sell
          online with confidence.
        </p>
      </div>
    </section>
  );
}
