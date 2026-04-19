import { cn } from '@/lib/utils';
import {
  Card,
  CardHeader,
  CardTitle,
  CardContent,
} from '@/components/ui/card';

const values = [
  {
    title: 'Quality',
    description:
      'We deliver robust, well-crafted solutions that merchants and customers can depend on every day.',
  },
  {
    title: 'Trust',
    description:
      'Transparency and reliability are at the core of everything we build — your data and business are safe with us.',
  },
  {
    title: 'Innovation',
    description:
      'We continuously evolve our platform with modern technology to keep Sri Lankan businesses ahead of the curve.',
  },
  {
    title: 'Community',
    description:
      'We grow together with our merchants, partners, and the wider Sri Lankan tech ecosystem.',
  },
];

interface AboutValuesProps {
  className?: string;
}

export function AboutValues({ className }: AboutValuesProps) {
  return (
    <section className={cn('py-12', className)}>
      <h2 className="text-3xl font-bold tracking-tight mb-8 text-center">
        Our Values
      </h2>
      <div className="grid sm:grid-cols-2 gap-6">
        {values.map((value) => (
          <Card key={value.title}>
            <CardHeader>
              <div className="w-10 h-10 rounded-md bg-muted mb-2" />
              <CardTitle>{value.title}</CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-muted-foreground">{value.description}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
