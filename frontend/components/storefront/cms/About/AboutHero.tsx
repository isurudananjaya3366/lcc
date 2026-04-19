import { cn } from '@/lib/utils';

interface AboutHeroProps {
  className?: string;
}

export function AboutHero({ className }: AboutHeroProps) {
  return (
    <section className={cn('text-center py-12 md:py-16', className)}>
      <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
        About Us
      </h1>
      <p className="text-lg md:text-xl text-muted-foreground max-w-2xl mx-auto mb-8">
        Empowering Sri Lankan e-commerce with modern, reliable, and locally
        relevant solutions for businesses and customers alike.
      </p>
      <div className="bg-muted aspect-video rounded-lg max-w-3xl mx-auto" />
    </section>
  );
}
