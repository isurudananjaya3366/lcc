import { cn } from '@/lib/utils';

interface AboutStoryProps {
  className?: string;
}

export function AboutStory({ className }: AboutStoryProps) {
  return (
    <section className={cn('py-12', className)}>
      <h2 className="text-3xl font-bold tracking-tight mb-8">Our Story</h2>
      <div className="grid md:grid-cols-2 gap-8 items-center">
        <div className="space-y-4 text-muted-foreground">
          <p>
            Founded in the heart of Colombo, our journey began with a simple
            vision: to make modern e-commerce accessible to every Sri Lankan
            business, from bustling markets in Pettah to boutique shops in
            Galle Fort.
          </p>
          <p>
            What started as a small team of passionate developers has grown
            into a platform trusted by merchants across the island. We
            understand the unique challenges of doing business in Sri Lanka
            — from multi-currency needs to local payment integrations.
          </p>
          <p>
            Today, we continue to build tools that respect local traditions
            while embracing global standards, helping Sri Lankan businesses
            thrive in the digital marketplace.
          </p>
        </div>
        <div className="bg-muted aspect-video rounded-lg" />
      </div>
    </section>
  );
}
