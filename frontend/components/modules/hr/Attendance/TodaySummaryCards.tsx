'use client';

import { Card, CardContent } from '@/components/ui/card';
import { UserCheck, UserX, Clock } from 'lucide-react';

interface TodaySummaryCardsProps {
  presentCount: number;
  absentCount: number;
  lateCount: number;
  totalEmployees: number;
}

export function TodaySummaryCards({
  presentCount,
  absentCount,
  lateCount,
  totalEmployees,
}: TodaySummaryCardsProps) {
  const presentPct = totalEmployees > 0 ? Math.round((presentCount / totalEmployees) * 100) : 0;
  const absentPct = totalEmployees > 0 ? Math.round((absentCount / totalEmployees) * 100) : 0;
  const latePct = totalEmployees > 0 ? Math.round((lateCount / totalEmployees) * 100) : 0;

  const cards = [
    {
      title: 'Present',
      value: presentCount,
      percentage: presentPct,
      icon: UserCheck,
      iconColor: 'text-green-500',
      bgColor: 'bg-green-50 dark:bg-green-950',
    },
    {
      title: 'Absent',
      value: absentCount,
      percentage: absentPct,
      icon: UserX,
      iconColor: 'text-red-500',
      bgColor: 'bg-red-50 dark:bg-red-950',
    },
    {
      title: 'Late',
      value: lateCount,
      percentage: latePct,
      icon: Clock,
      iconColor: 'text-yellow-500',
      bgColor: 'bg-yellow-50 dark:bg-yellow-950',
    },
  ];

  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardContent className="flex items-center gap-4 p-6">
            <div className={`rounded-lg p-3 ${card.bgColor}`}>
              <card.icon className={`h-6 w-6 ${card.iconColor}`} />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{card.title}</p>
              <p className="text-2xl font-bold">{card.value}</p>
              <p className="text-xs text-muted-foreground">{card.percentage}% of total</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
