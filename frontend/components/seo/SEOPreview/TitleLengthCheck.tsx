'use client';

import { Badge } from '@/components/ui/badge';
import { Progress } from '@/components/ui/progress';
import { cn } from '@/lib/utils';
import { SEO_TEST_IDS } from '@/components/seo/SEOTestIds';

interface TitleLengthCheckProps {
  title: string;
  maxLength?: number;
}

export function TitleLengthCheck({ title, maxLength = 70 }: TitleLengthCheckProps) {
  const length = title.length;
  const percentage = Math.min((length / maxLength) * 100, 100);

  const status = length <= 60 ? 'good' : length <= 70 ? 'warning' : 'bad';

  const colorClass = {
    good: 'text-green-600',
    warning: 'text-yellow-600',
    bad: 'text-red-600',
  }[status];

  const badgeVariant = {
    good: 'default' as const,
    warning: 'secondary' as const,
    bad: 'destructive' as const,
  }[status];

  const progressClass = {
    good: '[&>div]:bg-green-500',
    warning: '[&>div]:bg-yellow-500',
    bad: '[&>div]:bg-red-500',
  }[status];

  return (
    <div className="space-y-1" data-testid={SEO_TEST_IDS.titleLength}>
      <div className="flex items-center justify-between text-sm">
        <span className="text-muted-foreground">Title Length</span>
        <div className="flex items-center gap-2">
          <span className={cn('font-medium', colorClass)}>
            {length} / {maxLength}
          </span>
          <Badge variant={badgeVariant}>
            {status === 'good' ? 'Good' : status === 'warning' ? 'Warning' : 'Too Long'}
          </Badge>
        </div>
      </div>
      <Progress value={percentage} className={cn('h-2', progressClass)} />
    </div>
  );
}
