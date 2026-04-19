import { cn } from '@/lib/utils';

const team = [
  { name: 'Kasun Perera', role: 'Founder & CEO' },
  { name: 'Dilini Fernando', role: 'Head of Engineering' },
  { name: 'Amal Jayawardena', role: 'Product Lead' },
  { name: 'Nimasha Silva', role: 'Design Director' },
];

interface AboutTeamProps {
  className?: string;
}

export function AboutTeam({ className }: AboutTeamProps) {
  return (
    <section className={cn('py-12', className)}>
      <h2 className="text-3xl font-bold tracking-tight mb-8 text-center">
        Our Team
      </h2>
      <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
        {team.map((member) => (
          <div key={member.name} className="text-center">
            <div className="w-24 h-24 rounded-full bg-muted mx-auto mb-4" />
            <h3 className="font-semibold">{member.name}</h3>
            <p className="text-sm text-muted-foreground">{member.role}</p>
          </div>
        ))}
      </div>
    </section>
  );
}
